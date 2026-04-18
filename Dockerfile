from python:3.12.7-slim-bullseye

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

CMD set -e; \
    set -- python main.py -u "$TUBEARCHIVIST_URL" -a "$PRUNE_OLDER_THAN" -t "$API_TOKEN" -e; \
    if [ -n "$SLEEP" ]; then set -- "$@" -s "$SLEEP"; fi; \
    if [ -n "$IGNORE_WATCH_STATUS" ]; then set -- "$@" -i "$IGNORE_WATCH_STATUS"; fi; \
    exec "$@"
