import logging
import os
from datetime import datetime

import mpld3
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from mpld3 import plugins

from lib.API import API


class StatisticManager:
    def __init__(self, teams_name: list, downtime_count: int, services: list):
        self.teams = teams_name
        self.downtime_count = downtime_count
        self.services = services
        self.base_path = os.path.abspath(os.getcwd())
        self.api = API()
        self.init_directory()
        self.file_report = self.init_file_report()

        self.total_flags_lost = {team: {service: 0 for service in self.services} for team in teams_name}
        self.total_flags_submitted = {team: {service: 0 for service in self.services} for team in teams_name}
        self.max_score = {team: {} for team in teams_name}
        self.min_score = {team: {} for team in teams_name}
        self.max_score_service = {team: {} for team in teams_name}
        self.min_score_service = {team: {} for team in teams_name}
        self.min_sla = {team: {} for team in teams_name}
        self.max_rank = {team: {} for team in teams_name}
        self.min_rank = {team: {} for team in teams_name}

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
            self.gen_teams_rank_plot(team)
        logging.info(f"Statistic Generated")

    def generate_report(self) -> None:
        logging.info("Generating report")
        for team in self.teams:
            self.file_report.write(f"""
## Team: {team}


### Panoramic:

- **Max total score:** {self.max_score[team]}
- **Min total score:** {self.min_score[team]}
- **Max total rank:** {self.max_rank[team]}
- **Min total rank:** {self.min_rank[team]}
- **Total Flags submitted**: {sum(self.total_flags_submitted[team].values())}
- **Total Flags lost**: {sum(self.total_flags_lost[team].values())}
- **Flags submitted:** {self.format_results(self.total_flags_submitted, team)}
- **Flag lost:** {self.format_results(self.total_flags_lost, team)}
- **Min sla:** {self.format_results(self.min_sla, team)}
- **Max score for service:** {self.format_results(self.max_score_service, team)}
- **Min score for service:** {self.format_results(self.min_score_service, team)}
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

    def fetch_service_data(self):
        pass

    @staticmethod
    def format_label(title: str) -> None:

        plt.xlabel('Time')
        plt.ylabel('Score')
        plt.title(title)
        plt.grid(True)
        plt.legend()

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

    def fetch_score_team(self, team_name: str) -> list[int]:
        service_data = self.api.get_team_chart(team_name)

        score_team = []

        for round in range(int(service_data['rounds'] + 1)):
            score_team.append(0)
            for index, service in enumerate(self.services):
                score_team[round] += service_data['services'][index]['score'][round]

        return score_team

    def gen_teams_services_score_plot(self, team_name: str) -> None:
        service_data = self.api.get_team_chart(team_name)
        for index, service in enumerate(self.services):
            self.max_score_service[team_name][service] = int(max(service_data['services'][index]['score']))
            self.min_score_service[team_name][service] = int(min(service_data['services'][index]['score']))

        fig = self.create_plot_service_data(title=f"Services score: {team_name}", service_data=service_data,
                                            value="score")
        self.save_plot(fig, team_name, "team_services_score")

    def fetch_sla_service(self, team_name: str) -> dict:
        sla_data = self.api.get_team_table(team_name)

        rounds = len(sla_data['rounds'])

        sla_service = {service: [] for service in self.services}

        counters = {service: 0 for service in self.services}

        for round in range(rounds):
            for index, name_service in enumerate(self.services):
                service = sla_data['rounds'][round]['services'][index]
                if all(check['exitCode'] == 101 for check in service['checks']):
                    counters[name_service] += 1

                logging.debug(f"Service: {service['shortname']} | {counters[name_service]} / {round + 1}")
                sla_service[service['shortname']].append((counters[name_service] / (round + 1)) * 100)

        logging.debug(sla_service)

        return sla_service

    def gen_sla_service_score_plot(self, team_name: str) -> None:
        service_data = self.fetch_sla_service(team_name=team_name)

        for service in self.services:
            self.min_sla[team_name][service] = int(min(service_data[service]))

        fig = self.create_plot_service_sla(title=f"Sla value: {team_name}", service_data=service_data)
        self.save_plot(fig, team_name, "sla")

    def gen_teams_score_plot(self, team_name: str) -> None:
        team_data = self.fetch_score_team(team_name=team_name)
        logging.debug(team_name)

        logging.debug(f"Data fetched: {len(team_data)}")

        self.max_score[team_name] = max(team_data)
        self.min_score[team_name] = min(team_data)

        fig = self.create_plot_team(team_data, team_name)
        self.save_plot(fig, team_name, "team_score")

        plt.close()

    def gen_teams_rank_plot(self, team_name: str) -> None:
        team_data = self.api.get_team_table(team_name)
        logging.debug(team_name)

        logging.debug(f"Data fetched: {len(team_data)}")

        team_data = [round['position'] for round in team_data['rounds']]

        self.max_rank[team_name] = int(max(team_data))
        self.min_rank[team_name] = int(min(team_data))

        fig = self.create_plot_team(team_data, 'position')
        self.save_plot(fig, team_name, "rank_team")

        plt.close()

    def gen_flags_lost_service_score(self, team_name: str) -> None:
        service_data = self.api.get_team_table(team_name)

        for index, service in enumerate(self.services):
            self.total_flags_lost[team_name][service] += int(
                service_data['rounds'][-1]['services'][index]['lost'])

        fig = self.create_plot_lost_stolen_data(title=f"Flags lost: {team_name}", service_data=service_data,
                                                value="lost")
        self.save_plot(fig, team_name, "flags_lost")

    def gen_flags_submitted_service_score(self, team_name: str) -> None:
        service_data = self.api.get_team_table(team_name)

        for index, service in enumerate(self.services):
            self.total_flags_submitted[team_name][service] += int(
                service_data['rounds'][-1]['services'][index]['stolen'])

        fig = self.create_plot_lost_stolen_data(title=f"Flags submitted: {team_name}", service_data=service_data,
                                                value="stolen")
        self.save_plot(fig, team_name, "flags_submitted")

    # * ------------------ Plot creation  ------------------
    def create_plot_service_data(self, service_data: dict, title: str, value) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        rounds = [x for x in range(int(service_data['rounds'] + 1))]

        lines = []
        labels = []
        for index, service in enumerate(self.services):
            line, = ax.plot(rounds, service_data['services'][index][value], label=service, alpha=0.6)
            lines.append(line)
            labels.append(service)

        plt.ylim(bottom=0)

        plt.grid(visible=True, which='both', color='gray', linestyle='-', linewidth=0.5)

        self.format_label(title)

        interactive_legend = plugins.InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0, alpha_over=1.0)

        plugins.connect(fig, interactive_legend)

        return fig

    def create_plot_lost_stolen_data(self, service_data: dict, title: str, value: str) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        rounds = [x for x in range(len(service_data['rounds']))]

        lines = []
        labels = []
        for index, service in enumerate(self.services):
            data = [service_data['rounds'][x]['services'][index][value] for x in range(len(service_data['rounds']))]
            line, = ax.plot(rounds, data, label=service, alpha=0.6)
            lines.append(line)
            labels.append(service)

        plt.ylim(bottom=0)

        plt.grid(visible=True, which='both', color='gray', linestyle='-', linewidth=0.5)

        self.format_label(title)

        interactive_legend = plugins.InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0, alpha_over=1.0)

        plugins.connect(fig, interactive_legend)

        return fig

    def create_plot_service_sla(self, service_data: dict, title: str) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        lines = []
        labels = []
        for index, service in enumerate(self.services):
            rounds = [x for x in range(int(len(service_data[service])))]
            line, = ax.plot(rounds, service_data[service], label=service, alpha=0.6)
            lines.append(line)
            labels.append(service)

        plt.ylim(bottom=0)

        plt.grid(visible=True, which='both', color='gray', linestyle='-', linewidth=0.5)

        self.format_label(title)

        interactive_legend = plugins.InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0, alpha_over=1.0)

        plugins.connect(fig, interactive_legend)

        return fig

    def create_plot_team(self, data: list, team_name: str) -> Figure:
        fig, ax = plt.subplots(figsize=(20, 10))

        rounds = [x for x in range(int(len(data)))]

        plt.plot(rounds, data, linestyle='-', marker='o', markersize=3, alpha=0.6, label='Score')
        plt.ylim(bottom=0)
        plt.grid(True)

        self.format_label(f'Score trend for Team {team_name}')

        return fig
