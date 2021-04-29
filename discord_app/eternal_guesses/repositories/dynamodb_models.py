from pynamodb.attributes import UnicodeAttribute, MapAttribute, NumberAttribute, ListAttribute, BooleanAttribute
from pynamodb.models import Model

from eternal_guesses.util import app_config


class ChannelMessageMap(MapAttribute):
    channel_id = NumberAttribute()
    message_id = NumberAttribute()


class EternalGuessesTable(Model):
    class Meta:
        table_name = app_config.dynamodb_table_name
        region = app_config.aws_region

    # Common
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)

    # Games
    created_by = NumberAttribute(null=True)
    create_datetime = UnicodeAttribute(null=True)
    close_datetime = UnicodeAttribute(null=True)
    closed = BooleanAttribute(null=True)
    channel_messages = ListAttribute(of=ChannelMessageMap, null=True)
    guesses = UnicodeAttribute(null=True)
    title = UnicodeAttribute(null=True)
    description = UnicodeAttribute(null=True)
    min_guess = NumberAttribute(null=True)
    max_guess = NumberAttribute(null=True)

    # GuildConfig
    management_roles = ListAttribute(of=NumberAttribute, null=True)
    management_channels = ListAttribute(of=NumberAttribute, null=True)
