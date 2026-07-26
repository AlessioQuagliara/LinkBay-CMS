# LinkBay CMS — Business Plan

**Il monitor delle pagine che perdono traffico organico.**

---

## 1. In una frase

LinkBay CMS ti dice **quali pagine del tuo sito stanno perdendo traffico su Google, e quali conviene sistemare per prime.**

Non sostituisce il CMS del cliente. Ci lavora sopra.

---

## 2. Il problema, con un esempio vero

Un sito di contenuti ha 3.000 pagine pubblicate. Il traffico totale sembra stabile: 200.000 visite al mese, più o meno come l'anno scorso. Tutto ok, apparentemente.

In realtà sotto sta succedendo questo:

- 40 pagine nuove hanno portato +30.000 visite
- 180 pagine vecchie ne hanno perse -28.000

Il totale si compensa, quindi **nessuno se ne accorge.** Ma l'azienda sta bruciando pagine che aveva già pagato per scrivere, e sta correndo sempre più veloce solo per restare ferma.

Caso singolo, ancora più concreto: la guida "migliori scarpe da running" faceva 4.000 visite al mese. Oggi ne fa 900. È scesa piano, mese dopo mese, per 8 mesi. Nessuno ha ricevuto un allarme, perché in Search Console quel calo è una riga su tremila.

Il risultato tipico: **te ne accorgi un anno dopo, quando recuperare costa dieci volte di più.**

---

## 3. Cosa fa LinkBay CMS

Tre cose, in ordine.

**1. Ti dice cosa sta scendendo davvero.**
Non il su e giù di ogni giorno, che è rumore. Guarda la tendenza su mesi e isola le pagine in vera discesa, secondo regole precise (vedi sezione 4).

**2. Ti dice quanto pesa.**
Una pagina che passa da 4.000 a 900 visite non è come una pagina che passa da 50 a 20. Il peso si misura in **click persi al mese**: una moneta che abbiamo davvero, presa direttamente da Search Console.

**3. Ti dice cosa fare prima.**
L'output non è un grafico. È una lista di 5-10 pagine in ordine di priorità, ognuna con il motivo scritto in italiano semplice:

> **Priorità 1 — /guide/migliori-scarpe-running**
> Ha perso 3.100 click/mese negli ultimi 8 mesi.
> Era in posizione media 3,1, ora è 11,4.
> Il resto del sito nello stesso periodo è sceso solo del 4%: questa pagina sta scendendo per conto suo.
> Le impressioni sono rimaste alte: la domanda c'è ancora, il problema è il posizionamento.
> **Priorità alta:** valeva molto, sta perdendo molto, ed è a poca distanza dalla prima pagina.

Questo è il prodotto. Il resto è contorno.

---

## 4. Cosa vuol dire "vera discesa" (le regole scritte)

Questa è la parte tecnica del prodotto, ed è quella che decide se la lista è credibile o è rumore. Va scritta e va dichiarata al cliente.

**Una pagina entra in lista solo se rispetta tutte queste condizioni:**

| Regola | Valore di partenza | A cosa serve |
|---|---|---|
| **Soglia minima di rilevanza** | La pagina deve aver fatto almeno **50 click nel suo mese migliore** degli ultimi 16 | Non ha senso allarmarsi per una pagina che è passata da 6 a 2 click |
| **Perdita minima in percentuale** | Almeno **-30%** | Sotto è oscillazione normale |
| **Perdita minima assoluta** | Almeno **-20 click/mese** | Evita che una pagina da 60 a 40 click finisca sopra a una da 4.000 a 900 |
| **Finestra temporale** | Ultimi **3 mesi** contro i **3 mesi precedenti** | Un mese solo è troppo ballerino, sei mesi arrivano troppo tardi |
| **Persistenza** | Il calo deve esserci in almeno **2 mesi consecutivi** | Un mese storto capita a tutti |

**E in più, due filtri che tolgono i falsi allarmi:**

**Filtro stagionalità.** La pagina viene confrontata anche con **lo stesso trimestre dell'anno prima.** Una pagina sul costume da bagno che scende a ottobre non è malata: è ottobre. Se il calo c'è anche rispetto all'anno scorso, allora è vero.

