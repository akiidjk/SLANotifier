# SLANotifier

SLANotifier is a tool designed for Cyberchallange's A/D ctf that allows real-time notification of the status of its services. 

## Requirements

- Python
- Linux or Windows

## Installation

- Create a venv env with ``python -m venv env`` or ``python3 -m venv env``.
- Install the requirements with ``pip install -r requirements.txt``

## Configuration

In the file there are 4 params to configure:

- Log level (In logger.py): The possible log levels are [Debug,Info,Warning,Error,Critical].
- Services: The services must be set precisely, the numbers (the keys) must correspond to the indices of the order of the ranking, starting from the left, so the leftmost service will be 0.
- Target: The target is the university you want to track and it must match the name on the leaderboard.
- Reload: How often is the leaderboard reloaded




