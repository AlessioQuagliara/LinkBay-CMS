FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
EXPOSE 3000

# Server WSGI di produzione (niente dev server / debugger interattivo).
# run:app è l'istanza Flask creata da create_app() in run.py.
# I flag (bind/workers/timeout/log) e l'hook on_starting che crea le tabelle
# una volta sola nel master stanno in gunicorn.conf.py.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
