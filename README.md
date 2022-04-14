[![main](https://github.com/lesteenman/discord-bot-eternal-guesses/actions/workflows/main.yml/badge.svg)](https://github.com/lesteenman/discord-bot-eternal-guesses/actions/workflows/main.yml)
[![codeql](https://github.com/lesteenman/discord-bot-eternal-guesses/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/lesteenman/discord-bot-eternal-guesses/actions/workflows/codeql-analysis.yml)
[![codecov](https://codecov.io/gh/lesteenman/discord-bot-eternal-guesses/branch/main/graph/badge.svg?token=BWMVENG40H)](https://codecov.io/gh/lesteenman/discord-bot-eternal-guesses)

Eternal Guesses is a Discord bot which runs guessing games for your server. After creating a guessing game, it can post
a self-updating post to a channel of your choice, containing the title, description and an up-to-date view of all
guesses.

Anyone in your server can place a guess - but only once!

Eternal Guesses makes use of Discord slash-commands, which means the commands are auto-completed by your server.

# Installing

Invite the bot to your server by clicking the link below:

https://discord.com/api/oauth2/authorize?client_id=800097006251933706&permissions=0&scope=bot

# Usage

## Global commands

`/guess game-id:<game-id> guess:<guess>`

Adds a guess for the given game-id. Can only be done once per game by each Discord member. 

On error (i.e. a wrong game-id or duplicate guess), sends a DM to the user explaining what went wrong.

`/eternal-guess create`

`/eternal-guess create game-id:<game-id>`

Creates a new guessing game. When not called with an explicit game-id, it will generate a random string as the game id.

## Management commands
These commands can only be used by admins, people with a _management role_ or from a _management channel_ (see below).

`/eternal-guess manage list-games`

`/eternal-guess manage list-games closed:<true/false>`

Lists all games for this server. Can optionally list only open or closed games.

`/eternal-guess manage close game-id:<game-id>`

Closes a game. After a game is closed, no new guesses can be placed.

- What are the commands
- What is the permissions system (admin vs management permissions)

## Admin commands
These commands can only be run by members with administration privileges on the server.

`/eternal-guess admin info`

Lists the configuration for this guild. This includes its management roles and channels.

`/eternal-guess admin add-management-channel channel:<channel>`

Adds a channel as a management channel. Management commands (see above) are allowed to be called from a management
channel. Effectively, this means that anyone with access to a management channel can call all management commands.

`/eternal-guess admin remove-management-channel channel:<channel>`

Removes a channel from the list of management channels.

`/eternal-guess admin add-management-role role:<role>`

Adds a role to the list of management roles. Anyone with this role can run management commands from any channel.

`/eternal-guess admin remove-management-role role:<role>`

Removes a role from the list of management roles.

# Developing

Most development will happen in the `discord_app` repository, which is where all the functional logic lives.

The app uses `poetry` for its dependency management.

To install the dependencies, run `poetry install` from `discord_app`.

To run the tests, use `poetry run pytest` from `discord_app`.

# Releases

Releases are done through a CD pipeline in Github actions after all tests have passed, never manually.

## Structure of the project

- discord_app
- error_parser
- infra
