--TAGS!
CREATE TABLE IF NOT EXISTS tags(
    tag TEXT NOT NULL,
    content TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    creation_dt timestamp NOT NULL
)