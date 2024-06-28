import json
from typing import Any


def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    logging_level = config['logging_level']
    services = {int(key): value for key, value in config['services'].items()}
    targets = config['targets']
    reload = config['reload']
    report = config['report']

    return logging_level, services, targets, reload, report


def serialize(records: list) -> list[tuple]:
    serialized_records = []
    for record in records:
        for service in record['stats_service']:
            formatted_record = (
                record['name_team'],
                record['score_team'],
                service['name_service'],
                service['score_service'],
                service['flags_submitted'],
                service['flags_lost'],
                service['sla_value'],
                service['is_down'],
                service['timestamp']
            )
            serialized_records.append(formatted_record)

    return serialized_records


def deserialize(columns, records: list) -> list[dict[Any, Any]]:
    return [dict(zip(columns + ("timestamp",), row)) for row in records]
