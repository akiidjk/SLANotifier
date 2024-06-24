import random
from datetime import datetime, timedelta

from faker import Faker

from lib.db_manager import DBManager
from lib.logger import logging


def generate_fake_data(num_teams, num_records_per_team):
    fake = Faker()
    records = []

    for _ in range(num_teams):
        team_name = fake.company()
        score_team = random.randint(50, 100_000)
        team_record = {
            'name_team': team_name,
            'score_team': score_team,
            'stats_service': []
        }

        for _ in range(num_records_per_team):
            service_name = fake.bs()
            score_service = random.randint(0, 10_000)
            flag_submitted = random.randint(0, 200_000)
            flags_lost = random.randint(0, 100_000)
            status = str(random.randint(0, 100)) + '%'
            is_down = random.randint(0, 1)
            timestamp = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()

            service_record = {
                'name_service': service_name,
                'score_service': score_service,
                'flag_submitted': flag_submitted,
                'flags_lost': flags_lost,
                'sla_value': status,
                'is_down': is_down,
                'timestamp': timestamp
            }
            team_record['stats_service'].append(service_record)

        records.append(team_record)

    return records


class Test:
    def __init__(self):
        pass

    def run(self):
        logging.info(f'Running test')
        db = DBManager()
        num_teams = 5
        num_records_per_team = 10
        ticks = 1000
        logging.info(f'Params: {num_teams = }, {num_records_per_team = }, {ticks = }')
        for tick in range(ticks):
            logging.info(f'Cycle {tick + 1} of {ticks}')
            fake_records = generate_fake_data(num_teams, num_records_per_team)
            db.insert_records(fake_records)
        logging.info(f'Test ended')


if __name__ == '__main__':
    Test().run()
