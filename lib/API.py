import logging

import requests


class API:
    def __init__(self):
        self.address = "ad.cyberchallenge.it"

    def get_team_chart(self, team: str) -> dict:
        """Get the chart of the team from the API.
        Args:
            team: str: Name of the team

        Returns:
            dict: Data of the team
        """
        request = requests.get(f"http://{self.address}/api/scoreboard/team/chart/{team}")
        if request.status_code == 200:
            return request.json()

        logging.error(
            f"Error in the request to the API for the team chart | status: {request.status_code} | Error: {request.text}")

        exit(request.status_code)

    def get_team_table(self, team: str) -> dict:
        """Get the table of the team from the API.

        Args:
            team: str: Name of the team

        Returns:
            dict: Data of the team
        """

        request = requests.get(f"http://{self.address}/api/scoreboard/team/table/{team}")
        if request.status_code == 200:
            return request.json()

        logging.error(
            f"Error in the request to the API for the team table | status: {request.status_code} | Error: {request.text}")

        exit(request.status_code)

    def get_global_chart(self, round_number: int) -> dict:
        """Get the chart of the global scoreboard from the API.

        Args:
            round_number:

        Returns:
            dict: Data of the global scoreboard
        """
        request = requests.get(f"http://{self.address}/api/scoreboard/chart/{round_number}")
        if request.status_code == 200:
            return request.json()

        logging.error(
            f"Error in the request to the API for the chart  | status: {request.status_code} | Error: {request.text}")

        exit(request.status_code)

    def get_global_table(self, round_number: int) -> dict:
        """Get the table of the global scoreboard from the API.
        Args:
            round_number: int: Number of the round

        Returns:
            dict: Data of the global scoreboard
        """

        request = requests.get(f"http://{self.address}/api/scoreboard/table/{round_number}")
        if request.status_code == 200:
            return request.json()

        logging.error(
            f"Error in the request to the API for the chart  | status: {request.status_code} | Error: {request.text}")

        exit(request.status_code)

    def get_score_team(self, team: str, services: list) -> list[int]:
        """Get the score of the team in the services.
        Args:
            team: str: Name of the team
            services: list: List of the services

        Returns:
            list: List of team scores
        """

        service_data = self.get_team_chart(team)

        score_team = []

        for round in range(int(service_data['rounds'] + 1)):
            score_team.append(0)
            for index, service in enumerate(services):
                score_team[round] += service_data['services'][index]['score'][round]

        return score_team

    def get_score_service(self, team: str, services: list) -> dict[str, list[int]]:
        """Score the team's services.
        Args:
            team: str: Name of the team
            services: list: List of the services

        Returns:
            dict: Service Score Dictionary
        """

        data = self.get_team_chart(team)

        score_service = {service: [] for service in services}

        for index, service in enumerate(services):
            for round in range(int(data['rounds'] + 1)):
                score_service[service].append(data['services'][index]['score'][round])

        return score_service

    def get_round(self, team: str) -> int:
        """Get the round of the team.
        Args:
            team: str: Name of the team

        Returns:
            int: Round of the team
        """

        return self.get_team_chart(team=team)['rounds']

    def get_sla_services(self, team: str, services: list[str], rounds: list[int]) -> dict[str, list[float]]:
        """Get the SLA of the team's services.
        Args:
            team: str: Name of the team
            services: list: List of services
            rounds: list: List of the rounds

        Returns:
            dict: SLA Service Dictionary
        """

        sla_data = self.get_team_table(team)

        sla_service = {service: [] for service in services}
        counters = {service: 0 for service in services}

        for round in rounds:
            for index, name_service in enumerate(services):
                service = sla_data['rounds'][round]['services'][index]
                if all(check['exitCode'] == 101 for check in service['checks']):
                    counters[name_service] += 1

                logging.debug(f"Service: {service['shortname']} | {counters[name_service]} / {round + 1}")
                sla_service[service['shortname']].append((counters[name_service] / (round + 1)) * 100)

        logging.debug(sla_service)

        return sla_service

    # True for stolen, False for lost
    def get_flags_services(self, team: str, services: list[str], rounds: list[int], stolen_lost: bool) -> dict[
        str, list[int]]:
        """Dictionary of Service Flags

        Args:
            team: str: Name of the team
            services: list: List of services
            rounds: list: List of the rounds
            stolen_lost: bool: True for stolen, False for lost

        Returns:
            dict: Dictionary of Service Flags
        """

        service_data = self.get_team_table(team)

        flags = {service: [] for service in services}

        for index, service in enumerate(services):
            for round in rounds:
                flags[service].append(
                    service_data['rounds'][round]['services'][index]['stolen' if stolen_lost else 'lost'])

        return flags
