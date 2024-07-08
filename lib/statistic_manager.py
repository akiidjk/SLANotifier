import logging
import os
from datetime import datetime

import mpld3
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from mpld3 import plugins

from lib.API import API


class StatisticManager:
    def __init__(self, teams_name: list, downtime_count: dict[str, int], services: list):
        self.teams = teams_name
        self.downtime_count = downtime_count
        self.services = services

        self.base_path = os.path.abspath(os.getcwd())
        self.init_directory()
        self.file_report = self.init_file_report()

        self.api = API()
        self.rounds = [round for round in range(self.api.get_round(self.teams[0]) + 1)]

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
        """Create the directory for the report"""

        dirs = ["plots_image", "plots_interactive"]

        path_report = os.path.join(self.base_path, "reports")
        os.mkdir(path_report) if not os.path.exists(path_report) else None

        for directory in dirs:
            path = os.path.join(self.base_path, "reports", directory)
            if not os.path.exists(path):
                os.mkdir(path)

    def init_file_report(self):
        """Create the file report"""

        path_file_report = os.path.join(self.base_path, "reports",
                                        f"report-{datetime.now().strftime("%d-%m-%y_%H-%M")}.md")
        file_report = open(path_file_report, "w")
        file_report.write(f"""
# Report statistic A/D {datetime.now().strftime("%d-%m-%y|%H:%M")}
        
**For disable this feature go in config.json and uncheck "report"**
        """)

        return file_report

    # * ------------------ Main functions  ------------------

    def generate_plots(self):
        """Generate the statistic for the teams"""
        logging.info("Generating Statistic")
        for team in self.teams:
            self.gen_teams_score_plot(team)
            self.gen_teams_services_score_plot(team)
            self.gen_sla_service_score_plot(team)
            self.gen_flags_stolen_service_plot(team)
            self.gen_flags_lost_service_plot(team)
            self.gen_teams_position_plot(team)
        logging.info(f"Statistic Generated")

    def generate_report(self) -> None:
        """Generate the report for the teams."""

        logging.info("Generating report")
        for team in self.teams:
            content = self.generate_team_content(team)
            self.file_report.write(content)
        logging.info(f"Report generated and saved in {os.path.abspath(self.file_report.name)}")

    def generate_team_content(self, team: str) -> str:
        """Generate the content of report for the team.
        Args:
            team: str: Name of the team

        Returns:
            str: Content of the report
        """
        content = self.generate_panoramic_section(team)
        content += self.generate_score_team_section(team)
        content += self.generate_score_service_section(team)
        content += self.generate_sla_service_section(team)
        content += self.generate_flag_lost_section(team)
        content += self.generate_flag_submitted_section(team)
        return content

    # * ------------------ Report content function  ------------------
    def generate_panoramic_section(self, team: str) -> str:
        return f"""
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
- **Numbers of downtime:** {self.downtime_count[team]}
"""

    @staticmethod
    def generate_score_team_section(team: str) -> str:
        return f"""
### Score Team

![plot_score]({os.path.join("/", "reports", "plots_image", f"plot-{team}-team_score.png")})

**Interactive (better visual)**: {os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-team_score.html"))}
"""

    @staticmethod
    def generate_score_service_section(team: str) -> str:
        return f"""     
### Score Service

![plot_score]({os.path.join("/", "reports", "plots_image", f"plot-{team}-team_services_score.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-team_services_score.html"))}

---      
"""

    @staticmethod
    def generate_sla_service_section(team: str) -> str:
        return f"""      
### Sla Service

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-sla.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-sla.html"))}

---
"""

    @staticmethod
    def generate_flag_lost_section(team: str) -> str:
        return f"""      
### Flag lost

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-flags_lost.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-flags_lost.html"))}

---
"""

    @staticmethod
    def generate_flag_submitted_section(team: str) -> str:
        return f"""      
### Flag submitted

![plot_sla]({os.path.join("/", "reports", "plots_image", f"plot-{team}-flags_submitted.png")})

**Interactive (better visual)**:{os.path.abspath(os.path.join("reports", "plots_interactive", f"plot-{team}-flags_submitted.html"))}

---
"""

    # * ------------------ Utils function  ------------------

    @staticmethod
    def format_results(results: dict, team: str) -> str:
        """Format the result for the report
        Args:
            results: dict: Result of the
            team: str: Name of the team

        Returns:
            str: Formatted result

        """
        formatted_result = " ".join(
            ["\n\t- " + key + ": " + str(results[team][key]) + ", " for key in results[team].keys()])
        return formatted_result

    @staticmethod
    def format_label(title: str) -> None:
        """Format the label of the plot.

        Args:
            title: str: Title of the plot
        """

        plt.xlabel('Round')
        plt.ylabel('Score')
        plt.title(title)
        plt.grid(True)
        plt.legend()

        plt.gcf().autofmt_xdate()

    def save_plot(self, fig: Figure, team: str, spec: str) -> None:
        """Save the plot in the directory.

        Args:
            fig: Figure: Figure to save
            team: str: Name of the team
            spec: str: Specification of the plot
        """

        html_str = mpld3.fig_to_html(fig)

        path_image = os.path.join(self.base_path, "reports", "plots_image", f"plot-{team}-{spec}.png")
        path_interactive = os.path.join(self.base_path, "reports", "plots_interactive", f"plot-{team}-{spec}.html")

        with open(path_interactive, "w") as f:
            f.write(html_str)

        plt.savefig(path_image)
        plt.close()

    # * ------------------ Generation of statistic  ------------------

    def gen_teams_services_score_plot(self, team: str) -> None:
        """Generate the plot for the score of the services
        Args:
            team: str: Name of the team
        """

        service_data = self.api.get_score_service(team=team, services=self.services)

        for service in self.services:
            self.max_score_service[team][service] = max(service_data[service])
            self.min_score_service[team][service] = min(service_data[service])

        fig = self.create_plot_service_data(title=f"Services score: {team}", service_data=service_data, )

        self.save_plot(fig, team, "team_services_score")

    def gen_sla_service_score_plot(self, team: str) -> None:
        """Generate the plot for the sla of the services
        Args:
            team: str: Name of the team
        """

        service_data = self.api.get_sla_services(team=team, services=self.services, rounds=self.rounds)

        for service in self.services:
            self.min_sla[team][service] = min(service_data[service])

        fig = self.create_plot_service_data(title=f"Sla value: {team}", service_data=service_data)
        self.save_plot(fig, team, "sla")

    def gen_teams_score_plot(self, team: str) -> None:
        """Generate the plot for the score of the team
        Args:
            team: str: Name of the team
        """

        team_data = self.api.get_score_team(team=team, services=self.services)

        self.max_score[team], self.min_score[team] = max(team_data), min(team_data)

        fig = self.create_plot(data=team_data, team=team, label="Score")
        self.save_plot(fig, team, "team_score")

        plt.close()

    def gen_teams_position_plot(self, team: str) -> None:
        """Generate the plot for the position (in the leaderboard) of the team
        Args:
            team: str: Name of the team
        """

        team_data = self.api.get_team_table(team)
        logging.debug(team)

        logging.debug(f"Data fetched: {len(team_data)}")

        team_data = [round['position'] for round in team_data['rounds']]

        self.max_rank[team] = max(team_data)
        self.min_rank[team] = min(team_data)

        fig = self.create_plot(data=team_data, team='position', label="Position")
        self.save_plot(fig, team, "rank_team")

        plt.close()

    def gen_flags_lost_service_plot(self, team: str) -> None:
        """Generate the plot for the flags lost by the team for the services
        Args:
            team: str: Name of the team
        """

        service_data = self.api.get_flags_services(team=team, services=self.services,
                                                   rounds=self.rounds, stolen_lost=False)

        for service in self.services:
            self.total_flags_lost[team][service] += service_data[service][-1]

        fig = self.create_plot_service_data(title=f"Flags lost: {team}", service_data=service_data)
        self.save_plot(fig, team, "flags_lost")

    def gen_flags_stolen_service_plot(self, team: str) -> None:
        """Generate the plot for the flags stolen by the team for the services
        Args:
            team: str: Name of the team

        """
        service_data = self.api.get_flags_services(team=team, services=self.services,
                                                   rounds=self.rounds, stolen_lost=True)

        for service in self.services:
            self.total_flags_submitted[team][service] += service_data[service][-1]

        fig = self.create_plot_service_data(title=f"Flags stolen: {team}", service_data=service_data)
        self.save_plot(fig, team, "flags_submitted")

    # * ------------------ Plot creation  ------------------
    def create_plot_service_data(self, service_data: dict, title: str) -> Figure:
        """Create the plot based on the single services
        Args:
            service_data: dict: Service data
            title: str: Title of the plot

        Returns:
            Figure: Figure of the plot created
        """

        fig, ax = plt.subplots(figsize=(20, 10))

        lines = []
        labels = []
        for service in self.services:
            line, = ax.plot(self.rounds, service_data[service], label=service, alpha=0.6)
            lines.append(line)
            labels.append(service)

        plt.ylim(bottom=0)

        plt.grid(visible=True, which='both', color='gray', linestyle='-', linewidth=0.5)

        self.format_label(title)

        interactive_legend = plugins.InteractiveLegendPlugin(lines, labels, alpha_unsel=0.0, alpha_over=1.0)

        plugins.connect(fig, interactive_legend)

        return fig

    def create_plot(self, data: list, team: str, label="") -> Figure:
        """Create the plot for based on the team general data
        Args:
            data: list: Data to plot
            team: str: Name of the team
            label: str: Label of the plot

        Returns:
            Figure: Figure of the plot created
        """

        fig, ax = plt.subplots(figsize=(20, 10))

        plt.plot(self.rounds, data, linestyle='-', marker='o', markersize=3, alpha=0.6, label=label)
        plt.ylim(bottom=0)
        plt.grid(True)

        self.format_label(f'Score trend for Team {team}')

        return fig
