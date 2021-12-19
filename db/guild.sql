/*
Enables the bot to send different messages in different channels in different guilds on member join.
{0} represents the guild name, and {1} represents the member username
*/
CREATE TABLE IF NOT EXISTS welcome(
    welcome_channel_id INTEGER,
    guild_id INTEGER,
    welcome_message TEXT DEFAULT "Welcome to {0}, {1}!" NOT NULL
);

--Custom prefixes per-guild
CREATE TABLE IF NOT EXISTS custompfx(
    guild_id INTEGER,
    prefix TEXT DEFAULT "$" NOT NULL
);

--Enable logging features
CREATE TABLE IF NOT EXISTS logging(
    guild_id INTEGER,
    log_channel_id INTEGER
)