from typing import List

from eternal_guesses.model.discord.discord_component import ComponentType


class DiscordComponentAction:
    def __init__(
        self, component_type: ComponentType, component_custom_id: str,
        values: List[str] = None
    ):
        self.component_type = component_type
        self.component_custom_id = component_custom_id
        self.values = values

    def __repr__(self):
        return f"<DiscordModalSubmit component_type={self.component_type}" \
               f"component_custom_id={self.component_custom_id} " \
               f"values={self.values}>"
