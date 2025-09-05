# Overview

Sistema di Autenticazione Multitenant Centralizzato

Funzionalità Principali

<ul> <li>Gestione tenant tramite subdominio con isolamento dati</li> <li>Autenticazione cross-domain con supporto OAuth2, SAML e JWT</li> <li>Landing page pubblica come punto di ingresso unico</li> <li>Backoffice dedicato per ogni tenant con dashboard specifiche</li> </ul>
Flusso Principale di Autenticazione

<ul> <li>Utente accede alla landing page pubblica</li> <li>Selezione del provider di autenticazione</li> <li>Identificazione del tenant associato all'email</li> <li>Reindirizzamento al subdominio tenant-specifico</li> <li>Completamento autenticazione e generazione sessione JWT</li> </ul>