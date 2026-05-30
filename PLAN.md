LinkBay-CMS — Agency Operating System: Design Document
1. Analisi dello stato attuale
Fix infrastrutturali già completati
Fix	Stato	Impatto
Route slug su AgencyBillingPage e AiCreditsPage	✅ Done	Elimina 500 su Settings e link navigazione
Plan.$fillable completo	✅ Done	Mass assignment sicuro su tutti i campi
AgencyStatsWidget	✅ Done	Dashboard non più vuota
PlanUpsellWidget condizionale	✅ Done	CTA visibile quando agency non ha piano
AI Credits UX Stripe assente	✅ Done	UX chiara invece di errore silenzioso
UX base già presente
Filament panels separati: Admin, Agency, Tenant — routing multi-tenant via subdomain corretto
Agency Settings: white-label, custom domain, Stripe Connect onboarding
Agency Billing: lettura piano corrente, fee, feature
AI Credits: saldo, pacchetti, acquisto via Checkout, ledger storico
Admin: gestione Agency, Plan, Tenant, AiCreditPackage, stats globali
Tenant panel: prodotti, ordini, clienti, collezioni, sconti, shipping, stats
Moduli business totalmente assenti
Livello critico (blocca monetizzazione):

Nessuna AgencySubscription — l'agency non paga tramite Stripe Billing, il suo piano è solo un campo plan_id
PlatformFeeRule non esiste — la fee è hardcoded in plan.limits['transaction_fee_pct'], non versionata, non snapshot-abile
CommissionRecord non esiste — ogni pagamento con application fee non viene registrato internamente
handleSubscriptionDeleted è vuoto — un'agency che cancella abbonamento non viene sospesa
handlePaymentIntentSucceeded è vuoto — nessuna commissione registrata a fronte di charge
Livello operativo (blocca usabilità Agency):

Nessun AgencyMember / AgencyRole — l'agency è monouser
Nessun AgencyClient — i clienti finali non hanno entità propria separata dal Tenant
Nessun TermsAcceptance — nessuna accettazione T&C tracciata
Nessun AuditEvent — nessuna traccia operazioni sensitive
Nessun onboarding flow strutturato per creare store / invitare cliente
Livello ecosistema (futuro, non urgente):

Layout Manager non presente
Temi premium non presenti
Plugin non presenti
Marketplace non presente
2. Gap analysis del pannello Agency
Modulo	Stato attuale	Gap
Dashboard	Stats base (piano, store, crediti)	Manca: revenue summary, ultimi store creati, alert stato account
Clients	Non esiste	Da creare ex-novo: AgencyClient entity, vista lista+dettaglio
Client detail	Non esiste	Contatti, store associati, fatture, stato
Team members	Non esiste	AgencyMember + invito + ruoli
Stores	StoreResource (CRUD Tenant)	Esiste ma manca mapping esplicito Client→Store, max stores check
Store provisioning	Partial (StoreResource create)	Manca: email admin invite, setup wizard, domain assignment
Billing overview	AgencyBillingPage (read only)	Manca: link fatture Stripe, storico pagamenti, data rinnovo
Commissions / Fee	Non esiste	CommissionRecord + vista fee trattenute per store/periodo
Payouts	Non esiste	PayoutRecord + stato payout Stripe Connect
AI Credits	Presente e funzionale	Buono; manca: usage breakdown per store, alert saldo basso
White-label	AgencySettings (parziale)	Manca: preview live brand, gestione email template
Audit log	Non esiste	AuditEvent table + vista filtrata
Terms & Compliance	Non esiste	TermsAcceptance + blocco se non accettati
Support/health	Non esiste	Stato account, link supporto, uptime
3. Domain model da introdurre
Central DB
agency_subscriptions
Scopo: traccia l'abbonamento dell'agency a LinkBay. Separata da subscriptions (che è per tenant).


id                          bigint PK
agency_id                   bigint FK agencies
plan_id                     bigint FK plans
stripe_subscription_id      varchar nullable unique
stripe_customer_id          varchar nullable
status                      enum(trialing, active, past_due, cancelled, paused)
billing_type                enum(monthly, yearly, lifetime)
current_period_start        timestamp
current_period_end          timestamp
trial_ends_at               timestamp nullable
cancelled_at                timestamp nullable
created_at, updated_at
Relazioni: Agency hasOne AgencySubscription, belongsTo Plan

Ownership: central DB

Audit: ogni cambio di status → AuditEvent agency_subscription.status_changed

Note: billing_type = lifetime ha stripe_subscription_id = null, current_period_end = null. Non scade mai.

agency_members
Scopo: utenti interni all'agency (owner + collaboratori).


id
agency_id                   bigint FK agencies
user_id                     bigint FK users
role                        enum(owner, admin, member)
invited_by_user_id          bigint nullable FK users
invited_at                  timestamp nullable
accepted_at                 timestamp nullable
status                      enum(pending, active, suspended)
created_at, updated_at
Relazioni: Agency hasMany AgencyMember, User hasMany AgencyMember

Ownership: central DB

Audit: invite, accept, role change, suspend → AuditEvent

Note: owner = 1 per agency, inderogabile. Non può essere rimosso senza trasferimento.

agency_clients
Scopo: i clienti finali dell'agency, entità business separata dai Tenant (un client può avere più store).


