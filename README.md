# LinkBayCMS v0.1.0

> LinkBay-CMS è una Piattaforma di Infrastruttura E-Commerce multitenant di tipo B2B (Business-to-Business). È progettata per Agenzie Digitali, Software House e Brand consolidati che necessitano di gestire, sotto un'unica dashboard centrale, molteplici negozi online, marketplace o brand white-label per i propri clienti.

## Indice
1. [Sviluppo](#sviluppo)
2. [Architettura](#architettura)
3. [Database](#database)

## Sviluppo

### Per avviare il backend
Il backend in python FastAPI è il cuore pulsante del sistema, proprio per utilizzo
di struttura asincrona, ho scelto FastAPI di Python per integrazioni native con AI


`uvicorn main:app --reload`

Si avvia su http://localhost:8000 / http://127.0.0.1:8000

Per vedere gli API RESTful basta guardare su:
http://localhost:8000/docs / http://127.0.0.1:8000/docs

### Per avviare il frontend
Il frontend è garantito dall'efficienza di Next.JS con il suo routing dinamico

Per avvio backend in sviluppo:

`cd cartella && npm run dev`

## Architettura
Per visionare l'architettura rendere conto a questo file
[visualizza architettura](ARCHITECTURE.md)


## Database
Il Database è stato fatto adoperando PostgreSQL, molto veloce, stabile e scalabile
[visualizza database schema](DB_SCHEMAS.md)