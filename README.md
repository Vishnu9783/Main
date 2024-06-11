# File Store Bot

File Store Bot is a Telegram bot built using the Pyrogram library and Python. It provides a convenient way to store and manage files on Telegram.

## Requirements

To run the bot, you need to set up the following environment variables:

- `API_ID`: Your Telegram API ID. Obtain it by creating a new application on the [Telegram API website](https://my.telegram.org/apps).
- `API_HASH`: Your Telegram API hash. Obtain it from the same page where you obtained the API ID.
- `BOT_TOKEN`: The token for your bot. Create a new bot on Telegram and obtain the token from [BotFather](https://t.me/BotFather).
- `DATABASE_URL`: (Optional) The URL of the database to be used. If not provided, the bot will use an in-memory database.
- `OWNER_ID`: The Telegram user ID of the bot owner.
- `LOG_CHANNEL`: (Optional) The Telegram channel ID where logs will be sent. If not provided, logs will be printed to the console.


## Optional Configuration

The following environment variables can be optionally set to customize the bot's behavior:

- `DATABASE_NAME`: (Optional) The name of the database to be used. Defaults to "advancefilebot".
- `WEB_SERVER`: (Optional) Set to `True` to enable the web server for file download. Defaults to `False`.


## Usage

1. Set up the required environment variables mentioned above.
2. Install the necessary dependencies by running `pip install -r requirements.txt`.
3. Start the bot by running `python main.py`.

