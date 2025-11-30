# LinkBayCMS v0.1.0

## Indice


## Sviluppo

### Per avviare il backend
Il backend in python FastAPI è il cuore pulsante del sistema, proprio per utilizzo
di struttura asincrona, ho scelto FastAPI di Python per integrazioni native con AI

bash''''
uvicorn main:app --reload
''''

Si avvia su http://localhost:8000 / http://127.0.0.1:8000

Per vedere gli API RESTful basta guardare su:
http://localhost:8000/docs / http://127.0.0.1:8000/docs

### Per avviare il frontend
Il frontend è garantito dall'efficienza di Next.JS con il suo routing dinamico

Per avvio backend in sviluppo:
bash''''
cd cartella && npm run dev
''''
