from eternal_guesses.app import injector

discord_event_handler = None


def handle(event):
    event_handler = get_event_handler()
    return event_handler.handle(event)


def get_event_handler():
    global discord_event_handler

    if discord_event_handler is None:
        discord_event_handler = injector.discord_event_handler()

    return discord_event_handler
