# Manuale — GasNetSim 4Qgis

Plugin QGIS per la simulazione idraulica di reti gas (trasporto e distribuzione) basato sulla libreria **GasNetSim**.

---

## 1. Panoramica

GasNetSim 4Qgis legge i layer vettoriali di QGIS (condotte e nodi), li esporta in formato CSV compatibile con GasNetSim, avvia la simulazione idraulica in un thread separato e ricrea nel progetto due layer colorimetrici con i risultati (pressioni, portate, velocità).

Il flusso di lavoro si divide in due fasi principali:

1. **Prepara Rete** — selezione dei layer, mappatura dei campi, collasso topologico (opzionale), export in CSV.
2. **Simula** — impostazione dei parametri fisici e del solutore, avvio simulazione, visualizzazione risultati.

---

## 2. Interfaccia

La finestra principale è divisa in tre pannelli orizzontali:

| Pannello | Contenuto |
|----------|-----------|
| **Sinistra** | Pannello di preparazione (Tab 1 e Tab 2) |
| **Centro** | Dashboard — log della simulazione in tempo reale |
| **Destra** | Properties Inspector — attributi di una feature selezionata sulla mappa |

---

## 3. Tab 1 — Prepara Rete

### 3.1 Scelta modalità

| Opzione | Descrizione |
|---------|-------------|
| **Rete già collassata** (checkbox deselezionato = default) | **Modalità A**: si parte da un layer condotte "grezzo" (geometria originale GIS). Il plugin esegue il collasso topologico: collega le condotte ai nodi più vicini entro il raggio di aggancio, assegna gli ID univoci e genera i CSV. |
| **Rete già collassata** (checkbox selezionato) | **Modalità B**: si usano layer già processati (condotte e nodi già con `pipe_id`, `node_a`, `node_b`, `node_id`). Il collasso viene saltato; si mappano solo i campi e si esportano i CSV. |

---

### 3.2 Modalità A — Layer da Collassare

Visibile quando la checkbox "Rete già collassata" è **deselezionata**.

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer vettoriale lineare (LineString / MultiLineString) con le condotte grezze del GIS. Il plugin genera automaticamente `pipe_id`, `node_a`, `node_b`, `length_m`. |
| **Campo diametro** | Campo del layer condotte che contiene il diametro interno. Auto-selezionato cercando tra: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. |
| **Unità diametro** | Unità del campo diametro: `pollici (in)`, `metri (m)`, `centimetri (cm)`. Il valore viene convertito internamente in metri. |
| **DEM (opz.)** | Layer raster DEM (facoltativo). Se fornito, viene usato per estrarre l'altitudine di ogni nodo (`altitude_m`). Se assente, altitudine = 0. |
| **Layer nodi** | Layer vettoriale puntuale con i nodi di rete (opzionale in modalità A). Se fornito, i nodi reference (a pressione fissa) vengono riconosciuti tramite il campo/valore specificato sotto. |
| **Campo reference** | Campo del layer nodi + valore che identifica i **nodi reference** (es. campo `type` = `reference`, oppure campo `matched` = `1`). I nodi reference sono quelli a pressione fissa nota (boundary condition del solutore). Almeno un nodo reference è obbligatorio. |
| **Flusso orario nodi** | Campo del layer nodi contenente il profilo di consumo orario (24 valori Smc/h separati dal carattere scelto). Se non selezionato, tutti i nodi usano il "Flusso placeholder". |
| **Raggio aggancio** | Distanza massima (in metri, unità della proiezione del layer) entro cui un nodo viene associato all'estremità di una condotta durante il collasso topologico. Default: 50 m. |
| **Aggiungi layer collassati al progetto** | Se spuntato, i layer nodi e condotte risultanti dal collasso vengono aggiunti al progetto QGIS (utili per ispezione). |

---

### 3.3 Modalità B — Layer Già Collassati

Visibile quando la checkbox "Rete già collassata" è **selezionata**.

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer condotte già collassato. Deve contenere almeno i campi per ID condotta, nodo A, nodo B, lunghezza, diametro. |
| **Layer nodi** | Layer nodi già collassato. Deve contenere almeno i campi per ID nodo, flag reference, flusso. |

Dopo aver scelto i layer, appaiono due sezioni di mappatura campi (Condotte e Nodi) descritte di seguito.

