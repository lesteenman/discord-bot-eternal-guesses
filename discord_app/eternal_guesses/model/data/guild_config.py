from typing import List


class GuildConfig:
    guild_id: int
    management_channels: List[int] = []
    management_roles: List[int] = []
