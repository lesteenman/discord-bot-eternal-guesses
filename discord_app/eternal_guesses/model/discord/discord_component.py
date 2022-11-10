from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ComponentType(Enum):
    ACTION_ROW = 1
    BUTTON = 2
    STRING_SELECT = 3
    TEXT_INPUT = 4
    USER_SELECT = 5
    ROLE_SELECT = 6
    MENTIONABLE_SELECT = 7
    CHANNEL_SELECT = 8

    @classmethod
    def from_value(cls, value):
        for c in ComponentType:
            if c.value == value:
                return c

        return None


class ButtonStyle(Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@dataclass
class DiscordSelectOption:
    label: str
    value: str
    description: Optional[str]

    def json(self):
        j = {
            "label": self.label,
            "value": self.value,
        }

        if self.description is not None:
            j['description'] = self.description

        return j


class DiscordComponent(object):
    def __init__(self, type: ComponentType, fields: dict):
        self.type = type
        self.fields = fields

    def json(self):
        data = {
            "type": self.type.value,
        }

        return {**data, **self.fields}

    @classmethod
    def text_input(
        cls,
        custom_id: str,
        label: str,
        paragraph: bool = False,
        required: bool = True
    ):
        return DiscordComponent(
            type=ComponentType.TEXT_INPUT,
            fields={
                "custom_id": custom_id,
                "label": label,
                "style": (2 if paragraph else 1),
                "required": required,
            }
        )

    @classmethod
    def button(
        cls,
        custom_id: str,
        label: str,
        style: ButtonStyle = ButtonStyle.SECONDARY
    ):
        return DiscordComponent(
            type=ComponentType.BUTTON,
            fields={
                "custom_id": custom_id,
                "label": label,
                "style": style.value,
            }
        )

    @classmethod
    def url_button(cls, label: str, url: str):
        return DiscordComponent(
            type=ComponentType.BUTTON,
            fields={
                "label": label,
                "url": url,
                "style": ButtonStyle.LINK.value,
            }
        )

    @classmethod
    def string_select(
        cls,
        placeholder: str,
        custom_id: str,
        options: List[DiscordSelectOption]
    ):
        return DiscordComponent(
            type=ComponentType.STRING_SELECT,
            fields={
                "custom_id": custom_id,
                "placeholder": placeholder,
                "options": [o.json() for o in options]
            }
        )

    @classmethod
    def channel_select(cls, placeholder, custom_id):
        return DiscordComponent(
            type=ComponentType.CHANNEL_SELECT,
            fields={
                "custom_id": custom_id,
                "placeholder": placeholder,
            }
        )


class ActionRow(object):
    def __init__(self, components: List[DiscordComponent]):
        self.type = ComponentType.ACTION_ROW
        self.components = components

    def json(self):
        return {
            "type": self.type.value,
            "components": [c.json() for c in self.components]
        }
