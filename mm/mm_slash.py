"""Create slash commands based on available facts.

Unused for now but kept for the record.
"""
import json
import logging
from pathlib import Path
import requests
import os
import time
from urllib.parse import urljoin


logging.basicConfig(level=logging.DEBUG)

MYDIR = Path(__file__).parent.absolute()
# Directory where to look for json pre-generated files
JSON_DIR = MYDIR.parent / "src" / "_data" / "facts"

BASE_URL = "https://framateam.org/api/v4/"

# Web site url (where the json will be located)
TARGET_SITE = "https://mmouterde.github.io/regles-ultimate-fr/data/facts"

# mm parameters (taken from the env)
# thortles team_id = "3wu3mbytktbn3yktrn6898kifa"
MM_TEAM = os.environ.get("MM_TEAM", "Thortles")

MM_LOGIN = os.environ["MM_USERNAME"]
MM_PASSWORD = os.environ["MM_PASSWORD"]


def url_for(endpoint: str) -> str:
    global BASE_URL
    if endpoint.startswith("/"):
        endpoint = endpoint[1:]
    url = urljoin(BASE_URL, endpoint)
    print(f"-> url = {url}")
    return urljoin(BASE_URL, endpoint)


session = requests.session()

data = dict(
    login_id=MM_LOGIN,
    password=MM_PASSWORD,
)
headers = {
    "Content-Type": "application/json",
}

r = session.post(url_for("/users/login"), data=json.dumps(data), headers=headers)
r.raise_for_status()

# magic var for the following
token = r.headers["token"]
# can be found by listing the user's team
# carry the token for any subsequent request
headers.update({"Authorization": f"Bearer {token}"})

team = session.get(url_for(f"/teams/name/{MM_TEAM}"), headers=headers)
team.raise_for_status()
team = team.json()
team_id = team["id"]

# list all commands
commands = session.get(
    url_for(f"/commands"), headers=headers, params=dict(team_id=team_id)
)
commands.raise_for_status()
commands = commands.json()

# delete all of them
for c in commands:
    c_id = c["id"]
    if not c_id:
        continue
    print(f"deleting {c}")
    response = session.delete(url_for(f"/commands/{c_id}"), headers=headers)
    response.raise_for_status()
    # don't hit the rate limit...
    time.sleep(0.25)

# create them
# we list all the possible endpoint (the .json in the public dir)
for endpoint_file in JSON_DIR.rglob("*.json"):
    data = dict(
        team_id=team_id,
        method="G",
        # (stem) public/terrain.json -> u-terrain
        trigger=f"u-{endpoint_file.stem}",
        url=f"{TARGET_SITE}/{endpoint_file.name}",
        auto_complete=True,
    )
    print(data)
    slash = session.post(url_for("/commands"), data=json.dumps(data), headers=headers)
    slash.raise_for_status()
    # don't hit the rate limit...
    time.sleep(0.25)