# LinkBay CMS®

**Il monitor delle pagine che perdono traffico organico.**

Sono Alessio Quagliara, founder di LinkBayCMS. Questo repository è il prodotto che sto costruendo, in autonomia, da founder tecnico. Questo documento è la fotografia più onesta che posso dare di cosa sto costruendo, perché, e per chi.

> Nota di percorso: questo README descrive un cambio di rotta rispetto alle versioni precedenti del progetto (che era un CMS multi-tenant per agenzie). Il piano che segue è quello attuale, descritto per intero in [BUSINESS_PLAN.md](BUSINESS_PLAN.md).

## In una frase

LinkBay CMS ti dice **quali pagine del tuo sito stanno perdendo traffico su Google, e quali conviene sistemare per prime.**

Non sostituisce il CMS del cliente. Ci lavora sopra.

## Il problema, con un esempio vero

Un sito di contenuti ha 3.000 pagine pubblicate. Il traffico totale sembra stabile: 200.000 visite al mese, più o meno come l'anno scorso. Tutto ok, apparentemente.

In realtà sotto sta succedendo questo: 40 pagine nuove hanno portato +30.000 visite, 180 pagine vecchie ne hanno perse -28.000. Il totale si compensa, quindi **nessuno se ne accorge**, mentre l'azienda brucia pagine che aveva già pagato per scrivere.

Caso singolo, più concreto: la guida "migliori scarpe da running" faceva 4.000 visite al mese. Oggi ne fa 900. Scesa piano, mese dopo mese, per 8 mesi. Nessun allarme, perché in Search Console quel calo è una riga su tremila.

Il risultato tipico: **te ne accorgi un anno dopo, quando recuperare costa dieci volte di più.**

## Cosa fa

Tre cose, in ordine:

1. **Ti dice cosa sta scendendo davvero.** Non il rumore giornaliero: la tendenza su mesi, isolando le pagine in vera discesa secondo regole precise (sotto).
2. **Ti dice quanto pesa**, in **click persi al mese** — una moneta reale, presa da Search Console.
3. **Ti dice cosa fare prima**: non un grafico, ma 5-10 pagine in ordine di priorità, ognuna con il motivo scritto in italiano semplice.

Esempio di output:

> **Priorità 1 — /guide/migliori-scarpe-running**
> Ha perso 3.100 click/mese negli ultimi 8 mesi. Era in posizione media 3,1, ora è 11,4. Il resto del sito nello stesso periodo è sceso solo del 4%: questa pagina sta scendendo per conto suo. Le impressioni sono rimaste alte: la domanda c'è ancora, il problema è il posizionamento.
> **Priorità alta:** valeva molto, sta perdendo molto, ed è a poca distanza dalla prima pagina.

## Cosa vuol dire "vera discesa"

Una pagina entra in lista solo se rispetta **tutte** queste condizioni:

| Regola | Valore di partenza | A cosa serve |
|---|---|---|
| Soglia minima di rilevanza | almeno 50 click nel mese migliore degli ultimi 16 | non allarmarsi per pagine irrilevanti |
| Perdita minima percentuale | almeno -30% | sotto è oscillazione normale |
| Perdita minima assoluta | almeno -20 click/mese | evita di confrontare cali di scala diversa |
| Finestra temporale | ultimi 3 mesi vs 3 mesi precedenti | un mese è rumore, sei mesi arrivano tardi |
| Persistenza | calo in almeno 2 mesi consecutivi | un mese storto capita a tutti |

Più due filtri anti-falsi-allarme:

- **Stagionalità**: confronto anche con lo stesso trimestre dell'anno prima.
- **Colpa del sito o della pagina**: confronto con l'andamento medio dell'intero sito nello stesso periodo. Interessano solo le pagine che scendono **più del sito attorno a loro** — questo filtro elimina il 90% del rumore ed è la risposta alla prima domanda che farà ogni SEO in demo.

Le soglie sono **valori di partenza**, da tarare sui primi utenti reali e regolabili per cliente.

## Come si decide la priorità

Ogni pagina prende un punteggio su quattro domande: quanto valeva prima, quanto sta perdendo, quanto è facile da recuperare (posizione persa piccola vs grande), e se la domanda c'è ancora (impressioni stabili = si aggiusta; impressioni crollate = non c'è nulla da salvare). Ogni punteggio è accompagnato dalla spiegazione in italiano: nessun numero senza motivazione.

## Il valore in euro

La moneta di default è una sola: **click persi al mese**, dato reale e verificabile da Search Console. Gli euro arrivano solo se il cliente indica il valore di una visita o collega Analytics, e sempre etichettati come stima dichiarata. Se non c'è dato, non si inventa nulla — il giorno che un euro è sbagliato, il cliente non crede più nemmeno ai click.

