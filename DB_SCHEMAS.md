# SCHEMA DATABASE LinkBayCMS v0.1.0

## indice


## tenant_agency
Il tenant agency è la tabella di perno poiché tutte le altre dipendono da essa, la quale 
contiene i dati per inizializzare il workspace dell'agenzia/softwarehouse

| nome         | tipo    |
|--------------|---------|
| id           | int     |
| company_name | varchar |
| company_slug | varchar |
| password     | varchar |
| old_password | varchar |
| created_at   | date    |
| updated_at   | date    |