id
agency_id                   bigint FK agencies
name                        varchar
legal_name                  varchar nullable
vat_number                  varchar nullable
country                     char(2) nullable
billing_email               varchar
status                      enum(active, suspended, offboarded)
notes                       text nullable
created_at, updated_at
Relazioni: Agency hasMany AgencyClient; AgencyClient hasMany Tenant (via tenant.agency_client_id)

Ownership: central DB

Audit: status change → AuditEvent

Note: Non è un utente login. È un record anagrafico. L'accesso al panel avviene tramite invito su agency_client_contacts.

agency_client_contacts
Scopo: persone fisiche del cliente (es. CTO, marketing manager). Possono ricevere accesso al tenant panel.


id
agency_client_id            bigint FK agency_clients
user_id                     bigint nullable FK users
name                        varchar
email                       varchar
role                        varchar nullable (es. "Owner", "Developer")
can_access_tenant           boolean default false
created_at, updated_at
Ownership: central DB

Audit: grant/revoke access → AuditEvent

platform_fee_rules
Scopo: storico versionato delle regole fee per piano. Questo è il cuore del billing multilivello.


id
plan_id                     bigint FK plans nullable (null = default globale)
billing_type                enum(monthly, yearly, lifetime) nullable (null = tutti)
fee_pct                     decimal(5,4)       -- es. 0.3000 = 30%
fee_type                    enum(platform_share, transaction_fee)
valid_from                  timestamp
valid_until                 timestamp nullable  -- null = ancora attiva
description                 varchar             -- "Lancio: 30% su piano Starter"
created_by_user_id          bigint FK users
created_at
Relazioni: Plan hasMany PlatformFeeRule

Ownership: central DB

Audit: ogni insert/update → immutabile (append-only, mai update/delete)

Invariante: per risolvere la fee applicabile in un momento T → WHERE valid_from <= T AND (valid_until IS NULL OR valid_until > T) ORDER BY plan_id DESC NULLS LAST, valid_from DESC LIMIT 1

commission_records
Scopo: ogni singola commissione trattenuta da LinkBay. Audit trail immutabile.


id
agency_id                   bigint FK agencies
tenant_id                   varchar nullable FK tenants
platform_fee_rule_id        bigint FK platform_fee_rules    -- snapshot della regola usata
stripe_payment_intent_id    varchar nullable
stripe_charge_id            varchar nullable
gross_amount_cents          integer
fee_pct                     decimal(5,4)       -- valore effettivo applicato (snapshot)
fee_amount_cents            integer
net_to_agency_cents         integer
currency                    char(3)
status                      enum(pending, settled, refunded, disputed)
settled_at                  timestamp nullable
refund_amount_cents         integer default 0
metadata                    jsonb nullable
created_at
Ownership: central DB

Invariante: append-only. Refund crea un record separato con amount negativo e reference al record originale.

Audit: ogni record è già l'audit di sé stesso.

payout_accounts
Scopo: rappresenta l'account di destinazione payout per l'agency (Stripe Connect account).


id
agency_id                   bigint FK agencies unique
stripe_connect_account_id   varchar nullable
onboarded_at                timestamp nullable
currency                    char(3) default 'EUR'
status                      enum(pending, active, restricted, disabled)
last_verified_at            timestamp nullable
created_at, updated_at
Note: Attualmente questo è embeddate in agencies. Estrarlo permette di avere più payout accounts in futuro (es. per mercati diversi). Per ora 1:1 con agency.

payout_records
Scopo: ogni payout inviato all'agency via Stripe Connect.


id
agency_id                   bigint FK agencies
payout_account_id           bigint FK payout_accounts
stripe_payout_id            varchar unique
amount_cents                integer
currency                    char(3)
status                      enum(pending, in_transit, paid, failed, cancelled)
arrival_date                date nullable
failure_reason              varchar nullable
metadata                    jsonb nullable
created_at, updated_at
Webhook trigger: payout.created, payout.paid, payout.failed

billing_events
Scopo: log immutabile di tutti gli eventi billing rilevanti (webhook Stripe, cambi stato subscription, acquisti, refund). Separato da audit_events perché ha struttura diversa e volume più alto.


id
agency_id                   bigint nullable FK agencies
tenant_id                   varchar nullable
stripe_event_id             varchar nullable unique     -- idempotenza webhook
event_type                  varchar                     -- es. "checkout.session.completed"
payload                     jsonb
processed_at                timestamp nullable
error                       text nullable
created_at
Invariante: append-only. Ogni webhook viene scritto qui prima di essere processato.

Idempotenza: INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING → se già esiste, skip.

terms_acceptances
Scopo: traccia accettazione T&C e Privacy Policy per le agency.


id
agency_id                   bigint FK agencies
user_id                     bigint FK users
terms_version               varchar             -- es. "2026-01"
ip_address                  varchar
user_agent                  text nullable
accepted_at                 timestamp
Ownership: central DB

Note: Se l'agency non ha un record per la versione corrente dei T&C, il panel mostra un modal bloccante.

audit_events
Scopo: log operazioni sensitive nell'Agency panel.


id
agency_id                   bigint nullable FK agencies
user_id                     bigint nullable FK users
event                       varchar             -- es. "store.created", "member.role_changed"
subject_type                varchar nullable
subject_id                  varchar nullable
old_values                  jsonb nullable
new_values                  jsonb nullable
ip_address                  varchar nullable
metadata                    jsonb nullable
created_at
Ownership: central DB