## Cosa NON facciamo

- ❌ Non è un CMS e non modifica il sito del cliente
- ❌ Non è un page builder, non scrive contenuti, non è keyword research
- ❌ Non è l'ennesima dashboard che rimette in bella copia Search Console
- ❌ Non facciamo audit tecnici completi (ci sono già Screaming Frog, Ahrefs)

Una cosa sola: individuare le pagine che perdono traffico organico e metterle in fila per priorità.

## Per chi è

Cliente ideale, stretto e non largo: **publisher e siti editoriali** (non aziende con un blog, non e-commerce), tra **500 e 20.000 pagine indicizzate**, almeno **20.000 click organici/mese** da Search Console, dove il traffico organico è la fonte principale di ricavi, e dove **esiste già qualcuno che può mettere mano ai contenuti** (SEO interno, content manager, agenzia). Senza quest'ultimo punto, la lista resta lì inutilizzata e il cliente disdice al secondo mese.

Le agenzie SEO (multi-sito, white label) arrivano dal mese sei, non subito.

## Perché scelgono noi

| Cosa usano oggi | Perché non basta |
|---|---|
| Google Search Console | Archivio, non assistente: non avvisa, non toglie stagionalità, non distingue il calo tuo da quello generale, non prioritizza |
| Ahrefs / Semrush | Attrezzi da analisi completi ma costosi (100-500 €/mese), usati al 10% |
| Screaming Frog | Fotografia tecnica del momento, non ha memoria storica |
| Un Excel fatto a mano | Funziona finché c'è chi lo aggiorna, poi muore |

**Search Console ti dà i dati, noi ti diamo le cinque cose da fare lunedì mattina.** La differenza non è l'allarme, è l'ordine: cosa viene prima, cosa dopo, e perché.

## Modello: Free e Pro

| | Free | Pro |
|---|---|---|
| Siti | 1 | più siti |
| URL monitorate | 100 | tutte |
| Pagine in calo mostrate | prime 5 | tutte |
| Aggiornamento | manuale | automatico settimanale |
| Storico | 3 mesi | dal primo giorno |
| Email del lunedì / priorità completa / note / verifica recupero / team | ❌ | ✅ |

Free deve far vedere il problema e fermarsi lì; Pro serve a gestirlo nel tempo. **Gratis per accorgersi del problema, a pagamento per gestirlo davvero.** Dettagli su fasi di lancio (beta chiusa → free → Pro) e ordini di grandezza economici in [BUSINESS_PLAN.md](BUSINESS_PLAN.md#10-come-si-guadagna).

## Stato del progetto

Siamo al giorno zero del piano descritto nel business plan: **nessuna riga di prodotto ancora scritta per questo nuovo corso.** I primi 30 giorni sono un'unica schermata — Search Console → storico → regole → lista ordinata — e nient'altro. Ogni funzione successiva (email del lunedì, verifica del recupero, multi-sito, mappa dei link interni) è deliberatamente rimandata finché non è chiaro che quella prima lista, da sola, fa muovere le persone.

Il traguardo dei primi 30 giorni non è "il prodotto è pronto": è che **sette persone su dieci**, guardando la lista prodotta su un sito vero, dicano che le farebbe muovere lunedì mattina. Dettagli operativi in [BUSINESS_PLAN.md, sezione 15](BUSINESS_PLAN.md#15-i-prossimi-30-giorni-concretamente).

## Il vantaggio che cresce da solo

Search Console conserva 16 mesi di dati e poi li butta. Noi li salviamo dal primo giorno e non li buttiamo più. Dopo due anni un cliente ha dentro LinkBay CMS una storia del proprio sito che non esiste da nessun'altra parte. Non è un vantaggio tecnologico: si costruisce stando lì, e cresce ogni mese da solo.

## I numeri da guardare

Durante la beta, uno solo: **quante pagine della lista vengono davvero sistemate.** Non registrazioni, non accessi — se nessuno tocca una pagina, il prodotto non serve, e va saputo al mese due. Dopo il lancio: conversione free→Pro, apertura dell'email del lunedì, pagine segnate come "fatte", quante pagine sistemate risalgono davvero (obiettivo: più di 1 su 2), tasso di disdetta mensile (sotto il 4% = salute).

---

*Il piano completo, con le ipotesi di pricing, il canale di acquisizione clienti e la roadmap dettagliata, è in [BUSINESS_PLAN.md](BUSINESS_PLAN.md).*

*LinkBay CMS è un marchio registrato (deposito n. 302025000116815, UIBM) di Alessio Quagliara.*
