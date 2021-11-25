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

--Table for snipe command
CREATE TABLE IF NOT EXISTS sniper(
    channel_id INTEGER,
    author_id INTEGER,
    message TEXT
);

--Ditto, for edited messages
CREATE TABLE IF NOT EXISTS editsniper(
    channel_id INTEGER,
    author_id INTEGER,
    message_before TEXT,
    message_after TEXT
);

--Allow opting out of snipe commands
CREATE TABLE IF NOT EXISTS sniper_optout(
    guild_id INTEGER,
    user_id INTEGER
);

--TAGS!
CREATE TABLE IF NOT EXISTS tags(
    tag TEXT NOT NULL,
    content TEXT NOT NULL,
    guild_id INTEGER NOT NULL
)