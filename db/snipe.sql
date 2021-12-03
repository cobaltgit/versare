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