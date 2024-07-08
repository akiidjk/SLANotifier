import os
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from lib.db_manager import DBManager
from lib.logger import logging
from lib.statistic_manager import StatisticManager

teams_name = ["unisa"]
services_name = ['Inlook-1', 'Inlook-2', 'CCalendar-1', 'CCalendar-2', 'CCForms-1', 'CCForms-2', 'ExCCel-1', 'ExCCel-2']

score_tracker = [10_000 * len(services_name)] * len(teams_name)
sla_tracker = [[100] * len(services_name)] * len(teams_name)
flag_lost_tracker = [[0] * len(services_name)] * len(teams_name)
flag_submitted_tracker = [[0] * len(services_name)] * len(teams_name)


def divide_score_randomly(total, num_parts):
    if num_parts <= 0:
        raise ValueError("Number of parts must be greater than zero")
    if total <= 0:
        return [0] * num_parts
    if num_parts > total:
        raise ValueError("Number of parts must be less than or equal to the total")

    parts = sorted(random.sample(range(1, total), num_parts - 1))
    parts = [0] + parts + [total]
    return [parts[i + 1] - parts[i] for i in range(num_parts)]


def generate_realistic_score(start_value, num_records, max_change, max_value=None, decimal=False):
    if decimal:
        scores = [Decimal(start_value)]
    else:
        scores = [start_value]
    for _ in range(1, num_records):
        if decimal:
            change = Decimal(random.uniform(-max_change, max_change)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            new_value = max(Decimal('0.00'), scores[-1] + change)
        else:
            change = random.randint(-max_change, max_change)
            new_value = max(0, scores[-1] + change)

        if max_value:
            if decimal:
                new_value = min(Decimal(max_value), new_value)
            else:
                new_value = min(max_value, new_value)

        scores.append(new_value)

    return scores


def generate_fake_data(num_teams, num_records_per_team, timestamp):
    records = []
    for index in range(num_teams):
        team_record = {
            'name_team': teams_name[index],
            'score_team': score_tracker[index],
            'stats_service': []
        }
        scores = generate_realistic_score(score_tracker[index], num_records_per_team, max_change=5000)
        score_tracker[index] = scores[-1]
        service_scores = divide_score_randomly(score_tracker[index], len(services_name))

        for i in range(num_records_per_team):
            for j, service_name in enumerate(services_name):
                score_service = service_scores[j]
                is_down = random.randint(0, 1)

                sla = generate_realistic_score(sla_tracker[index][j], num_records_per_team, max_change=0.30,
                                               max_value=100.00, decimal=True)
                sla_tracker[index][j] = sla[-1]

                value = 10 * len(services_name) * len(teams_name)

                flag_lost_tracker[index][j] = flag_lost_tracker[index][j] + random.randint(0, value)
                flag_submitted_tracker[index][j] = flag_submitted_tracker[index][j] + random.randint(0, value)

                service_record = {
                    'name_service': service_name,
                    'score_service': score_service,
                    'flags_submitted': flag_submitted_tracker[index][j],
                    'flags_lost': flag_lost_tracker[index][j],
                    'sla_value': float(sla_tracker[index][j]),
                    'is_down': is_down,
                    'timestamp': timestamp
                }

                team_record['stats_service'].append(service_record)

            # Update team score for this record
            team_record['score_team'] = scores[i]

        records.append(team_record)

    return records


class Test:
    def __init__(self):
        self.db = DBManager()
        self.manager = StatisticManager(teams_name=teams_name, services=services_name, downtime_count=0)
        pass

    def generate_data(self, num_teams=10, num_records_per_team=10, ticks=1000):
        logging.info(f'Params: {num_teams = }, {num_records_per_team = }, {ticks = }')
        logging.info("Generating fake data")
        base_date = datetime(2024, 6, 26)
        for tick in range(ticks):
            logging.debug(f'Cycle {tick + 1} of {ticks}')
            fake_records = generate_fake_data(num_teams, num_records_per_team,
                                              timestamp=(base_date + timedelta(minutes=2 * (tick + 1))).isoformat())
            self.db.insert_records(fake_records)

    def run(self):
        logging.info(f'Running test')

        # self.generate_data(num_teams=len(teams_name), num_records_per_team=len(services_name), ticks=240)
        self.manager.generate_plots()
        self.manager.generate_report()
        # self.db.remove_db()
        logging.info(f'Test ended')


if __name__ == '__main__':
    logging.info(f'Waiting before starting test')
    logging.info(f"Pid: {os.getpid()}")
    time.sleep(5)
    Test().run()
