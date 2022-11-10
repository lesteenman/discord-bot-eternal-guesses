#!/usr/bin/env python3
import json
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
        # {
        #     "name": "modal",
        #     "description": "Test a modal",
        #     # "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #     # "options": [],
        # },
        # {
        #     "name": "message-with-buttons",
        #     "description": "Test a message with buttons",
        #     # "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #     # "options": [],
        # },
        {
            "name": "manage-game",
            "description": "Manage a guessing game",
            "options": [
                {
                    "name": "game-id",
                    "description": "The ID of the Eternal Guess game",
                    "type": COMMAND_OPTION_TYPE_STRING,
                    "required": True
                }
            ]
        },
        {
            "name": "create-game",
            "description": "Create a guessing game",
        },
        {
            "name": "guess",
            "description": "Submit your guess!",
            "options": [
                {
                    "name": "game-id",
                    "description": "The ID of the Eternal Guess game",
                    "type": COMMAND_OPTION_TYPE_STRING,
                    "required": True,
                },
                {
                    "name": "guess",
                    "description": "Your guess",
                    "type": COMMAND_OPTION_TYPE_STRING,
                    "required": True,
                }
            ]
        },
        # {
        #     "name": "eternal-guess",
        #     "description": "Management for the Eternal Guess bot.",
        #     "options": [
        #         {
        #             "name": "create",
        #             "description": "Set up an Eternal Guess game.",
        #             "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #             "options": [
        #                 {
        #                     "name": "game-id",
        #                     "description": "The ID of the Eternal Guess game. If omitted, will generate a random ID.",
        #                     "type": COMMAND_OPTION_TYPE_STRING,
        #                     "required": False,
        #                 },
        #                 {
        #                     "name": "title",
        #                     "description": "The (short) title of this game.",
        #                     "type": COMMAND_OPTION_TYPE_STRING,
        #                     "required": False,
        #                 },
        #                 {
        #                     "name": "description",
        #                     "description": "The (longer) description of this game.",
        #                     "type": COMMAND_OPTION_TYPE_STRING,
        #                     "required": False,
        #                 },
        #                 {
        #                     "name": "min",
        #                     "description": "The lowest guess allowed.",
        #                     "type": COMMAND_OPTION_TYPE_INTEGER,
        #                     "required": False,
        #                 },
        #                 {
        #                     "name": "max",
        #                     "description": "The highest guess allowed.",
        #                     "type": COMMAND_OPTION_TYPE_INTEGER,
        #                     "required": False,
        #                 },
        #             ],
        #         },
        #         {
        #             "name": "manage",
        #             "description": "Management for an Eternal Guess game. Only allowed by 'manage' roles and channels.",
        #             "type": COMMAND_OPTION_TYPE_SUB_COMMAND_GROUP,
        #             "options": [
        #                 {
        #                     "name": "post",
        #                     "description": "Post a list of the game's active guesses.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "game-id",
        #                             "description": "The ID of the Eternal Guess game",
        #                             "type": COMMAND_OPTION_TYPE_STRING,
        #                             "required": True,
        #                         },
        #                         {
        #                             "name": "channel",
        #                             "description": "Where to post the list. If omitted, will be posted in the current "
        #                                            "channel.",
        #                             "type": COMMAND_OPTION_TYPE_CHANNEL,
        #                             "required": False,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "close",
        #                     "description": "Closes new submissions for a game.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "game-id",
        #                             "description": "The ID of the Eternal Guess game",
        #                             "type": COMMAND_OPTION_TYPE_STRING,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "list-games",
        #                     "description": "Get a list of games.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "closed",
        #                             "description": "Whether to only find open or closed games. If empty, all games are "
        #                                            "returned.",
        #                             "type": COMMAND_OPTION_TYPE_BOOLEAN,
        #                             "required": False,
        #                         }
        #                     ]
        #                 },
        #                 {
        #                     "name": "delete-guess",
        #                     "description": "Delete a member's guess on a game.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "game-id",
        #                             "description": "The ID of the Eternal Guess game",
        #                             "type": COMMAND_OPTION_TYPE_STRING,
        #                             "required": True,
        #                         },
        #                         {
        #                             "name": "member",
        #                             "description": "The member whose guess to delete",
        #                             "type": COMMAND_OPTION_TYPE_USER,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "edit-guess",
        #                     "description": "Edit a member's guess on a game.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "game-id",
        #                             "description": "The ID of the Eternal Guess game",
        #                             "type": COMMAND_OPTION_TYPE_STRING,
        #                             "required": True,
        #                         },
        #                         {
        #                             "name": "member",
        #                             "description": "The member whose guess to change",
        #                             "type": COMMAND_OPTION_TYPE_USER,
        #                             "required": True,
        #                         },
        #                         {
        #                             "name": "guess",
        #                             "description": "The new guess",
        #                             "type": COMMAND_OPTION_TYPE_STRING,
        #                             "required": True,
        #                         },
        #                     ]
        #                 }
        #             ]
        #         },
        #         {
        #             "name": "admin",
        #             "description": "Admin options for the Eternal Guess game. Only allowed by admin users.",
        #             "type": COMMAND_OPTION_TYPE_SUB_COMMAND_GROUP,
        #             "options": [
        #                 {
        #                     "name": "info",
        #                     "description": "Lists the configuration for this Guild",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                 },
        #                 {
        #                     "name": "add-management-channel",
        #                     "description": "Adds a channel in which 'manage' options are allowed.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "channel",
        #                             "description": "The channel to add.",
        #                             "type": COMMAND_OPTION_TYPE_CHANNEL,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "remove-management-channel",
        #                     "description": "Removes a channel in which 'manage' options are allowed.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "channel",
        #                             "description": "The channel to remove.",
        #                             "type": COMMAND_OPTION_TYPE_CHANNEL,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "add-management-role",
        #                     "description": "Adds a role which is allowed to use 'manage' options.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "role",
        #                             "description": "The role to add permission to.",
        #                             "type": COMMAND_OPTION_TYPE_ROLE,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #                 {
        #                     "name": "remove-management-role",
        #                     "description": "Removes a role which is allowed to use 'manage' options.",
        #                     "type": COMMAND_OPTION_TYPE_SUB_COMMAND,
        #                     "options": [
        #                         {
        #                             "name": "role",
        #                             "description": "The role to remove permission from.",
        #                             "type": COMMAND_OPTION_TYPE_ROLE,
        #                             "required": True,
        #                         },
        #                     ]
        #                 },
        #             ]
        #         },
        #     ]
        # }
    ]

    for command in commands:
        create_command(command, config)

    # global_commands = [{
    #     "name": "guess",
    #     "description": "Submit your guess!",
    #     "options": [
    #         {
    #             "name": "game-id",
    #             "description": "The ID of the Eternal Guess game",
    #             "type": COMMAND_OPTION_TYPE_STRING,
    #             "required": True,
    #         },
    #         {
    #             "name": "guess",
    #             "description": "Your guess",
    #             "type": COMMAND_OPTION_TYPE_STRING,
    #             "required": True,
    #         }
    #     ]
    # }]
    #
    # for command in global_commands:
    #     create_command(command, config)


def get_config():
    with open('app_config.json', 'r') as config_file:
        return json.loads(config_file.read())


if __name__ == "__main__":
    config = get_config()

    existing = get_commands(config)
    pprint.pp(existing)
    for command in existing:
        print(f"Delete {command['id']}")
        delete_command(command['id'], config)

    register(config)
