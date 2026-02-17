from datetime import datetime as dt, timezone as tz
from typing import Optional, List
import requests
import json

from config import execute
import config


ID = {"team": "90181126619", "space": "90184131103"}


def team() -> Optional[dict]:
    response = requests.get(
        "https://api.clickup.com/api/v2/team",
        headers={"Authorization": config.CLICKUP_API_KEY},
    )
    if response.status_code == 200:
        for team in response.json()["teams"]:
            if str(team["id"]) == ID["team"]:
                return team
    return None


def team_members() -> List[dict]:
    members = []
    for member in team()["members"]:
        members.append(member["user"])
    return members


def convert_usernames_to_members(usernames: List[str]):
    members = []
    for username in usernames:
        member_name = execute(
            "SELECT name FROM members WHERE username = ?", (username.lower(),)
        ).fetchone()
        if member_name:
            member_name = member_name[0]
        else:
            return username

        for member in team_members():
            if member["username"] == member_name:
                members.append(member)
    return members


def space() -> Optional[dict]:
    response = requests.get(
        f"https://api.clickup.com/api/v2/team/{team()['id']}/space",
        headers={"Authorization": config.CLICKUP_API_KEY},
    )
    if response.status_code == 200:
        for space in response.json()["spaces"]:
            if str(space["id"]) == ID["space"]:
                return space
    return None


def folder() -> Optional[dict]:
    folder_name = execute("SELECT value FROM data WHERE key=?", ("folder",)).fetchone()[
        0
    ]
    response = requests.get(
        f"https://api.clickup.com/api/v2/space/{space()['id']}/folder",
        headers={"Authorization": config.CLICKUP_API_KEY},
    )
    if response.status_code == 200:
        for folder in response.json()["folders"]:
            if folder["name"] == folder_name:
                return folder
    return None


def list() -> Optional[dict]:
    list_name = execute("SELECT value FROM data WHERE key=?", ("list",)).fetchone()[0]

    for list in folder()["lists"]:
        if list["name"] == list_name:
            return list
    return None


def new_task(name: str, description: str, users: List[str], deadline: str, is_task_complete: bool):
    members = convert_usernames_to_members(users)
    if isinstance(members, str):
        raise Exception(f"A member {members} not found")
    assignees = [m["id"] for m in members]
    print('Assignees:', assignees)

    if deadline != "":
        try:
            due_day = (
                dt.strptime(deadline, "%d.%m").replace(year=dt.now().year).timestamp()
            )
        except ValueError:
            raise Exception(f"Wrong deadline format: '{deadline}' (it's not 'DD.MM')")
    else:
        due_day = dt.now().replace(hour=23, minute=59, second=59).timestamp()

    response = requests.post(
        f"https://api.clickup.com/api/v2/list/{list()['id']}/task",
        headers={
            "Authorization": config.CLICKUP_API_KEY,
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "name": name,
                "description": description,
                "assignees": assignees,
                "due_date": int(due_day * 1000),
                **({"status": "complete"} if is_task_complete else {})
            }
        ),
    )

    if response.status_code != 200:
        raise Exception(f"[CLICKUP {response.status_code}] {response.text}")
