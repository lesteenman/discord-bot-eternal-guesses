import os


discord_public_key: str = os.getenv('DISCORD_PUBLIC_KEY')
discord_bot_token: str = os.getenv('DISCORD_BOT_TOKEN')
dynamodb_table_name: str = os.getenv('DYNAMODB_TABLE_NAME')
aws_region: str = os.getenv('AWS_REGION')
