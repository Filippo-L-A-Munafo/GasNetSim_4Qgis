# GasNetSim_4Qgis — Analisi codice morto, bug e variabili inutilizzate

**Data:** 27 luglio 2026
**Ambito:** codice del plugin (~8.200 righe Python, escluso il motore `GasNetSim` esterno).
**Metodo:** lettura integrale di ogni modulo + analisi statica AST personalizzata (import/variabili inutilizzate, `except: pass`, default mutabili, marker). Tutti i file compilano senza errori di sintassi.

> Questo documento **complementa** `REPORT_ANALISI_TECNICA.md` (già presente, del 22/07). Non lo ripete: dove i temi coincidono lo cito e mi limito a **confermarne la validità sul codice attuale**; il grosso qui sono **nuovi ritrovamenti** (stub morti, catalogo import/variabili, ridondanze nei compressori) e un quadro d'insieme sull'architettura stratificata.

---

## 0. Sintesi

Il plugin funziona ma porta i segni evidenti di un'evoluzione: un'architettura precedente a **tre widget separati** (`Dashboard`, `PropertiesInspector`, `LayerMappingPanel`) è stata consolidata in un **unico pannello a schede** (`LayerMappingPanel`). Il consolidamento ha lasciato indietro moduli interi, metodi orfani e riferimenti rotti. La logica idraulica e di collasso è solida; gli interventi qui proposti sono di pulizia e robustezza, non di riscrittura.

**Validazione del report esistente (22/07):** ho ricontrollato sul codice odierno i due bug 🔴 più critici già segnalati e **li confermo entrambi ancora presenti**:
- **CRS mai propagato** — `make_memory_layers` (righe 1972, 2246), `split_network_at_user_nodes` (1862, 2168) e `match_user_nodes` (1884, ecc.) sono tutti chiamati **senza** `crs=`, quindi usano il default hardcoded `EPSG:25833`. I layer risultato sono geograficamente disallineati per qualunque utente non in 25833.
- **`worker_logic.py:526` `if best_tol != tol_ok or True:`** — l'`or True` rende il ramo sempre vero (residuo di debug).

---

## 1. Codice morto — unità intere mai usate (nuovi ritrovamenti)

### 1.1 `ui/properties_inspector.py` — intero file (300 righe)
`PropertiesInspector` non è mai istanziata né importata; l'unico riferimento è il rotto `self.inspector` di `main_dialog.py` (§3.1). La funzionalità (recolor + export CSV risultati) è già reimplementata nel tab «Visualizzazione» di `LayerMappingPanel` (`_apply_viz_recolor`, `_export_viz_csv`). **File eliminabile.** *(Coincide con §7 del report esistente; qui evidenzio che l'intero file è morto, non solo incoerente nei prefissi.)*

### 1.2 `ui/dashboard.py::Dashboard` — classe QWidget (~115 righe, 189–303)
Mai istanziata. Del modulo `dashboard.py` è usata **solo** `SimWorker` (importata in `layer_mapping_panel.py:2139`). Da rimuovere la classe `Dashboard` (con `_snapshot_results`, `_append`, `run_simulation`); conviene rinominare il modulo in `sim_worker.py`. Nota bug latente: `_snapshot_results` cerca layer con prefisso `[Risultati]` mentre i layer reali sono `R-N-`/`R-P-`.

### 1.3 `layer_mapping_panel.py` — metodi orfani (NON nel report esistente)
- **`_build_sim_tab`** (818–820): stub `pass`, mai chiamato. Attorno ha commenti disallineati (809–816) da ripulire.
- **`_browse_folder`** (1302–1304): stub `pass`, mai chiamato.
- **`_run_network_check`** (1306–1352): mai collegato ad alcun pulsante **e** contiene un bug (§2.1).

### 1.4 `result_visualizer.py::_remove_old_result_layers` (982–993)
Definita, **0 riferimenti**. *(Coincide con §2.1 del report esistente.)*

