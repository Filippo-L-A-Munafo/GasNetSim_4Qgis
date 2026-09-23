# 5. Tab 1 — Dati di ingresso e mappatura dei campi

## 5.1 Principio

La scheda costruisce, a partire dai layer vettoriali del progetto QGIS, i due
file che costituiscono l'ingresso del solutore: `sf_nodes.csv` e
`sf_pipelines.csv` (§5.7). I file sono rigenerati integralmente ad ogni
esecuzione; non esistono file di ingresso preesistenti da selezionare.

Le informazioni necessarie devono essere già presenti nei layer, in campi di
nome qualsiasi. La mappatura consiste nel dichiarare la corrispondenza fra
campi del layer e grandezze del modello. Il plugin non deduce grandezze
mancanti: in loro assenza applica i valori di ripiego del §6.2 e prosegue.

## 5.2 Blocco 1 — Dati di Input

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer lineare. Se è stata eseguita la verifica del §4, si utilizzi il layer corretto e non l'originale. |
| **Layer nodi** | Layer puntuale. Formalmente facoltativo, sostanzialmente necessario: da esso derivano i nodi di riferimento e le domande nodali. In sua assenza il modello risulta privo di condizioni al contorno. |
| **DEM (raster)** | Modello digitale del terreno, facoltativo. Utilizzato per l'assegnazione delle quote nodali secondo le regole del §5.4. |
| **Cartella output** | Cartella di destinazione di file di ingresso, risultati e layer persistiti (§7.6). Unica per l'intera elaborazione. Obbligatoria per il comando *Genera CSV* e per l'esecuzione in parallelo. |
| **Ora del giorno** | Indice orario 0–23 che seleziona il valore da estrarre dal profilo di domanda (§5.6). L'etichetta sottostante riporta il valore letto dal primo nodo dotato di profilo: costituisce la verifica immediata della corretta interpretazione del campo. |
| **Simula 24 ore in parallelo (0-23)** | Esecuzione simultanea dei 24 scenari orari (§7.3). |

## 5.3 Blocco 2 — Modalità di costruzione del modello

La casella **Rete già collassata** determina se il grafo di calcolo debba
essere costruito dalla geometria (Modalità A) o assunto dai layer (Modalità B).

### 5.3.1 Modalità A — costruzione del grafo dalla geometria

Attiva quando la casella è deselezionata (condizione di default). Il plugin
esegue il **collasso topologico**: esplode le polilinee, identifica gli estremi
coincidenti, genera i nodi, assegna gli identificativi e calcola le lunghezze
dalla geometria tridimensionale.

Al termine vengono aggiunti al progetto due layer, denominati `Condotte #N` e
`Nodi #N`, che costituiscono la rete effettivamente simulata.

**Comportamento da conoscere prima di adottare questa modalità:**

1. **Gli identificativi dei nodi sono generati dal plugin**, mediante un
   contatore progressivo che parte da **0** nell'ordine in cui gli estremi sono
   incontrati durante la scansione delle condotte. Gli identificativi
   eventualmente presenti nel layer nodi **non sono conservati**: essi
   sopravvivono unicamente nei campi `fid_ut` e `label_ut` del layer `Nodi #N`.
   La corrispondenza fra i propri nodi e quelli dei risultati va ricostruita
   attraverso tali campi o per via geometrica.
2. **Gli identificativi delle condotte** sono rinumerati progressivamente a
   partire da 1.
3. **Le quote non provengono dal layer nodi** (§5.4).

Il riquadro **Opzioni Collasso** espone:

| Campo | Descrizione |
|-------|-------------|
| **Diametro** e **Unità** | Campo del layer condotte contenente il diametro interno e relativa unità: `pollici (in)` — prima voce, quindi default —, `metri (m)`, `centimetri (cm)`. Il riconoscimento automatico del campo procede nell'ordine: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. La verifica dell'unità è essenziale: per la (2.5) la portata dipende da D^2,5, per cui un errore di unità di fattore 39,37 produce uno scostamento di circa dieci ordini di grandezza sulla capacità di trasporto. |
| **Campo reference** e valore | Campo del layer nodi e valore che identificano i nodi a pressione imposta (per esempio `type` = `reference`, oppure `is_ref` = `1`). Candidati provati automaticamente: `matched`, `type`, `Type`, `NodeID`, `is_ref`, `reference`, `nodo_tipo`. Il confronto è eseguito sia in forma testuale sia numerica. **Se il valore è lasciato vuoto, tutti i nodi agganciati sono trattati come nodi di riferimento**: la rete risulta a pressione imposta ovunque e i risultati privi di significato (§12.5). |

In Modalità A il campo dei consumi orari e il raggio di aggancio risiedono nel
blocco *⚙ Opzioni avanzate* (§6.2).

### 5.3.2 Modalità B — grafo assunto dai layer

Attiva quando la casella è selezionata. Presuppone che ciascuna condotta
dichiari esplicitamente i due nodi collegati. È la modalità da utilizzare
quando gli identificativi e le quote devono essere conservati, e quella
adottata nel caso di verifica del §11.

I layer tipicamente impiegati sono `Condotte #N` e `Nodi #N` prodotti da un
collasso precedente, che il plugin preseleziona automaticamente, oppure layer
predisposti dall'utente con i campi richiesti.

## 5.4 Origine delle quote nodali

La quota h che compare nella (2.8) è determinata come segue.