**Filtro "colpa del sito o colpa della pagina".** Ogni pagina viene confrontata con **l'andamento medio di tutto il sito** nello stesso periodo. Se il sito intero è sceso del 25% dopo un aggiornamento di Google, una pagina scesa del 25% non è in decadimento: sta seguendo la corrente. Ci interessano le pagine che scendono **più del sito attorno a loro.**

Questo secondo filtro è il vero motivo per cui la lista è utile: **elimina il 90% del rumore** che rende inservibili i report standard, ed è la risposta alla domanda che ogni SEO farà entro i primi due minuti di demo ("sì ma il calo è generale o è quella pagina?").

Le soglie qui sopra sono **valori di partenza, non verità**. Vanno tarate sui primi utenti reali, e ogni cliente deve poterle stringere o allargare. Ma di default il sistema decide da solo, altrimenti torniamo a chiedere all'utente esattamente quel lavoro che gli stiamo promettendo di togliere.

---

## 5. Come si decide la priorità

Ogni pagina in lista prende un punteggio che risponde a quattro domande:

| Domanda | Perché conta |
|---|---|
| Quanto valeva prima? | Sistemare una pagina che faceva 4.000 click rende molto più che una da 50 |
| Quanto sta perdendo? | Un calo del 70% è più urgente di un calo del 30% |
| È facile da recuperare? | Una pagina scesa dalla posizione 3 alla 11 si recupera; una scesa dalla 40 alla 60 no |
| La domanda c'è ancora? | Se le impressioni tengono e i click no, il problema sei tu e si aggiusta. Se sono crollate anche le impressioni, la gente ha semplicemente smesso di cercare quella cosa: lì non c'è niente da salvare |

Le prime due dicono **quanto vale intervenire**, le seconde due **quanto è probabile che funzioni.** La priorità finale è la combinazione: prima le pagine dove si guadagna tanto e si fatica poco.

E accanto a ogni punteggio c'è sempre la frase in italiano che spiega il perché. Un tool che dà un numero da 0 a 100 senza spiegazione non viene usato: nessuno lavora al buio.

---

## 6. Il valore in euro: come lo trattiamo

**La moneta di default è una sola: click persi al mese.** È un dato reale, verificabile, che arriva da Search Console.

Gli euro arrivano dopo, e solo così:

- il cliente inserisce a mano **quanto vale per lui una visita** (molti lo sanno già), **oppure** collega Analytics e lasciamo che sia il suo dato a parlare;
- il numero appare sempre come **stima dichiarata**, con scritto da dove viene;
- se non c'è nessun dato, **non inventiamo niente.** Nessun "€ persi" tirato fuori dal nulla.

Sembra una rinuncia commerciale, ed è invece la scelta che tiene in piedi tutto il resto: **il giorno che un cliente scopre un euro sbagliato, non crede più nemmeno ai click.** La credibilità della lista è l'unico patrimonio che abbiamo.

---

## 7. Cosa NON facciamo (e non faremo)

Questo elenco vale quanto tutto il resto del piano. È la ragione per cui questo prodotto si finisce, mentre il CMS non si finiva mai.

- ❌ Non è un CMS e non modifica il sito del cliente
- ❌ Non è un page builder
- ❌ Non scrive contenuti al posto tuo
- ❌ Non è un tool di keyword research
- ❌ Non è l'ennesima dashboard che rimette in bella copia i dati di Search Console
- ❌ Non facciamo audit tecnici completi (ci sono già Screaming Frog e Ahrefs, e lo fanno meglio)

**Facciamo una cosa sola: individuare le pagine che perdono traffico organico e metterle in fila per priorità.**

Ogni volta che un cliente chiederà "e potreste anche...", la risposta di default è no, salvo che lo chiedano in cinque e riguardi il calo dei contenuti.

---

## 8. Per chi è (stretto, non largo)

**Cliente ideale — i primi 20, e nessun altro:**

