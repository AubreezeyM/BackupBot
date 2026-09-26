# Backup Bot v0.1
While simple at the moment, this is mainly a bot used between me and a friend for backing up text channels that we write to.  

I'm not sure about setup steps as I'm new to uv.  Maybe they'd be able to help me with that, but my gut says that just cloning this repo should be fine.  Make sure that you create a `.env` file at the root of the repo, and add two variables;
* DISCORD_BOT_TOKEN
* OWNER_USER_ID
The bot uses both of the above to work properly.  Without the token you won't be able to conncet to discord, and the owner ID is used to sync the commands globally.

Then run the bot with `uv run backup-bot`

# Licnese
I guess I'm using the MIT license.  Do what you want, just know this code is not meant for production and is provided as is or whatever.  It's meant to be used personally. 