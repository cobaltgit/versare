CREATE TABLE IF NOT EXISTS prefixes(
    prefix varchar(8) NOT NULL,
    guild_id bigint NOT NULL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS sniper(
    message bytea NOT NULL,
    user_id bigint NOT NULL,
    channel_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS editsniper(
    before bytea NOT NULL,
    after bytea NOT NULL,
    user_id bigint NOT NULL,
    channel_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS snipe_optout(
    user_id bigint,
    guild_id bigint
);

CREATE TABLE IF NOT EXISTS dj(
    guild_id bigint NOT NULL,
    role_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS afk(
    user_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    message TEXT,
    timestamp TIMESTAMP NOT NULL
)