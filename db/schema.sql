CREATE TABLE IF NOT EXISTS prefixes(
    prefix varchar(8) NOT NULL PRIMARY KEY,
    guild_id bigint NOT NULL
)