---

### 3.4 Mappatura Campi Condotte (Modalità B)

| Campo UI | Campo CSV prodotto | Descrizione |
|----------|--------------------|-------------|
| **ID pipe** | `pipe_id` | Identificatore univoco della condotta. Auto-selezionato tra: `pipe_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Nodo A** | `node_a` | ID del nodo di ingresso (upstream). Auto: `node_a`, `from_node`, `inlet`, `a`, `start_node`. |
| **Nodo B** | `node_b` | ID del nodo di uscita (downstream). Auto: `node_b`, `to_node`, `outlet`, `b`, `end_node`. |
| **Lunghezza** | `length_m` | Lunghezza della condotta in metri. Auto: `length_m`, `length`, `L`, `len`, `lunghezza`. |
| **Diametro** | `diameter_m` | Diametro interno in metri (conversione automatica se unità diversa). Auto: `diameter_m`, `diam_m`, `D`, `Diametro_pollici`, ecc. |
| **Unità diametro** | — | Unità del campo diametro: `m`, `in`, `cm`. |

---

### 3.5 Mappatura Campi Nodi (Modalità B)

| Campo UI | Campo CSV prodotto | Descrizione |
|----------|--------------------|-------------|
| **ID nodo** | `node_id` | Identificatore univoco del nodo. Auto: `node_id`, `id`, `FID`, `OBJECTID`. |
| **Altitudine** | `altitude_m` | Quota del nodo in metri sul livello del mare. Auto: `altitude_m`, `z_m`, `elev`, `altitude`, `ALTITUDINE`. Se assente, = 0. |
| **Flag reference** | `node_type` = `reference` | Campo + valore che identifica i nodi a pressione fissa (boundary condition). Auto campo: `matched`, `type`, `is_ref`, `reference`, `nodo_tipo`. Default valore: `1`. **Obbligatorio**: almeno un nodo reference deve essere presente; la simulazione viene bloccata se non ne viene trovato nessuno. |
| **Flusso orario nodi** | `flow_sm3_per_s` | Campo con il profilo di consumo orario: 24 valori Smc/h separati da `;` (o dal separatore scelto), es: `1.23;0.98;0.87;...`. Viene usato il valore relativo all'ora scelta in "Ora del giorno", convertito in sm³/s. Se non selezionato, si usa il "Flusso placeholder". |

---

### 3.6 Parametri Export

| Campo | Descrizione |
|-------|-------------|
| **Ora del giorno** | Ora (0–23) usata per estrarre il consumo dal profilo orario. Il pannello mostra in anteprima il valore estratto dal primo nodo con profilo disponibile. |
| **Separatore flussi** | Carattere separatore dei 24 valori nel campo flusso orario. Default: `;`. Opzioni: `,`, `|`, `:`, spazio, tab. |
| **Cartella output** | Cartella dove vengono salvati `sf_nodes.csv` e `sf_pipelines.csv`. Usata dal pulsante "Genera CSV". |

---

### 3.7 Pulsanti Azione (Tab 1)

| Pulsante | Azione |
|----------|--------|
| **↺ Ricarica layer** | Aggiorna i menu a tendina con i layer attualmente caricati nel progetto QGIS. |
| **> Genera CSV** | Esporta `sf_nodes.csv` e `sf_pipelines.csv` nella cartella output selezionata. Non avvia la simulazione. |
| **>> Genera CSV e Simula** | Esporta i CSV in una cartella temporanea e avvia immediatamente la simulazione, senza toccare il filesystem permanente. Equivale a fare tutto in un solo click. |

---

## 4. Tab 2 — Parametri Simulazione

### 4.1 Cartella Input CSV

Seleziona la cartella che contiene `sf_nodes.csv` e `sf_pipelines.csv`. Viene popolata automaticamente dopo "Genera CSV" o "Genera CSV e Simula".

---

### 4.2 Parametri Fisici

Questi valori vengono applicati sia all'export dei CSV sia alla simulazione.

| Campo | Unità | Default | Descrizione |
|-------|-------|---------|-------------|
| **Pressione reference** | bar | 70 | Pressione assegnata ai nodi reference nel CSV. Tipica: 70 bar (RNT Sicilia), 25 bar (RRT). |
| **Temperatura** | K | 300 | Temperatura operativa del gas (27 °C ≈ 300 K). |
| **Flusso nodi senza domanda** | sm³/s | 0,0001 | Flusso minimo assegnato ai nodi junction che nel CSV risultano a domanda zero (es. nodi di transito). Evita righe vuote nel solutore. Aumentare a 0,001 se la rete non converge per nodi isolati. |

---

### 4.3 Parametri Solutore

| Campo | Default | Descrizione |
|-------|---------|-------------|
| **Max iterazioni** | 50 | Numero massimo di iterazioni Newton-Raphson. Aumentare a 100–200 per reti molto grandi o mal condizionate. |
| **Tolleranza** | 1,0 | Criterio di convergenza (in unità del solutore). Ridurre a 0,1 per risultati più precisi; aumentare se la rete non converge. |
| **URF** | 2,0 | Under-Relaxation Factor. Controlla la stabilità delle iterazioni. Ridurre a 1,0–1,5 se la simulazione oscilla; aumentare fino a 3,0 per accelerare la convergenza su reti ben condizionate. |
| **Auto-calibra tol e URF** | off | Se attivo, il plugin tenta automaticamente di trovare la combinazione tol/URF che porta a convergenza, partendo dai valori impostati e riducendoli progressivamente. |

---

### 4.4 Rete e Composizione Gas

| Campo | Default | Descrizione |
|-------|---------|-------------|
| **Rugosità condotte** | 5×10⁻⁵ m | Rugosità interna assoluta. Acciaio: ~5×10⁻⁵ m; PE/HDPE: ~7×10⁻⁶ m; ghisa: ~2,6×10⁻⁴ m. Usata nella formula di attrito di Chen (Darcy-Weisbach). |
| **Flusso minimo export** | 1×10⁻⁶ sm³/s | Valore placeholder per nodi senza domanda nota nel CSV. Evita matrice singolare. Diverso dal "Flusso nodi senza domanda": questo vale per il CSV, quello per la patch pre-simulazione. |
| **Preset gas** | Gas naturale (100% CH₄) | Scorciatoia per compilare la composizione. Opzioni: gas naturale puro, tipico (94% CH₄), mix H₂/CH₄ al 10/20/50%, idrogeno puro. Selezionare "Personalizzato..." per inserire manualmente la composizione. |
| **Composizione (dict)** | `{'methane': 1.0}` | Composizione del gas come dizionario Python con le frazioni molari. La somma deve essere 1,0. Chiavi supportate: `methane`, `ethane`, `propane`, `butane`, `nitrogen`, `carbon_dioxide`, `hydrogen`. |

---

### 4.5 Visualizzazione Risultati

Controlla quali layer colorimetrici vengono creati nel progetto QGIS dopo la simulazione.

#### Nodi

| Elemento | Descrizione |
|----------|-------------|
| **Colora per** | Campo usato per la scala cromatica del layer nodi. Opzioni: Pressione, Temperatura, Spec. gravity, Z-factor, HHV, Wobbe, Densità, Dens. std, Massa molare. |
| **Checkbox campi** | Seleziona quali campi risultato includere nel layer nodi. I campi selezionati sono attributi interrogabili con lo strumento identifica. Default attivi: Pressione, Temp., Sp.gravity, Z-factor, HHV, Wobbe. |

#### Condotte

| Elemento | Descrizione |
|----------|-------------|
| **Colora per** | Campo usato per la scala cromatica del layer condotte. Opzioni: Portata (Smc/h), Velocità (m/s), Press. media (bar), Spec. gravity, Z-factor, Densità. |
| **Checkbox campi** | Campi risultato da includere nel layer condotte. Default attivi: Portata, \|Portata\|, Velocità, Press.media, Sp.gravity. |
| **Mostra frecce direzione flusso** | Se attivo (default), aggiunge un marcatore triangolare al punto centrale di ogni condotta, orientato nel verso del flusso del gas. La geometria viene invertita automaticamente per le condotte con portata negativa (flusso inverso). |

---

## 5. Avvio Simulazione

La simulazione può essere avviata in tre modi equivalenti:

1. **Tab 1 → ">> Genera CSV e Simula"** — modo consigliato: export + simulazione in un click.
2. **Tab 1 → "> Genera CSV"** poi **Tab 2 → "▶ Avvia Simulazione"** — utile per ispezionare i CSV prima di simulare.
3. **Pulsante "▶ Avvia Simulazione"** nel footer della finestra — rigenera i CSV dai layer correnti e avvia subito.

La simulazione gira in un thread separato (non blocca QGIS). Il log della Dashboard mostra in tempo reale: validazione CSV, caricamento rete, iterazioni, riepilogo pressioni, creazione layer risultato.

---

## 6. Campi Risultato — Nodi

Disponibili nel layer `[Risultati] Nodi — <nome_layer>`.

| Campo | Unità | Descrizione |
|-------|-------|-------------|
| `pressure_bar` | bar | Pressione assoluta al nodo calcolata dalla simulazione. |
| `temperature_k` | K | Temperatura operativa al nodo (propaga dalla reference). |
| `sp_gravity` | — | Specific gravity del gas al nodo (rapporto densità gas / aria a condizioni standard). |
| `z_factor` | — | Fattore di comprimibilità Z (equazione di stato del gas reale). |
| `hhv_mj_sm3` | MJ/sm³ | Higher Heating Value (potere calorifico superiore) del gas al nodo. |
| `wobbe_mj_sm3` | MJ/sm³ | Indice di Wobbe = HHV / √(sp_gravity). Indice di intercambiabilità del gas. |
| `density_kg_m3` | kg/m³ | Densità del gas nelle condizioni operative (temperatura e pressione del nodo). |
| `std_density_kg_sm3` | kg/sm³ | Densità standard del gas a 15 °C e 1,01325 bar. |
| `molar_mass` | g/mol | Massa molare media della miscela gas al nodo. |

---

## 7. Campi Risultato — Condotte

Disponibili nel layer `[Risultati] Condotte — <nome_layer>`.

| Campo | Unità | Descrizione |
|-------|-------|-------------|
| `flow_sm3s` | Smc/h | Portata volumetrica con segno. Positiva = flusso da nodo A a nodo B; negativa = flusso inverso (da B ad A). Le frecce direzionali riflettono questo segno. |
| `flow_abs_sm3s` | Smc/h | Portata volumetrica in valore assoluto. Usata anche per il calcolo dello spessore della linea (condotte con portata maggiore appaiono più spesse). |
| `velocity_m_s` | m/s | Velocità media del gas nella condotta, calcolata tenendo conto della comprimibilità (gas reale). Il valore è sempre positivo (modulo). |
| `avg_pressure_bar` | bar | Pressione media lungo la condotta = media delle pressioni ai nodi A e B. |
| `sp_gravity` | — | Specific gravity della miscela gas nella condotta (media tra i due estremi). |
| `z_factor` | — | Fattore Z medio nella condotta. |
| `density_kg_m3` | kg/m³ | Densità media del gas nelle condizioni operative della condotta. |

---

## 8. Layer Risultato in QGIS

Dopo ogni simulazione vengono creati (o ricreati) due layer in memoria nel progetto QGIS:

- **`[Risultati] Nodi — <nome>`** — layer puntuale con la colorimetria graduata (5 classi quantile) sul campo scelto. Scala cromatica: blu (valore minimo) → rosso (valore massimo).
- **`[Risultati] Condotte — <nome>`** — layer lineare con colorimetria graduata e spessore linea proporzionale alla portata assoluta. Se le frecce sono attive, ogni condotta ha un marcatore triangolare al centro orientato nel verso del flusso.

I layer precedenti vengono rimossi automaticamente prima di aggiungere i nuovi. Possono essere esportati come GeoPackage o Shapefile con il classico tasto destro → "Esporta".

I risultati vengono anche salvati automaticamente in CSV nella sottocartella `output/` della cartella input:
- `output/results_nodes.csv`
- `output/results_pipes.csv`

---

## Riferimenti Tecnici

---

## Classificazione condotte per specie (D.M. 17/04/2008)

Valida per reti di **trasporto** (trasmissione) di gas naturale in Italia.

| Specie | MOP (Pressione Max Esercizio) | Note |
|--------|-------------------------------|------|
| **1a** | > 24 bar (2,4 MPa)            | Rete nazionale di trasporto (RNT) |
| **2a** | 12 bar < MOP ≤ 24 bar (1,2–2,4 MPa) | Rete regionale di trasporto (RRT) |
| **3a** | 5 bar < MOP ≤ 12 bar (0,5–1,2 MPa)  | Derivazioni d'utenza alta pressione |
| **4a** | 1,5 bar < MOP ≤ 5 bar (0,15–0,5 MPa) | Reti di distribuzione locale |

> Le simulazioni attuali riguardano reti di **1a e 2a specie** (RNT/RRT Sicilia,
> pressioni 24–70 bar).

---

## Velocità massima in condotta — formula erosione (API RP 14E)

$$V_e = \frac{C}{\sqrt{\rho_{gas}}}$$

- $V_e$ — velocità di erosione [m/s]
- $\rho_{gas}$ — densità del gas nelle condizioni operative [kg/m³]
- $C = 100$ — costante per servizio continuo, gas secco (SI)

### Stime per metano (CH₄) a 15 °C

| Specie | MOP tipico | ρ CH₄ stimata | $V_e$ (erosione) | Limite pratico |
|--------|-----------|----------------|-------------------|----------------|
| 1a     | 60–70 bar | ~44–55 kg/m³  | **~10–13 m/s**    | ~10–15 m/s     |
| 1a     | 24–40 bar | ~17–30 kg/m³  | **~13–18 m/s**    | ~15 m/s        |
| 2a     | 12–24 bar | ~8–17 kg/m³   | **~18–24 m/s**    | ~15–20 m/s     |
| 3a     | 5–12 bar  | ~3,5–8 kg/m³  | **~24–35 m/s**    | rumore ~15 m/s |
| 4a     | 1,5–5 bar | ~1–3,5 kg/m³  | > 35 m/s          | rumore ~10 m/s |

> **Nota**: alle pressioni più alte (1a specie), il gas è più denso e la velocità
> di erosione è quindi **più bassa**, non più alta. Il limite pratico per le
> condotte di trasmissione RNT Sicilia (60–70 bar) è circa **10–14 m/s**.

> **Da verificare**: i valori esatti di riferimento dal D.M. 17/04/2008 e dagli
> standard SNAM/Terna vanno inseriti qui quando disponibili.

---

## Composizioni gas supportate da GasNetSim

Componenti riconosciuti dal solutore (chiavi del dict Python):

| Chiave              | Componente         |
|---------------------|--------------------|
| `methane`           | Metano (CH₄)       |
| `ethane`            | Etano (C₂H₆)       |
| `propane`           | Propano (C₃H₈)     |
| `butane`            | Butano (C₄H₁₀)     |
| `nitrogen`          | Azoto (N₂)         |
| `carbon_dioxide`    | Anidride carbonica (CO₂) |
| `hydrogen`          | Idrogeno (H₂)      |

### Preset disponibili nel plugin

```python
# Gas naturale puro
{'methane': 1.0}

