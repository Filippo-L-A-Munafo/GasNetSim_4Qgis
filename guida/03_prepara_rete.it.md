# Tab 1 — Prepara Rete

Questa scheda parte dai layer che hai **già** nel tuo progetto QGIS (condotte
e nodi, con i loro attributi) e li usa per **creare da zero** due file CSV
nuovi — uno per i nodi, uno per le condotte — con i nomi di colonna esatti
che il motore di calcolo GasNetSim richiede. I due CSV non esistono prima:
vengono generati ogni volta che premi "Genera CSV", leggendo i dati dai tuoi
layer.

Perché tutto questo funzioni, però, **i tuoi layer devono già contenere, in
qualche campo, tutte le informazioni necessarie**: l'identificativo di ogni
condotta, a quali nodi è collegata, il suo diametro, l'identificativo di
ogni nodo, quali nodi sono a pressione nota, ecc. — anche se questi campi
nel tuo layer si chiamano in modo diverso da come li chiama GasNetSim. Il
compito di questa scheda è proprio dire al plugin **dove trovare** ciascuna
informazione nei tuoi layer (la cosiddetta "mappatura dei campi"): non
inventa né deduce dati che non ci sono. Questa è la fase più delicata del
flusso di lavoro, per due motivi distinti: se mappi il campo sbagliato, la
simulazione può fallire o produrre risultati errati senza avvisare; e se
un'informazione necessaria manca del tutto nel layer (in nessun campo),
nessuna mappatura potrà "inventarla" — va prima aggiunta come nuovo campo
nella tabella attributi del layer.

## 1. Scelta modalità

In cima alla scheda c'è una casella "Rete già collassata", che sceglie tra
due modalità di lavoro.

| Opzione | Cosa succede |
|---------|--------------|
| **Deselezionata (default) — Modalità A** | Parti da un layer condotte "grezzo", con la geometria così come l'hai importata dal GIS (per esempio da OpenStreetMap, da un rilievo, o da un catasto). Il plugin esegue il **collasso topologico**: individua dove le condotte si toccano o si avvicinano ai nodi, assegna un ID univoco a ogni condotta e a ogni nodo, e genera i CSV. |
| **Selezionata — Modalità B** | Usi layer già pronti, in cui i nodi e le condotte hanno già gli identificativi (`pipe_id`, `node_a`, `node_b`, `node_id`) collegati fra loro correttamente. Il collasso viene saltato: si mappano solo i nomi dei campi e si esporta. |

### Cos'è il "collasso topologico" e perché serve

I dati GIS grezzi (per esempio scaricati da OpenStreetMap o digitalizzati a
mano) spesso rappresentano le condotte come linee indipendenti, senza sapere
esplicitamente quali linee si toccano tra loro o dove si trovano i nodi della
rete. Per il calcolo idraulico, invece, serve sapere con precisione **quale
condotta collega quali due nodi** (vedi la sezione "Concetti fisici di base"
→ "La rete come grafo"): senza questa informazione non si possono scrivere le
equazioni di bilancio di massa.

Il "collasso" è l'operazione che analizza le geometrie, decide quali estremi
di condotta corrispondono allo stesso punto fisico (entro una certa
tolleranza di distanza) e costruisce così il grafo nodi/condotte pulito su
cui gira poi il calcolo.

## 2. Modalità A — Layer da Collassare