- **Publisher, magazine online, siti editoriali di contenuto.** Non "aziende con un blog", non e-commerce: chi campa di traffico organico e basta.
- **Da 500 a 20.000 pagine indicizzate.** Sotto le 500 il problema si gestisce a occhio, sopra le 20.000 servono cose che non abbiamo ancora.
- **Almeno 20.000 click organici al mese** da Search Console. Sotto questa soglia i cali sono statisticamente indistinguibili dal rumore, e il nostro output diventa inaffidabile: sono clienti che ci farebbero solo danno.
- **Il traffico organico è la fonte principale di ricavi** (pubblicità, affiliazione, abbonamenti).
- **C'è già una persona che può mettere mano ai contenuti**: un SEO interno, un content manager o un'agenzia che lavora per loro.

Quest'ultimo punto è il più sottovalutato: **se non hanno chi esegue, la lista resta lì e disdicono al secondo mese.** Non è colpa del prodotto, è un cliente sbagliato — e va riconosciuto prima di venderglielo, non dopo.

**Le agenzie SEO arrivano dopo, non subito.** Sono un ottimo canale — un'agenzia con 20 clienti ne porta 20 in una volta — ma richiedono multi-sito, white label e gestione team. È una cosa da mese sei, non da mese uno.

---

## 9. Perché scelgono noi

| Cosa usano oggi | Perché non basta |
|---|---|
| **Google Search Console** | Gratis e pieno di dati, ma è un archivio, non un assistente. Non ti avvisa di niente, non toglie la stagionalità, non distingue il calo tuo da quello generale del sito, e non mette niente in ordine di importanza. Ti dà 3.000 righe e ti augura buona fortuna |
| **Ahrefs / Semrush** | Ottimi e molto completi, ma sono attrezzi da analisi: mille numeri e sei tu a dover decidere. Costano 100-500 €/mese e vengono usati al 10% |
| **Screaming Frog** | Fotografia tecnica di un momento. Non guarda la storia, non sa quanto valeva una pagina otto mesi fa |
| **Un file Excel fatto a mano** | Funziona finché c'è la persona che lo aggiorna. Poi muore |

La frase di posizionamento: **Search Console ti dà i dati, noi ti diamo le cinque cose da fare lunedì mattina.**

Non "gli altri non ti avvisano". La differenza non è l'allarme — di allarmi ne ricevono già troppi. La differenza è **l'ordine**: cosa viene prima, cosa dopo, e perché.

---

## 10. Come si guadagna

⚠️ **Tutto quello che segue è un'ipotesi di lavoro, non un listino.** I prezzi si scrivono dopo aver parlato con venti utenti reali, non prima. Servono qui per verificare che i conti possano tornare, non per essere pubblicati.

### Le tre fasi, in ordine

**Fase 1 — Beta chiusa, su invito (mesi 1-3).**
10-20 utenti reali. Gratis, in cambio di feedback vero: una chiamata al mese e il permesso di guardare cosa fanno davvero con la lista. Non è generosità, è ricerca — e questi utenti saranno i primi casi studio e le prime referenze.

**Fase 2 — Si chiude la beta e si apre il piano gratuito (mese 4).**
La beta si chiude quando è chiaro **cosa fa reagire le persone**: quale riga della lista li fa cliccare, quale li lascia indifferenti. Chi era in beta riceve un anno di Pro gratis, per riconoscenza e perché continuino a parlare.

**Fase 3 — Si vende il Pro (mese 5 in poi).**
Non sulle funzioni, ma sul lavoro risparmiato: *"quante ore al mese passi dentro Search Console a cercare cosa sta scendendo?"*

### Free e Pro

| | **Free** | **Pro** |
|---|---|---|
| Siti | 1 | più siti |
| URL monitorate | 100 | tutte |
| Pagine in calo mostrate | le prime 5 | tutte |
| Aggiornamento | manuale, quando entri | automatico ogni settimana |
| Storico | ultimi 3 mesi | tutto, dal primo giorno |
| Email del lunedì | ❌ | ✅ |
| Priorità avanzata e spiegazioni complete | ❌ | ✅ |
| Segna come "fatto" e note | ❌ | ✅ |
| Verifica del recupero a 30/60 giorni | ❌ | ✅ |
| Team e permessi | ❌ | ✅ |