# Gas naturale tipico (rete italiana)
{'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}

# Mix idrogeno 10%
{'methane': 0.90, 'hydrogen': 0.10}

# Mix idrogeno 20%
{'methane': 0.80, 'hydrogen': 0.20}

# Mix idrogeno 50%
{'methane': 0.50, 'hydrogen': 0.50}

# Idrogeno puro
{'hydrogen': 1.0}
```

---

## Parametri solutore — valori di riferimento

| Parametro         | Default plugin | Note |
|-------------------|---------------|------|
| Max iterazioni    | 50            | Aumentare a 100–200 per reti complesse |
| Tolleranza        | 1.0           | [bar o unità solutore] |
| URF               | 2.0           | Under-relaxation factor |
| Pressione ref.    | 70 bar        | Tipica RNT Sicilia |
| Temperatura ref.  | 300 K (27 °C) | |
| Rugosità condotte | 5×10⁻⁵ m      | Acciaio. PE/HDPE: 7×10⁻⁶ m; ghisa: 2,6×10⁻⁴ m |

---

## Unità diametro supportate

| Codice | Conversione |
|--------|------------|
| `m`    | × 1         |
| `in`   | × 0,0254    |
| `cm`   | × 0,01      |

---

## Reti di riferimento testate

| Rete             | Nodi | Condotte | Pressione | Risultato |
|------------------|------|----------|-----------|-----------|
| RRT Trapani      | 7    | 6        | 70 bar    | Convergenza in 4 iter, 7,7 s |
| RNT Sicilia      | —    | —        | 24–25 bar | Convergenza OK (pressioni 24,08–25,33 bar) |