Invariante: append-only, nessun soft delete.

Aggiunte minori a tabelle esistenti
tenants — aggiungere:


agency_client_id            bigint nullable FK agency_clients
admin_email                 varchar nullable         -- già in seedTenantDefaults come setting, portarlo in central
stripe_customer_id          varchar nullable
agencies — aggiungere:


stripe_customer_id          varchar nullable     -- per Stripe Billing (abbonamento agency)
terms_accepted_version      varchar nullable     -- cache dell'ultima versione accettata
max_stores_override         integer nullable     -- override manuale del limite piano
Tenant DB — Aggiunte
Nessuna entità nuova urgente. Le seguenti sono per fasi future:

theme_activations — quale tema è attivo per questo tenant (futuro)
plugin_activations — quali plugin sono attivi (futuro)
layout_templates — salvataggio layout per Layout Manager (futuro, se tenant-scoped)
4. Regole economiche piano → fee
Il problema attuale
transactionFeePct() legge $this->plan?->limits['transaction_fee_pct']. Se domani cambio il piano di un'agency o modifico i limits del piano, lo storico delle fee applicate sparisce. Non è difendibile né auditabile.

Modello corretto: platform_fee_rules versionate + snapshot
Principio fondamentale: la fee va "fotografata" nel momento in cui viene creata la transazione (charge). Mai rileggere dal piano live.

Flusso corretto

1. Agency crea un PaymentIntent per un cliente finale
2. StripeConnectService chiama PlatformFeeService::resolveRule($agency, $timestamp)
3. PlatformFeeService cerca in platform_fee_rules la regola attiva
4. La regola viene usata per calcolare application_fee_amount
5. PRIMA di creare il PaymentIntent, salvo CommissionRecord con:
   - platform_fee_rule_id (FK alla regola)
   - fee_pct (valore numerico, snapshot)
   - stripe_payment_intent_id (popolato dopo)
6. Creo il PaymentIntent Stripe
7. Aggiorno CommissionRecord con stripe_payment_intent_id
8. Su webhook payment_intent.succeeded → CommissionRecord.status = 'settled'
Perché questo evita dispute retroattive: il fee_pct nel CommissionRecord è immutabile dopo la creazione. Anche se il piano cambia domani, il record storico mostra la fee applicata quel giorno con riferimento alla regola esatta.

Configurazione piani con fee

// platform_fee_rules seed
[
  ['plan_id' => $starter->id,  'billing_type' => null, 'fee_pct' => 0.3000, 'fee_type' => 'platform_share', 'valid_from' => '2026-01-01'],
  ['plan_id' => $growth->id,   'billing_type' => null, 'fee_pct' => 0.2000, 'fee_type' => 'platform_share', 'valid_from' => '2026-01-01'],
  ['plan_id' => $pro->id,      'billing_type' => null, 'fee_pct' => 0.1000, 'fee_type' => 'platform_share', 'valid_from' => '2026-01-01'],
  ['plan_id' => $ltd->id,      'billing_type' => 'lifetime', 'fee_pct' => 0.3800, 'fee_type' => 'platform_share', 'valid_from' => '2026-01-01'],
]
PlatformFeeService

class PlatformFeeService
{
    public function resolveRule(Agency $agency, ?Carbon $at = null): PlatformFeeRule
    {
        $at ??= now();

        return PlatformFeeRule::where(function ($q) use ($agency) {
                $q->where('plan_id', $agency->plan_id)
                  ->orWhereNull('plan_id');
            })
            ->where(function ($q) use ($agency) {
                $q->where('billing_type', $agency->billing_type)
                  ->orWhereNull('billing_type');
            })
            ->where('valid_from', '<=', $at)
            ->where(function ($q) use ($at) {
                $q->whereNull('valid_until')->orWhere('valid_until', '>', $at);
            })
            ->orderByRaw('plan_id IS NULL ASC')  // plan-specific wins over global
            ->orderByDesc('valid_from')
            ->firstOrFail();
    }

    public function calculateFee(int $grossCents, PlatformFeeRule $rule): int
    {
        return (int) round($grossCents * $rule->fee_pct);
    }
}
Come cambiare fee senza rompere lo storico
Se a giugno 2027 voglio ridurre la fee del piano Pro dal 10% al 8%:


UPDATE platform_fee_rules SET valid_until = '2027-06-01 00:00:00' WHERE plan_id = $pro AND valid_until IS NULL;
INSERT INTO platform_fee_rules (plan_id, fee_pct, valid_from, ...) VALUES ($pro, 0.0800, '2027-06-01', ...);
I CommissionRecord pre-giugno mantengono il loro fee_pct = 0.10 e platform_fee_rule_id che punta alla vecchia regola. Audit completo.

Mostrare la fee all'agency senza ambiguità
Sul panel Agency, in "Commissioni", mostrare:

Fee % applicata oggi (dalla PlatformFeeRule attiva)
Storico commissioni con fee_pct snapshot per ogni record
Alert se il piano è cambiato di recente e la fee è variata
Nota contrattuale critica: nei T&C scrivere esplicitamente:

"La platform share è determinata dal piano attivo al momento della transazione e applicata su ogni pagamento processato tramite l'infrastruttura LinkBay. Modifiche al piano dell'agenzia alterano la fee solo sulle transazioni future."

