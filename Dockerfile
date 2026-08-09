FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
EXPOSE 3000

# Server WSGI di produzione (niente dev server / debugger interattivo).
# run:app è l'istanza Flask creata da create_app() in run.py.
# --timeout 120: l'analisi AI fa una chiamata sincrona a DeepSeek che può
# superare i 30s di default.
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
