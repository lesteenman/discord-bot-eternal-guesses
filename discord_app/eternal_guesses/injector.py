from eternal_guesses.router import Router, RouterImpl


def manage_route():
    pass


def create_route():
    pass


def guess_route():
    pass


def ping_route():
    pass


def admin_route():
    pass


def router() -> Router:
    return RouterImpl(manage_route=manage_route(), create_route=create_route(), guess_route=guess_route,
                  ping_route=ping_route(), admin_route=admin_route())


def api_authorizer():
    pass
