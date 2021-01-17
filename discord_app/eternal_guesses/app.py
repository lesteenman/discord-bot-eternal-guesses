from typing import Optional
from flask import Flask, request
from eternal_guesses import config, discord_router


def create_app(cfg: Optional[config.Config] = None) -> Flask:
    app = Flask(__name__)

    if cfg is None:
        cfg = config.Config()
    app.config.from_object(cfg)

    @app.route('/', methods=['POST'])
    def handle_slash_command():
        return discord_router.handle(request.json)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