**Il principio:** il piano gratuito deve far vedere **il problema** — "hai 40 pagine che stanno scendendo, eccone 5" — e fermarsi lì. Il Pro serve a **gestirlo nel tempo**: ricordarselo ogni settimana, tenere traccia di cosa è stato fatto, dimostrare che è servito.

> **Gratis per accorgersi del problema, a pagamento per gestirlo davvero.**

### Le trappole del gratuito, evitate apposta

- ❌ **Gratis illimitato su tutti i siti** → non si converte più nessuno
- ❌ **Troppe funzioni centrali nel free** → il Pro diventa un lusso invece che una necessità
- ❌ **Passare da "era tutto gratis" a "ora paghi"** → è il modo migliore per farsi odiare da chi ti aveva difeso. Per questo la beta è **dichiarata come beta fin dal primo giorno**, e chi c'era viene premiato, non punito
- ❌ **Un gratis che non arriva mai a un momento di valore** → il free deve far dire *"ostia, non lo sapevo"* entro dieci minuti dalla registrazione. Se non ci arriva, il limite è messo nel punto sbagliato

### Ordini di grandezza (da verificare, non da credere)

Costi di gestione bassissimi: leggiamo da un'API gratuita, l'elaborazione gira una volta a settimana. Un cliente costa in infrastruttura pochi euro al mese, il margine sta sopra l'85%.

Con una fascia media intorno ai 90-100 €/mese, **servono circa 100-120 clienti paganti per superare i 10.000 €/mese ricorrenti.** È un numero raggiungibile da soli, senza investitori e senza rete di vendita. Se dopo venti colloqui il prezzo sostenibile risulta la metà, il numero raddoppia e il piano regge lo stesso — solo più lento.

---

## 11. Come si trovano i clienti

Questo pubblico non si convince con la pubblicità: si convince con la dimostrazione.

1. **Audit gratuiti mirati.** Scegli 30 publisher italiani, fai girare il tool sui dati che riesci a vedere, mandi due righe: *"ho guardato il vostro sito, 14 guide hanno perso più del 50% del traffico nell'ultimo anno mentre il resto del sito è stabile — ecco l'elenco"*. Chi risponde è già mezzo cliente, perché gli hai mostrato un problema che ha e che non vedeva. **Questi sono anche i primi 20 della beta.**
2. **Contenuti pubblici con dati veri.** Casi studio con numeri: *"come questo sito ha recuperato 80.000 visite sistemando 12 pagine"*. Il pubblico SEO legge, condivide e prova gli strumenti nuovi: è uno dei pochi settori dove il passaparola tecnico funziona ancora.
3. **Il piano gratuito come porta d'ingresso** (dal mese 4). Inserisci il sito, colleghi Search Console, vedi le tue 5 pagine peggiori. Chi vuole la lista completa e il monitoraggio nel tempo, passa a Pro.
4. **Le agenzie, dal mese sei.** Poche, curate, con margine di rivendita.

Nessuna spesa in pubblicità nei primi sei mesi. Prima serve la prova che il prodotto funziona.

---

## 12. Cosa si costruisce, e in che ordine

**Primi 30 giorni — una schermata, e basta**

Collegamento a Search Console → salvataggio dello storico → applicazione delle regole della sezione 4 → una lista ordinata di URL con priorità e spiegazione.

**Una sola schermata. Nessuna scansione del sito, nessuna mappa dei link interni, nessuna email, nessun grafico.** Se quella lista non fa muovere le persone, non la salva nessuna funzione aggiuntiva — e ogni riga scritta in più prima di saperlo è tempo buttato.

**Giorni 31-60 — solo dopo che la lista convince**

Il cancello è questo: **almeno 7 utenti su 10 della beta dicono che la lista li farebbe muovere lunedì mattina.**

