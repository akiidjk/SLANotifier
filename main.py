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
        self.notified = {}
        self.create_report = create_report
        self.downtime_count = 0
        self.services = []
        self.exec_counter = 20
        self.api = API()

    @staticmethod
    def notify(name_service: str, team_name: str) -> None:
        notification.notify(
            title='Alert',
            message=f'The service: {name_service} is down for target {team_name} | {datetime.now().strftime("%H:%M:%S")}',
            timeout=10
        )
        logging.info(
            f'Notification sent for service {name_service} in team {team_name}.')

    def check_notify(self, services_status: list, team_name: str) -> None:
        logging.info("Controlling the service...")
        service_down = False
        down_services = []

        for service in services_status:
            if service['exitCode'] != 101:
                service_down = True
                down_services.append(service['name_service'])
                self.downtime_count += 1
                logging.warning(
                    f"Service {service['name_service']} is down | {service['stdout']} | {service['action']} | {service['exitCode']}")
                if not self.notified[team_name]:
                    self.notify(name_service=service['name_service'], team_name=team_name)

        if service_down:
            self.notified[team_name] = True
            logging.warning(f"Some service are down: {down_services}")
        else:
            self.notified[team_name] = False
            logging.info(f'All service are UP.')
        logging.debug(f"{self.notified}")
        logging.info("Control ended!")

    def get_teams_info(self) -> list[dict]:
        data = []
        for team in self.target_team:
            data.append(self.api.get_team_table(team))
        return data

    def check_status(self, team_data: dict) -> list[dict[str, Any]]:
        # last_round = team_data['rounds'][-1]
        last_round = team_data['rounds'][self.exec_counter]
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

    def run(self, repeat_after: int) -> tuple[int, list[Any]]:
        logging.info("Starting the script...")
        logging.info("Ctrl-C for exit the execution")

        logging.debug(f"Targets {self.target_team}")

        try:
            while True:
                self.exec_counter += 1
                logging.info(f"Number of execution: {self.exec_counter}")
                teams_data = self.get_teams_info()
                self.services = [service['shortname'] for service in
                                 teams_data[0]['services']]  # For mapping the services

                logging.debug("Teams fetched:" + str(len(teams_data)))
                logging.debug(f"{self.services = }")

                for team in teams_data:
                    logging.info(f"Team: {team['teamName']}")
                    logging.debug(f"Found round: {len(team['rounds'])}")

                    status_report = self.check_status(team)
                    self.check_notify(status_report, team['teamName'])

                logging.info(f"Waiting {repeat_after}s before restart")
                time.sleep(repeat_after)
        except KeyboardInterrupt:
            logging.info("Stopping script...")
            return self.downtime_count, self.services


if __name__ == '__main__':
    # ! All parameters in config.json
    colorama.init(autoreset=True)
    logging.info("Cleaning db")
    notification.notify(
        title='Check notification',
        message=f'This notification is only for check the notification system',
        timeout=10
    )

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
            "No targets found | The target is the university you want to track, and it must match the name on the "
            "leaderboard.")
        exit(1)

    sla = SLANotifier(target_team=targets, create_report=create_report)
    downtime_count, services = sla.run(reload)

    if create_report:
        logging.info("Generating plot")
        statistic = StatisticManager(teams_name=targets, downtime_count=downtime_count, services=services)
        statistic.generate_statistic()
        statistic.generate_report()
        exit(0)
# * @akiidjk
