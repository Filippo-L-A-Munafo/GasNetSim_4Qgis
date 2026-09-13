# Concetti fisici di base

Questa sezione spiega, in linguaggio semplice, i concetti fisici che stanno
dietro a quasi tutti i campi dell'interfaccia. Non serve leggerla tutta prima
di iniziare a usare il plugin, ma è il punto di riferimento a cui le altre
sezioni rimanderanno spesso.

## La rete come "grafo": nodi e condotte

Per il calcolo, una rete gas è semplificata in due soli tipi di elementi:

- **Nodi**: punti dove il gas entra nella rete, esce dalla rete (consumo), o
  dove più condotte si incontrano. Ogni nodo ha una posizione, una quota
  altimetrica e, se è un punto di prelievo, una portata di consumo.
- **Condotte**: collegano due nodi (nodo A e nodo B) e trasportano il gas.
  Ogni condotta ha una lunghezza, un diametro e una rugosità interna.

Questa rappresentazione si chiama **grafo**: i nodi sono i "vertici", le
condotte sono gli "archi". È lo stesso tipo di schema che si usa per i
circuiti elettrici (nodi = punti del circuito, condotte = resistenze) o per
le reti idrauliche in generale. Il primo compito del plugin (il "collasso
topologico" descritto nella sezione Tab 1) è proprio trasformare le geometrie
GIS grezze in questo grafo pulito di nodi e condotte.

## Pressione: assoluta, relativa, e perché conta così tanto

La **pressione** è la grandezza più importante di tutta la simulazione: è
lei che "spinge" il gas lungo le condotte, dal punto a pressione più alta
verso quello a pressione più bassa (esattamente come l'acqua scende da un
punto più alto a uno più basso).

Un dettaglio da non sottovalutare: esistono due modi di misurare la
pressione:

- **Pressione assoluta**: misurata a partire dal vuoto assoluto (0 bar =
  nessuna pressione). È quella che usa il plugin.
- **Pressione relativa (o manometrica)**: misurata a partire dalla pressione
  atmosferica (0 bar = pressione atmosferica, ~1,013 bar assoluti). È quella
  che leggono di solito i manometri sul campo.

Il plugin lavora sempre in **pressione assoluta**. Se prendi un valore da un
manometro di campo (relativo), ricordati di sommare circa 1 bar (la
pressione atmosferica) prima di usarlo come pressione di riferimento.

## Portata: perché si misura in "Smc" e non in metri cubi qualsiasi

A differenza dell'acqua, il gas è **comprimibile**: lo stesso "pacchetto" di
molecole di gas occupa un volume diverso a seconda della pressione e della
temperatura in cui si trova (più pressione = più gas nello stesso spazio).

Questo crea un problema pratico: se dico "in questa condotta passano 100
metri cubi di gas all'ora", quella frase non ha senso finché non specifico
*a quale pressione e temperatura* sto misurando quel volume, perché lo stesso
gas a 70 bar occupa molto meno spazio dello stesso gas a pressione
atmosferica.

La soluzione adottata dall'industria del gas (e dal plugin) è misurare le
portate in **condizioni standard**: si immagina di riportare tutto il gas a
una pressione e temperatura di riferimento fisse (tipicamente 1,01325 bar e
15 °C) e si misura il volume che occuperebbe *in quelle condizioni*. L'unità
di misura che ne risulta si chiama **Smc** (Standard metro cubo) o Sm³, per
distinguerla dal metro cubo "vero" nelle condizioni operative reali.

Questo è il motivo per cui tutti i profili di consumo e tutti i risultati di
portata nel plugin sono espressi in Smc/h o sm³/s: permette di confrontare e
sommare portate senza doversi preoccupare della pressione a cui viaggia il
gas in quel punto della rete.

## Velocità: perché non è semplicemente "portata / area"

La **velocità** del gas in una condotta non si ottiene dividendo la portata
Smc/h per la sezione della condotta, perché quella portata è espressa in
condizioni standard, mentre il gas nella condotta viaggia nelle condizioni
operative reali (alta pressione). Bisogna prima convertire la portata da
condizioni standard a condizioni operative (usando la densità del gas a
quella pressione e temperatura, e il fattore di comprimibilità — vedi sotto),
e solo a quel punto dividerla per la sezione della condotta.

La velocità è un indicatore importante perché velocità troppo elevate
causano rumore, vibrazioni ed erosione delle pareti della condotta (vedi la
sezione "Riferimenti tecnici" per i limiti pratici).

## Perdita di carico: l'attrito che frena il gas

Man mano che il gas scorre lungo una condotta, perde pressione a causa
dell'attrito con le pareti interne della condotta — proprio come l'acqua che
scorre in un tubo perde pressione per attrito. Questo fenomeno si chiama
**perdita di carico**.

La perdita di carico dipende da:

- la **portata**: più gas passa, più attrito c'è (dipendenza non lineare: se
  raddoppio la portata, la perdita di carico più che raddoppia);
