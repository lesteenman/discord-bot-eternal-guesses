#!/usr/bin/env python3
import json
import os
import pprint
from typing import Dict

import requests

COMMAND_OPTION_TYPE_SUB_COMMAND = 1
COMMAND_OPTION_TYPE_SUB_COMMAND_GROUP = 2
COMMAND_OPTION_TYPE_STRING = 3
COMMAND_OPTION_TYPE_INTEGER = 4
COMMAND_OPTION_TYPE_BOOLEAN = 5
COMMAND_OPTION_TYPE_USER = 6
COMMAND_OPTION_TYPE_CHANNEL = 7
COMMAND_OPTION_TYPE_ROLE = 8

PERMISSION_ADMINISTRATOR = 0x8


def delete_guild_command(command_id: int, config: Dict, guild_name: str):
    print("Creating guild command")
    url = "https://discord.com/api/v8/applications/{}/guilds/{}/commands/{}".format(
        config['DISCORD_APPLICATION_ID'],
        config[guild_name.upper() + '_GUILD_ID'],
        command_id
    )

    headers = {
        "Authorization": f"Bot {config['DISCORD_BOT_TOKEN']}"
    }

    response = requests.delete(url, headers=headers)
    if response.status_code > 201:
        raise Exception(f"unexpected status_code {response.status_code} received: '{response.text}'")


def create_guild_command(command: Dict, config: Dict, guild_name: str):
    print("Creating guild command")
    url = "https://discord.com/api/v8/applications/{}/guilds/{}/commands".format(
        config['DISCORD_APPLICATION_ID'],
        config[guild_name.upper() + '_GUILD_ID'],
    )

    headers = {
        "Authorization": f"Bot {config['DISCORD_BOT_TOKEN']}"
    }

    response = requests.post(url, headers=headers, json=command)
    print(response.text)
    if response.status_code >= 300:
        raise Exception(f"unexpected status_code {response.status_code} received: '{response.text}'")


def delete_command(command_id: int, config: Dict):
    print("Deleting application command")
    url = "https://discord.com/api/v8/applications/{}/commands/{}".format(
        config['DISCORD_APPLICATION_ID'],
        command_id
    )

    headers = {
        "Authorization": f"Bot {config['DISCORD_BOT_TOKEN']}"
    }

    response = requests.delete(url, headers=headers)
    if response.status_code >= 300:
        raise Exception(f"unexpected status_code {response.status_code} received: '{response.text}'")


def create_command(command: Dict, config: Dict):
    print("Creating application command")
    url = "https://discord.com/api/v8/applications/{}/commands".format(
        config['DISCORD_APPLICATION_ID'],
    )

    headers = {
        "Authorization": f"Bot {config['DISCORD_BOT_TOKEN']}"
    }

    response = requests.post(url, headers=headers, json=command)
    pprint.pprint(response.text)
    if response.status_code >= 300:
        raise Exception(f"unexpected status_code {response.status_code} received: '{response.text}'")


def get_commands(config: Dict):
    url = "https://discord.com/api/v8/applications/{}/commands".format(
        config['DISCORD_APPLICATION_ID'],
    )

    headers = {
        "Authorization": f"Bot {config['DISCORD_BOT_TOKEN']}"
    }

    response = requests.get(url, headers=headers)
    # pprint.pprint(response.text)
    if response.status_code >= 300:
        raise Exception(f"unexpected status_code {response.status_code} received: '{response.text}'")

    return response.json()



def register(config: Dict):
    commands = [
        {
            "name": "create-game",
            "description": "Create a guessing game",
            "default_member_permissions": f"{PERMISSION_ADMINISTRATOR}",
        },
        {
            "name": "list-games",
            "description": "List all guessing games",
            "default_member_permissions": f"{PERMISSION_ADMINISTRATOR}",
            "options": [
                {
                    "name": "include-closed",
                    "description": "Include closed games",
                    "type": COMMAND_OPTION_TYPE_BOOLEAN,
                    "required": False,
                }
            ]
        },
    ]

    for command in commands:
        create_command(command, config)


def get_config():
    try:
        with open('app_config.json', 'r') as config_file:
            return json.loads(config_file.read())
    except FileNotFoundError:
        return {
            "DISCORD_APPLICATION_ID": os.environ['DISCORD_APPLICATION_ID'],
            "DISCORD_BOT_TOKEN": os.environ['DISCORD_BOT_TOKEN'],
        }


if __name__ == "__main__":
    config = get_config()

    existing = get_commands(config)
    for command in existing:
        delete_command(command['id'], config)

    register(config)
