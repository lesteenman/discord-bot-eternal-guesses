from eternal_guesses.model.discord.discord_command import DiscordCommand


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(f"could not handle command (command={command.command_name}, "
                         f"subcommand={command.subcommand_name})")