- il **diametro** della condotta: condotte più strette generano più attrito
  a parità di portata;
- la **lunghezza** della condotta: più lunga è, più perdita accumula;
- la **rugosità interna** della parete (quanto è "scabra" internamente il
  tubo — dipende dal materiale, vedi sezione Tab 2);
- la **densità e viscosità** del gas nelle condizioni operative.

Il plugin usa una formula specifica (la **formula di Chen**, una variante
della più nota equazione di Darcy-Weisbach) per calcolare questo effetto per
ogni condotta ad ogni iterazione del calcolo. I dettagli pratici (dove si
imposta la rugosità) sono nella sezione Tab 2.

## Bilancio di massa ai nodi: la legge fondamentale della rete

Ad ogni nodo della rete deve valere una regola semplicissima: **tutto il gas
che entra in un nodo deve uscirne** (o essere consumato in quel punto). Non
può "sparire" né "apparire" gas dal nulla. Questa regola si chiama
**bilancio di massa** (o principio di continuità), ed è l'equivalente della
legge di Kirchhoff delle correnti nei circuiti elettrici (la somma delle
correnti che entrano in un nodo è uguale alla somma di quelle che escono).

Il motore di calcolo scrive questa equazione per ogni nodo della rete e la
risolve simultaneamente insieme alle equazioni di perdita di carico su ogni
condotta: il risultato finale (pressioni e portate) è l'unica combinazione di
valori che soddisfa contemporaneamente tutte queste equazioni.

## Nodi di riferimento: perché servono e cosa rappresentano fisicamente

Il sistema di equazioni descritto sopra ha infinite soluzioni se non si
"ancora" a un valore assoluto noto: sapere che "il nodo X ha 2 bar in più del
nodo Y" non basta a determinare la pressione assoluta di nessuno dei due.
Serve almeno un punto della rete di cui si conosce già la pressione assoluta
reale — tipicamente un punto di interconnessione con un'altra rete, una
centrale di compressione, o uno stoccaggio.

Questo punto si chiama **nodo di riferimento** (o "reference"): è una
**condizione al contorno** del problema, esattamente come il "nodo di massa"
in un circuito elettrico (il punto a cui si assegna arbitrariamente 0 Volt,
da cui si misurano tutte le altre tensioni). Per questo il plugin **richiede
obbligatoriamente almeno un nodo reference**: senza, il problema matematico
non ha un'unica soluzione e la simulazione non può partire.

## Comprimibilità del gas reale: perché non basta la legge dei gas ideali

La legge dei gas ideali (pressione × volume = costante × temperatura) è
un'approssimazione che funziona bene a basse pressioni, ma **non è accurata**
alle pressioni tipiche delle reti di trasporto (decine di bar). I gas reali
si comportano in modo leggermente diverso, e questo scostamento si misura con
il **fattore di comprimibilità Z** (Z = 1 per un gas ideale; Z < 1 per il
metano nelle condizioni tipiche delle reti di trasporto).

Il motore di calcolo tiene conto di questo effetto per ogni nodo e ogni
condotta, ricalcolando Z in funzione della pressione, della temperatura e
della composizione del gas in quel punto. Il campo `z_factor` nei risultati
(vedi sezione "Risultati — Nodi") mostra proprio questo valore.

## Regime permanente ("steady-state"): cosa NON calcola il plugin

Il plugin calcola una **soluzione di regime permanente** (steady-state):
assume che i consumi restino costanti nel tempo (quelli scelti per l'ora del
giorno selezionata) e calcola qual è lo stato della rete una volta che si è
"stabilizzata" con quei consumi. Non simula quindi cosa succede durante un
transitorio (per esempio l'apertura improvvisa di una valvola, o come varia
la pressione minuto per minuto durante un cambio di consumo). Per confrontare
condizioni diverse (per esempio ora di punta vs ora di minimo consumo), si
lanciano simulazioni separate, una per ogni ora di interesse.

## In sintesi: l'analogia con i circuiti elettrici

Se hai familiarità con l'elettrotecnica, questa tabella può aiutarti:

| Circuito elettrico | Rete gas |
|---------------------|----------|
| Tensione (Volt) | Pressione (bar) |
| Corrente (Ampere) | Portata (Smc/h) |
| Resistenza (Ohm, lineare) | Perdita di carico in condotta (non lineare: dipende dalla portata stessa) |
| Legge di Kirchhoff (nodi) | Bilancio di massa ai nodi |
| Nodo di massa (0 V) | Nodo di riferimento (pressione nota) |

La differenza principale è che nella rete gas la "resistenza" di ogni
condotta non è costante come in un resistore elettrico, ma dipende essa
stessa dalla portata che ci scorre — motivo per cui il sistema di equazioni è
**non lineare** e richiede un metodo iterativo per essere risolto (vedi la
sezione Tab 2 → Parametri Solutore).
