from typing import List, Dict


class DiscordMember:
    def __init__(self, username: str = None, user_id: int = None, nickname: str = None, roles: List[int] = None,
                 is_admin: bool = False):
        if roles is None:
            roles = []

        self.username = username
        self.user_id = user_id
        self.nickname = nickname
        self.roles = roles
        self.is_admin = is_admin


def _member_from_data(member_data: Dict) -> DiscordMember:
    return DiscordMember(
        username=member_data['user']['username'],
        user_id=int(member_data['user']['id']),
        roles=list(map(int, member_data['roles'])),
        nickname=member_data['nick'],
        is_admin=int(member_data.get('permissions', 0)) & 0x8 == 0x8,
    )
