# SLANotifier

SLANotifier is a tool designed for Cyberchallange's A/D ctf that allows real-time notification of the status of its
services.

## Requirements

- Python
- Linux or Windows

## Installation

- Create a venv env with ``python -m venv env`` or ``python3 -m venv env``.
- Install the requirements with ``pip install -r requirements.txt``

## Usage

Run in the same directory of main.py

``python main.py -r`` ( -r for create a report)

## Configuration

In the file config.json there are 5 params to configure:

- **Log level**: The possible log levels are [Debug,Info,Warning,Error,Critical].
- **Services**: The services must be set precisely, the numbers (the keys) must correspond to the indices of the order
  of
  the ranking, starting from the left, so the leftmost service will be 0.
- **Target**: The target is the university you want to track, and it must match the name on the leaderboard.
- **Reload**: How often is the leaderboard reloaded, I recommend using 120 because it is the seconds of a single tick
- **Report**: whether or not to save a statistical report in the A/D (this parameter can also be activated via line
  argument with the -r flag)


