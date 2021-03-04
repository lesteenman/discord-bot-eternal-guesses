import json
import os

if os.path.exists('../app_config.json'):
    with open('../app_config.json', 'r') as env_file:
        config = json.loads(env_file.read())
else:
    config = {
        "DISCORD_PUBLIC_KEY": os.environ["DISCORD_PUBLIC_KEY"],
        "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
        "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
        "NOTIFICATION_EMAIL": os.environ["NOTIFICATION_EMAIL"],
        "APP_LOG_LEVEL": os.getenv("APP_LOG_LEVEL", "INFO")
    }
