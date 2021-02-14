from pynamodb.attributes import UnicodeAttribute, MapAttribute, NumberAttribute, ListAttribute, BooleanAttribute
from pynamodb.models import Model


class ChannelMessageMap(MapAttribute):
    channel_id = NumberAttribute()
    message_id = NumberAttribute()


# class GameGuessesMap(MapAttribute):
#     user_id = NumberAttribute()
#     guess = UnicodeAttribute()
#     nickname = UnicodeAttribute()
#     timestamp = UnicodeAttribute()


class EternalGuessesTable(Model):
    class Meta:
        table_name = "eternal-guesses"
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)

    # Games
    created_by = NumberAttribute(null=True)
    create_datetime = UnicodeAttribute(null=True)
    close_datetime = UnicodeAttribute(null=True)
    closed = BooleanAttribute(null=True)
    channel_messages = ListAttribute(of=ChannelMessageMap, null=True)
    guesses = UnicodeAttribute(null=True)
