# Setup e ambiente di sviluppo

Configurazione Ambiente di Sviluppo

Prerequisiti di Sistema

<ul> <li><code style="background-color:black; color:#ff5758; padding:3px">Node.js 18+</code> - Runtime JavaScript</li> <li><code style="background-color:black; color:#ff5758; padding:3px">PostgreSQL 12+</code> - Database relazionale</li> <li><code style="background-color:black; color:#ff5758; padding:3px">npm o yarn</code> - Gestori pacchetti</li> </ul>
Configurazione Iniziale

<ul> <li>Clonazione repository progetto</li> <li>Installazione dipendenze con <code style="background-color:black; color:#ff5758; padding:3px">npm install</code></li> <li>Creazione file <code style="background-color:black; color:#ff5758; padding:3px">.env</code> da template</li> <li>Configurazione variabili d'ambiente obbligatorie</li> </ul>
Variabili d'Ambiente Critiche

<ul> <li><code style="background-color:black; color:#ff5758; padding:3px">APP_URL</code> - URL base applicazione</li> <li><code style="background-color:black; color:#ff5758; padding:3px">DATABASE_URL</code> - Connection string PostgreSQL</li> <li><code style="background-color:black; color:#ff5758; padding:3px">JWT_SECRET</code> - Chiave crittografia token JWT</li> <li><code style="background-color:black; color:#ff5758; padding:3px">OAUTH_KEYS</code> - Credenziali provider OAuth</li> </ul>
Testing Subdomini in Locale

<ul> <li>Configurazione <code style="background-color:black; color:#ff5758; padding:3px">lvh.me</code> per risoluzione subdomini</li> <li>Accesso landing page: <code style="background-color:black; color:#ff5758; padding:3px">http://lvh.me:3001</code></li> <li>Accesso tenant specifico: <code style="background-color:black; color:#ff5758; padding:3px">http://default.lvh.me:3001</code></li> </ul>