from eternal_guesses.model.discord.discord_component import ComponentType


class DiscordComponentAction:
    def __init__(self, component_type: ComponentType, component_custom_id: str):
        self.component_type = component_type
        self.component_custom_id = component_custom_id