5. Architettura billing consigliata
Schema flusso soldi

Cliente finale
    │
    │ paga €100 per il suo negozio
    ▼
Stripe (destination charge)
    │
    ├── application_fee_amount = €30 → LinkBayCMS Platform Account (Stripe)
    └── net €70 → Agency Stripe Connect Account
    
LinkBay
    ├── CommissionRecord: gross=10000, fee_pct=0.30, fee=3000, net=7000, status=pending
    ├── BillingEvent: payment_intent.succeeded, payload completo
    └── su webhook: CommissionRecord.status = settled
Stripe Billing per abbonamento agency
L'agency paga LinkBayCMS direttamente (non tramite Connect). Flusso:

Admin assegna piano a agency → crea stripe_customer_id se non esiste
Crea Stripe Subscription con price = plan.stripe_price_id
Salva stripe_subscription_id in agency_subscriptions
Webhook invoice.paid → AgencySubscription.status = active, current_period_end = ...
Webhook customer.subscription.deleted → AgencySubscription.status = cancelled, sospendi agency
Webhook invoice.payment_failed → AgencySubscription.status = past_due, email all'owner, grace period 7gg
Webhook handling — regole ferree

// StripeWebhookController — pattern corretto

public function handle(Request $request): Response
{
    // 1. Valida firma
    // 2. Scrivi BillingEvent (idempotente su stripe_event_id)
    // 3. Se già processato (processed_at IS NOT NULL) → return 200 immediately
    // 4. Dispatcha job asincrono per processing
    // 5. Aggiorna BillingEvent.processed_at = now()
    // 6. Return 200

    return response('OK', 200); // Always 200 to Stripe, errors in logs/jobs
}
Regola fondamentale: Stripe considera un webhook fallito se non riceve 200 entro 30s. Il processing non deve mai bloccare la response. Usa ProcessStripeWebhook job con ShouldQueue.

Idempotenza
Per ogni operazione billing, usare BillingEvent.stripe_event_id come chiave idempotenza:


DB::transaction(function () use ($event) {
    $existing = BillingEvent::where('stripe_event_id', $event->id)->first();
    if ($existing?->processed_at) return; // già processato

    // ... processing ...
    
    BillingEvent::updateOrCreate(
        ['stripe_event_id' => $event->id],
        ['processed_at' => now()]
    );
});
Eventi Stripe chiave da ascoltare
Evento	Azione
checkout.session.completed	✅ Già gestito (AI credits)
account.updated	✅ Già gestito (onboarding status)
payment_intent.succeeded	❌ Manca: salva CommissionRecord.settled
payment_intent.payment_failed	❌ Manca: CommissionRecord.status = failed
customer.subscription.created	❌ Manca: crea/aggiorna AgencySubscription
customer.subscription.updated	❌ Manca: aggiorna AgencySubscription
customer.subscription.deleted	❌ Manca: sospendi agency
invoice.paid	❌ Manca: aggiorna current_period_end
invoice.payment_failed	❌ Manca: past_due + email
payout.paid	❌ Manca: aggiorna PayoutRecord
charge.dispute.created	❌ Manca: CommissionRecord.status = disputed, alert admin
charge.refunded	❌ Manca: reverse CommissionRecord parziale/totale
Gestione application_fee e refund
Refund parziale: Stripe permette refund_application_fee = true su Refund. Se il cliente finale ottiene rimborso, la fee viene rimborsata proporzionalmente.


// Su charge.refunded webhook:
$refundFee = (int) round($refundAmount * $originalCommission->fee_pct);
CommissionRecord::create([
    'agency_id' => ...,
    'gross_amount_cents' => -$refundAmount,
    'fee_amount_cents' => -$refundFee,
    'status' => 'refunded',
    'metadata' => ['original_commission_id' => $originalCommission->id],
]);
Store senza Stripe Connect configurato
Se stripe_connect_onboarded = false:

Il tenant può comunque vendere, ma i pagamenti vanno su un Stripe account placeholder o vengono bloccati
Scelta consigliata: blocco hard. Il tenant non può abilitare checkout finché l'agency non ha completato l'onboarding. Questo protegge LinkBayCMS da pagamenti non splitabili.
Implementazione: middleware RequireStripeConnect sul tenant storefront checkout
Fallback se webhook fallisce
BillingEvent rimane con processed_at = null
Job schedulato ogni ora: riprocessa BillingEvent non processati più vecchi di 5 minuti
Admin dashboard mostra contatore BillingEvent stuck
Alert email se stuck > 24 ore
6. AppSumo / LTD policy architecture
Cosa include il piano LTD
Accesso perpetuo alla piattaforma LinkBay-CMS
Numero di store definito al momento dell'acquisto (stack del codice AppSumo)
White-label base (brand name, logo, colori)
1 custom domain
Dashboard agency
Supporto standard
Cosa NON include mai — lista non negoziabile
Esclusione	Ragione
AI Credits	Costo marginale reale, scala con uso
Temi premium	Prodotto separato con licenza per store
Plugin a pagamento	Ricavo separato
Platform share ridotta	Il 38% è la condizione economica del LTD
SLA garantiti	AppSumo buyers non pagano per uptime
White-label avanzata (email template, subdomain multipli)	Solo piani ricorrenti
Payout prioritari	Solo piani ricorrenti
Seats aggiuntivi team	Solo piani ricorrenti
Perché AI credits e fee non sono inclusi — argomento difendibile
"LinkBay-CMS è un'infrastruttura. Il tuo piano LTD acquista l'accesso all'infrastruttura. I crediti AI sono carburante che alimenta servizi computazionali con costo variabile. La platform share è il modello di business che rende sostenibile l'infrastruttura stessa. Senza di essa, il LTD non sarebbe mai stato possibile."

