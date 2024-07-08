import time
from datetime import datetime
from sys import argv
from typing import Any

import colorama
from plyer import notification

from lib.API import API
from lib.logger import logging
from lib.statistic_manager import StatisticManager
from lib.utils import get_config


class SLANotifier:

    def __init__(self, create_report: bool, target_team: list[str] = None):
        self.target_team = target_team
        self.create_report = create_report

        self.exec_counter = 0

        self.downtime_count = {team: 0 for team in target_team}
        self.notified = {team: False for team in target_team}
        self.services = []

        self.api = API()

    @staticmethod
    def notify(name_service: str, team: str) -> None:
        """Notify the user that a service is down
        Args:
            name_service: str: Name of the service
            team: str: Name of the team

        Returns:
            None
        """
        notification.notify(
            title='Alert',
            message=f'The service: {name_service} is down for target {team} | {datetime.now().strftime("%H:%M:%S")}',
            timeout=10
        )
        logging.info(
            f'Notification sent for service {name_service} in team {team}.')

    def check_notify(self, services_status: list, team: str) -> None:
        """Check the status of the services and notify if some service is down

        Args:
            services_status: list: List of the status of the services
            team:str: Name of the team

        Returns:
            None
        """

        logging.info("Controlling the service...")
        service_down = False
        down_services = []

        for service in services_status:
            if service['exitCode'] != 101:
                service_down = True
                down_services.append(service['name_service'])
                self.downtime_count[team] += 1
                logging.warning(
                    f"Service {service['name_service']} is down | {service['stdout']} | {service['action']} | {service['exitCode']}")

                if not self.notified[team]:
                    self.notify(name_service=service['name_service'], team=team)

        if service_down:
            self.notified[team] = True
            logging.warning(f"Some service are down: {down_services}")
        else:
            self.notified[team] = False
            logging.info(f'All service are UP.')
        logging.debug(f"{self.notified}")
        logging.info("Control ended!")

    def get_teams_data(self) -> list[dict]:
        """Get the data of the teams
        Returns:
            list: List of the data of the teams
        """

        data = []
        for team in self.target_team:
            data.append(self.api.get_team_table(team))
        return data

    @staticmethod
    def check_status(team_data: dict) -> list[dict[str, Any]]:
        last_round = team_data['rounds'][-1]
        # last_round = team_data['rounds'][self.exec_counter] # For testing
        status_report = []
        for service in last_round['services']:
            for check in service['checks']:
                if check['exitCode'] != 101:
                    status_report.append({
                        "name_service": service['shortname'],
                        "stdout": check['stdout'],
                        "action": check['action'],
                        "exitCode": check['exitCode']
                    })

        return status_report

    def run(self, repeat_after: int) -> tuple[dict[str | Any, int], list[Any]]:
        """Main method for start the execution of the script

        Args:
            repeat_after: int: Time to wait before restarting the check

        Returns:
            tuple: (int, list): Amount of downtime and list of services
        """

        logging.info("Starting the script...")
        logging.info("Ctrl-C for exit the execution")

        logging.debug(f"Targets {self.target_team}")

        try:
            while True:
                self.exec_counter += 1
                logging.info(f"Number of execution: {self.exec_counter}")
                teams_data = self.get_teams_data()
                self.services = [service['shortname'] for service in
                                 teams_data[0]['services']]  # For mapping the services

                for team in teams_data:
                    logging.debug(f"Found round: {len(team['rounds'])}")
                    logging.info(f"Team: {team['teamShortname']}")

                    status_report = self.check_status(team)
                    self.check_notify(status_report, team['teamShortname'])

                logging.info(f"Waiting {repeat_after}s before restart")
                time.sleep(repeat_after)
        except KeyboardInterrupt:
            logging.info("Stopping script...")
            return self.downtime_count, self.services


if __name__ == '__main__':
    # ! All parameters in config.json
    colorama.init(autoreset=True)

    try:
        notification.notify(
            title='SLA Notifier: Notification system',
            message='This is a test of the SLA notification system. It verifies that the notifications are visible and functioning correctly.',
            timeout=15
        )
    except Exception as e:
        logging.error(f"Error in the notification system: {e}")
        exit(1)

    _, targets, reload, create_report = get_config()

    logging.debug(targets)
    logging.debug(reload)
    logging.debug(create_report)

    try:
        create_report = True if argv[1] == '-r' else None
    except IndexError:
        pass

    if not targets:
        logging.error(
            "No targets found | The target is the team you want to track, and it must match the name on the leaderboard.")
        exit(1)

    sla = SLANotifier(target_team=targets, create_report=create_report)
    downtime_count, services = sla.run(reload)

    if create_report:
        logging.info("Generating plot")
        statistic = StatisticManager(teams_name=targets, downtime_count=downtime_count, services=services)
        statistic.generate_plots()
        statistic.generate_report()
        exit(0)

# * @akiidjk @SuperSimo0
