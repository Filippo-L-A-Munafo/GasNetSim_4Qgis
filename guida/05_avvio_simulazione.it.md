# 7. Esecuzione e file prodotti

## 7.1 Comandi

I comandi risiedono nella colonna destra del Tab 1.

| Comando | Funzione |
|---------|----------|
| **↺ Ricarica layer** | Aggiorna gli elenchi dei layer del progetto. |
| **> Genera CSV** | Esegue costruzione del modello e mappatura e scrive i file di ingresso, senza avviare il solutore. In Modalità B è denominato *Genera CSV da Layer*. |
| **Solo export CSV** | Opzione: i risultati sono scritti su file ma non sono creati layer in QGIS. Riduce sensibilmente il tempo di esecuzione su reti estese. |
| **▶ Avvia Simulazione** | Genera i file di ingresso ed esegue il solutore. |
| **⏹ Ferma** | Interrompe l'elaborazione in corso. |
| **Campagna** | Esecuzione sequenziale del batch orario su una serie di giorni (§7.4). |

In assenza di cartella di output, una simulazione singola utilizza una cartella
temporanea di sistema; *Genera CSV* e l'esecuzione in parallelo la richiedono
esplicitamente.

## 7.2 Controlli preliminari

### 7.2.1 Condizioni bloccanti

- Modalità A: layer condotte non selezionato.
- Modalità B: layer condotte o layer nodi collassati non selezionati.
- Entrambe: assenza di nodi di riferimento al termine della costruzione del
  modello.

### 7.2.2 Condizioni di avvertimento

Le seguenti condizioni producono un avviso con richiesta di conferma; la
prosecuzione è ammessa ma in ciascun caso i risultati risultano compromessi:

| Condizione | Conseguenza |
|------------|-------------|
| Layer nodi non selezionato | Assenza di condizioni al contorno: sistema indeterminato |
| Campo *Flag reference* non assegnato | Tutti i nodi trattati come riferimento |
| Valore del flag reference vuoto | Tutti i nodi agganciati trattati come riferimento |
| Compressori attivi senza *Pressione OUT* | Rapporto di ripiego 1,1 (§6.1.2) |

## 7.3 Esecuzione

Il calcolo è eseguito in un thread separato e, se attiva l'opzione
*Forza Multiprocesso*, in processi indipendenti: l'interfaccia di QGIS resta
utilizzabile.

Il log riporta, nell'ordine:

1. cartella di lavoro e pressione di riferimento applicata;
2. esito della validazione dei file di ingresso, con la composizione adottata.
   In questa fase il plugin: scrive temperatura, pressione e composizione sui
   nodi di riferimento; sostituisce le domande nulle o assenti con il flusso di
   ripiego; azzera le quote mancanti; impone `friction_method = chen`;
3. eventuali messaggi relativi a compressori e composizioni multiple;
4. i parametri numerici effettivamente adottati;
5. l'esito: `✓ SIMULAZIONE CONVERSA in N iterazioni!` oppure segnalazione di
   mancata convergenza seguita da `Estraggo l'ultima soluzione calcolata…`;
6. percorso dei risultati e tempo di elaborazione.

Al termine di una simulazione singola sono creati i layer dei risultati e
l'interfaccia passa automaticamente al Tab 2.

### 7.3.1 Batch orario

L'opzione **Simula 24 ore in parallelo** esegue i 24 scenari orari
simultaneamente. Il grado di parallelismo è determinato dal numero di core
fisici stimati ed è dichiarato nel log. Il riepilogo finale riporta il numero
di ore converse, l'elenco di quelle non converse e il tempo complessivo.

## 7.4 Campagna multi-giorno

Il comando **Campagna** ripete il batch orario su una serie di giorni. La
rete (layer condotte) è comune; variano i layer dei nodi, che rappresentano i
profili di domanda dei singoli giorni.

La procedura richiede: la sorgente dei giorni (file su disco in formato
`.geojson`, `.shp` o equivalente, oppure layer già caricati nel progetto); la
cartella di output; la conferma, con indicazione del numero totale di
simulazioni (giorni × 24).

Durante la campagna l'opzione *Solo export CSV* è forzata e le finestre di
dialogo sono soppresse: un giorno che non superi i controlli del §7.2 viene
saltato e registrato nel log, senza interrompere l'elaborazione. Il riepilogo
finale riporta giorni completati, giorni con 24 ore converse su 24, totale
delle simulazioni converse e tempo complessivo.

## 7.5 Esito della simulazione

Il solutore restituisce un risultato anche in caso di mancata convergenza
(§2.7.1). Tale risultato è l'ultimo iterato calcolato: **non soddisfa i
bilanci nodali e non rappresenta uno stato fisicamente ammissibile**, pur
avendo l'aspetto di una soluzione ordinaria.

