from eternal_guesses.model.discord.discord_member import _member_from_data


def test_is_admin():
    # Given
    admin_member = _member_from_data(
        {
            'user': {
                'username': 'admin',
                'id': 1,
            },
            'roles': [],
            'nick': None,
            'permissions': 0x8
        }
    )
    non_admin_member = _member_from_data(
        {
            'user': {
                'username': 'non-admin',
                'id': 2,
            },
            'roles': [],
            'nick': None,
            'permissions': 0
        }
    )

    # Then
    assert admin_member.is_admin
    assert not non_admin_member.is_admin
