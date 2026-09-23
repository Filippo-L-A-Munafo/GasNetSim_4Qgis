# 12. Diagnostica della convergenza

La mancata convergenza si verifica quando il criterio (2.14) non è soddisfatto
entro il numero di iterazioni assegnato. Il solutore restituisce comunque
l'ultimo iterato, segnalato dal suffisso `_NONCONV` della cartella dei
risultati (§7.5): si tratta di uno stato intermedio, privo di significato
fisico, che non soddisfa i bilanci nodali.

Si sottolinea che la convergenza è proprietà del problema — topologia,
domande, diametri, stato iniziale — in combinazione con l'algoritmo impiegato,
e non del programma. Di quest'ultimo dipendono unicamente i valori di default
dei parametri numerici e lo schema di accoppiamento adottato (§12.3); tutte le
restanti cause elencate di seguito risiedono nei dati o nella rete.

La presente sezione elenca le cause in ordine di frequenza osservata, con le
verifiche corrispondenti.

## 12.1 Numero di iterazioni insufficiente

**Frequenza: la più elevata.** Il numero di iterazioni necessarie dipende dalla
distanza fra lo stato iniziale e la soluzione, non dalla dimensione della rete.
Nelle prove condotte (§11.7) il valore di default di 50 iterazioni non è
risultato sufficiente su nessuna delle tre reti esaminate:

| Rete | Nodi | Esito con 50 iterazioni | Esito con 200 |
|------|------|--------------------------|----------------|
| Caso di verifica (§11) | 4 | non converge | converge in 92 iterazioni |
| `toy_network_h2` | 10 | non converge | non determinato |
| `Sicily_transmission_network` | 340 | non converge (residuo 1×10⁻¹ Sm³/s) | non determinato |

**Azione.** Portare *Max iterazioni* a 200, se necessario a 500. L'incremento
non comporta penalizzazioni: l'esecuzione termina al soddisfacimento della
(2.14).

## 12.2 Passo di Newton non smorzato a sufficienza

Se il residuo oscilla senza decrescere — condizione frequente quando condotte
di diametro molto diverso sono direttamente connesse — l'ampiezza del passo è
eccessiva.

**Azione.** **Aumentare** l'URF, per esempio da 2,0 a 4,0. Si ricorda che
l'URF compare a denominatore nella (2.13): valori maggiori riducono il passo e
stabilizzano l'iterazione; valori minori di 1 amplificano il passo di Newton e
sono da riservare a reti che convergono agevolmente e per le quali si intenda
ridurre il numero di iterazioni.

Successivamente si può rilassare la tolleranza, da 0,001 a 0,01 Sm³/s
(36 Smc/h di squilibrio ammesso per nodo, trascurabile su reti che trasportano
centinaia di migliaia di Smc/h).

L'opzione *Auto-calibra tol e URF* automatizza questa ricerca, percorrendo la
scala del §13.1.1 verso combinazioni progressivamente più rilassate. Si
verifichi nel log con quali valori la convergenza è stata effettivamente
conseguita, poiché le tolleranze impiegate sono sensibilmente più larghe del
default.

## 12.3 Schema di accoppiamento adottato

La convergenza non è una proprietà del software: dipende dal problema —
topologia, domande, diametri, stato iniziale — in combinazione con l'algoritmo
impiegato per risolverlo. Il plugin determina tuttavia tre elementi
dell'algoritmo, e sono i soli su cui esso intervenga:

1. il numero massimo di iterazioni (§12.1), il cui valore di default è 50;
2. lo schema di accoppiamento fra problema idraulico e tracciamento della
   composizione;
3. le tolleranze del ciclo esterno dello schema staggered, imposte a
   `coupling_tol = tol × 10⁻²` e `coupling_max_iter = max_iter` in luogo dei
   valori predefiniti del motore (10⁻⁴ e 20).

### 12.3.1 Criterio di selezione