- Se **sì** → email del lunedì, segna-come-fatto, storico visibile.
- Se **no** → non si aggiunge niente. Si cambiano le soglie e i criteri di priorità e si torna dagli stessi 10 utenti. Quante volte serve.

**Giorni 61-90 — la parte che lo rende difendibile**

Verifica automatica del risultato dopo 30 e 60 giorni, report mensile "ecco cosa hai recuperato", piano gratuito pubblico.

**Dopo, e solo se lo chiedono i clienti paganti:**
mappa dei link interni e suggerimenti di linking, valore in euro da Analytics, multi-sito e white label per agenzie.

> **La scansione dei link interni è stata spostata qui apposta.** È la funzione più interessante da costruire e la più facile da rimandare senza perdere clienti: nessuno compra un tool per la mappa dei link, lo compra per sapere cosa fare lunedì. Se la lista base non funziona, aggiungere il linking non la salva; se funziona, il linking diventa il primo upgrade naturale e già richiesto.

Novanta giorni per avere qualcosa di vendibile. Questo è il punto di tutto il cambio di rotta: **è un prodotto che si finisce.**

---

## 13. Il vantaggio che cresce da solo

Search Console conserva 16 mesi di dati e poi li butta. Noi li salviamo dal primo giorno e non li buttiamo più.

Dopo due anni, un cliente ha dentro LinkBay CMS una storia del proprio sito che **non esiste da nessun'altra parte**: come si è mossa ogni pagina, cosa è stato fatto, cosa ha funzionato e cosa no. Andarsene significa perdere quella memoria e ripartire da zero.

Non è un vantaggio tecnologico. Si costruisce **stando lì**, e cresce ogni mese da solo. È il motivo per cui vale la pena partire adesso invece che tra un anno.

---

## 14. I numeri da guardare

**Durante la beta (mesi 1-3) — un numero solo:**

> **Quante pagine della lista vengono davvero sistemate.**

Non le registrazioni, non gli accessi. Se dieci utenti guardano la lista e nessuno tocca una pagina, il prodotto non serve — e va saputo al mese due, non al mese dodici.

**Dopo il lancio:**

1. **Da gratuito a pagante** (riferimento realistico per un B2B: 2-5%)
2. **Quanti aprono l'email del lunedì** (sotto il 40% i suggerimenti non sono utili → si sistema quello, prima di ogni altra cosa)
3. **Pagine segnate come "fatte" al mese per cliente** (misura l'uso reale, non l'accesso)
4. **Quante pagine sistemate risalgono davvero** (obiettivo: più di 1 su 2)
5. **Quanti clienti disdicono ogni mese** (sotto il 4% siamo in salute)

Il più importante resta il quarto. Se le pagine indicate per prime non risalgono, tutto il resto è inutile — e allora **si cambiano le soglie della sezione 4**, non il prezzo o il sito web.

---

## 15. I prossimi 30 giorni, concretamente

- [ ] Fissare le soglie della sezione 4 e scriverle nero su bianco
- [ ] Costruire il nocciolo: Search Console → storico → regole → lista ordinata. **Una schermata**
- [ ] Farlo girare su 5 siti veri (i propri, quelli di amici, quelli di agenzie conosciute)
- [ ] Controllare a mano le prime 20 righe prodotte: **la lista è d'accordo con quello che sai già di quei siti?** Se dice cose ovviamente sbagliate, il problema è nelle soglie e va risolto prima di mostrarla a chiunque
- [ ] Preparare 30 audit gratuiti su publisher italiani veri
- [ ] Da quei 30, portare **10 persone del mestiere** a guardare la lista e rispondere a una sola domanda: *"questa lista ti farebbe muovere lunedì mattina?"*
- [ ] Aprire una lista d'attesa con un solo esempio di report ben fatto in bella vista

**Il traguardo dei 30 giorni non è "il prodotto è pronto".** È: *sette persone su dieci hanno guardato la lista e hanno detto che l'avrebbero seguita.* Se lo dicono, si va avanti. Se non lo dicono, si cambiano le soglie finché non lo dicono — e si è speso un mese, non due anni.

---

*Un tool che fa una cosa sola, la fa bene, e si finisce.*