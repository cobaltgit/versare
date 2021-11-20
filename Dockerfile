FROM python:3.9.7-slim-bullseye AS base

ENV DEFAULT_PREFIX='$'
ENV DB_BACKUP_PATH=
ENV DEFAULT_WELCOME_MSG="Welcome to {0}, {1}!"

COPY . /app

WORKDIR /app

RUN apt-get update && apt-get install git gcc linux-libc-dev libc6-dev -y --no-install-recommends && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir micropipenv[toml] && \
    chmod +x /app/docker-init.sh && micropipenv install --deploy && apt-get autopurge -y git gcc && \
    pip uninstall -y micropipenv[toml]
    

VOLUME ["/app/db/backup", "/app/logs"]
ENTRYPOINT [ "/app/docker-init.sh" ]
CMD [ "python", "runner.py" ]