Lo schema staggered è attivato quando almeno un nodo non di riferimento
possiede una composizione propria nel file `sf_nodes.csv` (§5.7); in caso
contrario si adotta lo schema diretto. Il criterio è di natura sintattica —
presenza di un valore in un campo — e non numerica: non dipende in alcun modo
dalla difficoltà del problema.

### 12.3.2 Ragione dell'influenza dello schema

Nello schema diretto la miscela attribuita a ciascuna condotta è ridefinita in
base al segno della portata a ogni valutazione del residuo. Se le composizioni
nodali differiscono fra loro, una condotta che inverte il flusso nel corso
dell'iterazione muta la propria miscela e con essa le proprietà del gas: la
funzione residuo risulta discontinua in x e la ricerca lineare si arresta senza
conseguire una riduzione del residuo (cfr. i messaggi del §12.10). Lo schema
staggered rimuove la discontinuità congelando la composizione durante il passo
di Newton e aggiornandola in un passo distinto, a pressioni fissate, con
rilassamento.

Ne consegue che su una rete a composizione unica i due schemi coincidono nella
sostanza, poiché la ridefinizione della miscela restituisce sempre la medesima
miscela. In tal caso la mancata convergenza è da ricondurre al §12.1 e al
§12.2, non allo schema.

### 12.3.3 Qualità della soluzione

Il passo interno dello schema staggered è il medesimo solutore di Newton dello
schema diretto, invocato con la stessa tolleranza e lo stesso numero massimo di
iterazioni; l'iterazione interna è considerata conclusa solo al soddisfacimento
della (2.14). La convergenza dello schema staggered non è pertanto ottenuta con
un criterio più debole: al criterio (2.14) si aggiungono due condizioni sul
ciclo esterno — variazione massima di pressione fra due iterazioni esterne non
superiore a max(10; tol × 10⁵) Pa e variazione della composizione non superiore
a `coupling_tol`.

### 12.3.4 Azione

Su reti a composizioni differenti, qualora si osservino arresti della ricerca
lineare, si verifichi nel log la presenza della riga `Composizioni multiple
rilevate`: la sua assenza indica che il campo composizione non è stato letto e
che il problema viene risolto con lo schema diretto. Il campo è denominato
`gas_comp` nel layer nodi (§5.7); l'attribuzione di una composizione a un nodo
di transito non altera la fisica del problema qualora la composizione sia
identica a quella del nodo di riferimento, ma commuta lo schema di soluzione.

## 12.4 Assenza di nodi di riferimento

La simulazione è interrotta prima dell'avvio (§7.2.1). Nessun record del layer
nodi soddisfa la condizione campo = valore impostata in *Campo reference*.

**Verifiche.** Esistenza del campo; presenza del valore atteso (si considerino
le forme `1`, `1.0`, `"1"`); in Modalità A, appartenenza del nodo al raggio di
aggancio (§6.2): un nodo corretto ma distante dalla condotta più del raggio
impostato non viene riconosciuto.

## 12.5 Totalità dei nodi trattati come riferimento

Condizione simmetrica alla precedente, e più insidiosa perché **non impedisce
la convergenza**: con il valore del flag lasciato vuoto tutti i nodi agganciati
assumono pressione imposta. Il sistema (2.3) risulta privo di incognite, la
convergenza è immediata e i risultati sono privi di contenuto.

**Sintomi.** Pressioni identiche o quasi in tutti i nodi; portate incoerenti
con le domande; numero di iterazioni molto ridotto.

## 12.6 Componenti sconnesse

Una componente priva di nodo di riferimento rende il sistema indeterminato.
Sui dati vettoriali di origine non modellistica è la causa più frequente dopo
quella del §12.1.

**Azione.** Procedura del §4.5. Si osservi che l'eliminazione delle componenti
residue è necessaria anche quando esse corrispondono a porzioni realmente
isolate della rete.

## 12.7 Domande non acquisite

