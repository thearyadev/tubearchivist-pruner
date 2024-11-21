from python:3.12.7-slim-bullseye

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

CMD python main.py -u "$TUBEARCHIVIST_URL" -a "$PRUNE_OLDER_THAN" -t "$API_TOKEN" -e -s "$SLEEP"
