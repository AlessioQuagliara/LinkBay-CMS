# Database

Struttura e Gestione Database

Tabelle Principali

<ul> <li><code style="background-color:black; color:#ff5758; padding:3px">tenants</code> - Anagrafica tenant con configurazioni</li> <li><code style="background-color:black; color:#ff5758; padding:3px">users</code> - Utenti con relazione tenant_id</li> <li><code style="background-color:black; color:#ff5758; padding:3px">refresh_tokens</code> - Token di refresh per sessioni</li> </ul>
Gestione Migrazioni

<ul> <li>Applicazione migrazioni: <code style="background-color:black; color:#ff5758; padding:3px">npx knex migrate:latest</code></li> <li>Rollback migrazione: <code style="background-color:black; color:#ff5758; padding:3px">npx knex migrate:rollback</code></li> <li>Esecuzione seed: <code style="background-color:black; color:#ff5758; padding:3px">npx knex seed:run</code></li> </ul>
Isolamento Dati Multitenant

<ul> <li>Vincolo <code style="background-color:black; color:#ff5758; padding:3px">tenant_id</code> in tutte le query</li> <li>Filtri applicativi per garantire isolamento</li> <li>Middleware di verifica autorizzazione tenant-specifica</li> </ul>
Schema Tabella Tenants

<ul> <li><code style="background-color:black; color:#ff5758; padding:3px">id</code> - Identificativo univoco</li> <li><code style="background-color:black; color:#ff5758; padding:3px">name</code> - Nome visualizzato tenant</li> <li><code style="background-color:black; color:#ff5758; padding:3px">subdomain</code> - Subdominio associato</li> <li><code style="background-color:black; color:#ff5758; padding:3px">config</code> - Configurazioni JSON personalizzate</li> </ul>
