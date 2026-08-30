FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# supercronic: cron leggero per container (logga su stdout, gestisce i segnali
# correttamente — niente demone/syslog da configurare). Usato dal servizio
# "cron" in compose.prod.yml/compose.yml per i job ricorrenti (vedi ./crontab);
# il servizio "web" ignora questo binario e usa comunque gunicorn come CMD.
ADD https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic

COPY . .

ENV FLASK_APP=run.py
EXPOSE 3000

# Server WSGI di produzione (niente dev server / debugger interattivo).
# run:app è l'istanza Flask creata da create_app() in run.py.
# I flag (bind/workers/timeout/log) e l'hook on_starting che crea le tabelle
# una volta sola nel master stanno in gunicorn.conf.py.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
