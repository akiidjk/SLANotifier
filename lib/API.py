import requests


class API:
    def __init__(self):
        self.address = "ad.cyberchallenge.it"

    def get_team_chart(self, team_name: str) -> dict:
        return requests.get(f"http://{self.address}/api/scoreboard/team/chart/{team_name}").json()

    def get_team_table(self, team_name: str) -> dict:
        return requests.get(f"http://{self.address}/api/scoreboard/team/table/{team_name}").json()

    def get_global_chart(self, round_number: int) -> dict:
        return requests.get(f"http://{self.address}/api/scoreboard/chart/{round_number}").json()

    def get_global_table(self, round_number: int) -> dict:
        return requests.get(f"http://{self.address}/api/scoreboard/table/{round_number}").json()