Visibile quando la casella "Rete già collassata" è **deselezionata**.

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer vettoriale lineare (LineString / MultiLineString) con le condotte grezze. Da qui il plugin genera automaticamente `pipe_id`, `node_a`, `node_b` e `length_m` (calcolata dalla geometria stessa). |
| **Campo diametro** | Campo del layer condotte con il diametro interno del tubo. Il plugin prova ad auto-selezionarlo cercando nomi comuni: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. |
| **Unità diametro** | Unità in cui è espresso il campo diametro: pollici (in), metri (m) o centimetri (cm). Il plugin converte automaticamente tutto in metri prima di usarlo nel calcolo. |
| **DEM (opz.)** | Layer raster di un Modello Digitale del Terreno (facoltativo). Se lo fornisci, il plugin estrae automaticamente l'altitudine di ogni nodo campionando il raster in quel punto (`altitude_m`). Se non lo fornisci, l'altitudine di tutti i nodi viene impostata a 0. |
| **Layer nodi** | Layer vettoriale puntuale con i nodi della rete (facoltativo in questa modalità). Se lo fornisci, permette di riconoscere quali punti sono nodi "reference" (vedi sotto). |
| **Campo reference** | Coppia campo + valore che identifica i nodi reference nel layer nodi (per esempio campo `type` = `reference`, o campo `matched` = `1`). Vedi più sotto "Perché il nodo reference è obbligatorio". |
| **Flusso orario nodi** | Campo del layer nodi con il profilo di consumo orario (24 valori in Smc/h, separati da un carattere a scelta). Se non selezioni nulla, tutti i nodi useranno il valore fisso di "Flusso placeholder" (vedi Tab 2). |
| **Raggio aggancio** | Distanza massima (in metri, nell'unità di proiezione del layer) entro cui un nodo viene collegato all'estremità di una condotta durante il collasso. Default: 50 m. |
| **Aggiungi layer collassati al progetto** | Se spuntato, dopo il collasso il plugin aggiunge al progetto QGIS i due nuovi layer (nodi e condotte) risultanti dall'operazione, così puoi ispezionarli visivamente prima di simulare. |

### Perché il "raggio di aggancio" è importante

Nei dati GIS reali, due condotte che *dovrebbero* toccarsi nello stesso nodo
spesso hanno estremi leggermente disallineati (errori di digitalizzazione,
proiezioni diverse, arrotondamenti). Il raggio di aggancio dice al plugin
"considera collegati tutti gli estremi entro questa distanza": troppo
piccolo, e nodi che dovrebbero essere collegati restano separati (la rete si
spezza in pezzi isolati); troppo grande, e nodi che nella realtà sono
distinti vengono fusi insieme per errore. 50 metri è un buon punto di
partenza per dati a scala di rete di trasporto; per reti di distribuzione più
dense può essere opportuno ridurlo.

## 3. Modalità B — Layer Già Collassati

Visibile quando la casella "Rete già collassata" è **selezionata**.

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer condotte già collassato: deve avere già i campi per ID condotta, nodo A, nodo B, lunghezza e diametro (anche con nomi diversi — li mapperai nella sezione successiva). |
| **Layer nodi** | Layer nodi già collassato: deve avere già i campi per ID nodo, flag reference e portata. |

Dopo aver scelto entrambi i layer, appaiono due sezioni di mappatura campi
(condotte e nodi), descritte di seguito.

## 4. Mappatura Campi Condotte (Modalità B)

| Campo nell'interfaccia | Campo prodotto nel CSV | Descrizione |
|-------------------------|--------------------------|-------------|
| **ID pipe** | `pipe_id` | Identificatore univoco della condotta. Auto-riconosciuto tra: `pipe_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Nodo A** | `node_a` | ID del nodo di ingresso (upstream, cioè da cui il gas parte convenzionalmente). Auto: `node_a`, `from_node`, `inlet`, `a`, `start_node`. |
| **Nodo B** | `node_b` | ID del nodo di uscita (downstream). Auto: `node_b`, `to_node`, `outlet`, `b`, `end_node`. |
| **Lunghezza** | `length_m` | Lunghezza della condotta in metri. Auto: `length_m`, `length`, `L`, `len`, `lunghezza`. |
| **Diametro** | `diameter_m` | Diametro interno in metri (con conversione automatica se l'unità è diversa). Auto: `diameter_m`, `diam_m`, `D`, `Diametro_pollici`, ecc. |
| **Unità diametro** | — | Unità del campo diametro scelto: `m`, `in`, `cm`. |

> **Nota fisica**: la distinzione fra "Nodo A" e "Nodo B" non implica che il
> gas debba per forza scorrere in quella direzione — è solo una convenzione
> di etichettatura. Il calcolo determina da solo il verso reale del flusso;
> se il gas scorre da B verso A, il risultato mostrerà semplicemente una
> portata negativa su quella condotta (vedi sezione "Risultati — Condotte").

## 5. Mappatura Campi Nodi (Modalità B)

| Campo nell'interfaccia | Campo prodotto nel CSV | Descrizione |
|-------------------------|--------------------------|-------------|
| **ID nodo** | `node_id` | Identificatore univoco del nodo. Auto: `node_id`, `id`, `FID`, `OBJECTID`. |
| **Altitudine** | `altitude_m` | Quota del nodo in metri sul livello del mare. Auto: `altitude_m`, `z_m`, `elev`, `altitude`, `ALTITUDINE`. Se il campo non è presente, viene usato 0. |
| **Flag reference** | `node_type` = `reference` | Campo + valore che identifica i nodi a pressione fissa nota (vedi sotto). Auto campo: `matched`, `type`, `is_ref`, `reference`, `nodo_tipo`. Valore di default: `1`. |
| **Flusso orario nodi** | `flow_sm3_per_s` | Campo con il profilo di consumo orario: 24 valori in Smc/h separati da un carattere (es. `;`), tipo `1.23;0.98;0.87;...`. Viene usato il valore corrispondente all'ora scelta in "Ora del giorno" (Parametri Export), convertito in sm³/s. Se non selezioni nulla, si usa il "Flusso placeholder". |

### Perché il nodo reference è obbligatorio

Come spiegato nella sezione "Concetti fisici di base", il sistema di
equazioni della rete ha bisogno di almeno un punto di **pressione assoluta
nota** per avere un'unica soluzione (esattamente come un circuito elettrico
ha bisogno di un nodo di massa). Per questo motivo **almeno un nodo reference
è obbligatorio**: se il plugin non ne trova nessuno nel layer nodi, blocca la
simulazione prima ancora di avviarla, con un messaggio d'errore nel log della
Dashboard. Se la tua rete non ha un campo esplicito che marca i nodi
reference, puoi crearne uno rapidamente nella tabella attributi del layer
nodi (per esempio un campo `is_ref` con valore 1 sul punto di
interconnessione con la rete a monte).

## 6. Parametri Export

| Campo | Descrizione |
|-------|-------------|
| **Ora del giorno** | Ora del giorno (da 0 a 23) usata per estrarre il valore di consumo dal profilo orario di ciascun nodo. Il pannello mostra in anteprima il valore che verrebbe estratto dal primo nodo con un profilo disponibile, così puoi verificare a colpo d'occhio che la lettura sia corretta. |
| **Separatore flussi** | Carattere che separa i 24 valori nel campo del profilo orario. Default: `;`. Altre opzioni: `,`, `\|`, `:`, spazio, tabulazione. Deve corrispondere esattamente al formato usato nei tuoi dati, altrimenti il profilo non viene letto correttamente. |
| **Cartella output** | Cartella dove verranno salvati i file `sf_nodes.csv` e `sf_pipelines.csv` quando premi "Genera CSV". |

## 7. Pulsanti Azione

| Pulsante | Azione |
|----------|--------|
| **↺ Ricarica layer** | Aggiorna tutti i menu a tendina con l'elenco aggiornato dei layer attualmente caricati nel progetto QGIS (utile se hai appena aggiunto o rimosso un layer). |
| **> Genera CSV** | Esegue il collasso (se in Modalità A) e/o la mappatura campi, poi scrive `sf_nodes.csv` e `sf_pipelines.csv` nella cartella output scelta. Non avvia la simulazione: utile per controllare i CSV prima di lanciare il calcolo. |
| **>> Genera CSV e Simula** | Fa tutto in un solo passaggio: genera i CSV in una cartella temporanea (senza toccare il filesystem permanente) e avvia subito la simulazione. È il modo più rapido per andare dai layer QGIS ai risultati. |

La sezione "Avvio Simulazione" più avanti in questa Guida riepiloga tutti i
modi (equivalenti) per lanciare il calcolo.