Questo argomento regge sia su AppSumo (community) che legalmente.

Fair use rules per LTD

max_stores:             3 (stack 1), 6 (stack 2), 10 (stack 3)
max_monthly_api_calls:  100,000
max_storage_gb:         10
ai_credits_included:    0
platform_share:         38% fisso
custom_domains:         1 per stack
team_members:           2 (owner + 1)
Come evitare backlash AppSumo
Comunicazione pre-launch: nella campagna AppSumo, dichiarare esplicitamente "platform share 38% on client payments" e "AI credits sold separately"
FAQ dedicata nella landing: "What is the platform share?" con risposta chiara
Non cambiare retroattivamente le regole post-lancio
Dashboard trasparente: l'agency LTD vede sempre la sua fee attuale, non ha sorprese
Upgrade path chiaro: se un LTD user vuole fee più bassa, upgrade a piano ricorrente Pro (10%)
LTD come funnel entry, non buco di margine
Il 38% su transazioni clienti finali è potenzialmente più redditizio di qualsiasi piano ricorrente se l'agency scala il volume. Un'agency con €50k/mese di GMV clienti frutta a LinkBayCMS €19k/mese. Questo è il modello giusto per LTD heavy users.

Struttura il LTD come: "paghi una volta, non ci pagate l'affitto, ma paghiamo insieme sulla crescita."

7. Agency panel: schermate da costruire adesso
7.1 Dashboard
Scopo: panoramica operativa immediata

Dati:

Stats: piano attuale, negozi attivi/totali, crediti AI, commissioni del mese
Alert: stripe non configurato, piano scaduto, crediti bassi (<500), T&C da accettare
Ultimi 5 store creati
Revenue summary mese corrente (se Stripe Connect attivo)
Azioni: link rapidi a "Crea store", "Acquista crediti", "Configura Stripe"

Dipendenze backend: AgencyStatsWidget (fatto), CommissionRecord (da fare), alert system

Priorità: Alta — parzialmente fatto, manca alert layer

7.2 Clients
Scopo: anagrafica clienti finali dell'agency

Dati: nome, email fatturazione, numero store associati, stato, data creazione

Azioni: Crea client, Modifica, Sospendi, Aggiungi store, Invita contatto

Permessi: AgencyMember role >= admin

Dipendenze: AgencyClient, AgencyClientContact

Priorità: Alta — senza questa schermata, l'agency non gestisce i propri clienti

7.3 Client Detail
Scopo: vista completa di un singolo cliente

Dati: anagrafica, contatti, store associati, fatturazione cliente (se applicabile), note

Azioni: modifica anagrafica, aggiungi/rimuovi store, aggiungi contatto, sospendi

Priorità: Alta (dipende da Clients)

7.4 Team Members
Scopo: gestione utenti interni agency

Dati: nome, email, ruolo, stato, data invito, ultimo accesso

Azioni: Invita membro (email), Cambia ruolo, Rimuovi, Sospendi

Permessi: solo owner può cambiare ruolo owner, admin gestisce member

Dipendenze: AgencyMember, sistema inviti via email

Priorità: Media — necessario ma non blocca monetizzazione

7.5 Stores
Scopo: gestione negozi/tenant

Dati: nome, subdomain, stato, piano, cliente associato, data creazione

Azioni: Crea store, Modifica, Sospendi, Login al panel del store

Nota: aggiungere agency_client_id al form di creazione

Priorità: Alta — già esiste StoreResource, serve solo aggiornamento

7.6 Store Provisioning
Scopo: wizard per creare un nuovo store e onboardare il cliente

Flusso:

Seleziona o crea AgencyClient
Nome store + subdomain
Email admin store (invio email con credenziali)
Selezione piano tenant (opzionale)
Confirm + provisioning
Dipendenze: TenantProvisioningService (già fatto), email system, AgencyClient

Priorità: Media — l'attuale CRUD funziona, il wizard migliora UX onboarding

7.7 Billing Overview
Scopo: stato abbonamento agency + link fatture

Dati:

Piano corrente, prezzo, prossimo rinnovo
Tipo billing (mensile/annuale/lifetime)
Link al Stripe Customer Portal (per gestire metodo pagamento, download fatture)
Storico pagamenti (ultimi 12 mesi)
Azioni: "Gestisci abbonamento" → Stripe Customer Portal redirect

Dipendenze: AgencySubscription, Stripe Customer Portal session

Priorità: Alta — senza questo, le agency non possono gestire i propri pagamenti

7.8 Commissions / Platform Fees
Scopo: trasparenza completa sulle fee trattenute

Dati:

Fee % attuale per piano
Tabella CommissionRecord: data, store, GMV, fee %, importo fee, netto agency
Totale mese/anno
Export CSV
Azioni: filtro per periodo, per store, export

Dipendenze: CommissionRecord, PlatformFeeRule

Priorità: Alta — senza questo, le agenzie faranno domande e dispute