### 1.5 Cartella `gasnetsim/`
Contiene solo un `__init__.py` di 2 righe di commento + `__pycache__`. Il motore vero è importato dal package di sistema `import GasNetSim as gns` (maiuscolo). Cartella **placeholder vestigiale**. *(Il report esistente §9 cita core/results ma non questo dettaglio: la minuscola `gasnetsim/` è ingannevole perché sembra il motore locale e invece è vuota.)*

---

## 2. Bug non coperti dal report esistente

### 2.1 `_run_network_check` — spacchettamento errato del valore di ritorno
Riga 1342: `warnings = check_pipe_issues(archi, skipped_null=skipped_null)`. Ma `check_pipe_issues` ritorna una **tupla** `(warnings, bad_ids)` (network_builder.py:1089). Il codice poi itera la tupla (`for w in warnings`) e la passa a `notify_islands`. È rotto. Il metodo è però dead code (§1.3), quindi latente. Correzione: `warnings, _ = check_pipe_issues(...)`.

### 2.2 `inject_compressors_into_csvs` — ramo `if/else` identico + log fuorviante
Righe 1512–1539: i due rami di `if control_mode == "pressure": ... else: ...` impostano **gli stessi identici valori** (`dup['node_type'] = ''`, `dup['pressure_pa'] = ''`). La differenziazione è morta (residuo del refactoring spiegato nel lungo commento). Peggio: il log a riga 1572–1573 dice ancora *«OUT nodo … (Reference a X bar)»*, in **diretta contraddizione** con il codice (il nodo NON è più un reference). Unificare il ramo e correggere il messaggio.

### 2.3 `main_dialog.py` — `self.inspector` mai creato
Righe 36–39: `self.inspector.refresh_layers()` in `try/except: pass`. `self.inspector` non esiste (solo `self.mapping_panel`): `AttributeError` sistematico e silenziato. Rimuovere il blocco. *(Coincide con §8.1 del report esistente — confermato ancora presente.)*

---

## 3. Import inutilizzati (catalogo — non presente nel report esistente)

| File | Riga | Import morto |
|------|------|--------------|
| `plugin_main.py` | 3 | `QSettings`, `QTranslator`, `QCoreApplication` |
| `ui/dashboard.py` | 2 | `import ast` |
| `ui/dashboard.py` | 6 | `import pandas as pd` |
| `ui/tab_verifica.py` | 517 | `QgsFeatureRequest` (import locale) |
| `ui/layer_mapping_panel.py` | 3 | `QRadioButton`, `QButtonGroup` |
| `gis_integration/result_visualizer.py` | 24–33 | `QgsGeometry`, `QgsUnitTypes`, `QgsPalLayerSettings`, `QgsVectorLayerSimpleLabeling`, `QgsTextFormat` |
| `gis_integration/result_visualizer.py` | 35 | `QFont` |
| `gis_integration/result_visualizer.py` | 579 | `QgsGeometry` (import locale, mai usato) |

## 4. Variabili inutilizzate

- `ui/worker_logic.py:163` — `comp_csv_path` (2° valore di `inject_compressors_into_csvs`, mai letto).
- `gis_integration/result_visualizer.py:1073` — `ok` da `prov.addFeatures(feats)`: l'esito è ignorato, quindi un fallimento d'inserimento produce silenziosamente un layer risultato vuoto.
- Minori (variabili di ciclo): `pid` in `_extract_node_data:774`, ecc. — rinominare `_pid`.
- **Falsi positivi** da segnalare: `worker_logic.py:481/483` (`best_result`, `best_tol` in `_tenta`) risultano «non letti» all'analizzatore ma sono `nonlocal`, letti fuori dalla funzione interna: **non** sono da rimuovere.

## 5. Re-import ridondanti
`ui/dashboard.py` importa `traceback` a livello di modulo (riga 3) e lo **re-importa** localmente in `run` (41) e `_run_native` (54). Numerosi altri re-import locali di `traceback` sparsi nei moduli. Innocui ma superflui.

---

## 6. «Pezzi lasciati inutilmente» / qualità

