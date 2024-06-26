import time
from datetime import datetime
from typing import Any

import bs4
import colorama
from plyer import notification
from selenium import webdriver

from lib.db_manager import DBManager
from lib.logger import logging
from lib.statistic_manager import StatisticManager
from lib.utils import get_config

BASE_URL = "http://10.10.0.1/scoreboard"


class SLANotifier:

    def __init__(self, services: dict, save: bool, target_team: list[str] = None):
        self.services = services
        self.target_team = target_team
        self.notified = False
        self.save = save

        if save:
            self.dbmanager = DBManager()

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(options=options)

    def fetch_page_source(self, url: str) -> str:
        logging.info("Opening the browser")
        self.driver.get(url)
        logging.info("Loading content")
        time.sleep(2)
        logging.info("Content loaded")
        return self.driver.page_source

    def parse_teams_data(self, html: str) -> list[dict[str, list | int | list[dict[str, bool]]]] | int:
        logging.debug("Getting teams data")

        teams_data = []

        soup = bs4.BeautifulSoup(html, 'html.parser')
        tr_tags = soup.find_all('tr')

        logging.info(f"Found {len(tr_tags)} teams")

        if len(tr_tags) == 0:
            return 404

        for index, tr in enumerate(tr_tags):
            service_td = tr.find_all('td', class_="px-1 align-start text-start")
            team_name_spans = tr.find_all('span', class_='fw-bold')
            score_td = tr.find_all('td', class_='px-1 align-middle')

            team_names = [span.text for span in team_name_spans]

            if not any(target in team_names for target in self.target_team) and self.target_team is not None:
                continue

            scores = [td.text.strip() for td in score_td]

            stats_info = self.parse_service_stats(service_td)

            teams_data.append({
                "name": team_names,
                "index": index,
                "score": scores,
                "stats_service": stats_info
            })

        if self.save:
            logging.info("Saving data on database")
            self.dbmanager.insert_records(teams_data)

        return teams_data

    def parse_service_stats(self, service_td) -> list[dict[str, bool | Any]]:
        logging.debug("Getting service data")
        stats_info = []
        for index_service, service in enumerate(service_td):
            stats = service.find_all("div", class_="d-flex")
            is_down = any(button for button in service.find_all("button", class_="btn-danger"))

            score_service = [div.text.strip() for div in stats]

            stats_info.append({
                'name': self.services[str(index_service)],
                'score_service': int(score_service[0]),
                'flags_submitted': int(score_service[1]),
                'flags_lost': int(score_service[2]),
                'sla_value': score_service[3],
                'down': is_down,
                'timestamp': datetime.now().isoformat()
            })

        return stats_info

    def send_notify(self, teams: list) -> None:
        logging.info("Controlling the service...")
        service_down = False
        down_services = []
        for team in teams:
            for service in team['stats_service']:
                if service['down']:
                    service_down = True
                    if not self.notified:
                        notification.notify(
                            title='Alert',
                            message=f'The service: {service["name"]} is down for target {team["name"][0]} | {datetime.now().strftime("%H:%M:%S")}',
                            timeout=10
                        )
                        logging.info(f'Notification sent for service {service["name"]} in team {team["name"][0]}.')
                    down_services.append(service['name'])

        if service_down:
            self.notified = True
            logging.warning(f"Some service are down: {down_services}")
        else:
            self.notified = False
            logging.info(f'All service are UP.')

        logging.info("Control ended!")

    def run(self, repeat_after: int):
        logging.info("Starting the script...")
        logging.info("Ctrl-C for exit the execution")
        exec_count = 0

        logging.debug(f"Services {self.services}")
        logging.debug(f"Targets {self.target_team}")

        while True:
            exec_count += 1
            logging.info(f"Number of execution: {exec_count}")
            html = self.fetch_page_source(BASE_URL)
            teams_data = self.parse_teams_data(html)

            if teams_data != 404:
                if save:
                    self.dbmanager.insert_records(teams_data)
                self.send_notify(teams_data)
            else:
                logging.error("An error occurred in fetch of page")

            logging.debug(teams_data)
            time.sleep(repeat_after)


# ? Note si potrebbe cambiare la possibilità del salvataggio direttamente da riga di comando che da file config

if __name__ == '__main__':
    # ! All value in config.json
    colorama.init(autoreset=True)

    notification.notify(
        title='Check notification',
        message=f'This notification is only for check the notification system',
        timeout=10
    )

    _, services, targets, reload, save = get_config()

    if not services:
        logging.error(
            "No services found | The services must be set precisely, the numbers (the keys) must correspond to the indices of the order of the ranking, starting from the left, so the leftmost service will be 0.")
        exit(1)

    if targets is None:
        logging.error(
            "No targets found | The target is the university you want to track, and it must match the name on the leaderboard.")
        exit(1)

    sla = SLANotifier(services, targets, save)
    sla.run(reload)

    if save:
        # ! Operazioni sul DB e generazioni grafico
        logging.info("Generating plot")
        StatisticManager(targets, services)
        pass

# * @akiidjk
