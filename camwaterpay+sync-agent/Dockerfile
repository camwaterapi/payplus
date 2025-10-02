FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY luna_client.py sync_agent.py /app/
COPY cron/sync /etc/cron.d/sync
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chmod 0644 /etc/cron.d/sync

VOLUME ["/data"]
ENV SYNC_MODE=daemon

CMD ["/entrypoint.sh"]