### 6.1 Duplicazione massiva `run_collapse_pipeline` vs `run_nocollapse_pipeline`
network_builder.py:1785 e 2099 sono identiche al ~95% (~250 righe copia-incolla: step 1a–6, propagazione `load_smc_h`/`gas_comp`, export CSV, controllo reference==0, dump compressori). `run_nocollapse` salta solo collasso/potatura. Da fattorizzare in un'unica funzione con `do_collapse: bool`. Le docstring dichiarano un ritorno a **4** valori mentre entrambe ne ritornano **5** (con `warnings`). *(Il report esistente §1.8 lo cita; qui aggiungo la discrepanza docstring↔ritorno.)*

### 6.2 Controllo UI morto — `chk_use_pcm`
`layer_mapping_panel.py:394–396`: checkbox invisibile (`setVisible(False)`), sempre `True`, tenuta «per compatibilità di firma» (`comp_use_pcm`). Alimenta in `inject_compressors_into_csvs` un ramo `else` (use_pcm=False) non più raggiungibile dall'utente. Controllo + ramo di fatto morti.

### 6.3 `except: pass` pervasivi
~120 blocchi `except … : pass` nel plugin, concentrati in `result_visualizer.py` (~40) e `network_builder.py` (~11). Alcuni legittimi (refresh UI, `proc.kill()`), molti nascondono errori reali. In `_apply_node_proportional_size`/`_enrich_with_orig` i `traceback.print_exc()` scrivono su stdout invece che nel log UI.

### 6.4 Log di debug in produzione
`apply_results_to_layers` emette molte righe `[DEBUG] …` a ogni simulazione: da mettere dietro un flag verbose.

### 6.5 Approccio incoerente alle aggregate QGIS
`_apply_node_proportional_size` (417) pre-calcola il massimo in Python «per evitare problemi con le aggregate QGIS», ma `_set_line_width_expression` (1113) usa proprio `minimum()`/`maximum()` in espressione — ciò che l'altra evita. Uniformare.

---

## 7. Metadati e configurazione