**Sintomi.** Pressioni pressoché uniformi; velocità dell'ordine di 10⁻³ m/s;
`throughput_sm3h` prossimo a zero su tutta la rete.

**Verifiche, nell'ordine.**

1. Assegnazione del campo *Flusso orario nodi*. In Modalità A esso risiede nel
   blocco *⚙ Opzioni avanzate* (§6.2) e non nel blocco principale.
2. Valore riportato dall'anteprima sotto *Ora del giorno* (§5.2).
3. Corrispondenza fra il separatore impostato (§6.2) e quello effettivamente
   presente nei dati: una difformità comporta la lettura di un unico valore non
   interpretabile e la conseguente applicazione del valore di ripiego.
4. Unità dei valori: la (5.1) presuppone Smc/h.

## 12.8 Pressioni incoerenti o velocità anomale

**Causa prevalente: unità del diametro.** Il default del menu *Unità* è
`pollici`. Un campo espresso in metri e interpretato in pollici riduce i
diametri di un fattore 39,37; per la dipendenza D^2,5 della (2.5) la capacità
di trasporto risulta ridotta di oltre nove ordini di grandezza, con collasso
delle pressioni. L'errore inverso produce una rete che trasporta qualunque
portata senza perdite apprezzabili.

**Causa secondaria: quote.** In Modalità A le quote non provengono dal layer
nodi (§5.4). L'assenza di DEM con geometrie bidimensionali annulla il termine
(2.8); quote errate o in unità diverse dal metro lo rendono dominante.

## 12.9 Stazioni di compressione

L'omissione della *Pressione OUT* comporta l'adozione del rapporto di ripiego
1,1 (§6.1.2), con divergenza pressoché certa in condizioni di carico.

Qualora la configurazione sia corretta ma la rete non converga, si esaminino le
righe `[compressori]` del log: la procedura esegue dapprima una simulazione
senza compressore. La mancata convergenza di quest'ultima indica che il
problema risiede nella rete e non nella stazione.

## 12.10 Diagnostica per iterazione

Per le simulazioni singole il file
`<cartella>/run_NNN/output/convergence_log.txt` riporta il dettaglio di
ciascuna iterazione. Le righe significative sono quelle relative alle
**equazioni a residuo massimo**, che identificano il nodo il cui bilancio non
chiude e la pressione corrente in tale nodo.

La persistenza del medesimo nodo fra le equazioni critiche indica una causa
locale — domanda incompatibile con la capacità della condotta afferente, nodo
isolato, diametro errato — la cui rimozione è preferibile a qualsiasi
modifica dei parametri numerici.

Messaggi quali `trust region active`, `line search` e `stalled at iteration`
segnalano che il passo è stato ripetutamente ridotto senza ottenere una
diminuzione del residuo: condizione tipica di una discontinuità della funzione
residuo, riconducibile a inversioni di flusso o a commutazioni nella logica dei
compressori.

## 12.11 Tempi di elaborazione elevati

- Attivare *Solo export CSV* quando i layer non sono necessari: la costruzione
  della simbologia su reti estese incide sensibilmente.
- Mantenere attivo *Forza Multiprocesso* per le esecuzioni parallele.
- Evitare cartelle di output soggette a sincronizzazione su servizi cloud: la
  scrittura dei file intermedi ne risulta rallentata.
- In fase esplorativa, ridurre il numero di iterazioni e rilassare la
  tolleranza; l'affinamento (§6.3) è operazione conclusiva, non preliminare.

## 12.12 Lista di controllo prima dell'utilizzo dei risultati

1. Suffisso della cartella dei risultati: `_OK`.
2. Presenza nel log di `✓ SIMULAZIONE CONVERSA` e valore finale della
   tolleranza.
3. Bilancio ai nodi verificato entro la tolleranza (§10.5, §11.6).
4. Pressione al nodo di riferimento pari al valore assegnato più 1,013 bar.
5. Velocità e pressioni entro intervalli plausibili per la specie di condotta
   (§13.5).