7.9 Payouts
Scopo: stato pagamenti verso l'agency

Dati: tabella PayoutRecord con importo, data, stato, metodo

Azioni: link a Stripe Express Dashboard

Dipendenze: PayoutRecord, Stripe Connect

Priorità: Media — Stripe Express Dashboard copre già questo, ma avere il dato in-app è professionale

7.10 AI Credits
Scopo: saldo, acquisto, storico, usage per store

Stato attuale: funziona, ma manca breakdown per store

Aggiungere: tab "Usage per store" con sum consumo per tenant_id

Priorità: Media — già usabile, miglioramento incrementale

7.11 White-label Settings
Scopo: configurazione brand, dominio, email support

Stato attuale: AgencySettings parzialmente implementata

Manca: preview live del brand, gestione email transazionali

Priorità: Media

7.12 Audit Log
Scopo: cronologia operazioni sensitive

Dati: evento, utente, data, IP, vecchi/nuovi valori

Filtri: per tipo evento, per utente, per periodo

Dipendenze: AuditEvent

Priorità: Media — necessaria per compliance, non urgente per MVP

7.13 Terms & Compliance
Scopo: accettazione T&C e blocco se non accettati

Dati: versione T&C accettata, data, IP

Comportamento: modal bloccante su primo login dopo nuovo T&C

Dipendenze: TermsAcceptance

Priorità: Alta — legale, deve essere fatto prima del lancio pubblico

7.14 Layout Manager, Marketplace
Non fare ora. Sezione 9 copre il design, ma sono fase 3.

8. Parte cliente finale dell'agenzia
Decisione netta: accesso al tenant panel con ruolo limitato
Non creare un mini-panel separato — è costoso da mantenere e crea due code base parallele. Non fare accesso zero — è un limite operativo che le agenzie non accetteranno.

Il modello corretto: il cliente finale accede al Tenant panel Filament già esistente, con un ruolo client che ha visibilità ridotta.

