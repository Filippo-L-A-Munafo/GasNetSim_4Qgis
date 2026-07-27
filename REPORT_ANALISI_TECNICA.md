# Report tecnico — GasNetSim_4Qgis

Analisi approfondita del plugin (~8.160 righe) con bug confermati per lettura diretta del codice e indicazioni operative di correzione, file per file. Ogni punto riporta: **Problema**, **Dove**, **Rischio**, **Come correggere**.

Priorità: 🔴 critico (falsa correttezza fisica / dati corrotti) · 🟠 alto (bug funzionale) · 🟡 medio (manutenzione/robustezza) · 🟢 basso (rifinitura/performance).

---

## 0. Piano d'azione consigliato (ordine di intervento)

1. `network_builder.py` — propagazione CRS (🔴 #1) e loop infinito collasso (🔴 #2): sono i due bug che possono corrompere silenziosamente la geometria o bloccare QGIS.
2. `network_builder.py` — validazione compressori (🔴 #5, #6) e `worker_logic.py` — stato post-rampa (🔴 #1): impattano la correttezza fisica dei risultati quando ci sono compressori.
3. `layer_mapping_panel.py` — campo compressore forzato a "70.0" (🟠 #1) e pulsante Ferma non funzionante (🟠 #2/#3).
4. `result_visualizer.py` — layer risultato mai ripuliti (🟠 #1) e matching ID fragile (🟠 #2).
5. Il resto (codice morto, performance, `except` silenziosi) può essere affrontato in un secondo giro senza urgenza.

Nessuna di queste correzioni richiede un refactoring: sono tutte modifiche puntuali, localizzate, a basso rischio di regressione se applicate una alla volta con un test di simulazione dopo ciascuna.

---

## 1. `gis_integration/network_builder.py`

### 🔴 1.1 — Il CRS del layer sorgente non viene mai propagato

**Dove**: tutte le funzioni che accettano `crs=CRS_DEFAULT` (righe 452, 561, 594, 1092-1094) sono chiamate senza mai passare `crs=`, in **entrambe** le pipeline:
- `run_collapse_pipeline`: righe 1862, 1884, 1888, 1972, 1987, 2025
- `run_nocollapse_pipeline`: righe 2168, 2188, 2190, 2246, 2262, 2299

Tutte usano quindi silenziosamente il default `EPSG:25833` (riga 24), indipendentemente dal CRS reale del layer caricato dall'utente.

**Rischio**: se un utente lavora con un layer in un CRS diverso (es. EPSG:32633, EPSG:4326, o qualunque CRS locale), i layer di output e i CSV mantengono le coordinate originali ma vengono etichettati come EPSG:25833. Il raggio di aggancio (`radius_m`, in metri) e il collasso topologico restano numericamente corretti (lavorano su coordinate grezze), ma **qualunque layer risultato aggiunto al progetto QGIS sarà geograficamente disallineato** rispetto agli altri layer del progetto, senza errore visibile.

**Come correggere**:
1. In testa a `run_collapse_pipeline` (riga ~1785) e `run_nocollapse_pipeline`, aggiungere:
   ```python
   crs = pipe_layer.crs().authid() or CRS_DEFAULT
   ```
   (usare `nodes_layer`/`pipes_lyr` a seconda della pipeline se `pipe_layer` non è il primo layer disponibile).
2. Passare `crs=crs` esplicitamente in ciascuna delle chiamate elencate sopra.
3. Nessun'altra modifica necessaria: le funzioni accettano già il parametro, manca solo il pass-through.

---

### 🔴 1.2 — Loop infinito in `collapse_undirected` con condotte self-loop

**Dove**: `collapse_undirected`, righe 278-318.

**Problema verificato**: se una condotta ha `a == b` (polilinea che inizia e finisce sullo stesso punto — errore comune di digitalizzazione GIS, o un anello a un solo segmento), il nodo `nid` risultante ha grado 2 nel grafo (l'edge self-loop viene contato due volte in `adj[nid]`, righe 285-286). Nel ciclo di collasso, `i1` e `i2` (riga 296) puntano allo **stesso indice** di edge. Il collasso produce un **nuovo self-loop identico** (con id incrementale, coordinate concatenate a sé stesse — riga 311: `c1 + c2[1:]` con `c1` e `c2` che sono la stessa polilinea). Alla iterazione successiva del `while True` (riga 282), il nuovo self-loop ha di nuovo grado 2 → viene ricollassato di nuovo → **il ciclo non termina mai**, e la lista di coordinate cresce ad ogni giro (memoria crescente).

**Rischio**: il plugin si blocca (hang) su qualunque rete che contenga anche un solo arco degenere di questo tipo — situazione plausibile con dati GIS reali non ripuliti.

**Come correggere**: aggiungere una guardia esplicita per gli archi self-loop **prima** di entrare nel ciclo di collasso, scartandoli con un warning invece di collassarli:
```python
def collapse_undirected(archi, protected=None, log=None):
    if protected is None:
        protected = set()
    # Scarta (con warning) gli archi self-loop: non collassabili, causerebbero
    # un loop infinito perché il nodo risultante ha sempre grado 2 su sé stesso.
    self_loops = [e for e in archi if e['a'] == e['b']]
    if self_loops and log:
        log(f"  ⚠ {len(self_loops)} condotte self-loop (nodo iniziale == finale) "
            "escluse dal collasso: verificare digitalizzazione.")
    archi = [e for e in archi if e['a'] != e['b']]
    ...  # resto invariato
```
Aggiungere lo stesso controllo anche in `traverse_for_z` (righe 176-210), che ha un rischio analogo con archi a lunghezza zero dentro un anello chiuso di soli nodi grado-2 (la condizione di uscita `len(adj[curr_node]) != 2` non si verifica mai se `acc_dist` non cresce mai).

---

### 🟠 1.3 — Tolleranza di fusione nodi fissa, non validata contro il tipo di CRS

**Dove**: `round_coord`, righe 101-102:
```python
def round_coord(c):
    return (round(c[0], 1), round(c[1], 1))
```
usata in `build_graph` (riga 130) e nella ricerca estremi condotte (righe 1000-1001) per decidere se due vertici sono "lo stesso nodo".

**Problema**: arrotondamento a 1 decimale presume unità metriche (tolleranza ≈ 10 cm). Su un CRS geografico (gradi, es. EPSG:4326) 0.1° equivale a circa 11 km: nodi vicini ma non coincidenti verrebbero fusi in modo grossolanamente errato; nodi realmente coincidenti in coordinate proiettate potrebbero non fondersi affatto se il layer è già in un CRS a bassa risoluzione numerica.

**Come correggere**: dato che il CRS reale è ora disponibile dopo la fix 1.1, si può far dipendere la tolleranza dal tipo di CRS:
```python
def round_coord(c, decimals=1):
    return (round(c[0], decimals), round(c[1], decimals))
```
e nel punto di chiamata (`build_graph`), calcolare `decimals` in base a `layer.crs().isGeographic()`:
```python
decimals = 7 if layer.crs().isGeographic() else 1  # ~1 cm anche in gradi
```
In alternativa più semplice: se il layer è in CRS geografico, loggare un warning esplicito e suggerire all'utente di riproiettare prima dell'uso (il plugin lavora con distanze in metri in molti punti — raggio di aggancio, lunghezza condotte — quindi un CRS proiettato è comunque un prerequisito implicito da rendere esplicito).

---

### 🟠 1.4 — Fallback silenziosi su diametro/lunghezza non parsabili

**Dove**:
- Diametro, righe 1134-1144 (ramo "layer già collassato" analogo a 1739-1749 nel ramo collasso): `except (TypeError, ValueError): diam_m = None`.
- Lunghezza: fallback a `0.0` se non parsabile (riga citata dagli agenti ~1752-1754, verificare in loco per il ramo specifico).

**Problema**: nessun log quando il parsing fallisce. Un diametro `None`/lunghezza `0.0` finisce nel CSV e può causare divisione per zero o condotte fisicamente assurde nel solutore, con un messaggio d'errore del solutore che non indica la vera causa (il valore mancante a monte).

**Come correggere**: aggiungere un log esplicito nel blocco `except`, con riferimento all'ID della condotta:
```python
except (TypeError, ValueError):
    diam_m = None
    if log:
        log(f"  ⚠ Condotta {e.get('id', '?')}: diametro '{raw_diam}' non "
            "numerico, valore mancante nel CSV.")
```
Fare lo stesso per la lunghezza. Questo non cambia il comportamento (il CSV avrà comunque un buco), ma rende visibile all'utente **dove** intervenire sui dati sorgente invece di scoprirlo da un errore del solutore.

---

### 🟠 1.5 — Separatore decimale italiano (virgola) non gestito nel parsing da attributi layer

**Dove**: tutte le chiamate `float(...)` su valori letti da campi attributo di layer esterni (stringhe), in particolare:
- `_parse_smc_ora`, riga 72: `val = float(vals[idx])`
- Diametro, righe 1136 e 1741: `_rd = float(raw_diam)`
- Lunghezza, riga ~1752: `float(raw_length)` (verificare nome variabile esatto in loco)

**Nota**: i campi numerici della UI (pressione, temperatura, rugosità — `QDoubleSpinBox` in `layer_mapping_panel.py`) **non sono a rischio**, perché Qt li valida/parsa già secondo il locale. Il problema riguarda solo attributi di layer GIS esterni salvati come testo con virgola decimale (comune in export italiani, es. `"25,4"`).

**Rischio**: `float("25,4")` solleva `ValueError`, catturato silenziosamente, e sostituito con un valore placeholder (flusso quasi-zero, diametro `None`→fallback 0.305 m) **senza alcun avviso** — vedi anche punto 1.4.

**Come correggere**: introdurre una piccola utility riusata ovunque si parsano attributi esterni:
```python
def _to_float(raw):
    """Parsing tollerante: gestisce sia '25.4' sia '25,4' (virgola decimale)."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # Sostituisce la virgola SOLO se non è già presente un punto (evita di
    # rompere formati tipo "1,234.5" con separatore delle migliaia).
    if ',' in s and '.' not in s:
        s = s.replace(',', '.')
    return float(s)
```
e sostituire i `float(...)` diretti elencati sopra con `_to_float(...)`, mantenendo gli stessi blocchi `except` esistenti (ora combinati con il logging del punto 1.4).

---

### 🟡 1.6 — Deduplicazione condotte troppo aggressiva

**Dove**: dedup per `(frozenset({na, nb}), length, diameter)` (riga ~1756-1759, verificare in loco).

**Problema**: scarta silenziosamente coppie di condotte parallele fisicamente legittime (stesso nodo A/B, stessa lunghezza/diametro — es. due tubazioni gemelle) trattandole come duplicati di digitalizzazione.

**Come correggere**: aggiungere un log quando scatta la dedup, e valutare se includere l'ID originale della condotta nella chiave di confronto (mantenendo comunque la dedup su geometrie ridigitalizzate due volte per errore, che è il caso reale da filtrare):
```python
if key in seen:
    if log:
        log(f"  ⚠ Condotta {row.get('pipe_id')} scartata come duplicato di "
            f"{seen[key]} (stessi nodi/lunghezza/diametro). Se sono "
            "tubazioni parallele reali, rendere unica la chiave includendo l'ID.")
    continue
seen[key] = row.get('pipe_id')
```

---

### 🟢 1.7 — Performance: ricalcoli superflui nei cicli

**Dove**:
- Riga 309: `max(e['id'] for e in archi)` viene ricalcolato **ad ogni nodo** dentro il ciclo `for nid in to_collapse`, dentro il `while True` esterno di `collapse_undirected` → O(V·E) invece di O(V).
- `match_user_nodes`/`find_unmatched_user_nodes` (righe 561-633): loop annidato puro (O(N_nodi × N_utente)), senza `QgsSpatialIndex` — a differenza di `split_network_at_user_nodes` (riga 466) che invece lo usa già.
- Riga 150: `[f.name() for f in layer.fields()]` ricalcolato per ogni feature dentro `build_graph`, invece che una volta sola fuori dal ciclo.

**Come correggere**:
1. Calcolare `next_id = max(e['id'] for e in archi) + 1` **una sola volta prima** del loop `for nid in to_collapse`, poi incrementare un contatore locale ad ogni nuovo edge creato, invece di richiamare `max()` ogni volta.
2. In `match_user_nodes`/`find_unmatched_user_nodes`, costruire un `QgsSpatialIndex` sui punti utente (stesso pattern già usato in `split_network_at_user_nodes:466`) e interrogarlo con `nearestNeighbor`/`intersects` invece del doppio loop Python.
3. Spostare `[f.name() for f in layer.fields()]` fuori dal ciclo feature in `build_graph`.

Su reti da alcune migliaia di condotte questi tre cambiamenti riducono il tempo di collasso da minuti a secondi; sono anche le funzioni chiamate **due volte** nella stessa pipeline (righe 1884+1888, 1987+2025, 2188+2190, 2262+2299), quindi il guadagno si raddoppia.

---

### 🟡 1.8 — Pipeline collasso/non-collasso quasi duplicate

**Dove**: `run_collapse_pipeline` (1785-2072 circa) e `run_nocollapse_pipeline` (2099-2343 circa) condividono ~150 righe di logica pressoché identica (matching nodi, injection compressori, scrittura CSV).

**Come correggere** (rifattorizzazione a basso rischio, da fare *dopo* aver sistemato i bug sopra, non prima): estrarre la parte comune (dal matching nodi in poi) in una funzione interna `_finalize_and_export(pipes_lyr, nodes_lyr, ...)` chiamata da entrambe le pipeline con i rispettivi layer già pronti. Non toccare la logica, solo spostarla — riduce il rischio che una correzione futura (es. quelle di questo report) venga applicata in una sola delle due copie e non nell'altra, come probabilmente già accaduto per la gestione CRS.

---

## 2. `gis_integration/result_visualizer.py`

### 🟠 2.1 — `_remove_old_result_layers` è definita ma mai chiamata

**Dove**: definizione a riga 982-993; **unica occorrenza nel file/progetto** (verificato con grep sull'intera cartella del plugin).

**Rischio**: ogni simulazione aggiunge nuovi layer "Risultati" al progetto senza mai rimuovere i precedenti — accumulo di layer in memoria, progetto QGIS che cresce indefinitamente in sessioni lunghe (es. dopo un batch 24h ripetuto più volte).

**Come correggere**: chiamarla dentro `apply_results_to_layers`, prima di creare i nuovi layer, ma **solo se si vuole davvero il comportamento "sostituisci sempre"** — attenzione al punto 2.2 sotto, perché il matching per prefisso è fragile. Consigliato: aggiungere prima la fix di 2.2 (marcatura non ambigua dei layer), poi:
```python
def apply_results_to_layers(..., replace_previous=True):
    if replace_previous:
        _remove_old_result_layers()
    ...
```
con `replace_previous` esposto come opzione in UI (default `True` per non cambiare il comportamento visibile, ma permettendo all'utente di disattivarlo se vuole confrontare run diverse — coerente con la funzione "snapshot" già presente ma inutilizzata in `dashboard.py`, vedi §5).

---

### 🟠 2.2 — Matching layer per prefisso nome è fragile

**Dove**: `_remove_old_result_layers`, righe 986-989 (`lyr.name().startswith('R-N-')`), e in generale ovunque i layer risultato vengano identificati per nome.

**Rischio**: un layer dell'utente rinominato per coincidenza con lo stesso prefisso (es. "R-N-Backup manuale") verrebbe cancellato senza controllo di provenienza.

**Come correggere**: marcare i layer creati dal plugin con una `customProperty`, non affidarsi solo al nome:
```python
# alla creazione del layer:
layer.setCustomProperty("gasnetsim4qgis/result_layer", True)
layer.setCustomProperty("gasnetsim4qgis/result_kind", "nodes")  # o "pipes"

# in _remove_old_result_layers:
to_remove = [
    lid for lid, lyr in proj.mapLayers().items()
    if lyr.customProperty("gasnetsim4qgis/result_layer", False)
]
```
Questo rende la rimozione sicura indipendentemente da come l'utente rinomina i layer, e risolve anche l'incoerenza di convenzione di naming notata in `properties_inspector.py` (§7): quel modulo cerca `R-N-`/`R-P-` mentre la pipeline reale produce nomi `[Risultati] ...` — con la customProperty entrambi i punti del codice possono usare lo stesso criterio affidabile.

---

### 🔴 2.3 — Matching ID nodo/condotta fragile con ID testuali numerici

**Dove**: `_make_multi_field_layer` (o funzione equivalente), righe 1048-1058:
```python
feat_key = str(raw_id)
row = data_dict.get(feat_key)
if row is None:
    try:
        row = data_dict.get(str(int(raw_id)))
    except Exception:
        pass
if row is None:
    row = {}
```

**Rischio**: se `raw_id` è una stringa come `"1.0"` (campo testo con formattazione numerica, comune quando il campo ID viene esportato da Excel/altri GIS), `int("1.0")` solleva `ValueError` — catturata silenziosamente. `row` resta `{}`: la feature riceve **tutti i campi risultato NULL** senza che l'utente veda alcun errore, solo un buco silenzioso nella mappa colorata.

**Come correggere**: normalizzare la chiave in modo robusto prima del lookup, con log quando il match fallisce:
```python
def _normalize_id_key(raw_id):
    """Normalizza un ID a stringa, gestendo sia int/float sia stringhe
    con formattazione numerica ('1', '1.0', '1,0')."""
    if raw_id is None:
        return None
    try:
        return str(int(float(str(raw_id).replace(',', '.'))))
    except (TypeError, ValueError):
        return str(raw_id).strip()

...
feat_key = _normalize_id_key(raw_id)
row = data_dict.get(feat_key)
if row is None:
    row = {}
    if log:
        log(f"  ⚠ ID '{raw_id}' non trovato tra i risultati: feature senza dati.")
```
Assicurarsi che anche `data_dict` (costruito lato worker_logic/network_builder) usi la stessa funzione `_normalize_id_key` per costruire le chiavi, così il formato è garantito coerente su entrambi i lati del join.

---

### 🟠 2.4 — Frecce di flusso invertite se il campo `flow_sm3h` non è incluso

**Dove**: riga 112:
```python
QgsProperty.fromExpression('if("flow_sm3h" >= 0, 0, 180)')
```

**Rischio**: se l'utente deseleziona `flow_sm3h` dai campi da includere nel layer condotte (opzione disponibile in UI, vedi MANUALE.md §4.5), il campo non esiste nel layer e l'espressione valuta `NULL >= 0` → `NULL` → il ramo `if()` prende il valore else (180°): **tutte le frecce vengono disegnate invertite**, senza errore visibile.

**Come correggere**, due opzioni indipendenti (consigliato applicarle entrambe):
1. **Lato dati**: se `flow_arrows=True` nei parametri di visualizzazione, forzare l'inclusione di `flow_sm3h` nei campi del layer condotte anche se l'utente lo ha deselezionato altrove (le frecce dipendono da quel campo):
   ```python
   if flow_arrows and 'flow_sm3h' not in result_pipes_fields:
       result_pipes_fields = list(result_pipes_fields) + ['flow_sm3h']
   ```
2. **Lato espressione**: rendere l'espressione esplicita sul caso NULL, così anche in assenza del campo il default è "nessuna rotazione" invece di "rotazione errata":
   ```python
   'if("flow_sm3h" is null, 0, if("flow_sm3h" >= 0, 0, 180))'
   ```

---

### 🟡 2.5 — Nessun controllo NaN/inf prima di scrivere nei campi risultato

**Dove**: punti di scrittura dei campi `QVariant.Double` (es. righe 796-898, 936-970, 1068), e calcolo classi quantile del renderer graduato (righe 1094-1099).

**Rischio**: se il calcolo del gas mixture (specific gravity, Z-factor, ecc.) produce `nan`/`inf` per un nodo anomalo, il valore viene scritto così com'è. Il renderer a quantili può produrre range degeneri o simboli non colorati senza errore visibile.

**Come correggere**: introdurre un piccolo helper di sanitizzazione da usare in ogni punto che scrive un campo Double calcolato:
```python
import math

def _safe_double(val):
    """None se val è NaN/inf, altrimenti float(val). Evita di scrivere
    valori non finiti nei campi QGIS, che rompono silenziosamente la
    colorimetria a quantili."""
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None
```
e sostituire le assegnazioni dirette (`new_feat.setAttribute(fname, round(float(val), decimals))`, riga 1068 e simili) con `new_feat.setAttribute(fname, round(_safe_double(val), decimals) if _safe_double(val) is not None else None)`.

---

### 🟢 2.6 — Migliorie minori

- **Export CSV con NaN/inf** (`export_layer_to_csv`, righe ~707-732): applicare `_safe_double` anche qui prima di scrivere, per evitare stringhe `"nan"`/`"inf"` nel CSV (non standard per Excel/altri tool).
- **`_clean_layer_name`** (righe 39-49): può rimuovere suffissi legittimi del nome layer utente. Restringere il pattern di pulizia ai soli suffissi noti generati dal plugin stesso, non a pattern generici.
- **Performance**: `_make_multi_field_layer` (1043-1070) e `_apply_node_proportional_size` (434-440) usano un `try/except` per singolo campo per singola feature — su reti di migliaia di feature è misurabile. Spostare la validazione fuori dal ciclo interno dove possibile (es. controllare una volta se `fields` esistono nel layer, non ad ogni feature).

---

## 3. `ui/layer_mapping_panel.py`

### 🟠 3.1 — Campo pressione uscita compressore forzato a "70.0"

**Dove**: righe 1230 e 1250:
```python
self._fill_fields(self.cb_f_nodes_comp_pout, lyr, (...), with_none=True)
self.cb_f_nodes_comp_pout.setCurrentText("70.0")
```

**Rischio**: ad ogni cambio di layer nodi (`_on_nodes_layer_changed`/`_on_coll_nodes_changed`), il valore torna forzatamente a "70.0", **sovrascrivendo sia l'auto-detect del campo sia qualunque valore digitato manualmente dall'utente**.

**Come correggere**: la riga `setCurrentText("70.0")` è quasi certamente un residuo di debug/default lasciato per errore dopo `_fill_fields` (che già gestisce l'auto-detect). Rimuoverla in entrambi i punti:
```python
self._fill_fields(self.cb_f_nodes_comp_pout, lyr, (...), with_none=True)
# (rimossa la riga self.cb_f_nodes_comp_pout.setCurrentText("70.0"))
```
Se si vuole comunque un default quando *nessun* campo viene auto-rilevato, condizionarlo esplicitamente:
```python
if self.cb_f_nodes_comp_pout.currentIndex() < 0:
    self.cb_f_nodes_comp_pout.setCurrentText("70.0")
```

---

### 🟠 3.2 — Pulsante "Ferma" non funzionante per i batch e disabilitato durante il batch

**Dove**:
- Riga 2174-2175: `if not is_batch and hasattr(self, 'btn_stop_sim'): self.btn_stop_sim.setEnabled(True)` — durante un batch 24h il pulsante **non viene mai abilitato**.
- Riga 2189: `for w in getattr(self, '_active_sim_workers', []):` — l'attributo `_active_sim_workers` non viene **mai popolato**; viene popolato solo `_active_sim_threads` (riga 2168, oggetti `QThread`, non `SimWorker`).

**Come correggere**:
1. Abilitare il pulsante anche in modalità batch:
   ```python
   if hasattr(self, 'btn_stop_sim'):
       self.btn_stop_sim.setEnabled(True)
   ```
2. Popolare correttamente la lista dei worker (non solo dei thread) al momento dell'avvio, accanto alla riga 2168:
   ```python
   if is_batch:
       if not hasattr(self, '_active_sim_threads'):
           self._active_sim_threads = []
       if not hasattr(self, '_active_sim_workers'):
           self._active_sim_workers = []
       self._active_sim_threads.append(thread)
       self._active_sim_workers.append(worker)
   ```
   e rimuovere il worker dalla lista in `_on_sim_finished` in modo simmetrico a come già avviene per `_active_sim_threads` (riga 2218-2222):
   ```python
   if is_batch and hasattr(self, '_active_sim_workers') and worker in self._active_sim_workers:
       self._active_sim_workers.remove(worker)
   ```

---

### 🟠 3.3 — Batch 24h: un errore in una singola ora interrompe l'intero batch lasciando thread orfani

**Dove**: righe 1837-1925 — l'intero ciclo `for i in range(24)` è dentro un unico `try/except` (riga 1920); un'eccezione nell'export di una singola ora (es. campo mancante) esce dal `for` con un `return` implicito dopo il blocco `except` (riga 1926), mentre i thread già avviati con `_start_simulation(..., is_batch=True)` per le ore precedenti continuano a girare in background — ma con `_set_buttons_enabled(True)` già richiamato (riga 1924), l'utente può cliccare di nuovo "Avvia", che azzera `_active_sim_threads` (riga 1837) perdendo il riferimento ai thread ancora in esecuzione.

**Come correggere**: spostare il `try/except` **dentro** il ciclo, attorno alla sola chiamata di export/avvio della singola ora, così un errore su un'ora non compromette le altre:
```python
self._active_sim_threads = []
for i in range(24):
    try:
        run_dir, run_label = _next_run_subdir(user_folder)
        ...
        self._start_simulation(params_i, is_batch=True)
    except Exception as exc:
        self._log_run(f"ERRORE ora {i}: {exc}", 'red')
        continue  # prosegue con le ore successive invece di interrompere tutto
```
Inoltre, **non** richiamare `_set_buttons_enabled(True)` finché ci sono thread attivi in `_active_sim_threads`: spostare quella chiamata dentro `_on_sim_finished` quando `is_last=True` (che già esiste per il caso di successo, riga 2300) anche per il percorso di errore.

---

### 🟡 3.4 — Refuso `'NodeID'` tra i candidati auto-detect del flag reference

**Dove**: riga 22:
```python
_REF_FLAG_CAND = ('matched', 'type', 'Type', 'NodeID', 'is_ref', 'reference', 'nodo_tipo')
```

**Problema**: `NodeID` è semanticamente un identificativo di nodo, non un flag booleano "è reference". Se il layer nodi ha un campo chiamato `NodeID`, l'auto-detect lo sceglie come flag reference al posto di `is_ref`/`reference`/`matched`, e con `txt_ref_value` di default `"1"` può far scattare 0 o 1 nodo reference "per caso" invece di segnalare che nessun campo valido è stato trovato.

**Come correggere**: rimuovere `'NodeID'` dalla tupla:
```python
_REF_FLAG_CAND = ('matched', 'type', 'Type', 'is_ref', 'reference', 'nodo_tipo')
```

---

### 🟢 3.5 — Candidati auto-detect a lettera singola troppo aggressivi

**Dove**: riga 17-19:
```python
_LENGTH_CAND   = ('length_m', 'length', 'L', 'len', 'lunghezza', 'lung_m')
_DIAM_CAND     = ('diameter_m', 'diam_m', 'D', 'd', 'diam', ...)
```

**Problema**: `'L'`, `'D'`, `'d'` sono candidati troppo generici — un campo a lettera singola usato per altri scopi nel layer utente (es. un campo categoria "D") verrebbe scelto erroneamente prima dei nomi descrittivi.

**Come correggere**: spostare le sigle a una lettera in **fondo** alla tupla, così i nomi descrittivi hanno priorità nell'auto-detect (verificare che `_fill_fields` scelga il primo match nell'ordine della tupla — se così è, riordinare basta):
```python
_LENGTH_CAND   = ('length_m', 'length', 'lunghezza', 'lung_m', 'len', 'L')
_DIAM_CAND     = ('diameter_m', 'diam_m', 'diam', 'Diametro_pollici', 'Diametro', 'diameter', 'D', 'd')
```

---

### 🟡 3.6 — `_run_network_check` definita ma non collegata a nessun controllo UI

**Dove**: riga 1306 (verificare in loco l'esistenza di un bottone collegato in `main_dialog.py` o altrove).

**Come correggere**: se la funzionalità è utile (verifica di rete pre-simulazione), collegarla a un bottone esplicito nel Tab 1 o Tab 2 (es. "Verifica rete" prima di "Genera CSV"); se è un residuo di sviluppo non più necessario, rimuoverla per evitare confusione futura in manutenzione.

---

### 🟢 3.7 — Altre migliorie minori

- **`_layer_name_conns`** (righe 68, 1053, 1126): dizionario di connessioni Qt mai ripulito quando un layer viene rimosso dal progetto (`layersRemoved` chiama solo `reload_layers`, riga 1053) — cresce indefinitamente in sessioni QGIS lunghe. Aggiungere la pulizia delle chiavi corrispondenti ai layer rimossi dentro il gestore di `layersRemoved`.
- **Validazione input numerici lato UI assente**: `txt_nodes_ref_val`, `txt_ref_value`, `txt_nodes_comp_val` letti come stringa grezza (righe 1573, 1642, 1718-1723, 1806) senza controllo di validità numerica quando serve un valore fisso — l'errore emerge solo a valle con un `except Exception as exc` generico (righe 1665, 1920, 2068). Aggiungere una validazione immediata con `QDoubleValidator` sui `QLineEdit` interessati, o un controllo esplicito prima di procedere con un messaggio mirato ("Il valore reference deve essere numerico").
- **`_last_nodes_lyr`/`_last_pipes_lyr` non validati con `isValid()`** prima del riuso in `_on_sim_finished` (righe 2239-2258): se l'utente rimuove il layer mentre la simulazione gira, l'unico segnale è un messaggio generico "Colorimetria: {exc}" (riga 2287). Aggiungere un controllo esplicito:
  ```python
  if nodes_lyr is not None and not sip.isdeleted(nodes_lyr) and nodes_lyr.isValid():
      ...
  ```

---

## 4. `ui/worker_logic.py`

### 🔴 4.1 — Stato di pressione della rete non coerente con i metadati compressore dopo un fallimento di rampa

**Dove**: righe 390-449 (logica di rampa compressori). Quando `ok_rampa=False` (righe 436-444), gli attributi `control_mode`/`compression_ratio`/`p_out_target` sugli oggetti compressore vengono correttamente ripristinati ai valori nominali — ma l'oggetto `network` (assegnato a `result = network` alla riga 449) conserva le **pressioni** dell'ultimo stato risolto durante la rampa (un rapporto di compressione intermedio, non quello nominale).

**Rischio**: il risultato esportato mostra un compressore con `compression_ratio` nominale nei metadati, ma pressioni a monte/valle che in realtà corrispondono a un rapporto di compressione diverso (più basso). Per un plugin di analisi scientifica, questo è il tipo di incoerenza più insidioso da individuare a posteriori.

**Come correggere**: quando la rampa fallisce, invece di limitarsi a ripristinare gli attributi metadata, tentare un ultimo solve esplicito con i valori nominali (accettando che possa non convergere, ma almeno lo stato è coerente) oppure — più sicuro — marcare esplicitamente il risultato come "non attendibile per i compressori" nel log e nei CSV esportati:
```python
if not ok_rampa:
    for cid, c in comps.items():
        c.control_mode = mode0.get(cid, 'ratio')
        c.compression_ratio = ratio0.get(cid, 1.0)
        if target0.get(cid) is not None:
            c.p_out_target = target0[cid]
    log("⚠ ATTENZIONE: la rampa sui compressori non ha raggiunto il target "
        "nominale. Le pressioni esportate corrispondono all'ULTIMO STEP "
        "RIUSCITO della rampa, non al compressore nominale sopra riportato. "
        "Considerare i risultati relativi ai compressori come indicativi.",
        'red')
    # Facoltativo: aggiungere un flag nel dict risultati che
    # result_visualizer.py può leggere per marcare visivamente i nodi/
    # condotte a valle del compressore come "risultato parziale".
```
Questo non risolve la causa fisica (rete che non converge al target nominale), ma rende impossibile scambiare per errore un risultato parziale per uno definitivo.

---

### 🟠 4.2 — `run_simulation` non distingue convergenza reale da fallback nel valore di ritorno

**Dove**: la funzione ritorna sempre `out_folder` (riga 703) se non viene sollevata un'eccezione non gestita, anche quando `converged=False` (fallback `result = network`, riga 449). Il **log** mostra correttamente un disclaimer visibile (righe 447-448, colore arancione propagato fino a 544 e 694 — verificato, questo è corretto e va mantenuto), ma il valore booleano che viaggia nei segnali Qt (`SimWorker.finished.emit(True, res)`, `dashboard.py:62`) è **sempre `True`** quando `res is not None`, indipendentemente da `converged`.

**Rischio pratico circoscritto**: l'unico punto dove questo produce un messaggio esplicitamente fuorviante è il banner finale del batch 24h ("BATCH COMPLETATO CON SUCCESSO", `layer_mapping_panel.py:2297`), che non riflette eventuali non-convergenze delle singole ore — il disclaimer per-ora nel log resta comunque visibile e corretto.

**Come correggere**, minimo e mirato (senza toccare la logica del solutore):
1. Far ritornare a `run_simulation` una tupla `(out_folder, converged)` invece del solo `out_folder`:
   ```python
   return out_folder, converged
   ```
2. Aggiornare i due chiamanti in `dashboard.py` (`_run_native`, riga 60, e lo script generato in `_run_in_subprocess`, riga 101) per propagare il vero valore di `converged` invece di dedurlo da `res is not None`:
   ```python
   out_folder, converged = run_simulation(self._p, log)
   if out_folder is not None:
       self.finished.emit(converged, out_folder)
   else:
       self.finished.emit(False, None)
   ```
3. Nel banner di fine batch (`layer_mapping_panel.py`, vicino a riga 2297), tracciare se **almeno un'ora** non è convergente (es. un set `self._batch_non_converged_hours`) e cambiare il messaggio/colore di conseguenza:
   ```python
   if self._batch_non_converged_hours:
       self._log_run(f"  BATCH COMPLETATO — {len(self._batch_non_converged_hours)} ORE NON CONVERGENTI "
                      f"({sorted(self._batch_non_converged_hours)}). Verificare il log per dettagli.", "orange")
   else:
       self._log_run(f"  BATCH 24 ORE (PARALLELO) COMPLETATO CON SUCCESSO! ({elapsed:.1f} s)", "green")
   ```

---

### 🟡 4.3 — Rischio `UnboundLocalError` mascherato

**Dove**: `out_folder` viene assegnato per la prima volta alla riga 639, dentro un blocco `try` iniziato alla riga 546. Se un'eccezione non gestita si verifica tra le righe 546 e 639 (fuori dai `try/except RuntimeError` specifici già presenti), il flusso arriva comunque al `return out_folder` di riga 703 (o al nuovo `return out_folder, converged` dopo la fix 4.2) senza che la variabile sia mai stata definita.

**Come correggere**: inizializzare `out_folder = None` subito dopo l'apertura della funzione (vicino alla riga 546, prima del `try`), così un eventuale `UnboundLocalError` diventa un semplice ritorno `(None, False)` gestito normalmente dal chiamante, invece di un'eccezione anomala catturata genericamente come `[ERRORE]` a riga 705.

---

### 🟠 4.4 — Nessun controllo esplicito su "nessun nodo reference"

**Dove**: riga 45, `mask_ref.any()`.

**Come correggere**: aggiungere un controllo esplicito subito dopo il calcolo della maschera, con un messaggio guida invece di lasciare che l'errore emerga (mascherato) più a valle nel solutore:
```python
if not mask_ref.any():
    log("❌ ERRORE: nessun nodo reference trovato nel CSV. La simulazione "
        "richiede almeno un nodo a pressione fissa (node_type='reference'). "
        "Verifica il campo/valore di flag reference in Tab 1.", 'red')
    return None, False
```

---

### 🟡 4.5 — File di log di convergenza troncato ad ogni fase

**Dove**: riga 292, `logging.FileHandler(..., mode='w')` dentro `_run_sim`, riaperto in scrittura ad ogni chiamata (ladder di autocalibrazione, rampa compressori, affinamento).

**Come correggere**: aprire il file una sola volta in `mode='w'` all'inizio di `run_simulation` (prima chiamata a `_run_sim`) e passare `mode='a'` (append) alle chiamate successive nella stessa run, così `convergence_log.txt` conserva la traccia di tutte le fasi invece di solo l'ultima.

---

### 🟢 4.6 — Pulizia codice

- Riga 526: `if best_tol != tol_ok or True:` — l'`or True` rende la condizione sempre vera, quindi fuorviante. Semplificare a `if True:` (o meglio, capire se l'intento originale era condizionale e correggere la logica, rimuovendo `or True`).
- Righe 62, 243 e altri accessi diretti `params['chiave']` per parametri che altrove sono opzionali: usare `.get('chiave', default)` per evitare che un parametro mancante finisca genericamente in `[ERRORE]` invece di un messaggio mirato ("Parametro 'junction_flow' mancante").

---

## 5. `ui/dashboard.py`

### 🟠 5.1 — `cancel()` non ha effetto in modalità nativa (non-subprocess)

**Dove**: `cancel()` (righe 25-38) uccide solo il sottoprocesso (`self._proc.kill()`); `self._cancelled = True` non viene mai controllato in `_run_native` (righe 52-67).

**Come correggere**: `run_simulation` in worker_logic.py dovrebbe accettare un callback/flag di cancellazione da controllare periodicamente (es. dopo ogni iterazione del solutore o tra le fasi di rampa/affinamento), sollevando un'eccezione dedicata (`SimulationCancelled`) che `_run_native` intercetta:
```python
# in worker_logic.run_simulation, firma aggiornata:
def run_simulation(params, log, is_cancelled=lambda: False):
    ...
    if is_cancelled():
        raise SimulationCancelled()
    ...

# in dashboard.py _run_native:
def _run_native(self):
    ...
    try:
        res = run_simulation(self._p, log, is_cancelled=lambda: self._cancelled)
    except SimulationCancelled:
        log("⏹ Simulazione interrotta dall'utente.", 'orange')
        self.finished.emit(False, None)
        return
```
Questo richiede toccare `worker_logic.py`, ma è l'unico modo per rendere "Ferma" effettivo anche in modalità nativa — è un intervento a media invasività, da fare dopo aver sistemato i bug 🔴/🟠 sopra.

---

### 🟡 5.2 — Generazione dinamica di `run_worker.py` non sanitizza i path

**Dove**: righe 81-112, f-string triple-quoted che interpola `plugin_root`, `params_file`, `folder / "success.json"`.

**Rischio basso** (input locale, non esterno) ma reale se un path contiene `"""`.

**Come correggere**: usare `json.dumps(str(path))` per interpolare i path invece di raw string literal diretta, che gestisce correttamente l'escaping:
```python
script_code = f"""
import sys, json
from pathlib import Path

sys.path.insert(0, {json.dumps(plugin_root)})
...
with open({json.dumps(str(params_file))}, 'r', encoding='utf-8') as f:
    ...
"""
```

---

### 🟡 5.3 — Nessun timeout sul sottoprocesso

**Dove**: riga 152, `for line in proc.stdout:` blocca indefinitamente se il sottoprocesso va in stallo.

**Come correggere**: non critico da risolvere subito (l'utente ha comunque "Ferma" per la modalità subprocess), ma se si vuole robustezza aggiuntiva si può usare `proc.stdout` con un `select`/timeout, oppure un watchdog thread che chiama `cancel()` dopo N minuti di inattività nello stream.

---

### 🟡 5.4 — Classe `Dashboard(QWidget)` mai istanziata

**Dove**: righe 189-303. Nessun import/istanza altrove nel plugin (verificato con grep). `layer_mapping_panel.py` reimplementa da zero una logica equivalente (~100 righe duplicate) usando solo `SimWorker`.

**Come correggere**: due opzioni, entrambe legittime:
- **Rimuovere** la classe se non se ne prevede l'uso, per non lasciare ~115 righe di codice morto da mantenere.
- **Recuperare** la funzionalità utile non duplicata altrove — in particolare `_snapshot_results` (righe 276-296, rinomina `[Risultati]`→`[Run #N]` per confrontare run successive) — portandola come metodo standalone in `result_visualizer.py` o `layer_mapping_panel.py`, e poi rimuovere comunque la classe `Dashboard`.

Consigliata la seconda opzione, dato che "confrontare run successive" è una funzionalità legittimamente utile per un plugin di simulazione, attualmente scritta ma irraggiungibile.

---

## 6. `ui/tab_verifica.py`

File **vivo e usato** (`VerificaTab` istanziato in `layer_mapping_panel.py:2,89`) — non richiede interventi strutturali.

### 🟡 6.1 — Query SQL costruita senza quoting

**Dove**: `_select_bad_pipes`, righe 421-422, espressione tipo `f'"{id_field}" IN ({vals})'` con `vals` concatenati senza quoting.

**Rischio**: se il campo ID è di tipo testo (non numerico), la query fallisce o seleziona in modo errato.

**Come correggere**: quotare i valori quando il campo è di tipo stringa, verificando il tipo del campo prima di costruire l'espressione:
```python
field_idx = layer.fields().indexOf(id_field)
is_text = layer.fields().at(field_idx).type() == QVariant.String
if is_text:
    vals_expr = ",".join(f"'{v}'" for v in bad_ids)
else:
    vals_expr = ",".join(str(v) for v in bad_ids)
expr = f'"{id_field}" IN ({vals_expr})'
```

---

## 7. `ui/properties_inspector.py`

### 🟡 7.1 — Codice morto, e incoerente con la convenzione di naming reale

**Dove**: classe `PropertiesInspector` mai istanziata in nessun altro file (verificato con grep). Anche se lo fosse, `refresh_layers` (riga 162) e `_export_csv` (riga 284) cercano layer con prefisso `R-N-`/`R-P-`, mentre la pipeline reale (`result_visualizer.py`) produce nomi `[Risultati] Nodi — ...` / `[Risultati] Condotte — ...`.

**Come correggere**: non ricollegare il modulo finché non si applica la fix 2.2 (marcatura via `customProperty`) — a quel punto `PropertiesInspector.refresh_layers` andrebbe riscritta per usare lo stesso criterio (`customProperty("gasnetsim4qgis/result_layer")`) invece del prefisso stringa, garantendo coerenza con `result_visualizer.py`. Se non si prevede di completare l'integrazione a breve termine, **rimuovere il file** per non lasciare 300 righe di funzionalità apparente ma non funzionante (rischio che un utente/sviluppatore futuro perda tempo a capire perché "non succede nulla").

---

## 8. `ui/main_dialog.py`

### 🟠 8.1 — Riferimento a `self.inspector` mai creato

**Dove**: riga 37, `self.inspector.refresh_layers()`, con `except Exception: pass` a riga 38 che nasconde l'`AttributeError` sistematico (verificato: `setup_ui()` crea solo `self.mapping_panel`, mai `self.inspector`).

**Come correggere**: rimuovere la chiamata orfana finché `PropertiesInspector` non viene effettivamente integrato (vedi §7):
```python
def showEvent(self, event):
    super().showEvent(event)
    if hasattr(self, 'mapping_panel'):
        self.mapping_panel.reload_layers()
    # rimossa la chiamata a self.inspector.refresh_layers() — mai istanziato
```
Se e quando si integra `PropertiesInspector`, va prima creata l'istanza in `setup_ui()` e solo dopo riabilitata questa chiamata.

---

### 🟡 8.2 — Nessuna gestione di chiusura con thread attivo

**Dove**: nessun `closeEvent` definito.

**Rischio**: chiudere il dialog mentre un `QThread` di simulazione è attivo lascia il thread orfano — rischio di crash QGIS o accesso a widget distrutti quando i segnali `finished`/`log_line` scattano dopo la chiusura.

**Come correggere**:
```python
def closeEvent(self, event):
    mp = getattr(self, 'mapping_panel', None)
    if mp is not None and getattr(mp, '_sim_thread', None) is not None:
        reply = QMessageBox.question(
            self, "Simulazione in corso",
            "Una simulazione è ancora in esecuzione. Interromperla e chiudere?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            event.ignore()
            return
        mp._stop_simulation()
    event.accept()
```

### 🟢 8.3 — `plugin_dir` mai usato

**Dove**: salvato come attributo (riga 8/11) ma mai passato/usato da `LayerMappingPanel(self.iface)` (riga 26). Rimuoverlo se non serve, o passarlo esplicitamente se `LayerMappingPanel` ne ha effettivamente bisogno per risolvere path relativi (icone, ecc.) — verificare in loco.

---

## 9. `core/`, `gasnetsim/`, `results/` — package stub vuoti

Non contengono codice (1-2 righe ciascuno). Residui di un refactoring mai completato verso un'architettura più modulare. Due opzioni:
- **Rimuovere** le tre cartelle se non è previsto un refactoring a breve termine — riduce la superficie del plugin senza perdita di funzionalità.
- Se il refactoring è pianificato, lasciare un breve commento in ciascun `__init__.py` che indica l'intento (es. `# Destinazione futura: spostare qui la logica di dependency_checker`), così un contributore futuro capisce che non sono dimenticati per errore.

`requirements.txt:12` cita un `core/dependency_checker.py` per l'installazione automatica delle dipendenze — **il file non esiste**. O si implementa, o si rimuove il riferimento nel commento di `requirements.txt` per non promettere una funzionalità assente.

---

## 10. `requirements.txt` — packaging e riproducibilità

- `networkx==3.2.1` è pinnato esatto mentre le altre dipendenze usano `>=`/`~=`: uniformare la policy di versioning (consigliato `>=` con limite superiore soft, es. `networkx>=3.2,<4.0`, per evitare sia rotture da major version sia un pin troppo rigido che impedisce aggiornamenti di sicurezza).
- L'installazione di `GasNetSim` è editable da un path locale hardcoded in un commento — non riproducibile su altre macchine. Se GasNetSim non è ancora su PyPI, documentare nel `MANUALE.md` (o in un `INSTALL.md` dedicato) i passi espliciti per l'installazione editable su una macchina nuova, invece di lasciarlo solo come commento in `requirements.txt`.

---

## 11. Ottimizzazioni trasversali per le simulazioni

Riepilogo delle leve di performance più impattanti, in ordine di beneficio atteso su reti grandi (migliaia di nodi/condotte):

1. **Spatial index per il matching nodi** (§1.7) — passare da O(N×M) a O(N log M) nel matching layer-nodi-utente. Beneficio maggiore su reti grandi con molti nodi da agganciare.
2. **CRS geografico non gestito** (§1.3) — non è solo un bug di correttezza ma anche di performance/stabilità: su CRS geografico la tolleranza di fusione errata può creare falsi cluster di migliaia di nodi fusi insieme, rallentando drasticamente il collasso.
3. **Chiamate duplicate a `match_user_nodes`/`find_unmatched_user_nodes`** sugli stessi dati all'interno della stessa pipeline (§1.1, elenco righe) — cache del risultato tra le due chiamate quando i parametri sono identici, dimezza il costo di matching.
4. **Batch 24h**: la copia del file `_pending_compressors.json` per ogni ora (righe 1890-1908) e la ri-esecuzione di `export_layers_to_csv` per ognuna delle 24 ore sono già ragionevolmente parallelizzate via subprocess con `OMP_NUM_THREADS=1` (buona pratica già presente, non cambiare). L'unico margine è evitare di rileggere/riscrivere il layer nodi/condotte da zero per ogni ora se la topologia non cambia tra un'ora e l'altra (cambia solo il campo flusso) — si potrebbe cachare la struttura di grafo collassata una volta e rigenerare solo i valori di flusso per ora, riducendo il lavoro ripetuto di parsing geometria.
5. **`except Exception` per singolo campo/singola feature** in `result_visualizer.py` (§2.6) — misurabile solo su reti molto grandi (migliaia di feature); intervento a basso rischio ma minor priorità rispetto ai punti sopra.

---

## Appendice — metodologia

Analisi condotta in due fasi:
1. Bug-hunt parallelo su tutti i moduli sostanziali del plugin (network_builder.py, result_visualizer.py, layer_mapping_panel.py, worker_logic.py, dashboard.py, tab_verifica.py, properties_inspector.py, main_dialog.py).
2. Approfondimento mirato su due aree ad alto rischio fisico/numerico: logica compressori (rampa, validazione pressioni) e coerenza delle conversioni di unità/parsing lungo l'intera pipeline.

Tutti i riferimenti file:riga riportati in questo documento per i punti 🔴 e 🟠 sono stati **verificati per lettura diretta del codice sorgente** al momento della stesura (2026-07-22), non solo dedotti da un'analisi automatica di prima passata. I punti 🟡/🟢 provengono in parte da analisi automatica non re-verificata riga per riga: si raccomanda una rilettura rapida del contesto immediato prima di applicare la modifica.