| Modalità | Origine della quota |
|----------|---------------------|
| A, geometria delle condotte tridimensionale (LineString Z) | Coordinata Z dei vertici |
| A, geometria bidimensionale, DEM assegnato | Campionamento del DEM alle coordinate dei nodi |
| A, geometria bidimensionale, DEM assente | **h = 0 per tutti i nodi**: il termine (2.8) si annulla |
| A, opzione *Preserva nodi intermedi* attiva | Campionamento del DEM per ogni nodo, compresi gli intermedi (§6.2) |
| B | Campo mappato in *Altitudine* (§5.5.2) |

Il campo altitudine del layer nodi **non è utilizzato in Modalità A**. È un
punto di attenzione: una rete con dislivelli significativi simulata in Modalità
A senza DEM e con geometria bidimensionale restituisce pressioni prive del
contributo geodetico, che alle pressioni di trasporto è dell'ordine di 0,1 bar
ogni 100 m di dislivello.

## 5.5 Mappatura dei campi (Modalità B)

### 5.5.1 Condotte

| Campo interfaccia | Colonna prodotta | Riconoscimento automatico |
|-------------------|------------------|----------------------------|
| **ID pipe** | `pipeline_index` | `pipe_id`, `id`, `FID`, `fid`, `OBJECTID` |
| **Nodo A / B** | `inlet_index` / `outlet_index` | A: `node_a`, `from_node`, `inlet`, `a`, `start_node`; B: `node_b`, `to_node`, `outlet`, `b`, `end_node` |
| **Lunghezza** | `length_m` | `length_m`, `length`, `L`, `len`, `lunghezza`, `lung_m` |
| **Diametro** e unità | `diameter_m` | come in §5.3.1 |

L'orientamento A → B è convenzionale (§2.1): il verso effettivo del flusso è
restituito dal segno della portata (§10.2).

### 5.5.2 Nodi

| Campo interfaccia | Colonna prodotta | Note |
|-------------------|------------------|------|
| **ID nodo** | `node_index` | Intero, coerente con i valori usati in Nodo A / Nodo B. Candidati: `node_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Altitudine** | `altitude_m` | Candidati: `altitude_m`, `z_m`, `elev`, `altitude`, `alt`, `ALTITUDINE`, `quota`. In assenza del campo si assume h = 0. |
| **Flag reference** e valore | `node_type` = `reference` | Valore proposto: `1`. |
| **Flusso orario nodi** | `flow_sm3_per_s` | Profilo di domanda (§5.6). Se non assegnato, tutti i nodi ricevono il valore di ripiego e la rete risulta priva di domanda. |

## 5.6 Profilo di domanda oraria

**Formato.** Stringa contenente fino a 24 valori numerici separati dal
carattere impostato in *Separatore flussi* (default `;`):

```
1250.0;1180.5;1100.2; … ;1310.8
```

**Unità.** Smc/h. La conversione alle unità del modello è

    D = valore / 3600     [sm³/s]                                         (5.1)

**Selezione del valore.** Viene estratto l'elemento di indice pari all'*Ora del
giorno*; se la stringa contiene un numero di valori inferiore all'indice
richiesto, viene utilizzato l'ultimo disponibile. **Un valore singolo è
pertanto valido per qualunque ora** e rappresenta una domanda costante.

**Convenzione di segno.**

| Valore | Significato | Effetto |
|--------|-------------|---------|
| > 0 | Prelievo | D_i > 0 nella (2.3) |
| < 0 | Immissione in rete | D_i < 0 nella (2.3) |
| 0, vuoto, `NULL` | Nodo di transito | Assegnazione del valore di ripiego (§6.2) |

La convenzione di segno consente di modellare punti di immissione (biometano,
elettrolizzatori, interconnessioni) senza ricorrere a nodi di riferimento
aggiuntivi, che imporrebbero anche la pressione.

## 5.7 Composizione per nodo

Se il layer nodi contiene un campo denominato esattamente **`gas_comp`**, il
suo contenuto è assunto come composizione molare del nodo, in sostituzione
della composizione generale (§6.4).

La presenza di almeno una composizione nodale attiva lo schema di
accoppiamento staggered descritto al §2.6, segnalato nel log con
`Composizioni multiple rilevate`. I risultati includono in tal caso la
composizione locale (`gas_comp`) e la frazione di idrogeno (`h2_pct`) nodo per
nodo (§9.2).

## 5.8 Struttura dei file di ingresso prodotti

Separatore di campo `;`.

**`sf_nodes.csv`**

```
node_index;pressure_pa;flow_MW;flow_sm3_per_s;altitude_m;temperature_k;gas_composition;node_type;latitude;longitude;flow_type
1;7500000.0;;;10.0;288.15;{'methane': 0.86909, …};reference;;;volumetric
2;;;1e-06;50.0;;;;;;volumetric
3;;;3.33333333;120.0;;;;;;volumetric
```

I nodi di riferimento riportano pressione (relativa, cfr. 2.2), temperatura e
composizione; i nodi di domanda riportano portata e quota.

**`sf_pipelines.csv`**

```
pipeline_index;inlet_index;outlet_index;diameter_m;length_m;friction_method;roughness_m
1;1;2;0.508;12000.0;chen;1.2e-05
```

L'ispezione di questi due file dopo l'esecuzione del comando *Genera CSV*
costituisce la verifica più diretta della correttezza della mappatura: un
errore presente in questa fase si propaga inalterato ai risultati.
