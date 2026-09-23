# 8. Tab 2 — Post-processing e rappresentazione

La scheda non esegue calcoli: governa la rappresentazione tematica dei
risultati e la loro esportazione. L'interfaccia vi accede automaticamente al
termine di una simulazione singola.

## 8.1 Visualizza risultati su layer

Applica una nuova rappresentazione tematica a layer già esistenti, senza
ripetere il calcolo.

| Campo | Descrizione |
|-------|-------------|
| **Layer nodi** | Layer da rappresentare. I layer dei risultati (`R-N-…`) sono elencati per primi; è ammessa la selezione di qualunque layer vettoriale del progetto, compresi quelli di simulazioni precedenti. |
| **Colora nodi per** | Campo che governa la scala cromatica. L'elenco riporta i soli campi presenti nel layer selezionato. |
| **Dimensiona nodi per** | Rende il raggio del simbolo proporzionale al valore assoluto del campo scelto. |
| **Layer condotte** | Analogo per il layer lineare (`R-P-…`). |
| **Colora condotte per** | Campo che governa la scala cromatica delle condotte. |
| **Frecce direzione flusso** | Marcatore orientato secondo il verso effettivo del flusso, cioè secondo il segno di `flow_sm3h` (§10.2) e non secondo l'orientamento della geometria. |
| **▶ Applica colorimetria** | Applica le impostazioni. Il comando adiacente aggiorna l'elenco dei layer. |

### 8.1.1 Criteri di rappresentazione

La classificazione è **graduata a classi quantili**, con numerosità
approssimativamente uniforme per classe. Per le condotte lo spessore della
linea è reso proporzionale alla portata assoluta, in modo da evidenziare la
gerarchia di trasporto. Il campo `h2_pct` adotta una scala dedicata,
progressiva dal bianco/giallo (frazione nulla) al rosso.

L'uso di classi quantili implica che la scala cromatica sia **relativa al
singolo layer**: due simulazioni rappresentate con la stessa impostazione non
sono confrontabili per colore, ma solo per valore. Per confronti quantitativi
si utilizzino i valori numerici o una classificazione manuale a intervalli
fissati, impostabile con gli strumenti standard di QGIS.

## 8.2 Impostazioni per la prossima simulazione

Definisce i campi che verranno prodotti dalla simulazione successiva e la loro
rappresentazione iniziale. Non ha effetto sui risultati già calcolati.

**Nodi.** Campo di colorazione iniziale (default *Pressione*), campo di
dimensionamento (default assente) e selezione dei campi da produrre. Sono
attivi per default: pressione, consumo volumetrico, consumo energetico,
temperatura, densità relativa, fattore Z, potere calorifico, indice di Wobbe,
frazione di H₂, composizione e throughput; risultano disattivi densità, densità
standard, massa molare e tipo nodo.

**Condotte.** Campo di colorazione iniziale (default *Portata*) e selezione dei
campi: attivi per default portata con segno, portata assoluta, velocità,
pressione media e densità relativa; disattivi fattore Z e densità.

**Mostra frecce direzione flusso**: disattivo per default.

Un campo non selezionato non è scritto nel layer e non è pertanto disponibile
per la rappresentazione del §8.1 fino a nuova simulazione. I campi nodali
`volumetric_flow_sm3s`, `energy_flow_mw` e `node_type` sono presenti nei soli
layer QGIS e non nei file CSV (§9.1).

## 8.3 Esporta dati

| Campo | Descrizione |
|-------|-------------|
| **Layer** | Layer da esportare. |
| **Decimali** | Cifre decimali dei valori numerici. |
| **Esporta CSV** | Selezione del percorso di destinazione. |

La funzione è complementare ai file `results_nodes.csv` e `results_pipes.csv`
prodotti automaticamente (§7.6): consente di esportare un sottoinsieme, una
diversa precisione, o un layer la cui simbologia sia stata modificata
manualmente.

## 8.4 Confronto fra scenari

L'accumulo dei layer dei risultati (§7.7) consente il confronto diretto:

1. esecuzione dello scenario di riferimento;
2. modifica del parametro oggetto di analisi — ad esempio la frazione di
   idrogeno (§6.4) — e nuova esecuzione;
3. selezione alternata dei layer `#1` e `#2` sul medesimo campo, nel blocco
   §8.1.

Per il confronto quantitativo si utilizzino i file `results_nodes.csv` delle
rispettive cartelle `run_NNN/h<ora>_OK/`, tenendo presente quanto osservato al
§8.1.1 sulla non confrontabilità delle scale cromatiche quantili.
