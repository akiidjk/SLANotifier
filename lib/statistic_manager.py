import logging
import os
from datetime import datetime

import matplotlib.dates as mdates
import mpld3
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from mpld3 import plugins
from pandas import DataFrame

from lib.db_manager import DBManager


class StatisticManager:
    def __init__(self, teams_name: list, services_name: list, downtime_count: int):
        self.db = DBManager()
        self.teams = teams_name
        self.services = services_name
        self.downtime_count = downtime_count
        self.base_path = os.path.abspath(os.getcwd())

        self.init_directory()
        self.file_report = self.init_file_report()

        self.total_flags_lost = {team: {} for team in teams_name}
        self.total_flags_submitted = {team: {} for team in teams_name}
        self.max_score = {team: {} for team in teams_name}
        self.min_score = {team: {} for team in teams_name}
        self.max_score_service = {team: {} for team in teams_name}
        self.min_score_service = {team: {} for team in teams_name}
        self.min_sla = {team: {} for team in teams_name}

    # * ------------------ Init functions  ------------------

    def init_directory(self):
        dirs = ["plots_image", "plots_interactive"]

        path_report = os.path.join(self.base_path, "reports")
        os.mkdir(path_report) if not os.path.exists(path_report) else None

        for directory in dirs:
            path = os.path.join(self.base_path, "reports", directory)
            if not os.path.exists(path):
                os.mkdir(path)

    def init_file_report(self):
        path_file_report = os.path.join(self.base_path, "reports",
                                        f"report-{datetime.now().strftime("%d-%m-%y_%H-%M")}.md")
        file_report = open(path_file_report, "w")
        file_report.write(f"""
# Report statistic A/D {datetime.now().strftime("%d-%m-%y|%H:%M")}
        
**For disable this feature go in config.json and uncheck "report"**
        """)

        return file_report

    # * ------------------ Main functions  ------------------

    def generate_statistic(self):
        logging.info("Generating Statistic")
        for team in self.teams:
            self.gen_teams_score_plot(team)
            self.gen_teams_services_score_plot(team)
            self.gen_sla_service_score_plot(team)
            self.gen_flags_submitted_service_score(team)
            self.gen_flags_lost_service_score(team)
        logging.info(f"Statistic Generated")

    def generate_report(self) -> None:
        logging.info("Generating report")
        for team in self.teams:
            self.file_report.write(f"""
## Team: {team}


### Panoramic:

- **Max total score:** {self.max_score[team]}
- **Min total score:** {self.min_score[team]}
- **Total Flags submitted**: {sum(self.total_flags_submitted[team].values())}
- **Total Flags lost**: {sum(self.total_flags_lost[team].values())}
- **Flags submitted:** {self.format_results(self.total_flags_submitted, team)}
- **Flag lost:** {self.format_results(self.total_flags_lost, team)}
- **Min sla:** {self.format_results(self.min_sla, team)}
- **Max score for service:** {self.format_results(self.max_score_service, team)}
- **Min score:** {self.format_results(self.min_score_service, team)}
- **Numbers of downtime:** {self.downtime_count}

### Score Team

![plot_score]({os.path.join("/", "reports", "plots_image", f"plot-{team}-team_score.png")})

**Interactive (better visual)**: {os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-team_score.html"))}

---

### Score Service

![plot_score]({os.path.join("/", "reports", "plots_image", f"plot-{team}-team_services_score.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-team_services_score.html"))}

---

### Sla Service

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-sla.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-sla.html"))}

---

### Flag lost

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-flags_lost.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-flags_lost.html"))}

---

### Flag submitted 

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-flags_submitted.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-flags_submitted.html"))}

---

""")

        logging.info(
            f"Report generated and save in {os.path.abspath(os.path.join(self.base_path, "reports", self.file_report.name))}")

    # * ------------------ Utils function  ------------------

    @staticmethod
    def format_results(results: dict, team: str):
        formatted_result = " ".join(
            ["\n\t- " + key + ": " + str(results[team][key]) + ", " for key in results[team].keys()])
        return formatted_result

    def fetch_service_data(self, team_name: str, columns: tuple) -> dict[str, DataFrame]:
        service_data = {}

        for service_name in self.services:
            data = self.db.fetch_by_team_service(team=team_name, service=service_name, columns=columns)
            logging.debug(f"{len(data)}, {service_name}, {team_name}, {columns}")
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            service_data[service_name] = df

        return service_data

    @staticmethod
    def format_label(title: str) -> None:

        plt.xlabel('Time')
        plt.ylabel('Score')
        plt.title(title)
        plt.grid(True)
        plt.legend()

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.gcf().autofmt_xdate()

    def save_plot(self, fig, team_name: str, spec: str) -> None:
        html_str = mpld3.fig_to_html(fig)

        path_image = os.path.join(self.base_path, "reports", "plots_image", f"plot-{team_name}-{spec}.png")
        path_interactive = os.path.join(self.base_path, "reports", "plots_interactive", f"plot-{team_name}-{spec}.html")

        with open(path_interactive, "w") as f:
            f.write(html_str)

        plt.savefig(path_image)
        plt.close()

    # * ------------------ Generation of statistic  ------------------

    def gen_teams_services_score_plot(self, team_name: str) -> None:
        service_data = self.fetch_service_data(team_name, columns=("score_service",))

        for service in service_data:
            self.max_score_service[team_name][service] = int(service_data[service]['score_service'].max())
            self.min_score_service[team_name][service] = int(service_data[service]['score_service'].min())

        fig = self.create_plot_service_data(title=f"Services score: {team_name}", service_data=service_data,
                                            columns="score_service")
        self.save_plot(fig, team_name, "team_services_score")

    def gen_sla_service_score_plot(self, team_name: str) -> None:
        service_data = self.fetch_service_data(team_name=team_name, columns=("sla_value",))

        for service in service_data:
            self.min_sla[team_name][service] = int(service_data[service]['sla_value'].min())

        fig = self.create_plot_service_data(title=f"Sla value: {team_name}", service_data=service_data,
                                            columns="sla_value")
        self.save_plot(fig, team_name, "sla")

    def gen_teams_score_plot(self, team_name: str) -> None:
        data = self.db.fetch_by_team(team=team_name, columns=("score_team",))

        logging.debug(f"Data fetched: {len(data)}")

        data_frame = pd.DataFrame(data)
        data_frame['timestamp'] = pd.to_datetime(data_frame['timestamp'])

        self.max_score[team_name] = int(data_frame['score_team'].max())
        self.min_score[team_name] = int(data_frame['score_team'].min())

        fig = self.create_plot_score_team(data_frame, team_name)
        self.save_plot(fig, team_name, "team_score")

        plt.close()

    def gen_flags_lost_service_score(self, team_name: str) -> None:
        service_data = self.fetch_service_data(team_name=team_name, columns=("flags_lost",))

        for service in self.services:
            self.total_flags_lost[team_name][service] = int(service_data[service]['flags_lost'].iloc[-1])

        fig = self.create_plot_service_data(title=f"Flags lost: {team_name}", service_data=service_data,
                                            columns="flags_lost")
        self.save_plot(fig, team_name, "flags_lost")

    def gen_flags_submitted_service_score(self, team_name: str) -> None:
        service_data = self.fetch_service_data(team_name=team_name, columns=("flags_submitted",))

        for service in self.services:
            self.total_flags_submitted[team_name][service] = int(service_data[service]['flags_submitted'].iloc[-1])

        fig = self.create_plot_service_data(title=f"Flags submitted: {team_name}", service_data=service_data,
                                            columns="flags_submitted")
        self.save_plot(fig, team_name, "flags_submitted")

    # * ------------------ Plot creation  ------------------
    def create_plot_service_data(self, service_data: dict[str, DataFrame], columns: str, title: str) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        timestamps = service_data[self.services[0]]['timestamp']

        lines = []
        labels = []
        for service in self.services:
            line, = ax.plot(timestamps, service_data[service][columns], label=service, alpha=0.6)
            lines.append(line)
            labels.append(service)

        plt.ylim(bottom=0)

        plt.grid(visible=True, which='both', color='gray', linestyle='-', linewidth=0.5)

        self.format_label(title)

        interactive_legend = plugins.InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0, alpha_over=1.0)

        plugins.connect(fig, interactive_legend)

        return fig

    def create_plot_score_team(self, df: DataFrame, team_name: str) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        plt.plot(df['timestamp'], df['score_team'], linestyle='-', marker='o', markersize=3, alpha=0.6, label='Score')
        plt.ylim(bottom=0)
        plt.grid(True)

        self.format_label(f'Score trend for Team {team_name}')

        return fig