L'esito è dichiarato in tre forme: messaggio nel log, colore della riga
conclusiva e — elemento determinante — **suffisso del nome della cartella dei
risultati**, `_OK` oppure `_NONCONV`. La verifica del suffisso deve precedere
qualsiasi utilizzo dei valori prodotti.

## 7.6 Organizzazione dei file prodotti

Ogni esecuzione genera una sottocartella progressiva; nessun file viene
sovrascritto.

```
<cartella output>/
├─ _warmstart_seed.csv              pressioni dell'ultima soluzione conversa
├─ run_001/
│  ├─ input/
│  │  ├─ sf_nodes.csv               dati di ingresso generati (§5.8)
│  │  ├─ sf_pipelines.csv
│  │  └─ sf_compressors.csv         se presenti stazioni di compressione
│  ├─ output/
│  │  └─ convergence_log.txt        diagnostica per iterazione (§12.10)
│  └─ h00_OK/                       risultati dell'ora 0, convergenza raggiunta
│     ├─ results_nodes.csv
│     ├─ results_pipes.csv
│     ├─ results_compressors.csv
│     ├─ run_info.json           provenienza del calcolo (§7.8)
│     ├─ R-N-<nome>_#1.gpkg
│     └─ R-P-<nome>_#1.gpkg
└─ run_002/ …
```

Note:

- i file dei risultati adottano il separatore `;`;
- rieseguendo la medesima ora con esito diverso, la cartella corrispondente
  all'esito precedente viene rimossa, evitando la coesistenza di risultati
  contraddittori;
- i layer dei risultati sono persistiti come **GeoPackage** nella medesima
  cartella: il layer presente in QGIS fa riferimento a tale file e permane alla
  chiusura del progetto;
- il file `_warmstart_seed.csv`, scritto al termine di ogni simulazione singola
  conversa, è riutilizzato come stato iniziale dalle esecuzioni successive
  (§2.7), riducendone il numero di iterazioni.

## 7.7 Layer prodotti nel progetto

| Denominazione | Contenuto |
|---------------|-----------|
| `Condotte #N` / `Nodi #N` | Rete collassata, effettivamente simulata (Modalità A) |
| `R-N-<nome> #N` | Risultati nodali (§9) |
| `R-P-<nome> #N` | Risultati sulle condotte (§10) |
| `R-P-orig-<nome> #N` | Risultati riportati sulla geometria originale, se richiesto (§6.2) |

L'indice progressivo `#N` è incrementato ad ogni esecuzione: **i layer delle
simulazioni precedenti non vengono rimossi**. La scelta consente il confronto
diretto fra scenari (§8.4) ma comporta l'accumulo progressivo di elementi nella
legenda.

## 7.8 Tracciabilità dei risultati

La versione del plugin e quella del motore di calcolo sono **indipendenti**: il
plugin usa un fork di GasNetSim contenente modifiche non presenti in alcuna
versione rilasciata a monte, per cui la sola stringa di versione del motore non
è sufficiente a identificare il codice eseguito.

Ogni esecuzione registra pertanto entrambe le identità in due punti:

1. la **prima riga del log**, nella forma
   `GasNetSim_4Qgis 0.9.0 · motore GasNetSim 0.2.2 (improvement/modular-simulation-architecture @ 6079ec1)`;
2. il file **`run_info.json`**, scritto nella cartella dei risultati accanto ai
   CSV, che contiene:

| Blocco | Contenuto |
|--------|-----------|
| `plugin` | nome e versione del plugin |
| `engine` | versione dichiarata del motore, branch e commit del clone da cui è importato, percorso di installazione |
| `run` | data e ora, ora simulata, esito di convergenza, numero di iterazioni, tempo di calcolo |
| `parameters` | pressione di riferimento, temperatura, rugosità, portate di ripiego, numero massimo di iterazioni, tolleranza, URF, auto-calibrazione, affinamento, composizione del gas |

Il file è scritto in formato JSON separato, e non come intestazione dei CSV,
affinché i file di risultato restino leggibili da qualunque parser senza
opzioni aggiuntive.

Il contenuto di `run_info.json` è l'informazione minima da riportare nella
documentazione di un risultato pubblicato: identifica il codice e i parametri
con cui esso è stato prodotto, e consente di ripetere il calcolo anche dopo
che i file siano stati spostati o rielaborati. Si noti che il commit del motore
viene letto dal clone da cui il pacchetto è importato: un'installazione
effettuata clonando un *branch* anziché un tag o un commit specifico non
garantisce che altri ottengano lo stesso motore.
