#!/bin/sh -e

cd "$(dirname $0)"

cat<<EOF > /app/config/auth.json
{
    "token": "${TOKEN}"
}
EOF

cat<<EOF > /app/config/config.json
{
    "defaults": {
        "prefix": "${DEFAULT_PREFIX}",
        "welcome_msg": "${DEFAULT_WELCOME_MSG}"
    },
    "db_dump_path": "/app/db/backup",
    "intents": {
        "members": true,
        "messages": true,
        "guilds": true
    }
}
EOF

exec "$@"