- **`metadata.txt`**: `email=your.email@example.com` (placeholder), `tracker=`/`repository=` vuoti, `version=0.1` (mentre l'ambiente installa un motore 0.2.2), `author=Filadelfo Munafo` (verificare), `qgisMinimumVersion=3.10` in contrasto con `requirements.txt` che punta a QGIS 3.44 / Python 3.12.
- **`requirements.txt:11–12`** rimanda a `core/dependency_checker.py` per l'installazione automatica, ma `core/` contiene **solo** un `__init__.py` vuoto: quel file non esiste. Implementare o correggere il commento. *(Coincide con §9–10 del report esistente.)*

---

## 8. Riepilogo prioritizzato (di questo documento)

**Correttezza (da fare)**
1. Rimuovere il blocco `self.inspector` in `main_dialog.py` (§2.3).
2. Togliere l'`or True` in `worker_logic.py:526`.
3. Unificare il ramo identico e correggere il log «Reference» in `inject_compressors_into_csvs` (§2.2).
4. Correggere/eliminare `_run_network_check` (bug tupla, §2.1).

**Manutenibilità**
5. Eliminare codice morto: `properties_inspector.py`, classe `Dashboard`, `_build_sim_tab`, `_browse_folder`, `_remove_old_result_layers`, cartella `gasnetsim/` (§1).
6. Ripulire import e variabili inutilizzati (§3–5).
7. Fattorizzare le due pipeline e allineare le docstring (§6.1).

**Rifinitura**
8. Ridurre gli `except: pass`, mettere i `[DEBUG]` dietro flag, uniformare le aggregate QGIS (§6.3–6.5), sistemare `metadata.txt`/`requirements.txt` (§7).

> Per i bug 🔴/🟠 di natura **fisico-numerica** (propagazione CRS, loop self-loop nel collasso, stato post-rampa compressori, parsing virgola decimale, matching ID fragile) si rimanda al `REPORT_ANALISI_TECNICA.md` esistente, di cui ho verificato e confermato i due punti più critici sul codice attuale.

---

# 9. Approfondimento — architettura multiprocesso e risoluzione delle simulazioni

Analisi mirata su **come vengono orchestrati i processi paralleli e come i risultati tornano alla UI**. È l'area più delicata del plugin dal punto di vista della concorrenza.

## 9.1 Come funziona (mappa del flusso)

- **«Multiprocesso» NON è `multiprocessing`/`Pool`.** Verificato: nessun uso di `multiprocessing`, `concurrent.futures`, `Pool`, `os.cpu_count()`. Il parallelismo è ottenuto con **`subprocess.Popen` manuale — un processo Python separato per ogni ora** (`dashboard.py:137`).
- **Simulazione singola:** `_run_and_simulate` → `_start_simulation` crea un `QThread` + `SimWorker` → se `use_subprocess=True`, `_run_in_subprocess` **genera a runtime** `run_worker.py` + `params.json` nella cartella dell'ora, lancia `python.exe run_worker.py`, legge lo `stdout` riga per riga (prefisso `LOG::colore::msg`) e al termine legge `success.json`.
- **Batch 24h:** loop `for i in range(24)` (`layer_mapping_panel.py:1839`): esporta 24 cartelle `run_NNN/input` con i CSV (sul **main thread**, sequenziale), e per ognuna avvia un `QThread→SimWorker→subprocess`. Risultato: **24 subprocessi Python in parallelo**, ciascuno con i thread BLAS pinnati a 1.
- **Ritorno dei risultati:** ogni subprocess scrive `results_nodes.csv`/`results_pipes.csv` in `output/`; `run_simulation` ritorna il **path della cartella** e la UI ricolora **rileggendo quei CSV**. Nessun oggetto-rete attraversa il confine di processo.

## 9.2 Criticità di concorrenza

### 🟠 9.2.1 Nessun tetto al numero di processi
Vengono avviati **sempre 24 subprocessi** a prescindere dai core disponibili (nessun `os.cpu_count()`, nessun `Semaphore`/pool a scaglioni). Su macchine con pochi core → contesa e pressione di memoria (ogni processo ricarica rete + tabelle GERG2008); su macchine con molti più di 24 core → sottoutilizzo. Consigliato: limitare la concorrenza a ~`os.cpu_count()` con una coda che avvia i processi a ondate.

### 🟠 9.2.2 Fallback `python_exe` pericoloso — `dashboard.py:116-118`
```python
python_exe = os.path.join(sys.base_exec_prefix, 'python.exe')
if not os.path.exists(python_exe):
    python_exe = sys.executable
```
In QGIS `sys.executable` è tipicamente `qgis-bin.exe`, **non** un interprete Python: se il primo path fallisce (installazioni non-OSGeo4W standard), il fallback **riapre QGIS** invece di eseguire lo script. Meglio cercare esplicitamente `python-qgis.bat`/`python3.exe`, o validare che l'eseguibile sia davvero Python prima di usarlo.

### 🟠 9.2.3 Deadlock della UI se tutte le 24 ore hanno 0 reference
Nel loop, se `c_ref == 0` si fa `continue` senza avviare il thread (righe 1910-1912). Se accade per **tutte** le 24 ore, nessun thread parte e `_on_sim_finished` (che riabilita i pulsanti solo con `is_last=True`) non viene **mai** chiamato: `_set_buttons_enabled(True)` non scatta → **i pulsanti restano disabilitati a tempo indefinito**. Correzione: dopo il loop, se `len(self._active_sim_threads) == 0`, riabilitare i pulsanti e loggare l'errore.

### 🟠 9.2.4 Reset di `_active_sim_threads` orfana i thread ancora vivi — riga 1837
`self._active_sim_threads = []` all'avvio del batch: se l'utente clicca «Avvia» mentre un batch precedente è ancora in corso, i riferimenti ai `QThread` in esecuzione vengono persi → l'oggetto C++ può essere distrutto mentre gira → **crash di QGIS**. Serve una guardia: rifiutare un nuovo batch se `any(t.isRunning() for t in self._active_sim_threads)`.

### 🟠 9.2.5 «Ferma» inefficace nel batch e in modalità nativa
- Batch: i `SimWorker` non sono memorizzati da nessuna parte (solo i thread, in `_active_sim_threads`); `_stop_simulation` itera `_active_sim_workers`, **mai creato** → no-op. (Già in §2/§3 del report esistente; qui confermato nel contesto batch.)
- Nativa (`use_subprocess=False`): `cancel()` (dashboard.py:25-38) uccide solo `self._proc`, che nel path nativo è `None`; `self._cancelled` non è mai controllato dentro `run_simulation`. Quindi in modalità nativa «Ferma» non ferma nulla.

### 🟡 9.2.6 Race sul logger globale in modalità nativa batch
`run_simulation` riconfigura a livello di **processo** `logging.getLogger("GasNetSim")` e `...newton_raphson` (level/propagate/handler — worker_logic.py:27-31, 266-296). Con `use_subprocess=False` + 24 `QThread` nello stesso processo, i thread riconfigurano concorrentemente lo stesso logger globale → stato di logging non deterministico e handler di file in contesa. In modalità subprocess il problema non si pone (ogni processo ha il proprio logging).

### 🟡 9.2.7 Modalità nativa batch = falso parallelismo
Il pinning BLAS a 1 thread è impostato **solo** nel path subprocess (dashboard.py:132-135). Con 24 `QThread` nello stesso processo Python: il GIL serializza il calcolo numerico e in più si ha oversubscription BLAS → prestazioni **peggiori** del run singolo. Consigliato: quando `is_parallel`, forzare (o almeno raccomandare esplicitamente) la modalità subprocess.

## 9.3 Codice morto legato al «come si risolvono le simulazioni»

### 🟡 9.3.1 Estrazione da «rete viva» mai eseguita nel flusso UI
Poiché `run_simulation` ritorna **sempre un path di cartella** (sia native `emit(True, res)` sia subprocess `emit(True, data['out_folder'])`), la UI passa un **path** a `apply_results_to_layers`. Di conseguenza i rami «oggetto rete viva» di `_extract_node_data` (result_visualizer.py ~769-901) e `_extract_pipe_data` (~931-975) **non vengono mai eseguiti**: si usa solo il ramo che rilegge i CSV (742-767, 907-929). Sono ~150 righe che **duplicano** la logica già presente in `worker_logic.py` — es. il calcolo del throughput nodale è **identico** in `worker_logic.py:547-561` e `result_visualizer.py:772-788`. Da consolidare: un'unica funzione di estrazione (nel worker, che scrive i CSV); il visualizer legge solo i CSV.

## 9.4 Cose fatte BENE (da NON toccare)

- **Pinning BLAS a 1 thread/processo** nel path subprocess (dashboard.py:132-135): corretto e importante per il parallelismo numerico a processi.
- **Cartelle per-ora distinte** (`run_NNN`): nessuna collisione su `params.json`/`success.json`/CSV tra i 24 processi.
- **Taglio della propagazione dei log DEBUG del solutore in batch** (worker_logic.py:27-31, 284-296): elimina il collo di bottiglia I/O (24 processi che inondano lo stdout letto dal thread unico della UI) descritto nei commenti — diagnosi corretta e ben risolta.
- **Warm-start autocontenuto per ora** (ogni ora calcola la propria baseline): nessuno stato condiviso né corse tra processi.

## 9.5 Riepilogo priorità §9

1. Guardia anti-riavvio batch + riabilitazione pulsanti se 0 thread (9.2.3, 9.2.4) — evitano deadlock UI e crash.
2. Validazione `python_exe` (9.2.2) — evita di riaprire QGIS al posto della simulazione.
3. Rendere «Ferma» effettivo (9.2.5) e scoraggiare/forzare subprocess nel batch (9.2.6, 9.2.7).
4. Cap sui processi concorrenti (9.2.1) e consolidamento estrazione risultati (9.3.1).