Cosa vede il cliente finale (ruolo client in tenant panel)
Sezione	Accesso
Ordini	Sola lettura
Prodotti	Lettura + modifica
Clienti del negozio	Lettura
Impostazioni negozio	Lettura (no modifica billing)
Dashboard	Sì (versione ridotta)
Collezioni, sconti	Sì
Shipping	Sola lettura
Cosa NON vede il cliente finale
Piano/abbonamento del negozio (lo gestisce l'agency)
Fee platform (non deve sapere quanto LinkBayCMS trattiene)
Stripe Connect dell'agency
Crediti AI (li gestisce l'agency)
Sezioni admin del tenant panel
Flusso invito

Agency panel → Client Detail → "Invita contatto al panel store"
    → sistema manda email con link firmato (signed URL, 72h)
    → il contatto crea account o accede con account esistente
    → gets TenantUser con role = 'client' per quel tenant
Fee visibility verso il cliente finale
Il cliente finale non vede mai la platform share di LinkBay. L'agency può scegliere se:

Passare la fee al cliente (es. fare pagare il 30% in più)
Assorbirla nel proprio margine
Questo è un rapporto agency-cliente, non LinkBay-cliente. LinkBayCMS non ha rapporto contrattuale con il cliente finale.

9. Layout Manager, temi, plugin
A. Layout Manager
Pricing: add-on mensile, non one-time. Ragione: ha costo di infrastruttura continuo (storage layout, rendering, aggiornamenti compatibilità). €29-49/mese per agency.

Cosa si salva: configurazione JSON del layout (sezioni, ordine, componenti, settings). Non asset binari.

Cosa si clona: la struttura del layout, senza contenuto reale (prodotti, immagini, testi).

Cosa NON si clona mai: licenze di componenti premium, API keys, dati clienti.

Versioning: ogni salvataggio layout crea una nuova versione con timestamp. Rollback disponibile agli ultimi N (es. 10) snapshot.

Permessi: solo agency con add-on Layout Manager attivo. Clonare tra store della stessa agency è incluso. Clonare verso store di agency diverse richiede marketplace (futuro).

Rischio lock-in e abuso: limitare numero di layout templates per tier. Esportare layout come JSON scaricabile è ok (non crea lock-in negativo).

B. Temi premium
Modello: licenza per tenant (non per agency). L'agency acquista il tema, lo attiva su uno o più store. Ogni attivazione aggiuntiva su store diverso richiede licenza aggiuntiva (prezzo ridotto, es. 50% dello stesso tema).

Activation: ThemeActivation in central DB con tenant_id, theme_id, activated_at, license_key. Il tenant panel verifica la licenza attiva prima di rendere il tema selezionabile.

Blocco riuso: un tema acquistato per tenant A non è trasferibile a tenant B senza nuova licenza. Gestito via license_key per tenant.

Aggiornamenti: temi ricevono aggiornamenti di compatibilità per 12 mesi dalla data di acquisto. Dopo, servono per versioni major del core. Comunicato chiaramente al momento dell'acquisto.

Futuro marketplace creator: i creator caricano temi, LinkBayCMS trattiene il 30% (o fee di piano), il creator riceve il 70%. Revenue split basato su ThemePurchase record.

C. Plugin
Pricing: ricorrente mensile per tenant. Non one-time — plugin hanno costo manutenzione.

Architettura a hook/capabilities:


// Plugin registra capabilities
PluginRegistry::register('seo-optimizer', [
    'capabilities' => ['tenant.settings.extend', 'product.metafields'],
    'hooks' => ['order.completed', 'product.updated'],
]);
Isolamento: plugin non accedono al DB direttamente. Usano solo API interne esposte da hook. Mai query raw, mai accesso a modelli non passati come parametro.

Dipendenze: un plugin può dipendere da un altro plugin. Il sistema di attivazione verifica e installa in ordine.

Sandboxing fase 1: code review manuale di ogni plugin. Non sandbox automatica (troppo costosa da implementare ora).

Update strategy: plugin ha versione semver. LinkBayCMS Core espone versione API hook. Plugin dichiara requires_core: ">=2.0". Se il core si aggiorna e rompe la compatibilità, il plugin viene disabilitato automaticamente con email all'agency.

10. Sicurezza, compliance, legale
Fee contestate
Rischio: agency dice "non sapevo che trattenevi il 30%"

Mitigazione tecnica: dashboard Commissions mostra ogni singola fee con dettaglio

Mitigazione UX: durante onboarding, mostrare card esplicita "Su ogni pagamento del tuo cliente finale, LinkBayCMS trattiene X%" con formula chiara

Mitigazione contrattuale: T&C art. X: "La Platform Share è descritta nel piano selezionato e applicata su ogni charge processato tramite Stripe Connect dell'agenzia. La percentuale è visibile in qualsiasi momento nella dashboard."

Ricavi condivisi contestati
Rischio: agency disputa il calcolo specifico di una commissione

Mitigazione tecnica: CommissionRecord con fee_pct snapshot, stripe_charge_id, gross_amount_cents. La cifra è riconciliabile con il dashboard Stripe in ogni momento

Mitigazione UX: export CSV delle commissioni con Stripe charge ID come colonna

Mitigazione contrattuale: "In caso di discrepanza, fa fede il report Stripe."

LTD users che si lamentano della fee
Rischio: AppSumo buyer si aspetta zero fee

Mitigazione tecnica: fee è 38%, non 0%. Il codice non ha eccezioni nascoste

Mitigazione UX: la pagina billing mostra "Piano LTD — Platform Share: 38%"

Mitigazione contrattuale: la campagna AppSumo deve dichiarare esplicitamente la fee. Screenshot conservato come prova marketing.

Crediti AI e contestazioni consumo
Rischio: agency dice "ho consumato X ma il ledger dice Y"

Mitigazione tecnica: AiCreditLedger con tenant_id, description, amount su ogni consumo. Impossibile contestare

Mitigazione UX: storico ultimi 100 movimenti con filtro per store

Mitigazione contrattuale: "I crediti AI sono consumabili. Il saldo mostrato in dashboard è autorevole."

White-label e responsabilità contenuti
Rischio: un'agency usa il white-label per attività illegali o fraudolente

Mitigazione tecnica: ogni tenant è tracciato con agency_id. Ogni contenuto è attribuibile

Mitigazione contrattuale: T&C agency: "L'agenzia è responsabile in solido dei contenuti pubblicati dai propri store sulla piattaforma."

Export dati e offboarding
Rischio: agency vuole portare via i dati e chiede di non averli

Mitigazione tecnica: export JSON/CSV di ordini, prodotti, clienti disponibile nel tenant panel

Mitigazione contrattuale: "I dati del negozio sono di proprietà dell'agenzia/cliente. LinkBayCMS fornisce export su richiesta entro 30 giorni dalla cancellazione."

Freeze e termination account
Rischio: agency non paga, ma continua ad operare

Mitigazione tecnica:

AgencySubscription.status = past_due → grace period 7 giorni → suspended
suspended: accesso panel in sola lettura, store clienti disabilitati (checkout bloccato, non eliminati)
cancelled: dopo 30 giorni dalla sospensione, trigger data deletion job con email preavviso 14 giorni
Mai eliminare dati senza preavviso di 14 giorni via email
11. Roadmap decisionale
Fase 1 — Monetizzazione blindata (adesso, 0-8 settimane)
Obiettivo: ogni euro che passa su LinkBayCMS è tracciato, auditabile e riconciliabile.

Cosa costruire	Perché
platform_fee_rules + PlatformFeeService	Base di tutto il billing
commission_records + salvataggio su webhook	Audit trail fee
billing_events con idempotenza	Webhook sicuri
agency_subscriptions	Agency paga tramite Stripe Billing
terms_acceptances + modal bloccante	Compliance legale
Webhook customer.subscription.deleted → sospensione	Controllo morosità
Webhook payment_intent.succeeded → CommissionRecord	Revenue tracking
Pagina Commissions nel Agency panel	Trasparenza fee
Rimandare: team members, client entity, layout manager, marketplace

Quick win: commissioni trasparenti in dashboard = 0 dispute

Rischio se non fatto: un'agency ti contesta una fee e non hai audit trail

Fase 2 — Agency OS credibile (8-20 settimane)
Obiettivo: l'Agency panel è uno strumento operativo reale, non un cruscotto.

Cosa costruire	Perché
AgencyClient + AgencyClientContact	Gestione clienti strutturata
AgencyMember + AgencyRole + inviti	Multi-user agency
Store provisioning wizard	Onboarding clienti fluido
AuditEvent + pagina Audit Log	Compliance operativa
Stripe Customer Portal link	Agency gestisce da sola i propri pagamenti
PayoutRecord + pagina Payouts	Visibilità payout
AI Credits usage breakdown per store	Controllo spesa AI
Alert layer (stripe, piano, crediti, T&C)	UX proattiva
Rimandare: layout manager, temi, plugin

Quick win: team members = agency può delegare operazioni senza condividere password

Rischio se non fatto: churn agency perché il panel non è abbastanza utile

Fase 3 — Ecosistema marketplace (20+ settimane)
Cosa costruire	Perché
Layout Manager (add-on mensile)	Ricavo add-on
Temi premium + licensing	Ricavo one-shot + upgrade
Plugin system + marketplace	Ricavo ricorrente ecosistema
Creator revenue split	Crescita esterna
API pubblica per integrazioni	Espansione
Rimandare tutto questo finché fase 1 e 2 non sono solide.

12. Conclusione
Tabella "Subito / Dopo / Non ora"
Cosa	Timing
platform_fee_rules + PlatformFeeService	Subito
commission_records + webhook payment_intent	Subito
billing_events idempotenti	Subito
agency_subscriptions + Stripe Billing	Subito
terms_acceptances	Subito
Pagina Commissions Agency panel	Subito
Sospensione su subscription deleted	Subito
AgencyClient + AgencyClientContact	Dopo
AgencyMember + inviti	Dopo
PayoutRecord	Dopo
AuditEvent	Dopo
Store provisioning wizard	Dopo
AI Credits usage per store	Dopo
Stripe Customer Portal link	Dopo
Layout Manager	Non ora
Temi premium	Non ora
Plugin system	Non ora
Marketplace	Non ora
API pubblica	Non ora
Top 10 entità da introdurre
platform_fee_rules — senza questo, ogni commissione è indifendibile
commission_records — audit trail immutabile delle fee
billing_events — idempotenza webhook, base di tutto
agency_subscriptions — l'agency deve pagare tramite Stripe Billing
terms_acceptances — compliance legale pre-lancio
agency_clients — i clienti dell'agency come entità propria
agency_members — multi-user e delegation
audit_events — traccia operazioni sensitive
payout_records — visibilità payout Connect
agency_client_contacts — persone fisiche dei clienti con accesso opzionale
Top 10 schermate Agency da fare
Commissions — fee trattenute, trasparenza assoluta
Billing Overview — stato abbonamento + Stripe Customer Portal
Clients — lista clienti agency con stato e store
Client Detail — anagrafica + store + contatti
Terms & Compliance — modal bloccante + pagina storico
Dashboard (migliorata) — alert proattivi + revenue summary
Team Members — inviti + ruoli
Store Provisioning — wizard onboarding cliente
Payouts — stato payout Stripe Connect
Audit Log — cronologia operazioni
Top 10 clausole business da scrivere nei T&C
Platform Share rate per piano — percentuale esatta per piano, incluso LTD 38%, con formula esplicita
Snapshot fee at charge time — la fee si applica al piano attivo al momento della transazione, non alle transazioni future o passate
Modifiche tariffarie — LinkBayCMS può modificare la fee con 30 giorni di preavviso per i piani ricorrenti; LTD è fisso a vita
Responsabilità contenuti store — l'agency è responsabile in solido dei contenuti pubblicati dai propri store
Esclusioni LTD — AI Credits, temi premium, plugin, support prioritario non inclusi nel LTD
Sospensione per morosità — grace period 7 giorni su pagamento fallito, poi sospensione store, poi cancellazione dopo 30 giorni
Export dati e offboarding — export disponibile su richiesta, dati cancellati 30 giorni dopo la cancellazione
Divieto rivendita/reselling platform — l'agency non può rivendere l'accesso alla piattaforma come se fosse proprio prodotto senza accordo white-label esplicito
Dati transazionali — LinkBayCMS ha accesso ai dati di transazione dei clienti degli store ai soli fini di calcolo commissioni e compliance; questi dati non vengono venduti
Risoluzione dispute fee — in caso di discrepanza, fa fede il report Stripe reconciliato con i CommissionRecord di LinkBay
Raccomandazione netta: primo blocco da sviluppare
Inizia dal sistema fee — non dalla UX.

La ragione è semplice: ogni giorno che passa senza commission_records, stai creando fee non auditabili. Se un'agency ti fa causa o semplicemente ti chiede un rendiconto dettagliato delle commissioni degli ultimi 6 mesi, non hai nulla di difendibile.

Il codice attuale in StripeConnectService.createPaymentWithFee calcola $feeCents correttamente e lo passa a Stripe, ma non salva nulla internamente. Stripe sa quello che ha trattenuto; tu no.

Il blocco da fare nella prossima sprint:

Migration platform_fee_rules + seed delle 4 regole piano
Migration commission_records
Migration billing_events
PlatformFeeService::resolveRule()
Aggiornare StripeConnectService::createPaymentWithFee() per salvare CommissionRecord prima di creare il PaymentIntent
Webhook payment_intent.succeeded → CommissionRecord.status = settled
Webhook checkout.session.completed → idempotenza su billing_events
Pagina "Commissioni" nel Agency panel — tabella read-only con export CSV
Tutto il resto viene dopo. Questo blocco richiede 1-2 settimane, non rompe nulla di esistente, e mette la monetizzazione su fondamenta solide.