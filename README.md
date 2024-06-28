# SLANotifier

SLANotifier is a tool written in Python to report the status of the CyberChallenge A/D services that I developed for the UNISA team, the tool was initially born only as a pop-up notification tool that signals when a service goes down, but later I wrote a part that can be activated or not that generates a report with the total statistics of the whole race, allowing after an analysis of the team's weaknesses and strengths.

## Requirements

- Python (3.12 >=)
  - For install python3.12 on linux install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) !!! Remind to install the [prerequisite](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) for pyenv
- Linux or Windows

## Installation

- Create a venv env with ``python -m venv env`` or ``python3 -m venv env``.
- Install the requirements with ``pip install -r requirements.txt``

## Usage

Run in the same directory of main.py

``python main.py -r`` ( -r for create a report)

## Note for use

To use the tool you need Python 3.12 (for a string interpolation problem if you change it you can also use it in 3.11 at your discretion)

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


