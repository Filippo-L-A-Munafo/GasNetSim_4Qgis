# -*- coding: utf-8 -*-
import os
import time
from .tab_verifica import VerificaTab
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QFileDialog, QDoubleSpinBox, QSpinBox, QCheckBox,
    QTabWidget, QComboBox, QTextEdit, QScrollArea, QMessageBox,
    QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor

from .i18n import tr, register

register({
    # ── Tab ──────────────────────────────────────────────────────────────────
    "mapping.tab0_title": {"it": "0. Verifica Condotte", "en": "0. Check Pipelines"},
    "mapping.tab1_title": {"it": "1. Prepara e Simula", "en": "1. Prepare & Simulate"},
    "mapping.tab2_title": {"it": "2. Visualizzazione Risultati", "en": "2. View Results"},

    # ── Blocco 1 — Dati di input ────────────────────────────────────────────
    "mapping.grp_input": {"it": "Dati di Input", "en": "Input Data"},
    "mapping.row_pipes_layer": {"it": "Layer condotte:", "en": "Pipeline layer:"},
    "mapping.row_nodes_layer": {"it": "Layer nodi:", "en": "Node layer:"},
    "mapping.none_item": {"it": "-- nessuno --", "en": "-- none --"},
    "mapping.none_placeholder_item": {"it": "-- nessuno (usa placeholder) --", "en": "-- none (use placeholder) --"},
    "mapping.lbl_dem": {"it": "DEM (raster):", "en": "DEM (raster):"},
    "mapping.placeholder_out_folder": {"it": "Cartella dove salvare i CSV", "en": "Folder to save the CSVs"},
    "mapping.row_out_folder": {"it": "Cartella output:", "en": "Output folder:"},
    "mapping.row_ora": {"it": "Ora del giorno:", "en": "Hour of day:"},
    "mapping.chk_sim24": {"it": "Simula 24 ore in parallelo (0-23)", "en": "Simulate 24 hours in parallel (0-23)"},
    "mapping.chk_sim24_tooltip": {
        "it": "Avvia la simulazione contemporanea per tutte le 24 ore.",
        "en": "Starts the simulation simultaneously for all 24 hours.",
    },

    # ── Blocco 2 — Modalità collasso ────────────────────────────────────────
    "mapping.chk_already_collapsed": {
        "it": "Rete già collassata  (salta il collasso, usa layer esistenti)",
        "en": "Network already collapsed  (skip collapse, use existing layers)",
    },
    "mapping.grp_collapse_mode": {"it": "Opzioni Collasso", "en": "Collapse Options"},
    "mapping.diam_field_tooltip": {
        "it": "Campo del diametro nel layer condotte.\n"
              "Auto-selezionato cercando (nell'ordine):\n"
              "  {cands}\n"
              "Se nessuno corrisponde, seleziona manualmente.",
        "en": "Diameter field in the pipeline layer.\n"
              "Auto-selected by searching (in order):\n"
              "  {cands}\n"
              "If none match, select manually.",
    },
    "mapping.unit_in": {"it": "pollici (in)", "en": "inches (in)"},
    "mapping.unit_m": {"it": "metri (m)", "en": "metres (m)"},
    "mapping.unit_cm": {"it": "centimetri (cm)", "en": "centimetres (cm)"},
    "mapping.lbl_unit": {"it": "Unità:", "en": "Unit:"},
    "mapping.row_diameter": {"it": "Diametro:", "en": "Diameter:"},
    "mapping.row_ref_field": {"it": "Campo reference:", "en": "Reference field:"},
    "mapping.ref_val_placeholder": {"it": "tutti", "en": "all"},
    "mapping.grp_collapsed_layers": {"it": "Layer Già Collassati", "en": "Already Collapsed Layers"},
    "mapping.grp_field_pipes": {"it": "Mappatura Campi Condotte", "en": "Pipeline Field Mapping"},
    "mapping.row_pipe_id": {"it": "ID pipe:", "en": "Pipe ID:"},
    "mapping.row_node_ab": {"it": "Nodo A / B:", "en": "Node A / B:"},
    "mapping.row_length": {"it": "Lunghezza:", "en": "Length:"},
    "mapping.grp_field_nodes": {"it": "Mappatura Campi Nodi", "en": "Node Field Mapping"},
    "mapping.row_node_id": {"it": "ID nodo:", "en": "Node ID:"},
    "mapping.row_altitude": {"it": "Altitudine:", "en": "Altitude:"},
    "mapping.ref_value_tooltip": {
        "it": "Valore del campo che identifica i nodi reference.\n"
              "Esempi:\n"
              "  '1'          se campo 'matched'\n"
              "  'reference'  se campo 'Type'\n"
              "  '1'          se campo 'is_ref'",
        "en": "Value of the field that identifies reference nodes.\n"
              "Examples:\n"
              "  '1'          if field 'matched'\n"
              "  'reference'  if field 'Type'\n"
              "  '1'          if field 'is_ref'",
    },
    "mapping.row_ref_flag": {"it": "Flag reference:", "en": "Reference flag:"},
    "mapping.cb_f_flow_tooltip": {
        "it": "Campo con i consumi orari di gas per ogni nodo junction.\n"
              "Formato atteso: 24 valori numerici separati dal carattere\n"
              "scelto in 'Separatore flussi' (es: 1.23;0.98;0.87;...)\n"
              "Unita': Smc/h (metri cubi standard per ora).\n"
              "Viene usato il valore all'ora impostata in 'Ora del giorno'.\n"
              "Se non selezionato: usa il valore 'Flusso placeholder'.",
        "en": "Field with hourly gas consumption for each junction node.\n"
              "Expected format: 24 numeric values separated by the character\n"
              "chosen in 'Flow separator' (e.g. 1.23;0.98;0.87;...)\n"
              "Unit: Sm3/h (standard cubic metres per hour).\n"
              "The value at the hour set in 'Hour of day' is used.\n"
              "If not selected: uses the 'Placeholder flow' value.",
    },
    "mapping.row_flow_hourly": {"it": "Flusso orario nodi:", "en": "Hourly node flow:"},
    "mapping.flow_hint_b": {
        "it": "<i style='color:gray'>24 val. Smc/h separati (es: 1.2;0.9;0.8;...)</i>",
        "en": "<i style='color:gray'>24 Sm3/h values, separated (e.g. 1.2;0.9;0.8;...)</i>",
    },

    # ── Blocco 3 — Compressori ───────────────────────────────────────────────
    "mapping.chk_enable_compressor": {"it": "⚙  Compressori", "en": "⚙  Compressors"},
    "mapping.chk_enable_compressor_tooltip": {
        "it": "Attiva la gestione dei nodi compressore.",
        "en": "Enables management of compressor nodes.",
    },
    "mapping.grp_compressor": {"it": "Opzioni Compressore", "en": "Compressor Options"},
    "mapping.cb_f_nodes_comp_field_tooltip": {
        "it": "Campo che identifica i nodi compressore.",
        "en": "Field that identifies compressor nodes.",
    },
    "mapping.row_field_value": {"it": "Campo e Valore:", "en": "Field and Value:"},
    "mapping.txt_nodes_comp_val_placeholder": {"it": "es. compressore", "en": "e.g. compressor"},
    "mapping.txt_nodes_comp_val_tooltip": {
        "it": "Valore del campo che identifica i nodi compressore.",
        "en": "Value of the field that identifies compressor nodes.",
    },
    "mapping.lbl_pressure_out": {"it": "Pressione OUT [bar]:", "en": "Pressure OUT [bar]:"},
    "mapping.comp_pout_tooltip": {
        "it": "Campo con pressione di uscita [bar] oppure VALORE FISSO (es. 70.0).\n"
              "Se valorizzato, sovrascrive 'ratio' calcolando ratio = p_out / p_in.",
        "en": "Field with outlet pressure [bar] or a FIXED VALUE (e.g. 70.0).\n"
              "If set, it overrides 'ratio' by computing ratio = p_out / p_in.",
    },
    "mapping.chk_use_pcm": {"it": "Usa PCM (Pressure Control Mode)", "en": "Use PCM (Pressure Control Mode)"},
    "mapping.row_parameters": {"it": "Parametri:", "en": "Parameters:"},

    # ── Blocco 4 — Opzioni avanzate ──────────────────────────────────────────
    "mapping.chk_advanced": {"it": "⚙  Opzioni avanzate", "en": "⚙  Advanced options"},
    "mapping.grp_advanced": {"it": "Opzioni Avanzate", "en": "Advanced Options"},
    "mapping.chk_no_collapse": {
        "it": "Preserva nodi intermedi (quota reale da DEM)",
        "en": "Preserve intermediate nodes (real elevation from DEM)",
    },
    "mapping.chk_no_collapse_tooltip": {
        "it": "Se attivato, NON esegue il collasso topologico.\n"
              "Tutti i nodi intermedi vengono mantenuti, usando la quota\n"
              "reale dal raster DEM per ogni nodo della rete.\n"
              "Genera reti più grandi ma con differenze di quota accurate.",
        "en": "If enabled, topological collapse is NOT performed.\n"
              "All intermediate nodes are kept, using the real elevation\n"
              "from the DEM raster for every node in the network.\n"
              "Produces larger networks but with accurate elevation differences.",
    },
    "mapping.cb_f_nodes_flow_tooltip": {
        "it": "Campo con i consumi orari di gas per ogni nodo junction (Mod. A).\n"
              "Formato: 24 valori Smc/h separati da ';'.",
        "en": "Field with hourly gas consumption for each junction node (Mode A).\n"
              "Format: 24 Sm3/h values separated by ';'.",
    },
    "mapping.adv_flow_hint": {
        "it": "<i style='color:gray'>24 val. Smc/h sep. da ';'</i>",
        "en": "<i style='color:gray'>24 Sm3/h values sep. by ';'</i>",
    },
    "mapping.row_radius": {"it": "Raggio aggancio:", "en": "Snap radius:"},
    "mapping.sep_semicolon": {"it": ";  (punto e virgola)", "en": ";  (semicolon)"},
    "mapping.sep_comma": {"it": ",  (virgola)", "en": ",  (comma)"},
    "mapping.sep_pipe": {"it": "|  (pipe)", "en": "|  (pipe)"},
    "mapping.sep_colon": {"it": ":  (due punti)", "en": ":  (colon)"},
    "mapping.sep_space": {"it": "spazio", "en": "space"},
    "mapping.sep_tab": {"it": "\\t  (tabulazione)", "en": "\\t  (tab)"},
    "mapping.row_separator": {"it": "Separatore flussi:", "en": "Flow separator:"},
    "mapping.row_pressure_ref": {"it": "Pressione reference:", "en": "Reference pressure:"},
    "mapping.row_temperature": {"it": "Temperatura:", "en": "Temperature:"},
    "mapping.row_placeholder_flow": {"it": "Flusso placeholder:", "en": "Placeholder flow:"},
    "mapping.row_roughness": {"it": "Rugosità condotte:", "en": "Pipe roughness:"},
    "mapping.row_min_export_flow": {"it": "Flusso minimo export:", "en": "Minimum export flow:"},
    "mapping.row_result_decimals": {"it": "Decimali layer risultato:", "en": "Result layer decimals:"},
    "mapping.chk_show_collapsed": {
        "it": "Mostra layer collassato nella legenda",
        "en": "Show collapsed layer in the legend",
    },
    "mapping.chk_show_orig_pipes": {
        "it": "Crea layer condotte originali colorato",
        "en": "Create coloured original pipelines layer",
    },

    # ── Blocco 5 — Parametri solutore ────────────────────────────────────────
    "mapping.chk_solver": {"it": "⚙  Parametri solutore", "en": "⚙  Solver parameters"},
    "mapping.grp_solver": {"it": "Parametri Solutore", "en": "Solver Parameters"},
    "mapping.row_maxiter": {"it": "Max iterazioni:", "en": "Max iterations:"},
    "mapping.spin_tol_tooltip": {
        "it": "Es. 1.0 Sm³/s equivale a ben 3600 Sm³/h di errore nel bilancio del nodo.",
        "en": "E.g. 1.0 Sm³/s equals as much as 3600 Sm³/h of error in the node balance.",
    },
    "mapping.txt_tol_smc_h_tooltip": {
        "it": "Tolleranza equivalente in Sm³/h (= valore in Sm³/s × 3600). Solo lettura.",
        "en": "Tolerance equivalent in Sm³/h (= value in Sm³/s × 3600). Read-only.",
    },
    "mapping.row_tol": {"it": "Tolleranza [Sm³/s]:", "en": "Tolerance [Sm³/s]:"},
    "mapping.row_urf": {"it": "URF:", "en": "URF:"},
    "mapping.chk_autocal": {"it": "Auto-calibra tol e URF", "en": "Auto-calibrate tol and URF"},
    "mapping.chk_autocal_tooltip": {
        "it": "Imposta automaticamente tol e URF in base alla dimensione della rete:\n"
              "  < 100 nodi  → tol=0.1,  urf=1.5\n"
              "  < 500 nodi  → tol=1.0,  urf=2.0\n"
              "  < 2000 nodi → tol=5.0,  urf=2.5\n"
              "  ≥ 2000 nodi → tol=10.0, urf=3.0",
        "en": "Automatically sets tol and URF based on network size:\n"
              "  < 100 nodes  → tol=0.1,  urf=1.5\n"
              "  < 500 nodes  → tol=1.0,  urf=2.0\n"
              "  < 2000 nodes → tol=5.0,  urf=2.5\n"
              "  ≥ 2000 nodes → tol=10.0, urf=3.0",
    },
    "mapping.chk_refine": {"it": "Affina precisione", "en": "Refine precision"},
    "mapping.chk_refine_tooltip": {
        "it": "Dopo la prima convergenza, ritenta con tol÷10 fino a 1e-4.\n"
              "Funziona sia con 'Auto-calibra' attivo sia con tol impostata a mano:\n"
              "il valore da riportare e' sempre la tolleranza FINALE.",
        "en": "After the first convergence, retries with tol÷10 down to 1e-4.\n"
              "Works both with 'Auto-calibrate' enabled and with tol set manually:\n"
              "the value to report is always the FINAL tolerance.",
    },
    "mapping.chk_multiprocess": {"it": "Forza Multiprocesso (Subprocess)", "en": "Force Multiprocess (Subprocess)"},
    "mapping.chk_multiprocess_tooltip": {
        "it": "Crea processi Python indipendenti per bypassare il GIL di Python\n"
              "e usare il 100% della CPU nelle simulazioni parallele (consigliato).",
        "en": "Creates independent Python processes to bypass Python's GIL\n"
              "and use 100% of the CPU in parallel simulations (recommended).",
    },

    # ── Blocco 6 — Composizione gas ──────────────────────────────────────────
    "mapping.grp_gas": {"it": "Composizione Gas", "en": "Gas Composition"},
    "mapping.gas_mazara": {"it": "SNAM — Mazara del Vallo (gas algerino)", "en": "SNAM — Mazara del Vallo (Algerian gas)"},
    "mapping.gas_gela": {"it": "SNAM — Gela (gas libico)", "en": "SNAM — Gela (Libyan gas)"},
    "mapping.gas_pure_methane": {"it": "Metano puro (100% CH4)", "en": "Pure methane (100% CH4)"},
    "mapping.gas_typical_natural": {"it": "Gas naturale tipico (94% CH4)", "en": "Typical natural gas (94% CH4)"},
    "mapping.gas_pure_hydrogen": {"it": "Idrogeno puro (H2)", "en": "Pure hydrogen (H2)"},
    "mapping.gas_custom": {"it": "Personalizzato...", "en": "Custom..."},
    "mapping.row_gas_base": {"it": "Gas base:", "en": "Base gas:"},
    "mapping.spin_h2_pct_tooltip": {
        "it": "Percentuale molare di H₂ da aggiungere al gas base.\n"
              "La composizione base viene riscalata proporzionalmente.\n"
              "Esempio: 20% H₂ + SNAM Mazara → 80% della composizione Mazara + 20% H₂.",
        "en": "Molar percentage of H₂ to add to the base gas.\n"
              "The base composition is rescaled proportionally.\n"
              "Example: 20% H₂ + SNAM Mazara → 80% of the Mazara composition + 20% H₂.",
    },
    "mapping.row_h2_addition": {"it": "Aggiunta H₂:", "en": "H₂ addition:"},
    "mapping.btn_reset_h2_tooltip": {"it": "Azzera percentuale H₂", "en": "Reset H₂ percentage"},
    "mapping.txt_gas_comp_placeholder": {
        "it": "nome preset  oppure  {'methane': 0.9, ...}",
        "en": "preset name  or  {'methane': 0.9, ...}",
    },
    "mapping.txt_gas_comp_tooltip": {
        "it": "Composizione che viene scritta nel CSV di input.\n"
              "Viene aggiornata automaticamente quando si cambia il preset o la % H₂.\n"
              "Modificabile manualmente per composizioni personalizzate.",
        "en": "Composition written into the input CSV.\n"
              "Updated automatically when the preset or the H₂ % changes.\n"
              "Can be edited manually for custom compositions.",
    },
    "mapping.row_gas_export": {"it": "Composizione export:", "en": "Export composition:"},

    # ── Pulsanti / Log Tab 1 ─────────────────────────────────────────────────
    "mapping.btn_reload": {"it": "↺  Ricarica layer", "en": "↺  Reload layers"},
    "mapping.btn_collapse": {"it": "> Genera CSV", "en": "> Generate CSV"},
    "mapping.btn_collapse_from_layer": {"it": "> Genera CSV da Layer", "en": "> Generate CSV from Layer"},
    "mapping.btn_collapse_tooltip": {
        "it": "Esporta i CSV nella cartella di output selezionata.\n"
              "Non avvia la simulazione.",
        "en": "Exports the CSVs to the selected output folder.\n"
              "Does not start the simulation.",
    },
    "mapping.chk_only_export": {"it": "Solo export CSV (non caricare in mappa)", "en": "CSV export only (do not load into the map)"},
    "mapping.chk_only_export_tooltip": {
        "it": "Velocizza simulazioni multiple saltando rendering e layer su QGIS.",
        "en": "Speeds up multiple simulations by skipping QGIS rendering and layers.",
    },
    "mapping.btn_start_sim": {"it": "▶  Avvia Simulazione", "en": "▶  Start Simulation"},
    "mapping.btn_start_sim_tooltip": {
        "it": "Genera i CSV ed esegue la simulazione GasNetSim.\n"
              "Il log compare qui a destra.",
        "en": "Generates the CSVs and runs the GasNetSim simulation.\n"
              "The log appears here on the right.",
    },
    "mapping.btn_stop_sim": {"it": "⏹  Ferma", "en": "⏹  Stop"},
    "mapping.btn_stop_sim_tooltip": {
        "it": "Interrompe la simulazione in corso senza chiudere QGIS.",
        "en": "Stops the running simulation without closing QGIS.",
    },
    "mapping.btn_campaign": {"it": "\U0001F4C5  Campagna (cartella di giorni)", "en": "\U0001F4C5  Campaign (folder of days)"},
    "mapping.btn_campaign_tooltip": {
        "it": "Seleziona una cartella con i file-giorno (.geojson dei nodi).\n"
              "Per ciascuno esegue il batch 24 ore in sequenza (solo file, niente mappa)\n"
              "e stampa un riepilogo finale della campagna.",
        "en": "Select a folder with the day files (node .geojson).\n"
              "For each one, runs the 24-hour batch in sequence (files only, no map)\n"
              "and prints a final campaign summary.",
    },
    "mapping.lbl_log": {"it": "Log:", "en": "Log:"},
    "mapping.act_clear_log": {"it": "\U0001f5d1  Svuota log", "en": "\U0001f5d1  Clear log"},

    # ── Tab 2 — Visualizzazione ──────────────────────────────────────────────
    "mapping.grp_recolor": {"it": "Visualizza risultati su layer", "en": "View results on layer"},
    "mapping.lbl_rc_hint": {
        "it": "<i style='color:gray;font-size:10px;'>"
              "Dopo ogni simulazione i campi vengono compilati automaticamente.<br>"
              "Puoi selezionare manualmente qualsiasi layer vettoriale del progetto<br>"
              "(risultati di simulazioni precedenti inclusi).</i>",
        "en": "<i style='color:gray;font-size:10px;'>"
              "After each simulation the fields are filled in automatically.<br>"
              "You can manually select any vector layer in the project<br>"
              "(including results from previous simulations).</i>",
    },
    "mapping.cb_viz_nodes_lyr_tooltip": {
        "it": "Layer nodi su cui applicare la colorimetria.\n"
              "I layer R-N-* (risultati) appaiono in cima alla lista.",
        "en": "Node layer to apply the colouring to.\n"
              "R-N-* (result) layers appear at the top of the list.",
    },
    "mapping.row_color_nodes": {"it": "Colora nodi per:", "en": "Colour nodes by:"},
    "mapping.cb_viz_nodes_size_tooltip": {
        "it": "Dimensiona i cerchi nodi proporzionalmente al campo scelto.\n"
              "Seleziona '-- nessuno --' per usare dimensione fissa.",
        "en": "Sizes the node circles proportionally to the chosen field.\n"
              "Select '-- none --' to use a fixed size.",
    },
    "mapping.row_size_nodes": {"it": "Dimensiona nodi per:", "en": "Size nodes by:"},
    "mapping.cb_viz_pipes_lyr_tooltip": {
        "it": "Layer condotte su cui applicare la colorimetria.\n"
              "I layer R-P-* (risultati) appaiono in cima alla lista.",
        "en": "Pipeline layer to apply the colouring to.\n"
              "R-P-* (result) layers appear at the top of the list.",
    },
    "mapping.row_color_pipes": {"it": "Colora condotte per:", "en": "Colour pipelines by:"},
    "mapping.chk_viz_arrows": {"it": "Frecce direzione flusso", "en": "Flow direction arrows"},
    "mapping.btn_viz_refresh_tooltip": {
        "it": "Aggiorna lista layer disponibili",
        "en": "Refresh the list of available layers",
    },
    "mapping.btn_viz_apply": {"it": "▶  Applica colorimetria", "en": "▶  Apply colouring"},
    "mapping.grp_sim_opts": {"it": "Impostazioni per la prossima simulazione", "en": "Settings for the next simulation"},
    "mapping.lbl_sim_opts_hint": {
        "it": "Configura i campi e la colorimetria che verranno usati\n"
              "quando si avvia una nuova simulazione.",
        "en": "Configure the fields and colouring that will be used\n"
              "when a new simulation is started.",
    },
    "mapping.grp_nodes": {"it": "Nodi", "en": "Nodes"},
    "mapping.grp_pipes": {"it": "Condotte", "en": "Pipelines"},
    "mapping.row_color_by": {"it": "Colora per:", "en": "Colour by:"},
    "mapping.row_size_by": {"it": "Dimensiona per:", "en": "Size by:"},
    "mapping.cb_res_nodes_size_tooltip": {
        "it": "Se selezionato, dimensiona i cerchi dei nodi\n"
              "proporzionalmente al valore assoluto del campo scelto.\n"
              "Utile per visualizzare i consumi come bolle.",
        "en": "If selected, sizes the node circles\n"
              "proportionally to the absolute value of the chosen field.\n"
              "Useful for visualising consumption as bubbles.",
    },

    # Etichette campi risultato (combo "Colora/Dimensiona per")
    "mapping.f_pressure_bar": {"it": "Pressione (bar)", "en": "Pressure (bar)"},
    "mapping.f_vol_flow": {"it": "Consumo (sm3/s)", "en": "Consumption (sm3/s)"},
    "mapping.f_energy_flow": {"it": "Consumo energetico (MW)", "en": "Energy consumption (MW)"},
    "mapping.f_temp_k": {"it": "Temperatura (K)", "en": "Temperature (K)"},
    "mapping.f_sp_gravity": {"it": "Spec. gravity", "en": "Spec. gravity"},
    "mapping.f_z_factor": {"it": "Z-factor", "en": "Z-factor"},
    "mapping.f_hhv": {"it": "HHV (MJ/sm3)", "en": "HHV (MJ/sm3)"},
    "mapping.f_wobbe": {"it": "Wobbe (MJ/sm3)", "en": "Wobbe (MJ/sm3)"},
    "mapping.f_density": {"it": "Densità (kg/m3)", "en": "Density (kg/m3)"},
    "mapping.f_std_density": {"it": "Dens. std (kg/sm3)", "en": "Std density (kg/sm3)"},
    "mapping.f_molar_mass": {"it": "Massa molare (g/mol)", "en": "Molar mass (g/mol)"},
    "mapping.f_h2_pct": {"it": "H₂ (%)", "en": "H₂ (%)"},
    "mapping.f_throughput": {"it": "Throughput (Smc/h)", "en": "Throughput (Sm3/h)"},

    # Etichette abbreviate checkbox campi nodo
    "mapping.fs_pressure": {"it": "Pressione", "en": "Pressure"},
    "mapping.fs_vol_flow": {"it": "Consumo sm3/s", "en": "Consumption sm3/s"},
    "mapping.fs_energy_flow": {"it": "Consumo MW", "en": "Consumption MW"},
    "mapping.fs_temp": {"it": "Temp.", "en": "Temp."},
    "mapping.fs_sp_gravity": {"it": "Sp.gravity", "en": "Sp.gravity"},
    "mapping.fs_hhv": {"it": "HHV", "en": "HHV"},
    "mapping.fs_wobbe": {"it": "Wobbe", "en": "Wobbe"},
    "mapping.fs_density": {"it": "Densità", "en": "Density"},
    "mapping.fs_std_density": {"it": "Dens.std", "en": "Std density"},
    "mapping.fs_mm": {"it": "MM", "en": "MM"},
    "mapping.fs_gas_comp": {"it": "Comp.gas", "en": "Gas comp."},
    "mapping.fs_throughput": {"it": "Throughput", "en": "Throughput"},
    "mapping.fs_node_type": {"it": "Tipo nodo", "en": "Node type"},

    # Etichette combo/checkbox campi condotte
    "mapping.fp_flow_abs": {"it": "Portata (Smc/h)", "en": "Flow (Sm3/h)"},
    "mapping.fp_velocity": {"it": "Velocità (m/s)", "en": "Velocity (m/s)"},
    "mapping.fp_avg_pressure": {"it": "Press. media (bar)", "en": "Avg pressure (bar)"},
    "mapping.fp_density": {"it": "Densità (kg/m3)", "en": "Density (kg/m3)"},
    "mapping.fps_flow_signed": {"it": "Portata Smc/h", "en": "Flow Sm3/h"},
    "mapping.fps_flow_abs": {"it": "|Portata| Smc/h", "en": "|Flow| Sm3/h"},
    "mapping.fps_velocity": {"it": "Velocità", "en": "Velocity"},
    "mapping.fps_avg_pressure": {"it": "Press.media", "en": "Avg pressure"},
    "mapping.fps_density": {"it": "Densità", "en": "Density"},

    "mapping.chk_flow_arrows": {"it": "Mostra frecce direzione flusso", "en": "Show flow direction arrows"},
    "mapping.chk_flow_arrows_tooltip": {
        "it": "Aggiunge una freccia al centro di ogni condotta, orientata nel verso del flusso del gas.",
        "en": "Adds an arrow at the centre of each pipeline, oriented in the direction of gas flow.",
    },

    "mapping.grp_export": {"it": "Esporta dati", "en": "Export data"},
    "mapping.row_layer": {"it": "Layer:", "en": "Layer:"},
    "mapping.row_decimals": {"it": "Decimali:", "en": "Decimals:"},
    "mapping.spin_viz_decimals_tooltip": {
        "it": "Cifre decimali per i valori numerici nel CSV",
        "en": "Decimal digits for numeric values in the CSV",
    },
    "mapping.btn_export_csv": {"it": "Esporta CSV", "en": "Export CSV"},

    # ── Dialog avvisi rete ───────────────────────────────────────────────────
    "mapping.warn_dlg_title": {"it": "⚠ Avvisi rete", "en": "⚠ Network warnings"},
    "mapping.warn_dlg_lbl": {"it": "<b>Problemi rilevati durante il collasso:</b>", "en": "<b>Problems detected during collapse:</b>"},
    "mapping.btn_zoom": {"it": "\U0001F50D  Zoom su condotte", "en": "\U0001F50D  Zoom to pipelines"},
    "mapping.btn_zoom_tooltip": {
        "it": "Centra e zooma la mappa sulle condotte problematiche.",
        "en": "Centres and zooms the map on the problem pipelines.",
    },
    "mapping.btn_flash": {"it": "\U0001F526  Flash", "en": "\U0001F526  Flash"},
    "mapping.btn_flash_tooltip": {
        "it": "Fa lampeggiare sulla mappa le condotte con problemi.\n"
              "Puoi cliccare più volte.",
        "en": "Flashes the problem pipelines on the map.\n"
              "You can click multiple times.",
    },
    "mapping.warn_no_geom": {
        "it": "<i style='color:gray'>Coordinate non disponibili per il flash<br>"
              "(condotte generate dal collasso, non dal layer originale).</i>",
        "en": "<i style='color:gray'>Coordinates not available for flashing<br>"
              "(pipelines generated by the collapse, not from the original layer).</i>",
    },

    # ── Dialoghi validazione / errori simulazione ───────────────────────────
    "mapping.no_ref_title": {"it": "Nessun nodo reference", "en": "No reference node"},
    "mapping.no_ref_msg": {
        "it": "Nessun nodo reference trovato nel layer nodi.\n\n"
              "La simulazione richiede almeno un nodo a pressione fissa.\n"
              "Verifica il campo 'Flag reference' e il suo valore.",
        "en": "No reference node found in the node layer.\n\n"
              "The simulation requires at least one fixed-pressure node.\n"
              "Check the 'Reference flag' field and its value.",
    },
    "mapping.err_no_pipes_a": {"it": "Nessun layer condotte selezionato (Modalità A).", "en": "No pipeline layer selected (Mode A)."},
    "mapping.warn_no_nodes_layer": {
        "it": "Nessun layer nodi selezionato: non ci saranno nodi reference.\n"
              "La simulazione fallirà senza almeno un nodo a pressione fissa.",
        "en": "No node layer selected: there will be no reference nodes.\n"
              "The simulation will fail without at least one fixed-pressure node.",
    },
    "mapping.warn_no_ref_field_a": {
        "it": "Campo 'Flag reference' non selezionato nel layer nodi.\n"
              "GasNetSim tratterà tutti i nodi agganciati come reference.",
        "en": "'Reference flag' field not selected in the node layer.\n"
              "GasNetSim will treat all snapped nodes as reference.",
    },
    "mapping.warn_empty_ref_val_a": {
        "it": "Valore 'Flag reference' vuoto: tutti i nodi agganciati\n"
              "saranno trattati come reference (potrebbe non essere corretto).",
        "en": "'Reference flag' value empty: all snapped nodes\n"
              "will be treated as reference (this might not be correct).",
    },
    "mapping.err_no_pipes_b": {"it": "Nessun layer condotte collassate selezionato (Modalità B).", "en": "No collapsed pipeline layer selected (Mode B)."},
    "mapping.err_no_nodes_b": {"it": "Nessun layer nodi collassati selezionato (Modalità B).", "en": "No collapsed node layer selected (Mode B)."},
    "mapping.warn_no_ref_field_b": {
        "it": "Campo 'Flag reference' non selezionato nel layer nodi.\n"
              "GasNetSim tratterà tutti i nodi come reference.",
        "en": "'Reference flag' field not selected in the node layer.\n"
              "GasNetSim will treat all nodes as reference.",
    },
    "mapping.warn_empty_ref_val_b": {
        "it": "Valore 'Flag reference' vuoto: tutti i nodi saranno\n"
              "trattati come reference (potrebbe non essere corretto).",
        "en": "'Reference flag' value empty: all nodes will be\n"
              "treated as reference (this might not be correct).",
    },
    "mapping.warn_comp_pout": {
        "it": "Hai attivato il compressore ma NON hai specificato un campo o un valore numerico per 'Pressione OUT'.\n"
              "Il simulatore utilizzerà un ratio di default debole (1.1) che causerà molto probabilmente\n"
              "il fallimento della simulazione (stallo a 0.00 bar) in condizioni di forte carico.",
        "en": "You enabled the compressor but did NOT specify a field or numeric value for 'Pressure OUT'.\n"
              "The simulator will use a weak default ratio (1.1) which will most likely cause\n"
              "the simulation to fail (stalling at 0.00 bar) under heavy load conditions.",
    },
    "mapping.err_missing_data_title": {"it": "Dati mancanti", "en": "Missing data"},
    "mapping.err_missing_data_prefix": {
        "it": "Non è possibile avviare la simulazione:\n\n",
        "en": "The simulation cannot be started:\n\n",
    },
    "mapping.warn_check_params_title": {"it": "Verifica parametri", "en": "Check parameters"},
    "mapping.warn_check_params_prefix": {
        "it": "Attenzione — potrebbero mancare dati importanti:\n\n",
        "en": "Warning — some important data might be missing:\n\n",
    },
    "mapping.warn_check_params_suffix": {
        "it": "\n\nVuoi continuare comunque?",
        "en": "\n\nDo you want to continue anyway?",
    },

    # ── Dialoghi Campagna ────────────────────────────────────────────────────
    "mapping.campaign_title": {"it": "Campagna", "en": "Campaign"},
    "mapping.campaign_need_pipes": {
        "it": "Seleziona prima il layer delle CONDOTTE (la rete è la stessa per tutti i giorni).",
        "en": "First select the PIPELINE layer (the network is the same for all days).",
    },
    "mapping.campaign_source_title": {"it": "Sorgente dati Campagna", "en": "Campaign data source"},
    "mapping.campaign_source_question": {
        "it": "Da dove vuoi importare i giorni (nodi) per la simulazione?",
        "en": "Where do you want to import the days (nodes) for the simulation from?",
    },
    "mapping.campaign_btn_files": {"it": "\U0001F4C1 Scegli file dal disco (.geojson, .shp, ecc)", "en": "\U0001F4C1 Choose files from disk (.geojson, .shp, etc)"},
    "mapping.campaign_btn_layers": {"it": "\U0001F5FA Scegli layer già caricati in QGIS", "en": "\U0001F5FA Choose layers already loaded in QGIS"},
    "mapping.campaign_files_dlg_caption": {
        "it": "Seleziona i file-giorno (.geojson dei nodi) — Ctrl+A per tutti",
        "en": "Select the day files (node .geojson) — Ctrl+A to select all",
    },
    "mapping.campaign_files_filter": {
        "it": "GeoJSON (*.geojson *.json);;Tutti i file (*)",
        "en": "GeoJSON (*.geojson *.json);;All files (*)",
    },
    "mapping.campaign_layers_title": {"it": "Seleziona layer per la Campagna", "en": "Select layers for the Campaign"},
    "mapping.campaign_layers_hint": {
        "it": "Spunta i layer dei nodi (giorni) da simulare in sequenza:",
        "en": "Check the node layers (days) to simulate in sequence:",
    },
    "mapping.campaign_out_dir_caption": {"it": "Cartella di OUTPUT della campagna", "en": "Campaign OUTPUT folder"},
    "mapping.campaign_more_files": {"it": "\n  … e altri {n}", "en": "\n  … and {n} more"},
    "mapping.campaign_start_title": {"it": "Avvio campagna", "en": "Start campaign"},
    "mapping.campaign_start_msg": {
        "it": "Eseguo il batch 24 ore per {n_files} giorni "
              "({n_sims} simulazioni totali), uno dopo l'altro.\n\n"
              "{names}\n\nProcedo?",
        "en": "Running the 24-hour batch for {n_files} days "
              "({n_sims} total simulations), one after another.\n\n"
              "{names}\n\nProceed?",
    },
    "mapping.browse_out_dir_caption": {"it": "Seleziona cartella output CSV", "en": "Select CSV output folder"},

    # ── Dialog export CSV (Tab 2) ────────────────────────────────────────────
    "mapping.export_no_layer_title": {"it": "Nessun layer", "en": "No layer"},
    "mapping.export_no_layer_msg": {"it": "Seleziona un layer da esportare.", "en": "Select a layer to export."},
    "mapping.export_layer_not_found_title": {"it": "Layer non trovato", "en": "Layer not found"},
    "mapping.export_layer_not_found_msg": {"it": "Il layer non è più disponibile.", "en": "The layer is no longer available."},
    "mapping.export_csv_dialog_title": {"it": "Esporta CSV", "en": "Export CSV"},
    "mapping.export_done_title": {"it": "Esportazione completata", "en": "Export complete"},
    "mapping.export_done_msg": {
        "it": "Layer esportato con {decimals} decimali:\n{filepath}",
        "en": "Layer exported with {decimals} decimals:\n{filepath}",
    },
    "mapping.export_error_title": {"it": "Errore esportazione", "en": "Export error"},
    # Titoli/riepiloghi principali del log di esecuzione: sono gli unici
    # messaggi dinamici tradotti (sono i "grandi annunci", non la
    # diagnostica fine per-ora/per-iterazione, che resta in italiano).
    "mapping.log_campaign_start": {
        "it": "  CAMPAGNA: {ndays} giorni × 24 ore = {ntot} simulazioni",
        "en": "  CAMPAIGN: {ndays} days × 24 hours = {ntot} simulations",
    },
    "mapping.log_campaign_summary_title": {"it": "  RIEPILOGO CAMPAGNA", "en": "  CAMPAIGN SUMMARY"},
    "mapping.log_campaign_days_done": {"it": "  Giorni completati:            {n}", "en": "  Days completed:               {n}"},
    "mapping.log_campaign_days_full": {"it": "  Giorni con 24/24 converse:    {n}/{tot}", "en": "  Days with 24/24 converged:    {n}/{tot}"},
    "mapping.log_campaign_sims_conv": {"it": "  Simulazioni converse totali:  {n}/{tot}", "en": "  Total converged simulations:  {n}/{tot}"},
    "mapping.log_campaign_not_conv": {"it": "  ← NON converse: {hours}", "en": "  ← NOT converged: {hours}"},
    "mapping.log_campaign_total_time": {"it": "  Tempo totale campagna:        {t}", "en": "  Total campaign time:          {t}"},
    "mapping.log_batch24_start": {"it": "  AVVIO SIMULAZIONE 24 ORE (PARALLELO)", "en": "  STARTING 24-HOUR SIMULATION (PARALLEL)"},
    "mapping.log_single_start": {"it": "  Avvio simulazione GasNetSim...", "en": "  Starting GasNetSim simulation..."},
    "mapping.log_batch24_summary_title": {"it": "  RIEPILOGO BATCH 24 ORE (PARALLELO)", "en": "  24-HOUR BATCH SUMMARY (PARALLEL)"},
    "mapping.log_batch24_converged": {"it": "  Simulazioni converse:     {n}/{tot}", "en": "  Converged simulations:    {n}/{tot}"},
    "mapping.log_batch24_not_converged": {"it": "  NON converse (best iterate): {hours}", "en": "  NOT converged (best iterate): {hours}"},
    "mapping.log_batch24_not_converged_note1": {
        "it": "     → per queste ore il risultato è il miglior iterato,",
        "en": "     → for these hours the result is the best iterate found,",
    },
    "mapping.log_batch24_not_converged_note2": {
        "it": "       NON una soluzione convergente: verificarle.",
        "en": "       NOT a converged solution: please check them.",
    },
    "mapping.log_batch24_skipped": {"it": "  Ore saltate (0 reference): {n}", "en": "  Hours skipped (0 reference): {n}"},
    "mapping.log_batch24_total_time": {"it": "  Tempo totale (parallelo): {t}", "en": "  Total time (parallel): {t}"},
    "mapping.log_batch_concurrency": {
        "it": "Concorrenza batch: max {n} simulazioni in parallelo (stima core fisici, os.cpu_count()={logical}).",
        "en": "Batch concurrency: max {n} parallel simulations (estimated physical cores, os.cpu_count()={logical}).",
    },
})

# ── Candidati per auto-selezione campo ───────────────────────────────────────
_PIPE_ID_CAND  = ('pipe_id', 'id', 'FID', 'fid', 'OBJECTID')
_NODE_A_CAND   = ('node_a', 'from_node', 'inlet', 'a', 'start_node')
_NODE_B_CAND   = ('node_b', 'to_node', 'outlet', 'b', 'end_node')
_LENGTH_CAND   = ('length_m', 'length', 'L', 'len', 'lunghezza', 'lung_m')
_DIAM_CAND     = ('diameter_m', 'diam_m', 'D', 'd', 'diam',
                  'Diametro_pollici', 'Diametro', 'diameter')
_NODE_ID_CAND  = ('node_id', 'id', 'FID', 'fid', 'OBJECTID')
_ALT_CAND      = ('altitude_m', 'z_m', 'elev', 'altitude', 'alt', 'ALTITUDINE', 'quota')
_REF_FLAG_CAND = ('matched', 'type', 'Type', 'NodeID', 'is_ref', 'reference', 'nodo_tipo')
_FLOW_CAND     = ('load_smc_h', 'Totale_Smc', 'flusso_smc', 'flow', 'demand', 'smc')


def _best_field(combo, candidates):
    """Seleziona il primo campo che matcha tra i candidati (case-insensitive)."""
    fields_lower = [combo.itemText(i).lower() for i in range(combo.count())]
    for c in candidates:
        if c.lower() in fields_lower:
            combo.setCurrentIndex(fields_lower.index(c.lower()))
            return


def _next_run_subdir(base):
    """Restituisce (Path, label) per la prima sottocartella run_NNN non esistente."""
    from pathlib import Path
    base = Path(base)
    i = 1
    while True:
        label = f"run_{i:03d}"
        if not (base / label).exists():
            return base / label, label
        i += 1


def _next_layer_run_number():
    """Restituisce il primo indice N tale che 'Condotte #N' e 'Nodi #N' non esistono nel progetto."""
    try:
        from qgis.core import QgsProject
        existing = {lyr.name() for lyr in QgsProject.instance().mapLayers().values()}
    except Exception:
        return 1
    i = 1
    while f"Condotte #{i}" in existing or f"Nodi #{i}" in existing:
        i += 1
    return i


class LayerMappingPanel(QWidget):
    # Emesso quando l'export è pronto: porta il dict params già con cartella compilata
    simulate_ready = pyqtSignal(dict)
    simulation_done = pyqtSignal(bool, object)  # (converged, result)

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self._layer_name_conns = {}   # layer_id ? nameChanged connection
        self._last_nodes_lyr = None   # layer nodi usato nell'ultima simulazione
        self._last_pipes_lyr = None   # layer condotte usato nell'ultima simulazione
        self._last_orig_nodes_lyr = None  # layer nodi originale pre-collasso
        self._last_orig_pipes_lyr = None  # layer condotte originale pre-collasso
        self._last_run_params = {}
        self._last_input_dir = ''
        self._sim_thread = None
        self._sim_worker = None
        self._active_sim_threads = []
        self.setup_ui()
        self._connect_project_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self._tab_repair = VerificaTab(iface=self.iface)
        self._tab_repair.layer_verified.connect(self._on_layer_verified)
        self._tab_repair.analysis_ok.connect(self._on_analysis_ok)
        self.tabs.addTab(self._tab_repair, tr("mapping.tab0_title"))

        self._tab_prepare = QWidget()
        self._build_prepare_tab(self._tab_prepare)
        self.tabs.addTab(self._tab_prepare, tr("mapping.tab1_title"))

        self._tab_viz = QWidget()
        self._build_viz_tab(self._tab_viz)
        self.tabs.addTab(self._tab_viz, tr("mapping.tab2_title"))

        # Routing interno: simulate_ready avvia la sim senza passare da main_dialog
        self.simulate_ready.connect(self._start_simulation)

        layout.addWidget(self.tabs)

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 1 — Prepara Rete
    # ─────────────────────────────────────────────────────────────────────────

    # -----------------------------------------------------------------------
    # Tab 0 – Verifica Rete
    # -----------------------------------------------------------------------

    def _build_prepare_tab(self, widget):
        _root = QVBoxLayout(widget)
        _root.setContentsMargins(4, 6, 4, 4)
        _root.setSpacing(0)
        h_main = QSplitter(Qt.Horizontal)
        h_main.setHandleWidth(4)
        _root.addWidget(h_main)

        # Colonna sinistra: form (scorrevole)
        left_content = QWidget()
        outer = QVBoxLayout(left_content)
        outer.setContentsMargins(2, 2, 6, 2)
        outer.setSpacing(5)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setWidget(left_content)
        h_main.addWidget(left_scroll)

        # Colonna destra: bottoni + log
        right_panel = QWidget()
        right_panel.setMinimumWidth(200)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(2, 2, 2, 2)
        right_layout.setSpacing(4)
        h_main.addWidget(right_panel)
        h_main.setStretchFactor(0, 3)
        h_main.setStretchFactor(1, 2)
        h_main.setSizes([580, 300])
        h_main.setCollapsible(0, False)
        h_main.setCollapsible(1, False)

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 1 — Dati di input (sempre visibile)
        # ══════════════════════════════════════════════════════════════════════
        grp_input = QGroupBox(tr("mapping.grp_input"))
        fl_input = QFormLayout(grp_input)
        fl_input.setLabelAlignment(Qt.AlignRight)

        self.cb_pipes = QComboBox()
        self.cb_pipes.currentIndexChanged.connect(self._on_pipes_layer_changed)
        fl_input.addRow(tr("mapping.row_pipes_layer"), self.cb_pipes)

        self.cb_nodes = QComboBox()
        self.cb_nodes.currentIndexChanged.connect(self._on_nodes_layer_changed)
        fl_input.addRow(tr("mapping.row_nodes_layer"), self.cb_nodes)

        # DEM — sempre visibile; usato solo se "Preserva nodi intermedi" è attivo
        self.cb_dem = QComboBox()
        self.cb_dem.addItem(tr("mapping.none_item"), None)
        self._row_dem_label = QLabel(tr("mapping.lbl_dem"))
        fl_input.addRow(self._row_dem_label, self.cb_dem)

        out_row = QHBoxLayout()
        self.txt_prepare_folder = QLineEdit()
        self.txt_prepare_folder.setPlaceholderText(tr("mapping.placeholder_out_folder"))
        out_row.addWidget(self.txt_prepare_folder)
        btn_browse_out = QPushButton("...")
        btn_browse_out.setFixedWidth(32)
        btn_browse_out.clicked.connect(self._browse_prepare_folder)
        out_row.addWidget(btn_browse_out)
        fl_input.addRow(tr("mapping.row_out_folder"), out_row)

        self.spin_ora = QSpinBox()
        self.spin_ora.setRange(0, 23)
        self.spin_ora.setValue(0)
        self.spin_ora.setSuffix("h")
        self.spin_ora.valueChanged.connect(self._update_ora_preview)
        fl_input.addRow(tr("mapping.row_ora"), self.spin_ora)
        self.lbl_ora_preview = QLabel("")
        self.lbl_ora_preview.setTextFormat(Qt.RichText)
        fl_input.addRow("", self.lbl_ora_preview)

        self.chk_sim_24 = QCheckBox(tr("mapping.chk_sim24"))
        self.chk_sim_24.setToolTip(tr("mapping.chk_sim24_tooltip"))
        fl_input.addRow("", self.chk_sim_24)

        outer.addWidget(grp_input)

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 2 — Modalità collasso
        # ══════════════════════════════════════════════════════════════════════
        self.chk_already_collapsed = QCheckBox(tr("mapping.chk_already_collapsed"))
        self.chk_already_collapsed.setChecked(False)
        self.chk_already_collapsed.toggled.connect(self._on_mode_changed)
        outer.addWidget(self.chk_already_collapsed)

        # — Modalità A: collassa —
        self.grp_collapse_mode = QGroupBox(tr("mapping.grp_collapse_mode"))
        fl_a = QFormLayout(self.grp_collapse_mode)
        fl_a.setLabelAlignment(Qt.AlignRight)

        self.cb_diam_field = QComboBox()
        self.cb_diam_field.setToolTip(
            tr("mapping.diam_field_tooltip", cands=', '.join(_DIAM_CAND)))
        self.cb_diam_unit = QComboBox()
        self.cb_diam_unit.addItem(tr("mapping.unit_in"), "in")
        self.cb_diam_unit.addItem(tr("mapping.unit_m"), "m")
        self.cb_diam_unit.addItem(tr("mapping.unit_cm"), "cm")
        _diam_row = QHBoxLayout()
        _diam_row.addWidget(self.cb_diam_field)
        _diam_row.addSpacing(4)
        _diam_row.addWidget(QLabel(tr("mapping.lbl_unit")))
        _diam_row.addWidget(self.cb_diam_unit)
        fl_a.addRow(tr("mapping.row_diameter"), _diam_row)

        ref_row = QHBoxLayout()
        ref_row.setContentsMargins(0, 0, 0, 0)
        self.cb_f_nodes_ref = QComboBox()
        self.cb_f_nodes_ref.setEnabled(False)
        self.cb_f_nodes_ref.setMinimumWidth(100)
        ref_row.addWidget(self.cb_f_nodes_ref)
        ref_row.addWidget(QLabel(" = "))
        self.txt_nodes_ref_val = QLineEdit()
        self.txt_nodes_ref_val.setEnabled(False)
        self.txt_nodes_ref_val.setPlaceholderText(tr("mapping.ref_val_placeholder"))
        self.txt_nodes_ref_val.setFixedWidth(80)
        ref_row.addWidget(self.txt_nodes_ref_val)
        ref_row.addStretch()
        fl_a.addRow(tr("mapping.row_ref_field"), ref_row)

        outer.addWidget(self.grp_collapse_mode)

        # — Modalità B: già collassata —
        self.grp_collapsed_layers = QGroupBox(tr("mapping.grp_collapsed_layers"))
        fl_b = QFormLayout(self.grp_collapsed_layers)
        fl_b.setLabelAlignment(Qt.AlignRight)

        self.cb_coll_pipes = QComboBox()
        self.cb_coll_pipes.currentIndexChanged.connect(self._on_coll_pipes_changed)
        fl_b.addRow(tr("mapping.row_pipes_layer"), self.cb_coll_pipes)

        self.cb_coll_nodes = QComboBox()
        self.cb_coll_nodes.currentIndexChanged.connect(self._on_coll_nodes_changed)
        fl_b.addRow(tr("mapping.row_nodes_layer"), self.cb_coll_nodes)

        outer.addWidget(self.grp_collapsed_layers)
        self.grp_collapsed_layers.setVisible(False)

        # Mappatura campi (Mod. B — nascosti di default)
        self.grp_field_pipes = QGroupBox(tr("mapping.grp_field_pipes"))
        fl_bp = QFormLayout(self.grp_field_pipes)
        fl_bp.setLabelAlignment(Qt.AlignRight)

        self.cb_f_pipe_id = QComboBox()
        fl_bp.addRow(tr("mapping.row_pipe_id"), self.cb_f_pipe_id)

        row_ab = QHBoxLayout()
        self.cb_f_node_a = QComboBox()
        self.cb_f_node_b = QComboBox()
        row_ab.addWidget(QLabel("A:")); row_ab.addWidget(self.cb_f_node_a)
        row_ab.addSpacing(8)
        row_ab.addWidget(QLabel("B:")); row_ab.addWidget(self.cb_f_node_b)
        fl_bp.addRow(tr("mapping.row_node_ab"), row_ab)

        self.cb_f_length = QComboBox()
        fl_bp.addRow(tr("mapping.row_length"), self.cb_f_length)

        row_diam = QHBoxLayout()
        self.cb_f_diam = QComboBox()
        self.cb_f_diam_unit = QComboBox()
        self.cb_f_diam_unit.addItem(tr("mapping.unit_m"), "m")
        self.cb_f_diam_unit.addItem(tr("mapping.unit_in"), "in")
        self.cb_f_diam_unit.addItem(tr("mapping.unit_cm"), "cm")
        row_diam.addWidget(self.cb_f_diam)
        row_diam.addSpacing(4)
        row_diam.addWidget(QLabel(tr("mapping.lbl_unit")))
        row_diam.addWidget(self.cb_f_diam_unit)
        fl_bp.addRow(tr("mapping.row_diameter"), row_diam)

        outer.addWidget(self.grp_field_pipes)
        self.grp_field_pipes.setVisible(False)

        # ── Mappatura campi nodi ──────────────────────────────────────────────
        self.grp_field_nodes = QGroupBox(tr("mapping.grp_field_nodes"))
        fl_bn = QFormLayout(self.grp_field_nodes)
        fl_bn.setLabelAlignment(Qt.AlignRight)

        self.cb_f_node_id = QComboBox()
        fl_bn.addRow(tr("mapping.row_node_id"), self.cb_f_node_id)

        self.cb_f_altitude = QComboBox()
        fl_bn.addRow(tr("mapping.row_altitude"), self.cb_f_altitude)

        row_ref = QHBoxLayout()
        self.cb_f_ref_flag = QComboBox()
        self.txt_ref_value = QLineEdit("1")
        self.txt_ref_value.setFixedWidth(70)
        self.txt_ref_value.setToolTip(tr("mapping.ref_value_tooltip"))
        row_ref.addWidget(self.cb_f_ref_flag)
        row_ref.addWidget(QLabel(" = "))
        row_ref.addWidget(self.txt_ref_value)
        fl_bn.addRow(tr("mapping.row_ref_flag"), row_ref)

        self.cb_f_flow = QComboBox()
        self.cb_f_flow.addItem(tr("mapping.none_placeholder_item"), "")
        self.cb_f_flow.setToolTip(tr("mapping.cb_f_flow_tooltip"))
        fl_bn.addRow(tr("mapping.row_flow_hourly"), self.cb_f_flow)
        self.cb_f_flow.currentIndexChanged.connect(self._update_ora_preview)
        lbl_flow_hint_b = QLabel(tr("mapping.flow_hint_b"))
        lbl_flow_hint_b.setTextFormat(Qt.RichText)
        fl_bn.addRow("", lbl_flow_hint_b)

        outer.addWidget(self.grp_field_nodes)
        self.grp_field_nodes.setVisible(False)

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 3 — Compressori (flag)
        # ══════════════════════════════════════════════════════════════════════
        self.chk_enable_compressor = QCheckBox(tr("mapping.chk_enable_compressor"))
        self.chk_enable_compressor.setChecked(False)
        self.chk_enable_compressor.setToolTip(tr("mapping.chk_enable_compressor_tooltip"))
        outer.addWidget(self.chk_enable_compressor)

        self._grp_compressor = QGroupBox(tr("mapping.grp_compressor"))
        self._grp_compressor.setVisible(False)
        comp_inner = QFormLayout(self._grp_compressor)
        comp_inner.setLabelAlignment(Qt.AlignRight)

        comp_row_a = QHBoxLayout()
        comp_row_a.setContentsMargins(0, 0, 0, 0)

        self.cb_f_nodes_comp_field = QComboBox()
        self.cb_f_nodes_comp_field.setEnabled(False)
        self.cb_f_nodes_comp_field.setToolTip(tr("mapping.cb_f_nodes_comp_field_tooltip"))
        comp_row_a.addWidget(self.cb_f_nodes_comp_field)

        comp_row_a.addWidget(QLabel(" = "))

        self.txt_nodes_comp_val = QLineEdit()
        self.txt_nodes_comp_val.setEnabled(False)
        self.txt_nodes_comp_val.setPlaceholderText(tr("mapping.txt_nodes_comp_val_placeholder"))
        self.txt_nodes_comp_val.setFixedWidth(120)
        self.txt_nodes_comp_val.setToolTip(tr("mapping.txt_nodes_comp_val_tooltip"))
        comp_row_a.addWidget(self.txt_nodes_comp_val)

        comp_row_a.addStretch()
        comp_inner.addRow(tr("mapping.row_field_value"), comp_row_a)

        comp_attr_row_a = QHBoxLayout()
        comp_attr_row_a.setContentsMargins(0, 0, 0, 0)
        self.cb_f_nodes_comp_pout = QComboBox()
        self.cb_f_nodes_comp_pout.setEnabled(False)
        self.cb_f_nodes_comp_pout.setEditable(True)
        self.cb_f_nodes_comp_pout.setToolTip(tr("mapping.comp_pout_tooltip"))
        comp_attr_row_a.addWidget(QLabel(tr("mapping.lbl_pressure_out"))); comp_attr_row_a.addWidget(self.cb_f_nodes_comp_pout)
        
        # Il controllo di pressione e' ora l'UNICA modalita' esposta.
        #
        # La vecchia casella "Usa PCM" sceglieva fra due formulazioni entrambe
        # difettose: PCM trasformava la mandata in un nodo Reference (sorgente
        # illimitata in mezzo alla rete) e il controllo di rapporto
        # sovrascriveva la pressione di mandata durante il calcolo del residuo.
        # Con la formulazione aumentata la mandata e' imposta da una riga di
        # vincolo, quindi il vincolo di pressione e' sia il piu' fedele a una
        # stazione reale che mantiene una pressione di targa, sia il meglio
        # condizionato: la sua riga ha un solo termine (d/dp_out), mentre il
        # vincolo di rapporto accoppia mandata e aspirazione.
        #
        # Si mantiene l'attributo per compatibilita' con le firme esistenti
        # (comp_use_pcm), ma non e' piu' una scelta dell'utente.
        self.chk_use_pcm = QCheckBox(tr("mapping.chk_use_pcm"))
        self.chk_use_pcm.setChecked(True)
        self.chk_use_pcm.setVisible(False)

        comp_inner.addRow(tr("mapping.row_parameters"), comp_attr_row_a)

        outer.addWidget(self._grp_compressor)
        self.chk_enable_compressor.toggled.connect(
            lambda checked: self._grp_compressor.setVisible(checked))

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 4 — Opzioni avanzate (flag)
        # ══════════════════════════════════════════════════════════════════════
        self._chk_advanced = QCheckBox(tr("mapping.chk_advanced"))
        self._chk_advanced.setChecked(False)
        outer.addWidget(self._chk_advanced)

        self._grp_advanced = QGroupBox(tr("mapping.grp_advanced"))
        self._grp_advanced.setVisible(False)
        adv_form = QFormLayout(self._grp_advanced)
        adv_form.setLabelAlignment(Qt.AlignRight)

        # Preserva nodi intermedi — il DEM è in "Dati di Input"
        self.chk_no_collapse = QCheckBox(tr("mapping.chk_no_collapse"))
        self.chk_no_collapse.setChecked(False)
        self.chk_no_collapse.setToolTip(tr("mapping.chk_no_collapse_tooltip"))
        adv_form.addRow("", self.chk_no_collapse)

        adv_form.addRow(QLabel())  # separatore visivo

        self.cb_f_nodes_flow = QComboBox()
        self.cb_f_nodes_flow.addItem(tr("mapping.none_placeholder_item"), "")
        self.cb_f_nodes_flow.setEnabled(False)
        self.cb_f_nodes_flow.setToolTip(tr("mapping.cb_f_nodes_flow_tooltip"))
        adv_form.addRow(tr("mapping.row_flow_hourly"), self.cb_f_nodes_flow)
        _lbl_adv_hint = QLabel(tr("mapping.adv_flow_hint"))
        _lbl_adv_hint.setTextFormat(Qt.RichText)
        adv_form.addRow("", _lbl_adv_hint)

        self.spin_radius = QDoubleSpinBox()
        self.spin_radius.setRange(0.1, 10000.0)
        self.spin_radius.setDecimals(1)
        self.spin_radius.setValue(50.0)
        self.spin_radius.setSuffix(" m")
        adv_form.addRow(tr("mapping.row_radius"), self.spin_radius)

        self.cb_separator = QComboBox()
        self.cb_separator.addItem(tr("mapping.sep_semicolon"), ";")
        self.cb_separator.addItem(tr("mapping.sep_comma"), ",")
        self.cb_separator.addItem(tr("mapping.sep_pipe"), "|")
        self.cb_separator.addItem(tr("mapping.sep_colon"), ":")
        self.cb_separator.addItem(tr("mapping.sep_space"), " ")
        self.cb_separator.addItem(tr("mapping.sep_tab"), "\t")
        adv_form.addRow(tr("mapping.row_separator"), self.cb_separator)

        self.spin_pressure = QDoubleSpinBox()
        self.spin_pressure.setRange(1.0, 300.0)
        self.spin_pressure.setDecimals(1)
        self.spin_pressure.setValue(75.0)
        self.spin_pressure.setSuffix(" bar")
        adv_form.addRow(tr("mapping.row_pressure_ref"), self.spin_pressure)

        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(250.0, 400.0)
        self.spin_temp.setDecimals(2)
        self.spin_temp.setValue(288.15)
        self.spin_temp.setSuffix(" K")
        adv_form.addRow(tr("mapping.row_temperature"), self.spin_temp)

        _jflow_row = QHBoxLayout()
        self.spin_jflow = QDoubleSpinBox()
        self.spin_jflow.setRange(0.0, 10.0)
        self.spin_jflow.setDecimals(4)
        self.spin_jflow.setValue(0.0001)
        self.spin_jflow.setSuffix(" sm3/s")
        _jflow_row.addWidget(self.spin_jflow)
        _btn_reset_jflow = QPushButton("\u21ba")
        _btn_reset_jflow.setFixedWidth(26)
        _btn_reset_jflow.clicked.connect(lambda: self.spin_jflow.setValue(0.0001))
        _jflow_row.addWidget(_btn_reset_jflow)
        adv_form.addRow(tr("mapping.row_placeholder_flow"), _jflow_row)

        _rough_row = QHBoxLayout()
        self.spin_roughness = QDoubleSpinBox()
        self.spin_roughness.setRange(1e-7, 0.1)
        self.spin_roughness.setDecimals(7)
        self.spin_roughness.setValue(0.000012)
        self.spin_roughness.setSuffix(" m")
        _rough_row.addWidget(self.spin_roughness)
        _btn_reset_rough = QPushButton("\u21ba")
        _btn_reset_rough.setFixedWidth(26)
        _btn_reset_rough.clicked.connect(lambda: self.spin_roughness.setValue(0.000012))
        _rough_row.addWidget(_btn_reset_rough)
        adv_form.addRow(tr("mapping.row_roughness"), _rough_row)

        _phflow_row = QHBoxLayout()
        self.spin_placeholder_flow = QDoubleSpinBox()
        self.spin_placeholder_flow.setRange(1e-10, 1.0)
        self.spin_placeholder_flow.setDecimals(9)
        self.spin_placeholder_flow.setValue(1e-6)
        self.spin_placeholder_flow.setSuffix(" sm3/s")
        _phflow_row.addWidget(self.spin_placeholder_flow)
        _btn_reset_phflow = QPushButton("\u21ba")
        _btn_reset_phflow.setFixedWidth(26)
        _btn_reset_phflow.clicked.connect(lambda: self.spin_placeholder_flow.setValue(1e-6))
        _phflow_row.addWidget(_btn_reset_phflow)
        adv_form.addRow(tr("mapping.row_min_export_flow"), _phflow_row)

        self.spin_result_decimals = QSpinBox()
        self.spin_result_decimals.setRange(0, 10)
        self.spin_result_decimals.setValue(4)
        adv_form.addRow(tr("mapping.row_result_decimals"), self.spin_result_decimals)

        self.chk_show_collapsed = QCheckBox(tr("mapping.chk_show_collapsed"))
        self.chk_show_collapsed.setChecked(True)
        adv_form.addRow("", self.chk_show_collapsed)

        self.chk_show_orig_pipes = QCheckBox(tr("mapping.chk_show_orig_pipes"))
        self.chk_show_orig_pipes.setChecked(False)
        adv_form.addRow("", self.chk_show_orig_pipes)

        outer.addWidget(self._grp_advanced)
        self._chk_advanced.toggled.connect(
            lambda checked: self._grp_advanced.setVisible(checked))

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 5 — Parametri solutore (flag)
        # ══════════════════════════════════════════════════════════════════════
        self._chk_solver = QCheckBox(tr("mapping.chk_solver"))
        self._chk_solver.setChecked(False)
        outer.addWidget(self._chk_solver)

        self._grp_solver = QGroupBox(tr("mapping.grp_solver"))
        self._grp_solver.setVisible(False)
        sform = QFormLayout(self._grp_solver)
        sform.setLabelAlignment(Qt.AlignRight)

        self.spin_maxiter = QSpinBox()
        self.spin_maxiter.setRange(10, 2000)
        self.spin_maxiter.setValue(50)
        sform.addRow(tr("mapping.row_maxiter"), self.spin_maxiter)

        self.spin_tol = QDoubleSpinBox()
        self.spin_tol.setRange(0.0001, 10.0)
        self.spin_tol.setDecimals(4)
        self.spin_tol.setValue(0.001)
        self.spin_tol.setToolTip(tr("mapping.spin_tol_tooltip"))
        # Riquadro accanto: mostra la tolleranza convertita in Sm³/h (× 3600),
        # aggiornato in tempo reale, così non serve convertirla a mano.
        _tol_row = QHBoxLayout()
        _tol_row.setContentsMargins(0, 0, 0, 0)
        _tol_row.setSpacing(6)
        _tol_row.addWidget(self.spin_tol)
        _tol_row.addWidget(QLabel("="))
        self.txt_tol_smc_h = QLineEdit()
        self.txt_tol_smc_h.setReadOnly(True)
        self.txt_tol_smc_h.setFixedWidth(90)
        self.txt_tol_smc_h.setToolTip(tr("mapping.txt_tol_smc_h_tooltip"))
        _tol_row.addWidget(self.txt_tol_smc_h)
        _tol_row.addWidget(QLabel("Sm³/h"))
        _tol_row.addStretch()

        def _update_tol_smc_h(_=None):
            self.txt_tol_smc_h.setText(f"{self.spin_tol.value() * 3600.0:.1f}")
        self.spin_tol.valueChanged.connect(_update_tol_smc_h)
        _update_tol_smc_h()
        sform.addRow(tr("mapping.row_tol"), _tol_row)

        self.spin_urf = QDoubleSpinBox()
        self.spin_urf.setRange(0.1, 20.0)
        self.spin_urf.setDecimals(1)
        self.spin_urf.setValue(2.0)
        sform.addRow(tr("mapping.row_urf"), self.spin_urf)

        self.chk_autocal = QCheckBox(tr("mapping.chk_autocal"))
        self.chk_autocal.setChecked(False)
        self.chk_autocal.setToolTip(tr("mapping.chk_autocal_tooltip"))

        # L'affinamento e' INDIPENDENTE dall'auto-calibrazione: la prima
        # sceglie il punto di PARTENZA (tol e urf iniziali in base alla
        # dimensione della rete), il secondo determina il punto di ARRIVO
        # stringendo la tolleranza di un fattore 10 per volta a partire da
        # qualunque valore. Legarli costringeva ad accettare la tol imposta
        # dall'auto-calibrazione per poter affinare, e impediva di partire da
        # una tolleranza scelta a mano.
        self.chk_refine = QCheckBox(tr("mapping.chk_refine"))
        self.chk_refine.setChecked(False)
        self.chk_refine.setToolTip(tr("mapping.chk_refine_tooltip"))

        _autocal_row = QHBoxLayout()
        _autocal_row.setSpacing(8)
        _autocal_row.addWidget(self.chk_autocal)
        _autocal_row.addWidget(self.chk_refine)
        _autocal_row.addStretch()
        sform.addRow("", _autocal_row)

        self.chk_multiprocess = QCheckBox(tr("mapping.chk_multiprocess"))
        self.chk_multiprocess.setChecked(True)
        self.chk_multiprocess.setToolTip(tr("mapping.chk_multiprocess_tooltip"))
        sform.addRow("", self.chk_multiprocess)

        def _on_autocal_toggled(checked):
            # L'auto-calibrazione disabilita i campi tol/urf perche' li
            # sovrascrive, ma NON tocca piu' l'affinamento: sono scelte
            # ortogonali (punto di partenza vs punto di arrivo).
            self.spin_tol.setEnabled(not checked)
            self.spin_urf.setEnabled(not checked)
        self.chk_autocal.toggled.connect(_on_autocal_toggled)

        outer.addWidget(self._grp_solver)
        self._chk_solver.toggled.connect(
            lambda checked: self._grp_solver.setVisible(checked))

        # ══════════════════════════════════════════════════════════════════════
        # BLOCCO 6 — Composizione gas (sempre visibile)
        # ══════════════════════════════════════════════════════════════════════
        grp_adv = QGroupBox(tr("mapping.grp_gas"))
        aform = QFormLayout(grp_adv)
        aform.setLabelAlignment(Qt.AlignRight)

        self.cb_gas_preset = QComboBox()
        # Composizioni SNAM — frazioni molari da dati qualità gas SNAM (rif. UNI EN ISO 13443)
        _MAZARA_DICT = {
            'methane': 0.86909, 'ethane': 0.08661, 'propane': 0.01163,
            'isobutane': 0.00072, 'butane': 0.00112, 'isopentane': 0.00019,
            'pentane': 0.00019, 'hexane': 0.00014, 'nitrogen': 0.01334,
            'carbon dioxide': 0.01672, 'helium': 0.00025,
        }
        _GELA_DICT = {
            'methane': 0.86645, 'ethane': 0.05246, 'propane': 0.02022,
            'isobutane': 0.00317, 'butane': 0.00478, 'isopentane': 0.00071,
            'pentane': 0.00026, 'hexane': 0.00060, 'nitrogen': 0.04455,
            'carbon dioxide': 0.00602, 'helium': 0.00078,
        }
        _GAS_PRESETS = [
            (tr("mapping.gas_mazara"),
             "SNAM_MAZARA_GAS", _MAZARA_DICT),
            (tr("mapping.gas_gela"),
             "SNAM_GELA_GAS", _GELA_DICT),
            (tr("mapping.gas_pure_methane"),
             "{'methane': 1.0}", {'methane': 1.0}),
            (tr("mapping.gas_typical_natural"),
             "{'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}",
             {'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}),
            (tr("mapping.gas_pure_hydrogen"),
             "{'hydrogen': 1.0}", {'hydrogen': 1.0}),
            (tr("mapping.gas_custom"), None, None),
        ]
        for label, csv_str, blend_dict in _GAS_PRESETS:
            self.cb_gas_preset.addItem(label, (csv_str, blend_dict))
        aform.addRow(tr("mapping.row_gas_base"), self.cb_gas_preset)

        # Aggiunta percentuale molare di H2
        _h2_row = QHBoxLayout()
        self.spin_h2_pct = QDoubleSpinBox()
        self.spin_h2_pct.setRange(0.0, 99.0)
        self.spin_h2_pct.setDecimals(2)
        self.spin_h2_pct.setSingleStep(0.01)
        self.spin_h2_pct.setValue(0.0)
        self.spin_h2_pct.setSuffix(" %")
        self.spin_h2_pct.setToolTip(tr("mapping.spin_h2_pct_tooltip"))
        _h2_row.addWidget(self.spin_h2_pct)
        _btn_reset_h2 = QPushButton("\u21ba")
        _btn_reset_h2.setFixedWidth(26)
        _btn_reset_h2.setToolTip(tr("mapping.btn_reset_h2_tooltip"))
        _btn_reset_h2.clicked.connect(lambda: self.spin_h2_pct.setValue(0.0))
        _h2_row.addWidget(_btn_reset_h2)
        aform.addRow(tr("mapping.row_h2_addition"), _h2_row)

        self.txt_gas_comp = QLineEdit("SNAM_MAZARA_GAS")
        self.txt_gas_comp.setPlaceholderText(tr("mapping.txt_gas_comp_placeholder"))
        self.txt_gas_comp.setToolTip(tr("mapping.txt_gas_comp_tooltip"))
        aform.addRow(tr("mapping.row_gas_export"), self.txt_gas_comp)

        def _build_blended_str():
            """Aggiorna txt_gas_comp combinando il preset base con la % H2."""
            data = self.cb_gas_preset.currentData()
            if data is None:
                return  # "Personalizzato" — non sovrascrivere il campo
            csv_str, blend_dict = data
            h2_frac = self.spin_h2_pct.value() / 100.0
            if h2_frac <= 0.0:
                result = csv_str
            elif blend_dict is None:
                return  # base personalizzata senza dict — non toccare
            else:
                blended = {}
                for k, v in blend_dict.items():
                    new_v = v * (1.0 - h2_frac)
                    if new_v > 1e-9:
                        blended[k] = new_v
                blended['hydrogen'] = blended.get('hydrogen', 0.0) + h2_frac
                # Usa JSON valido (virgolette doppie) così QGIS accetta il valore
                import json as _json
                result = _json.dumps({k: round(v, 5) for k, v in blended.items()})
            self.txt_gas_comp.blockSignals(True)
            self.txt_gas_comp.setText(result)
            self.txt_gas_comp.blockSignals(False)

        def _on_preset_changed(_idx):
            _build_blended_str()
        self.cb_gas_preset.currentIndexChanged.connect(_on_preset_changed)
        self.spin_h2_pct.valueChanged.connect(lambda _v: _build_blended_str())

        def _on_gas_text_changed():
            txt = self.txt_gas_comp.text().strip()
            for i in range(self.cb_gas_preset.count()):
                v = self.cb_gas_preset.itemData(i)
                if v is not None and v[0] == txt:
                    self.cb_gas_preset.blockSignals(True)
                    self.cb_gas_preset.setCurrentIndex(i)
                    self.cb_gas_preset.blockSignals(False)
                    return
            custom_idx = self.cb_gas_preset.count() - 1
            self.cb_gas_preset.blockSignals(True)
            self.cb_gas_preset.setCurrentIndex(custom_idx)
            self.cb_gas_preset.blockSignals(False)
        self.txt_gas_comp.textChanged.connect(_on_gas_text_changed)
        # Sync iniziale: imposta txt_gas_comp dal preset 0 (SNAM Mazara)
        _build_blended_str()
        outer.addWidget(grp_adv)
        outer.addStretch()
        btn_reload = QPushButton(tr("mapping.btn_reload"))
        btn_reload.clicked.connect(self.reload_layers)
        right_layout.addWidget(btn_reload)

        self.btn_collapse = QPushButton(tr("mapping.btn_collapse"))
        self.btn_collapse.setStyleSheet(
            "QPushButton { background-color: #2e6da4; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_collapse.clicked.connect(self._run_collapse)
        self.btn_collapse.setToolTip(tr("mapping.btn_collapse_tooltip"))
        right_layout.addWidget(self.btn_collapse)

        self.chk_only_export = QCheckBox(tr("mapping.chk_only_export"))
        self.chk_only_export.setChecked(False)
        self.chk_only_export.setToolTip(tr("mapping.chk_only_export_tooltip"))
        right_layout.addWidget(self.chk_only_export)

        # Avvia + Ferma affiancati.
        _sim_btn_row = QHBoxLayout()
        _sim_btn_row.setSpacing(6)

        self.btn_collapse_sim = QPushButton(tr("mapping.btn_start_sim"))
        self.btn_collapse_sim.setStyleSheet(
            "QPushButton { background-color: #1e7a1e; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_collapse_sim.clicked.connect(self._run_and_simulate)
        self.btn_collapse_sim.setToolTip(tr("mapping.btn_start_sim_tooltip"))
        _sim_btn_row.addWidget(self.btn_collapse_sim, stretch=3)

        self.btn_stop_sim = QPushButton(tr("mapping.btn_stop_sim"))
        self.btn_stop_sim.setStyleSheet(
            "QPushButton { background-color: #a11; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_stop_sim.setEnabled(False)   # attivo solo mentre gira
        self.btn_stop_sim.clicked.connect(self._stop_simulation)
        self.btn_stop_sim.setToolTip(tr("mapping.btn_stop_sim_tooltip"))
        _sim_btn_row.addWidget(self.btn_stop_sim, stretch=1)

        right_layout.addLayout(_sim_btn_row)

        # Campagna multi-giorno: esegue in sequenza il batch 24h su TUTTI i
        # file-giorno di una cartella (es. i 19 GeoJSON dello Scenario 1).
        self.btn_campaign = QPushButton(tr("mapping.btn_campaign"))
        self.btn_campaign.setStyleSheet(
            "QPushButton { background-color: #6a1b9a; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_campaign.clicked.connect(self._run_campaign)
        self.btn_campaign.setToolTip(tr("mapping.btn_campaign_tooltip"))
        right_layout.addWidget(self.btn_campaign)

        lbl_log = QLabel(tr("mapping.lbl_log"))
        lbl_log.setStyleSheet("font-weight: bold; margin-top: 8px;")
        right_layout.addWidget(lbl_log)

        self.txt_log_run = QTextEdit()
        self.txt_log_run.setReadOnly(True)
        self.txt_log_run.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_log_run.customContextMenuRequested.connect(self._show_log_context_menu)
        right_layout.addWidget(self.txt_log_run, 1)

        self.reload_layers()

    # -------------------------------------------------------------------------
    # Tab 1 – Prepara e Simula: helper log/params
    # -------------------------------------------------------------------------

    def _show_log_context_menu(self, pos):
        menu = self.txt_log_run.createStandardContextMenu()
        menu.addSeparator()
        act_clear = menu.addAction(tr("mapping.act_clear_log"))
        act_clear.triggered.connect(self.txt_log_run.clear)
        menu.exec_(self.txt_log_run.mapToGlobal(pos))

    def _log_run(self, msg: str, color: str = ''):
        """Aggiunge msg al log di Tab 1 con colore opzionale sul testo."""
        from PyQt5.QtCore import QCoreApplication
        cursor = self.txt_log_run.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        if color == 'green':
            fmt.setForeground(QColor('#1a7a1a'))
        elif color == 'red':
            fmt.setForeground(QColor('#cc0000'))
        elif color == 'orange':
            fmt.setForeground(QColor('#b85c00'))
        else:
            fmt.setForeground(self.txt_log_run.palette().text().color())
        cursor.setCharFormat(fmt)
        cursor.insertText(msg + '\n')
        self.txt_log_run.setTextCursor(cursor)
        self.txt_log_run.ensureCursorVisible()
        QCoreApplication.processEvents()

    # ─────────────────────────────────────────────────────────────────────────
    # Gestione layer QGIS
    # ─────────────────────────────────────────────────────────────────────────

    # -- Segnali progetto QGIS ------------------------------------------------

    def _build_viz_tab(self, widget):
        """Tab 2 – Visualizzazione Risultati."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(6)
        scroll.setWidget(inner)
        outer_layout = QVBoxLayout(widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        # -- Selezione layer risultati (PRIMA SEZIONE, subito visibile) --------
        grp_recolor = QGroupBox(tr("mapping.grp_recolor"))
        grp_recolor.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 2px solid #0078d7; "
            "border-radius: 4px; margin-top: 6px; padding-top: 4px; }"
            "QGroupBox::title { color: #0078d7; }")
        fl_rc = QFormLayout(grp_recolor)
        fl_rc.setLabelAlignment(Qt.AlignRight)

        lbl_rc = QLabel(tr("mapping.lbl_rc_hint"))
        lbl_rc.setTextFormat(Qt.RichText)
        fl_rc.addRow("", lbl_rc)

        self.cb_viz_nodes_lyr = QComboBox()
        self.cb_viz_nodes_lyr.setToolTip(tr("mapping.cb_viz_nodes_lyr_tooltip"))
        fl_rc.addRow(tr("mapping.row_nodes_layer"), self.cb_viz_nodes_lyr)

        self.cb_viz_nodes_field = QComboBox()
        fl_rc.addRow(tr("mapping.row_color_nodes"), self.cb_viz_nodes_field)

        self.cb_viz_nodes_size = QComboBox()
        self.cb_viz_nodes_size.setToolTip(tr("mapping.cb_viz_nodes_size_tooltip"))
        fl_rc.addRow(tr("mapping.row_size_nodes"), self.cb_viz_nodes_size)

        self.cb_viz_pipes_lyr = QComboBox()
        self.cb_viz_pipes_lyr.setToolTip(tr("mapping.cb_viz_pipes_lyr_tooltip"))
        fl_rc.addRow(tr("mapping.row_pipes_layer"), self.cb_viz_pipes_lyr)

        self.cb_viz_pipes_field = QComboBox()
        fl_rc.addRow(tr("mapping.row_color_pipes"), self.cb_viz_pipes_field)

        self.chk_viz_arrows = QCheckBox(tr("mapping.chk_viz_arrows"))
        self.chk_viz_arrows.setChecked(False)
        fl_rc.addRow("", self.chk_viz_arrows)

        rc_btn_row = QHBoxLayout()
        btn_viz_refresh = QPushButton("\u21ba")
        btn_viz_refresh.setFixedWidth(32)
        btn_viz_refresh.setToolTip(tr("mapping.btn_viz_refresh_tooltip"))
        btn_viz_refresh.clicked.connect(self._refresh_viz_combos)
        rc_btn_row.addWidget(btn_viz_refresh)
        self.btn_viz_apply = QPushButton(tr("mapping.btn_viz_apply"))
        self.btn_viz_apply.setStyleSheet(
            "QPushButton { background-color: #0078d7; color: white; "
            "font-weight: bold; padding: 5px; border-radius: 3px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_viz_apply.clicked.connect(self._apply_viz_recolor)
        rc_btn_row.addWidget(self.btn_viz_apply)
        fl_rc.addRow("", rc_btn_row)
        layout.addWidget(grp_recolor)

        # Connetti cambio layer ai combo field
        self.cb_viz_nodes_lyr.currentIndexChanged.connect(
            lambda _: self._on_viz_nodes_lyr_changed())
        self.cb_viz_pipes_lyr.currentIndexChanged.connect(
            lambda _: self._on_viz_pipes_lyr_changed())

        # -- Impostazioni per la prossima simulazione -----------------------
        grp_sim_opts = QGroupBox(tr("mapping.grp_sim_opts"))
        sim_layout = QVBoxLayout(grp_sim_opts)
        sim_layout.setSpacing(4)

        lbl_hint = QLabel(tr("mapping.lbl_sim_opts_hint"))
        lbl_hint.setStyleSheet("color: #aaa; font-size: 10px;")
        sim_layout.addWidget(lbl_hint)

        # -- Nodi -------------------------------------------------------------
        grp_nodes = QGroupBox(tr("mapping.grp_nodes"))
        rlayout_n = QVBoxLayout(grp_nodes)
        rlayout_n.setSpacing(4)
        rform_n = QFormLayout()
        rform_n.setLabelAlignment(Qt.AlignRight)
        self.cb_res_nodes_color = QComboBox()
        self.cb_res_nodes_color.addItem(tr("mapping.f_pressure_bar"),        "pressure_bar")
        self.cb_res_nodes_color.addItem(tr("mapping.f_vol_flow"),        "volumetric_flow_sm3s")
        self.cb_res_nodes_color.addItem(tr("mapping.f_energy_flow"),"energy_flow_mw")
        self.cb_res_nodes_color.addItem(tr("mapping.f_temp_k"),        "temperature_k")
        self.cb_res_nodes_color.addItem(tr("mapping.f_sp_gravity"),          "sp_gravity")
        self.cb_res_nodes_color.addItem(tr("mapping.f_z_factor"),               "z_factor")
        self.cb_res_nodes_color.addItem(tr("mapping.f_hhv"),           "hhv_mj_sm3")
        self.cb_res_nodes_color.addItem(tr("mapping.f_wobbe"),         "wobbe_mj_sm3")
        self.cb_res_nodes_color.addItem(tr("mapping.f_density"),   "density_kg_m3")
        self.cb_res_nodes_color.addItem(tr("mapping.f_std_density"),     "std_density_kg_sm3")
        self.cb_res_nodes_color.addItem(tr("mapping.f_molar_mass"),   "molar_mass")
        self.cb_res_nodes_color.addItem(tr("mapping.f_h2_pct"),                 "h2_pct")
        self.cb_res_nodes_color.addItem(tr("mapping.f_throughput"),     "throughput_sm3h")
        rform_n.addRow(tr("mapping.row_color_by"), self.cb_res_nodes_color)

        self.cb_res_nodes_size = QComboBox()
        self.cb_res_nodes_size.addItem(tr("mapping.none_item"),             None)
        self.cb_res_nodes_size.addItem(tr("mapping.f_vol_flow"),          "volumetric_flow_sm3s")
        self.cb_res_nodes_size.addItem(tr("mapping.f_energy_flow"),  "energy_flow_mw")
        self.cb_res_nodes_size.addItem(tr("mapping.f_pressure_bar"),          "pressure_bar")
        self.cb_res_nodes_size.addItem(tr("mapping.f_temp_k"),          "temperature_k")
        self.cb_res_nodes_size.setToolTip(tr("mapping.cb_res_nodes_size_tooltip"))
        rform_n.addRow(tr("mapping.row_size_by"), self.cb_res_nodes_size)
        rlayout_n.addLayout(rform_n)
        self._res_node_checks = []
        _node_fields = [
            ("pressure_bar",          tr("mapping.fs_pressure")),
            ("volumetric_flow_sm3s",  tr("mapping.fs_vol_flow")),
            ("energy_flow_mw",        tr("mapping.fs_energy_flow")),
            ("temperature_k",         tr("mapping.fs_temp")),
            ("sp_gravity",            tr("mapping.fs_sp_gravity")),
            ("z_factor",              tr("mapping.f_z_factor")),
            ("hhv_mj_sm3",            tr("mapping.fs_hhv")),
            ("wobbe_mj_sm3",          tr("mapping.fs_wobbe")),
            ("density_kg_m3",         tr("mapping.fs_density")),
            ("std_density_kg_sm3",    tr("mapping.fs_std_density")),
            ("molar_mass",            tr("mapping.fs_mm")),
            ("h2_pct",                tr("mapping.f_h2_pct")),
            ("gas_comp",              tr("mapping.fs_gas_comp")),
            ("throughput_sm3h",       tr("mapping.fs_throughput")),
            ("node_type",             tr("mapping.fs_node_type")),
        ]
        node_grid = QGridLayout()
        for col, (fid, fname) in enumerate(_node_fields):
            cb = QCheckBox(fname)
            cb.setChecked(fid in ("pressure_bar", "volumetric_flow_sm3s", "energy_flow_mw",
                                  "temperature_k", "sp_gravity",
                                  "z_factor", "hhv_mj_sm3", "wobbe_mj_sm3",
                                  "h2_pct", "gas_comp", "throughput_sm3h"))
            self._res_node_checks.append((fid, cb))
            node_grid.addWidget(cb, col // 5, col % 5)
        rlayout_n.addLayout(node_grid)
        sim_layout.addWidget(grp_nodes)

        # -- Condotte ----------------------------------------------------------
        grp_pipes = QGroupBox(tr("mapping.grp_pipes"))
        rlayout_p = QVBoxLayout(grp_pipes)
        rlayout_p.setSpacing(4)
        rform_p = QFormLayout()
        rform_p.setLabelAlignment(Qt.AlignRight)
        self.cb_res_pipes_color = QComboBox()
        self.cb_res_pipes_color.addItem(tr("mapping.fp_flow_abs"),      "flow_abs_sm3h")
        self.cb_res_pipes_color.addItem(tr("mapping.fp_velocity"),  "velocity_m_s")
        self.cb_res_pipes_color.addItem(tr("mapping.fp_avg_pressure"),   "avg_pressure_bar")
        self.cb_res_pipes_color.addItem(tr("mapping.f_sp_gravity"),        "sp_gravity")
        self.cb_res_pipes_color.addItem(tr("mapping.f_z_factor"),             "z_factor")
        self.cb_res_pipes_color.addItem(tr("mapping.fp_density"), "density_kg_m3")
        rform_p.addRow(tr("mapping.row_color_by"), self.cb_res_pipes_color)
        rlayout_p.addLayout(rform_p)
        self._res_pipe_checks = []
        _pipe_fields = [
            ("flow_sm3h",        tr("mapping.fps_flow_signed")),
            ("flow_abs_sm3h",    tr("mapping.fps_flow_abs")),
            ("velocity_m_s",     tr("mapping.fps_velocity")),
            ("avg_pressure_bar", tr("mapping.fps_avg_pressure")),
            ("sp_gravity",       tr("mapping.fs_sp_gravity")),
            ("z_factor",         tr("mapping.f_z_factor")),
            ("density_kg_m3",    tr("mapping.fps_density")),
        ]
        pipe_grid = QGridLayout()
        for col, (fid, fname) in enumerate(_pipe_fields):
            cb = QCheckBox(fname)
            cb.setChecked(fid in ("flow_sm3h", "flow_abs_sm3h", "velocity_m_s",
                                  "avg_pressure_bar", "sp_gravity"))
            self._res_pipe_checks.append((fid, cb))
            pipe_grid.addWidget(cb, col // 4, col % 4)
        rlayout_p.addLayout(pipe_grid)
        sim_layout.addWidget(grp_pipes)

        self.chk_flow_arrows = QCheckBox(tr("mapping.chk_flow_arrows"))
        self.chk_flow_arrows.setChecked(False)
        self.chk_flow_arrows.setToolTip(tr("mapping.chk_flow_arrows_tooltip"))
        sim_layout.addWidget(self.chk_flow_arrows)
        layout.addWidget(grp_sim_opts)

        # -- Esporta dati --------------------------------------------------
        grp_exp = QGroupBox(tr("mapping.grp_export"))
        fl_exp = QFormLayout(grp_exp)
        fl_exp.setLabelAlignment(Qt.AlignRight)

        self.cb_viz_export_lyr = QComboBox()
        fl_exp.addRow(tr("mapping.row_layer"), self.cb_viz_export_lyr)

        self.spin_viz_decimals = QSpinBox()
        self.spin_viz_decimals.setRange(0, 10)
        self.spin_viz_decimals.setValue(4)
        self.spin_viz_decimals.setToolTip(tr("mapping.spin_viz_decimals_tooltip"))
        fl_exp.addRow(tr("mapping.row_decimals"), self.spin_viz_decimals)

        btn_exp = QPushButton(tr("mapping.btn_export_csv"))
        btn_exp.clicked.connect(self._export_viz_csv)
        fl_exp.addRow("", btn_exp)
        layout.addWidget(grp_exp)

        layout.addStretch()

    def _connect_project_signals(self):
        """Connette i segnali del progetto per auto-aggiornare i ComboBox."""
        try:
            from qgis.core import QgsProject
            proj = QgsProject.instance()
            proj.layersAdded.connect(self._on_layers_added)
            proj.layersRemoved.connect(self.reload_layers)
        except Exception:
            pass
        # Popola subito i combo (inclusi quelli viz) con i layer già presenti nel progetto
        self._refresh_viz_combos()

    def _on_layers_added(self, layers):
        """Quando vengono aggiunti layer, connette nameChanged e ricarica."""
        for lyr in layers:
            lid = lyr.id()
            if lid not in self._layer_name_conns:
                self._layer_name_conns[lid] = lyr.nameChanged.connect(self.reload_layers)
        self.reload_layers()

    @staticmethod
    def _layer_label(layer):
        """Restituisce il nome del layer con il conteggio feature per disambiguare."""
        try:
            from qgis.core import QgsMapLayer
            if layer.type() == QgsMapLayer.VectorLayer:
                return f"{layer.name()}  [{layer.featureCount()} feat]"
            return f"{layer.name()}  [raster]"
        except Exception:
            return layer.name()

    def _on_mode_changed(self, is_collapsed: bool):
        """Mostra/nasconde i gruppi in base alla modalità selezionata."""
        self.grp_collapse_mode.setVisible(not is_collapsed)
        self.grp_collapsed_layers.setVisible(is_collapsed)
        self.grp_field_pipes.setVisible(is_collapsed)
        self.grp_field_nodes.setVisible(is_collapsed)
        if is_collapsed:
            self.btn_collapse.setText(tr("mapping.btn_collapse_from_layer"))
            self.btn_collapse_sim.setText(tr("mapping.btn_start_sim"))
        else:
            self.btn_collapse.setText(tr("mapping.btn_collapse"))
            self.btn_collapse_sim.setText(tr("mapping.btn_start_sim"))

    def reload_layers(self):
        """Ripopola tutti i ComboBox dai layer del progetto QGIS.

        Modalit\u00e0 A e Tab 0: solo layer visibili nella legenda (layer-tree).
        Modalit\u00e0 B: tutti i layer del progetto, inclusi quelli nascosti
                    (es. Condotte #N / Nodi #N aggiunti senza flag legenda).
        """
        try:
            from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes
            proj = QgsProject.instance()
            all_layers = list(proj.mapLayers().values())
            tree_ids = {n.layerId() for n in proj.layerTreeRoot().findLayers()}
            legend_layers = [l for l in all_layers if l.id() in tree_ids]
        except Exception:
            return

        def _line(src): return [l for l in src
                                 if l.type() == QgsMapLayer.VectorLayer
                                 and l.geometryType() == QgsWkbTypes.LineGeometry]
        def _pt(src):   return [l for l in src
                                 if l.type() == QgsMapLayer.VectorLayer
                                 and l.geometryType() == QgsWkbTypes.PointGeometry]
        def _ras(src):  return [l for l in src
                                 if l.type() == QgsMapLayer.RasterLayer]

        line_lys_legend = _line(legend_layers)
        pt_lys_legend   = _pt(legend_layers)
        ras_lys         = _ras(legend_layers)
        line_lys_all    = _line(all_layers)
        pt_lys_all      = _pt(all_layers)

        # Connetti nameChanged per layer non ancora tracciati
        for l in all_layers:
            lid = l.id()
            if lid not in self._layer_name_conns:
                self._layer_name_conns[lid] = l.nameChanged.connect(self.reload_layers)

        # Tab 0 – Verifica Condotte: il widget si aggiorna autonomamente via QgsProject
        # Forziamo comunque un refresh esplicito
        self._tab_repair._refresh_combos()

        # Modalità A
        prev = self.cb_pipes.currentData()
        self.cb_pipes.blockSignals(True)
        self.cb_pipes.clear()
        for l in line_lys_legend:
            self.cb_pipes.addItem(self._layer_label(l), l)
        self.cb_pipes.blockSignals(False)
        self._restore(self.cb_pipes, prev)
        self._on_pipes_layer_changed(self.cb_pipes.currentIndex())

        self._refill_none(self.cb_dem,   ras_lys,       self.cb_dem.currentData())
        self._refill_none(self.cb_nodes, pt_lys_legend, self.cb_nodes.currentData())
        self._on_nodes_layer_changed(self.cb_nodes.currentIndex())

        # Modalità B
        prev_cp = self.cb_coll_pipes.currentData()
        self.cb_coll_pipes.blockSignals(True)
        self.cb_coll_pipes.clear()
        for l in line_lys_legend:
            self.cb_coll_pipes.addItem(self._layer_label(l), l)
        self.cb_coll_pipes.blockSignals(False)
        self._restore(self.cb_coll_pipes, prev_cp)
        self._on_coll_pipes_changed(self.cb_coll_pipes.currentIndex())

        prev_cn = self.cb_coll_nodes.currentData()
        self.cb_coll_nodes.blockSignals(True)
        self.cb_coll_nodes.clear()
        for l in pt_lys_legend:
            self.cb_coll_nodes.addItem(self._layer_label(l), l)
        self.cb_coll_nodes.blockSignals(False)
        self._restore(self.cb_coll_nodes, prev_cn)
        self._on_coll_nodes_changed(self.cb_coll_nodes.currentIndex())

        # Tab 2 – Visualizzazione: aggiorna combos layer [Risultati]
        if hasattr(self, 'cb_viz_nodes_lyr'):
            self._refresh_viz_combos()

    @staticmethod
    def _restore(combo, prev_data):
        if prev_data is not None:
            for i in range(combo.count()):
                if combo.itemData(i) is prev_data:
                    combo.setCurrentIndex(i)
                    return

    def _refill_none(self, combo, layers, prev_data):
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(tr("mapping.none_item"), None)
        for l in layers:
            combo.addItem(self._layer_label(l), l)
        combo.blockSignals(False)
        self._restore(combo, prev_data)

    def _fill_fields(self, combo, layer, candidates=None, with_none=False):
        """Popola combo con i campi del layer, poi auto-seleziona il migliore."""
        prev = combo.currentData()  # '' per nessuno/vuoto, field_name per campi reali
        combo.blockSignals(True)
        combo.clear()
        if with_none:
            combo.addItem(tr("mapping.none_placeholder_item"), "")
        if layer is not None:
            for field in layer.fields():
                combo.addItem(field.name(), field.name())
        combo.blockSignals(False)
        # Ripristina selezione precedente solo se era un campo reale (data non vuota)
        if prev:
            for i in range(combo.count()):
                if combo.itemData(i) == prev:
                    combo.setCurrentIndex(i)
                    return
        # Auto-selezione da candidati
        if candidates:
            _best_field(combo, candidates)

    def _on_pipes_layer_changed(self, _idx):
        lyr = self.cb_pipes.currentData()
        self._fill_fields(self.cb_diam_field, lyr, _DIAM_CAND)

    def _on_nodes_layer_changed(self, _idx):
        lyr = self.cb_nodes.currentData()
        has_layer = lyr is not None
        self.cb_f_nodes_ref.setEnabled(has_layer)
        self.txt_nodes_ref_val.setEnabled(has_layer)
        self.cb_f_nodes_flow.setEnabled(has_layer)
        self.txt_nodes_comp_val.setEnabled(has_layer)
        self.cb_f_nodes_comp_pout.setEnabled(has_layer)
        if hasattr(self, 'cb_f_nodes_comp_field'):
            self.cb_f_nodes_comp_field.setEnabled(has_layer)
        self._fill_fields(self.cb_f_nodes_ref, lyr, with_none=True)
        self._fill_fields(self.cb_f_nodes_flow, lyr, _FLOW_CAND, with_none=True)
        # Combo opzionali per i parametri compressore
        if hasattr(self, 'cb_f_nodes_comp_field'):
            self._fill_fields(self.cb_f_nodes_comp_field, lyr, ('Type', 'type', 'tipo', 'is_comp'), with_none=True)
        self._fill_fields(self.cb_f_nodes_comp_pout, lyr,
                          ('comp_pout', 'p_out_bar', 'pressione_out',
                           'p_out', 'pout_bar'),
                          with_none=True)
        self.cb_f_nodes_comp_pout.setCurrentText("70.0")
        self._update_ora_preview()

    def _on_coll_pipes_changed(self, _idx):
        lyr = self.cb_coll_pipes.currentData()
        self._fill_fields(self.cb_f_pipe_id, lyr, _PIPE_ID_CAND)
        self._fill_fields(self.cb_f_node_a,  lyr, _NODE_A_CAND)
        self._fill_fields(self.cb_f_node_b,  lyr, _NODE_B_CAND)
        self._fill_fields(self.cb_f_length,  lyr, _LENGTH_CAND)
        self._fill_fields(self.cb_f_diam,    lyr, _DIAM_CAND)

    def _on_coll_nodes_changed(self, _idx):
        lyr = self.cb_coll_nodes.currentData()
        self._fill_fields(self.cb_f_node_id,  lyr, _NODE_ID_CAND)
        self._fill_fields(self.cb_f_altitude, lyr, _ALT_CAND)
        self._fill_fields(self.cb_f_ref_flag, lyr, _REF_FLAG_CAND)
        self._fill_fields(self.cb_f_flow,     lyr, _FLOW_CAND, with_none=True)
        if hasattr(self, 'cb_f_nodes_comp_field'):
            self._fill_fields(self.cb_f_nodes_comp_field, lyr, ('Type', 'type', 'tipo', 'is_comp'), with_none=True)
            self._fill_fields(self.cb_f_nodes_comp_pout, lyr, ('comp_pout', 'p_out_bar', 'pressione_out', 'p_out', 'pout_bar'), with_none=True)
            self.cb_f_nodes_comp_pout.setCurrentText("70.0")
        self._update_ora_preview()

    # ─────────────────────────────────────────────────────────────────────────
    # Azioni
    # ─────────────────────────────────────────────────────────────────────────

    def _update_ora_preview(self):
        """Mostra il valore di flusso (Smc/h) per l'ora selezionata, campionando il layer attivo."""
        if not hasattr(self, 'lbl_ora_preview'):
            return
        try:
            ora = self.spin_ora.value()
            sep = self.cb_separator.currentData() or ';'
            if self.chk_already_collapsed.isChecked():
                lyr = self.cb_coll_nodes.currentData()
                f_flow = self.cb_f_flow.currentData() or ''
            else:
                lyr = self.cb_nodes.currentData()
                f_flow = self.cb_f_nodes_flow.currentData() or ''
            if lyr is None or not f_flow:
                self.lbl_ora_preview.setText('')
                return
            fields = [f.name() for f in lyr.fields()]
            if f_flow not in fields:
                self.lbl_ora_preview.setText(
                    f"<i style='color:red'>campo '{f_flow}' non trovato</i>")
                return
            from ..gis_integration.network_builder import _parse_smc_ora, PLACEHOLDER_FLOW
            for feat in lyr.getFeatures():
                smc_str = str(feat[f_flow] or '')
                if not smc_str:
                    continue
                parsed = _parse_smc_ora(smc_str, ora, sep)
                if parsed != PLACEHOLDER_FLOW:
                    nid = feat['node_id'] if 'node_id' in fields else feat.id()
                    val_h = parsed * 3600.0
                    self.lbl_ora_preview.setText(
                        f"<i style='color:gray'>es. nodo {nid}: {val_h:.4g} Smc/h @ ora {ora}</i>")
                    return
            self.lbl_ora_preview.setText(
                "<i style='color:orange'>nessun valore reale (tutti placeholder)</i>")
        except Exception:
            self.lbl_ora_preview.setText('')

    def _browse_prepare_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, tr("mapping.browse_out_dir_caption"), "",
            QFileDialog.ShowDirsOnly)
        if folder:
            self.txt_prepare_folder.setText(folder)

    def _show_warnings_dialog(self, warnings, pipe_layer=None):
        """Dialog NON modale per avvisi rete con pulsante Flash condotte problematiche."""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                                     QPushButton, QHBoxLayout, QTextEdit)
        from PyQt5.QtCore import Qt

        # Estrai geometrie problematiche dalla lista warnings
        # Le coordinate sono nel formato "(x0,y0)→(x1,y1)" inserito da check_pipe_issues
        import re as _re
        _geoms = []
        if pipe_layer is not None:
            # Costruisci set di id_interni problematici da bad_ids via _arc_label
            # Alternativa più robusta: cerca le coordinate nei messaggi e trova le feature
            _coord_re = _re.compile(r'\[?\((\d+),(\d+)\)\u2192\((\d+),(\d+)\)\]?')
            for w in warnings:
                for m in _coord_re.finditer(w):
                    x0, y0, x1, y1 = [int(v) for v in m.groups()]
                    # Cerca la feature con quegli estremi
                    for feat in pipe_layer.getFeatures():
                        g = feat.geometry()
                        if g is None or g.isNull():
                            continue
                        try:
                            from qgis.core import QgsGeometry
                            pts = g.asPolyline() or (
                                g.asMultiPolyline()[0] if g.isMultipart() else [])
                            if not pts:
                                continue
                            p0, p1 = pts[0], pts[-1]
                            if (abs(p0.x() - x0) < 2 and abs(p0.y() - y0) < 2 and
                                    abs(p1.x() - x1) < 2 and abs(p1.y() - y1) < 2):
                                _geoms.append(g)
                                break
                            if (abs(p1.x() - x0) < 2 and abs(p1.y() - y0) < 2 and
                                    abs(p0.x() - x1) < 2 and abs(p0.y() - y1) < 2):
                                _geoms.append(g)
                                break
                        except Exception:
                            pass

        # Usa la finestra principale di QGIS come parent così il dialog
        # fluttua sopra la mappa senza portare in primo piano il pannello plugin
        _main_win = self.iface.mainWindow() if self.iface else self
        dlg = QDialog(_main_win)
        dlg.setWindowTitle(tr("mapping.warn_dlg_title"))
        # Finestra indipendente (Tool): non nasconde la mappa, non ha WindowStaysOnTopHint
        dlg.setWindowFlags(Qt.Tool | Qt.WindowCloseButtonHint)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.setMinimumWidth(620)
        layout = QVBoxLayout(dlg)

        lbl = QLabel(tr("mapping.warn_dlg_lbl"))
        layout.addWidget(lbl)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setMaximumHeight(220)
        txt.setHtml("<br>".join(
            f"• {w}" for w in warnings
        ))
        layout.addWidget(txt)

        btn_row = QHBoxLayout()

        if _geoms:
            # CRS del layer sorgente — serve per trasformare correttamente zoom e flash
            _layer_crs = pipe_layer.crs() if pipe_layer is not None else None

            def _raise_map():
                if self.iface:
                    self.iface.mainWindow().raise_()
                    self.iface.mainWindow().activateWindow()

            btn_zoom = QPushButton(tr("mapping.btn_zoom"))
            btn_zoom.setToolTip(tr("mapping.btn_zoom_tooltip"))
            def _do_zoom():
                try:
                    from qgis.core import QgsRectangle, QgsCoordinateTransform, QgsProject
                    canvas = self.iface.mapCanvas() if self.iface else None
                    if canvas is None:
                        return
                    bbox = QgsRectangle()
                    for g in _geoms:
                        bbox.combineExtentWith(g.boundingBox())
                    if not bbox.isEmpty():
                        # Trasforma il bbox dal CRS del layer al CRS del canvas
                        if _layer_crs is not None and _layer_crs != canvas.mapSettings().destinationCrs():
                            xform = QgsCoordinateTransform(
                                _layer_crs,
                                canvas.mapSettings().destinationCrs(),
                                QgsProject.instance())
                            bbox = xform.transformBoundingBox(bbox)
                        bbox.scale(2.0)
                        canvas.setExtent(bbox)
                        canvas.refresh()
                    _raise_map()
                except Exception:
                    pass
            btn_zoom.clicked.connect(_do_zoom)
            btn_row.addWidget(btn_zoom)

            btn_flash = QPushButton(tr("mapping.btn_flash"))
            btn_flash.setToolTip(tr("mapping.btn_flash_tooltip"))
            def _do_flash():
                try:
                    from PyQt5.QtGui import QColor
                    canvas = self.iface.mapCanvas() if self.iface else None
                    if canvas is None:
                        return
                    _raise_map()
                    # Passa il CRS del layer a flashGeometries per la conversione automatica
                    canvas.flashGeometries(
                        _geoms,
                        _layer_crs if _layer_crs is not None else canvas.mapSettings().destinationCrs(),
                        startColor=QColor(255, 50, 50, 200),
                        endColor=QColor(255, 200, 0, 0),
                        flashes=5, duration=1500)
                except Exception:
                    pass
            btn_flash.clicked.connect(_do_flash)
            btn_row.addWidget(btn_flash)
            # Zoom + flash automatici all'apertura
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(400, lambda: (_do_zoom(), _do_flash()))
        else:
            lbl_no = QLabel(tr("mapping.warn_no_geom"))
            lbl_no.setTextFormat(Qt.RichText)
            layout.addWidget(lbl_no)

        btn_row.addStretch()
        btn_ok = QPushButton("OK")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        dlg.show()   # Non-modale: show() invece di exec_()

    def _log_prepare(self, msg: str, color: str = ''):
        """Proxy per retrocompatibilita': usa _log_run."""
        self._log_run(msg, color)

    def _set_buttons_enabled(self, enabled: bool):
        self.btn_collapse.setEnabled(enabled)
        self.btn_collapse_sim.setEnabled(enabled)
        self.chk_sim_24.setEnabled(enabled)
        self.spin_ora.setEnabled(enabled)
        if hasattr(self, 'btn_campaign'):
            self.btn_campaign.setEnabled(enabled)

    def _phys_params(self) -> dict:
        """Legge i parametri fisici da Tab 2 (usati sia per export che per sim)."""
        return {
            'pressure_ref_pa': self.spin_pressure.value() * 1e5,
            'temp_ref_k':      self.spin_temp.value(),
            'roughness_m':     self.spin_roughness.value(),
            'placeholder_flow': self.spin_placeholder_flow.value(),
            'gas_comp_ref':    self.txt_gas_comp.text().strip()
                               or "{'methane': 1.0}",
        }

    def _run_collapse(self):
        """
        Modalità A: collassa → esporta CSV → aggiungi layer al progetto.
        Modalità B: esporta CSV da layer già collassati (con mappatura campi).
        Al termine auto-popola la cartella nella tab Simula.
        """
        out_folder = self.txt_prepare_folder.text().strip()
        if not out_folder:
            self._log_prepare("ERRORE: seleziona una cartella di output.")
            return

        self._set_buttons_enabled(False)
        self.txt_log_run.clear()
        phys = self._phys_params()
        from pathlib import Path
        run_dir, run_label = _next_run_subdir(out_folder)
        out_input_dir = str(run_dir / "input")
        self._last_input_dir = out_input_dir  # imposta subito, anche se fallisce
        ora = self.spin_ora.value()

        try:
            from ..gis_integration.network_builder import (
                run_collapse_pipeline, run_nocollapse_pipeline, export_layers_to_csv)
            from qgis.core import QgsProject

            if not self.chk_already_collapsed.isChecked():
                # ── Modalità A: Collassa rete ─────────────────────────────────
                pipe_layer = self.cb_pipes.currentData()
                if pipe_layer is None:
                    self._log_prepare("ERRORE: nessun layer condotte selezionato.")
                    return


                # Salva layer originali per backprojection risultati
                self._last_orig_pipes_lyr = pipe_layer
                self._last_orig_nodes_lyr = self.cb_nodes.currentData()

                _pipeline_fn = run_nocollapse_pipeline if self.chk_no_collapse.isChecked() \
                    else run_collapse_pipeline
                pipes_lyr, nodes_lyr, nodes_csv, pipes_csv, warnings = _pipeline_fn(
                    pipe_layer=pipe_layer,
                    out_dir=out_input_dir,
                    ora=ora,
                    dem_layer=self.cb_dem.currentData(),
                    nodes_layer=self.cb_nodes.currentData(),
                    diam_field=self.cb_diam_field.currentData() or 'Diametro_pollici',
                    diam_unit=self.cb_diam_unit.currentData() or 'in',
                    radius_m=self.spin_radius.value(),
                    log=self._log_prepare,
                    pressure_ref_pa=phys['pressure_ref_pa'],
                    temp_ref_k=phys['temp_ref_k'],
                    roughness_m=phys['roughness_m'],
                    gas_comp_ref=phys['gas_comp_ref'],
                    placeholder_flow=phys['placeholder_flow'],
                    loads_layer=self.cb_nodes.currentData(),
                    loads_field=self.cb_f_nodes_flow.currentData() or '',
                    ref_field=self.cb_f_nodes_ref.currentData() or '',
                    ref_value=self.txt_nodes_ref_val.text().strip(),
                    comp_field=self.cb_f_nodes_comp_field.currentData() or '' if self.chk_enable_compressor.isChecked() else '',
                    comp_value=self.txt_nodes_comp_val.text().strip() if self.chk_enable_compressor.isChecked() else '',
                    comp_pout_field=(self.cb_f_nodes_comp_pout.currentData() or self.cb_f_nodes_comp_pout.currentText().strip()) if self.chk_enable_compressor.isChecked() else '',
                    comp_use_pcm=self.chk_use_pcm.isChecked() if self.chk_enable_compressor.isChecked() else True,
                    flow_sep=self.cb_separator.currentData() or ';',
                )
                if warnings:
                    self._show_warnings_dialog(warnings, pipe_layer=pipe_layer)
                self._tab_repair.notify_islands(pipe_layer, warnings)
                # Rinomina con numero progressivo
                _n = _next_layer_run_number()
                pipes_lyr.setName(f"Condotte #{_n}")
                nodes_lyr.setName(f"Nodi #{_n}")
                # Registra sempre nel progetto (serve per Modalità B)
                # ma mostra in legenda solo se il flag è attivo
                add_legend = self.chk_show_collapsed.isChecked()
                QgsProject.instance().addMapLayer(pipes_lyr, add_legend)
                QgsProject.instance().addMapLayer(nodes_lyr, add_legend)
                if add_legend and self.iface is not None:
                    self.iface.mapCanvas().refresh()
                # Pre-seleziona in Modalità B per eventuale ri-simulazione
                self.chk_already_collapsed.setChecked(True)
                self._restore(self.cb_coll_pipes, pipes_lyr)
                self._restore(self.cb_coll_nodes, nodes_lyr)
                self._on_coll_pipes_changed(self.cb_coll_pipes.currentIndex())
                self._on_coll_nodes_changed(self.cb_coll_nodes.currentIndex())
                self._log_prepare(
                    f"Layer '{pipes_lyr.name()}' "
                    f"({pipes_lyr.featureCount()} condotte, "
                    f"{nodes_lyr.featureCount()} nodi)")
                self._log_prepare(
                    "[OK] Modalit\u00e0 B attiva: modifica i layer e ri-esegui senza ri-collassare.")

            else:
                # ── Modalità B: Già collassata ────────────────────────────────
                pipes_lyr = self.cb_coll_pipes.currentData()
                nodes_lyr = self.cb_coll_nodes.currentData()
                if pipes_lyr is None or nodes_lyr is None:
                    self._log_prepare(
                        "ERRORE: seleziona layer condotte E nodi collassati.")
                    return

                self._log_prepare(
                    f"Pipe: {pipes_lyr.name()} ({pipes_lyr.featureCount()} feat)")
                self._log_prepare(
                    f"Nodi: {nodes_lyr.name()} ({nodes_lyr.featureCount()} feat)")
                self._log_prepare(f"Export CSV (ora={ora})...")

                nodes_csv, pipes_csv, n_nodes, c_ref, c_junc, n_pipes = \
                    export_layers_to_csv(
                        pipes_lyr=pipes_lyr,
                        nodes_lyr=nodes_lyr,
                        out_dir=out_input_dir,
                        ora=ora,
                        pressure_ref_pa=phys['pressure_ref_pa'],
                        temp_ref_k=phys['temp_ref_k'],
                        gas_comp_ref=phys['gas_comp_ref'],
                        roughness_m=phys['roughness_m'],
                        placeholder_flow=phys['placeholder_flow'],
                        f_pipe_id=self.cb_f_pipe_id.currentData() or 'pipe_id',
                        f_node_a=self.cb_f_node_a.currentData() or 'node_a',
                        f_node_b=self.cb_f_node_b.currentData() or 'node_b',
                        f_length=self.cb_f_length.currentData() or 'length_m',
                        f_diam=self.cb_f_diam.currentData() or 'diameter_m',
                        f_diam_unit=self.cb_f_diam_unit.currentData() or 'm',
                        f_node_id=self.cb_f_node_id.currentData() or 'node_id',
                        f_altitude=self.cb_f_altitude.currentData() or 'altitude_m',
                        f_ref_flag=self.cb_f_ref_flag.currentData() or 'matched',
                        ref_flag_value=self.txt_ref_value.text().strip() or '1',
                        f_flow=self.cb_f_flow.currentData() or '',
                        flow_sep=self.cb_separator.currentData() or ';',
                    )
                self._log_prepare(
                    f"sf_nodes.csv:     {n_nodes} nodi "
                    f"({c_ref} reference, {c_junc} junction)")
                self._log_prepare(f"sf_pipelines.csv: {n_pipes} pipe")
                if c_ref == 0:
                    self._log_prepare(
                        "ERRORE: 0 nodi reference! Verifica il campo 'Flag reference' e il suo valore.")
                    QMessageBox.critical(
                        self, tr("mapping.no_ref_title"),
                        tr("mapping.no_ref_msg"))
                    return

            self._log_prepare("-" * 40)
            self._log_prepare(f"CSV in: {out_input_dir}")
            self._last_input_dir = out_input_dir
            self._log_run(f"[OK] CSV esportati in: {out_input_dir}", 'green')

        except Exception as exc:
            import traceback
            self._log_prepare(f"ERRORE: {exc}")
            self._log_prepare(traceback.format_exc())
        finally:
            self._set_buttons_enabled(True)

    def _validate_before_run(self) -> bool:
        """
        Controlla che i parametri minimi siano impostati prima di avviare la simulazione.
        Mostra un dialogo di avviso per ogni problema rilevato.
        Ritorna True se tutto è a posto, False se mancano dati critici.
        """
        errors = []
        warnings_list = []

        if not self.chk_already_collapsed.isChecked():
            # Modalità A
            if self.cb_pipes.currentData() is None:
                errors.append(tr("mapping.err_no_pipes_a"))
            nodes_lyr = self.cb_nodes.currentData()
            if nodes_lyr is None:
                warnings_list.append(tr("mapping.warn_no_nodes_layer"))
            else:
                ref_field = self.cb_f_nodes_ref.currentData() or ''
                if not ref_field:
                    warnings_list.append(tr("mapping.warn_no_ref_field_a"))
                elif not self.txt_nodes_ref_val.text().strip():
                    warnings_list.append(tr("mapping.warn_empty_ref_val_a"))
        else:
            # Modalità B
            if self.cb_coll_pipes.currentData() is None:
                errors.append(tr("mapping.err_no_pipes_b"))
            if self.cb_coll_nodes.currentData() is None:
                errors.append(tr("mapping.err_no_nodes_b"))
            else:
                ref_flag = self.cb_f_ref_flag.currentData() or ''
                if not ref_flag:
                    warnings_list.append(tr("mapping.warn_no_ref_field_b"))
                elif not self.txt_ref_value.text().strip():
                    warnings_list.append(tr("mapping.warn_empty_ref_val_b"))

        if self.chk_enable_compressor.isChecked():
            pout = self.cb_f_nodes_comp_pout.currentData() or self.cb_f_nodes_comp_pout.currentText().strip()
            if not pout:
                warnings_list.append(tr("mapping.warn_comp_pout"))

        # In campagna (19 giorni non presidiati) NON si mostrano dialoghi
        # modali: un errore reale ferma la campagna in silenzio (loggato dal
        # chiamante), i warning si ignorano.
        if getattr(self, '_campaign_active', False):
            return not errors

        if errors:
            QMessageBox.critical(
                self, tr("mapping.err_missing_data_title"),
                tr("mapping.err_missing_data_prefix")
                + "\n".join(f"\u2022 {e}" for e in errors))
            return False

        if warnings_list:
            reply = QMessageBox.warning(
                self, tr("mapping.warn_check_params_title"),
                tr("mapping.warn_check_params_prefix")
                + "\n\n".join(f"\u26a0 {w}" for w in warnings_list)
                + tr("mapping.warn_check_params_suffix"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        return True

    # ==================================================================
    #  CAMPAGNA MULTI-GIORNO
    #  Esegue in sequenza il batch 24h su tutti i file-giorno di una
    #  cartella (es. i 19 GeoJSON dello Scenario 1). Ogni giorno riusa
    #  l'intero flusso del batch (collasso + 24 ore in parallelo); il
    #  passaggio al giorno dopo avviene alla fine del batch (is_last in
    #  _on_sim_finished). Solo file, niente mappa.
    # ==================================================================
    def _run_campaign(self):
        from pathlib import Path
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QDialogButtonBox, QLabel
        from PyQt5.QtCore import Qt
        from qgis.core import QgsProject

        if getattr(self, '_campaign_active', False):
            self._log_run("Campagna già in corso.", 'orange')
            return

        # La topologia (condotte) resta fissa: serve un layer condotte.
        if not self.chk_already_collapsed.isChecked() and self.cb_pipes.currentData() is None:
            QMessageBox.critical(self, tr("mapping.campaign_title"),
                                 tr("mapping.campaign_need_pipes"))
            return

        start_dir = (getattr(self, '_campaign_last_dir', '')
                     or self.txt_prepare_folder.text().strip() or '')

        # Scelta del metodo di input
        dlg_choice = QDialog(self)
        dlg_choice.setWindowTitle(tr("mapping.campaign_source_title"))
        vbox_choice = QVBoxLayout(dlg_choice)
        vbox_choice.addWidget(QLabel(tr("mapping.campaign_source_question")))
        btn_files = QPushButton(tr("mapping.campaign_btn_files"))
        btn_layers = QPushButton(tr("mapping.campaign_btn_layers"))
        vbox_choice.addWidget(btn_files)
        vbox_choice.addWidget(btn_layers)
        
        choice = []
        def _set_choice(c):
            choice.append(c)
            dlg_choice.accept()
            
        btn_files.clicked.connect(lambda: _set_choice("files"))
        btn_layers.clicked.connect(lambda: _set_choice("layers"))
        
        if dlg_choice.exec_() != QDialog.Accepted or not choice:
            return
            
        input_type = choice[0]
        files = []
        
        if input_type == "files":
            _files, _ = QFileDialog.getOpenFileNames(
                self,
                tr("mapping.campaign_files_dlg_caption"),
                start_dir,
                tr("mapping.campaign_files_filter"))
            if not _files:
                return
            files = sorted(_files)
            self._campaign_last_dir = str(Path(files[0]).parent)
        else:
            dlg_layers = QDialog(self)
            dlg_layers.setWindowTitle(tr("mapping.campaign_layers_title"))
            dlg_layers.resize(400, 300)
            vbox_layers = QVBoxLayout(dlg_layers)
            vbox_layers.addWidget(QLabel(tr("mapping.campaign_layers_hint")))
            list_layers = QListWidget()
            layers_dict = QgsProject.instance().mapLayers()
            for lyr_id, lyr in layers_dict.items():
                if int(lyr.type()) == 0: # 0 = QgsMapLayerType.VectorLayer
                    item = QListWidgetItem(lyr.name())
                    item.setData(Qt.UserRole, lyr.id())
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    list_layers.addItem(item)
            vbox_layers.addWidget(list_layers)
            
            bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bbox.accepted.connect(dlg_layers.accept)
            bbox.rejected.connect(dlg_layers.reject)
            vbox_layers.addWidget(bbox)
            
            if dlg_layers.exec_() != QDialog.Accepted:
                return
                
            for i in range(list_layers.count()):
                item = list_layers.item(i)
                if item.checkState() == Qt.Checked:
                    files.append(item.data(Qt.UserRole))
            
            if not files:
                return
            self._campaign_last_dir = start_dir

        # 2) Cartella di OUTPUT
        base_out = self.txt_prepare_folder.text().strip()
        if not base_out:
            base_out = QFileDialog.getExistingDirectory(
                self, tr("mapping.campaign_out_dir_caption"), self._campaign_last_dir)
            if not base_out:
                return
            self.txt_prepare_folder.setText(base_out)

        def _get_name(x):
            lyr = QgsProject.instance().mapLayer(x)
            if lyr: return lyr.name()
            if isinstance(x, str) and (Path(x).exists() or "/" in x or "\\" in x):
                return Path(x).name
            return str(x)

        _names = "\n".join(f"  • {_get_name(f)}" for f in files[:25])
        _more = "" if len(files) <= 25 else tr("mapping.campaign_more_files", n=len(files) - 25)
        reply = QMessageBox.question(
            self, tr("mapping.campaign_start_title"),
            tr("mapping.campaign_start_msg",
               n_files=len(files), n_sims=len(files) * 24, names=f"{_names}{_more}"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # Stato campagna
        self._campaign_active = True
        self._campaign_files = files
        self._campaign_idx = 0
        self._campaign_summary = []            # (nome, n_conv, launched, failed, elapsed)
        self._campaign_base_out = base_out
        self._campaign_layer_id = None
        self._campaign_start_time = time.time()
        # Forza export-only + 24h; ricorda gli stati per ripristinarli a fine.
        self._campaign_prev_only_export = self.chk_only_export.isChecked()
        self._campaign_prev_sim24 = self.chk_sim_24.isChecked()
        self.chk_only_export.setChecked(True)
        self.chk_sim_24.setChecked(True)

        # FOTOGRAFIA delle mappature dei campi impostate ORA (configurazione che
        # l'utente ha gia' validato con la run singola). Cambiando layer nodi a
        # ogni giorno, i combo dei campi si ripopolano e l'auto-selezione puo'
        # sbagliare (bug: si perdeva 'Totale_Smc' → domanda oraria a zero →
        # compressore mal posto → stallo). Le ri-applichiamo identiche a ogni
        # giorno: i 19 file hanno lo stesso schema, quindi i nomi-campo esistono
        # sempre. Salviamo (currentData, currentText) per i combo editabili.
        self._campaign_field_map = {}
        for _name in ('cb_f_nodes_flow', 'cb_f_nodes_ref',
                      'cb_f_nodes_comp_field', 'cb_f_nodes_comp_pout',
                      'cb_diam_field', 'cb_diam_unit'):
            _cb = getattr(self, _name, None)
            if _cb is not None:
                self._campaign_field_map[_name] = (
                    _cb.currentData(),
                    _cb.currentText() if _cb.isEditable() else None,
                )

        self.txt_log_run.clear()
        self._log_run("=" * 50, 'green')
        self._log_run(tr("mapping.log_campaign_start",
                          ndays=len(files), ntot=len(files) * 24), 'green')
        self._log_run("=" * 50, 'green')
        self._set_buttons_enabled(False)
        self._start_next_campaign_day()

    def _start_next_campaign_day(self):
        from pathlib import Path
        from qgis.core import QgsVectorLayer, QgsProject

        idx = self._campaign_idx
        files = self._campaign_files
        if idx >= len(files):
            self._finalize_campaign()
            return

        path_or_id = files[idx]
        lyr = None
        loaded_from_file = False
        
        existing_lyr = QgsProject.instance().mapLayer(path_or_id)
        if existing_lyr:
            lyr = existing_lyr
            name = lyr.name()
        else:
            name = Path(path_or_id).stem
            lyr = QgsVectorLayer(path_or_id, name, "ogr")
            loaded_from_file = True

        self._campaign_day_name = name
        self._campaign_day_start = time.time()
        self._log_run("", '')
        self._log_run(f"── GIORNO {idx + 1}/{len(files)}: {name} "
                      f"{'─' * 20}", 'green')

        if not lyr or not lyr.isValid():
            self._log_run(f"  ⚠ layer/file non valido, salto: {name}", 'orange')
            self._campaign_summary.append((name, 0, 0, [], 0.0))
            self._campaign_idx += 1
            self._schedule_next_campaign_day()
            return

        if loaded_from_file:
            QgsProject.instance().addMapLayer(lyr)
            self._campaign_layer_id = lyr.id()
            _lyr_id = lyr.id()
        else:
            # Non impostiamo _campaign_layer_id cosi' a fine giorno NON viene rimosso 
            # dal progetto, siccome era gia' presente originariamente.
            self._campaign_layer_id = None
            _lyr_id = lyr.id()
            
        self.reload_layers()
        # Seleziona il layer-giorno come layer nodi (Modalità A). Confronto per
        # ID, NON per identita' (is): QGIS puo' restituire un wrapper Python
        # diverso per lo stesso layer C++, e `is` fallirebbe silenziosamente.
        _sel = False
        for i in range(self.cb_nodes.count()):
            _it = self.cb_nodes.itemData(i)
            if _it is not None and _it.id() == _lyr_id:
                self.cb_nodes.setCurrentIndex(i)
                _sel = True
                break
        if not _sel:
            self._log_run(f"  ⚠ non riesco a selezionare il layer del giorno "
                          f"'{name}' nel combo nodi.", 'orange')
        self._on_nodes_layer_changed(self.cb_nodes.currentIndex())

        # RI-APPLICA le mappature dei campi fotografate all'avvio: cambiando
        # layer l'auto-selezione puo' perdere 'Totale_Smc' (→ domanda a zero).
        for _name, (_data, _text) in getattr(self, '_campaign_field_map', {}).items():
            _cb = getattr(self, _name, None)
            if _cb is None:
                continue
            _done = False
            if _data is not None:
                for i in range(_cb.count()):
                    if _cb.itemData(i) == _data:
                        _cb.setCurrentIndex(i)
                        _done = True
                        break
            if not _done and _text and _cb.isEditable():
                _cb.setEditText(_text)

        # Cartella di output dedicata al giorno.
        day_out = Path(self._campaign_base_out) / name
        try:
            day_out.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        self.txt_prepare_folder.setText(str(day_out))

        # Avvia il batch 24h per questo giorno (riusa tutto il flusso esistente).
        self._run_and_simulate()

    def _schedule_next_campaign_day(self):
        """Passa al giorno dopo sul loop degli eventi (lascia a Qt il tempo di
        distruggere i thread appena terminati)."""
        from qgis.PyQt.QtCore import QTimer
        QTimer.singleShot(50, self._start_next_campaign_day)

    def _finalize_campaign(self):
        from pathlib import Path
        summ = getattr(self, '_campaign_summary', []) or []
        total_elapsed = time.time() - getattr(self, '_campaign_start_time', time.time())
        _mm, _ss = divmod(total_elapsed, 60)
        _hh, _mm = divmod(int(_mm), 60)
        _tstr = (f"{_hh}h {int(_mm):02d}m" if _hh else
                 (f"{int(_mm)}m {int(_ss):02d}s" if _mm else f"{_ss:.1f}s"))

        tot_conv = sum(n for _n, n, _l, _f, _e in summ)
        tot_launched = sum(l for _n, _c, l, _f, _e in summ)
        days_full = sum(1 for _n, c, l, _f, _e in summ if l > 0 and c == l)

        self._log_run("", '')
        self._log_run("=" * 50, 'green')
        self._log_run(tr("mapping.log_campaign_summary_title"), 'green')
        self._log_run("=" * 50, 'green')
        self._log_run(tr("mapping.log_campaign_days_done", n=len(summ)), 'green')
        self._log_run(tr("mapping.log_campaign_days_full", n=days_full, tot=len(summ)),
                      'green' if days_full == len(summ) else 'orange')
        self._log_run(tr("mapping.log_campaign_sims_conv", n=tot_conv, tot=tot_launched),
                      'green' if tot_conv == tot_launched else 'orange')
        for name, n_conv, launched, failed, _e in summ:
            _c = 'green' if (launched > 0 and n_conv == launched) else 'orange'
            _fh = (tr("mapping.log_campaign_not_conv",
                      hours=", ".join(f"h{o}" for o in failed))) if failed else ""
            self._log_run(f"    {name}: {n_conv}/{launched}{_fh}", _c)
        self._log_run(tr("mapping.log_campaign_total_time", t=_tstr), 'green')
        self._log_run("=" * 50, 'green')

        # Ripristina gli stati dei checkbox e la cartella base.
        try:
            self.chk_only_export.setChecked(getattr(self, '_campaign_prev_only_export', False))
            self.chk_sim_24.setChecked(getattr(self, '_campaign_prev_sim24', False))
            self.txt_prepare_folder.setText(getattr(self, '_campaign_base_out', ''))
        except Exception:
            pass
        self._campaign_active = False
        self._set_buttons_enabled(True)

    def _run_and_simulate(self):
        """
        Esporta i CSV e avvia la simulazione.
        Se l'utente ha spuntato 'chk_sim_24', esegue 24 simulazioni in parallelo.
        """
        _in_campaign = getattr(self, '_campaign_active', False)
        if not self._validate_before_run():
            if _in_campaign:
                # Non bloccare la campagna: segna il giorno come fallito e prosegui.
                self._log_run("  ⚠ validazione fallita, giorno saltato.", 'orange')
                self._campaign_summary.append(
                    (getattr(self, '_campaign_day_name', '?'), 0, 0, [], 0.0))
                self._campaign_idx += 1
                self._schedule_next_campaign_day()
            return

        is_parallel = hasattr(self, 'chk_sim_24') and self.chk_sim_24.isChecked()
        from pathlib import Path
        user_folder = self.txt_prepare_folder.text().strip()

        if is_parallel and not user_folder:
            self._log_run("ERRORE: per simulare 24 ore in parallelo devi selezionare una cartella di output.", 'red')
            if _in_campaign:
                self._campaign_summary.append(
                    (getattr(self, '_campaign_day_name', '?'), 0, 0, [], 0.0))
                self._campaign_idx += 1
                self._schedule_next_campaign_day()
            return

        self._set_buttons_enabled(False)
        if not _in_campaign:
            self.txt_log_run.clear()
        
        import time
        self._batch_start_time = time.time()
        
        if is_parallel:
            self._log_run("=" * 50)
            self._log_run(tr("mapping.log_batch24_start"), 'green')
            self._log_run("=" * 50)
            
            phys = self._phys_params()
            # Percorso del _pending_compressors.json creato UNA VOLTA dal
            # collasso di preparazione; verra' copiato in ogni cartella-ora.
            self._batch_pending_json = None
            try:
                from ..gis_integration.network_builder import run_collapse_pipeline, run_nocollapse_pipeline, export_layers_to_csv
                import tempfile

                if not self.chk_already_collapsed.isChecked():
                    pipe_layer = self.cb_pipes.currentData()
                    tmp_out = str(Path(tempfile.mkdtemp(prefix="gasnetsim_pre_")) / "input")
                    
                    _pipeline_fn = run_nocollapse_pipeline if self.chk_no_collapse.isChecked() else run_collapse_pipeline
                    pipes_lyr, nodes_lyr, _, _, warnings = _pipeline_fn(
                        pipe_layer=pipe_layer,
                        out_dir=tmp_out,
                        ora=0,
                        dem_layer=self.cb_dem.currentData(),
                        nodes_layer=self.cb_nodes.currentData(),
                        diam_field=self.cb_diam_field.currentData() or 'Diametro_pollici',
                        diam_unit=self.cb_diam_unit.currentData() or 'in',
                        radius_m=self.spin_radius.value(),
                        log=self._log_prepare,
                        pressure_ref_pa=phys['pressure_ref_pa'],
                        temp_ref_k=phys['temp_ref_k'],
                        roughness_m=phys['roughness_m'],
                        gas_comp_ref=phys['gas_comp_ref'],
                        placeholder_flow=phys['placeholder_flow'],
                        loads_layer=self.cb_nodes.currentData(),
                        loads_field=self.cb_f_nodes_flow.currentData() or '',
                        ref_field=self.cb_f_nodes_ref.currentData() or '',
                        ref_value=self.txt_nodes_ref_val.text().strip(),
                        comp_field=self.cb_f_nodes_comp_field.currentData() or '' if self.chk_enable_compressor.isChecked() else '',
                        comp_value=self.txt_nodes_comp_val.text().strip() if self.chk_enable_compressor.isChecked() else '',
                        comp_pout_field=(self.cb_f_nodes_comp_pout.currentData() or self.cb_f_nodes_comp_pout.currentText().strip()) if self.chk_enable_compressor.isChecked() else '',
                    comp_use_pcm=self.chk_use_pcm.isChecked() if self.chk_enable_compressor.isChecked() else True,
                        flow_sep=self.cb_separator.currentData() or ';',
                    )
                    if warnings:
                        self._show_warnings_dialog(warnings, pipe_layer=pipe_layer)
                    if any('nessun nodo reference' in w.lower() for w in warnings):
                        self._log_prepare("Simulazione bloccata: nessun nodo reference trovato.")
                        self._set_buttons_enabled(True)
                        return

                    # La marcatura compressore e' stata scritta qui dal
                    # collasso: la ricordiamo per copiarla in ogni ora.
                    _pj = Path(tmp_out) / '_pending_compressors.json'
                    if _pj.exists():
                        self._batch_pending_json = str(_pj)

                    # Copia la mappa collasso→fid originali (scritta dal collasso
                    # nella cartella temporanea) nella cartella di output, cosi
                    # resta accessibile: dato un collo di bottiglia sul modello
                    # collassato, dice quali condotte ORIGINALI (fid) modificare.
                    try:
                        import shutil as _sh
                        _cm = Path(tmp_out) / 'collapse_map.csv'
                        if _cm.exists() and user_folder:
                            _sh.copy2(str(_cm), str(Path(user_folder) / 'collapse_map.csv'))
                            self._log_run("Mappa collasso→fid salvata: collapse_map.csv", '')
                    except Exception:
                        pass

                    self._last_orig_pipes_lyr = pipe_layer
                    self._last_orig_nodes_lyr = self.cb_nodes.currentData()
                else:
                    pipes_lyr = self.cb_coll_pipes.currentData()
                    nodes_lyr = self.cb_coll_nodes.currentData()
                    if pipes_lyr is None or nodes_lyr is None:
                        self._log_prepare("ERRORE: seleziona layer condotte E nodi collassati.")
                        self._set_buttons_enabled(True)
                        return
                
                self._last_pipes_lyr = pipes_lyr
                self._last_nodes_lyr = nodes_lyr
                
                self._active_sim_threads = []
                self._active_sim_workers = []   # per il tasto Ferma nel batch
                self._batch_conv = []       # (ora, converged) per il riepilogo finale
                self._batch_launched = 0    # quante ore effettivamente avviate
                self._batch_queue = []      # ore in attesa di uno slot libero (throttling core)
                self._batch_cancelled = False
                self._log_run("Creazione rapida di tutti i CSV in corso...", 'orange')
                # --- FASE 1: Estrazione Dati e Calcolo Carico Orario (Pre-Simulazione) ---
                out_dirs = []
                hourly_loads = []
                
                run_dir, run_label = _next_run_subdir(user_folder)
                run_dir.mkdir(parents=True, exist_ok=True)
                
                for i in range(24):
                    out_input_dir = str(run_dir / f"input_h{i:02d}")
                    out_dirs.append(out_input_dir)
                    
                    if not self.chk_already_collapsed.isChecked():
                        _f_pipe_id = 'pipe_id'
                        _f_node_a = 'node_a'
                        _f_node_b = 'node_b'
                        _f_length = 'length_m'
                        _f_diam = 'diameter_m'
                        _f_diam_unit = 'm'
                        _f_node_id = 'node_id'
                        _f_alt = 'altitude_m'
                        _f_ref_flag = 'matched'
                        _ref_val = '1'
                        _f_flow = 'load_smc_h'
                    else:
                        _f_pipe_id = self.cb_f_pipe_id.currentData() or 'pipe_id'
                        _f_node_a = self.cb_f_node_a.currentData() or 'node_a'
                        _f_node_b = self.cb_f_node_b.currentData() or 'node_b'
                        _f_length = self.cb_f_length.currentData() or 'length_m'
                        _f_diam = self.cb_f_diam.currentData() or 'diameter_m'
                        _f_diam_unit = self.cb_f_diam_unit.currentData() or 'm'
                        _f_node_id = self.cb_f_node_id.currentData() or 'node_id'
                        _f_alt = self.cb_f_altitude.currentData() or 'altitude_m'
                        _f_ref_flag = self.cb_f_ref_flag.currentData() or 'matched'
                        _ref_val = self.txt_ref_value.text().strip() or '1'
                        _f_flow = self.cb_f_flow.currentData() or ''
                    
                    _, _, _, c_ref, _, _ = export_layers_to_csv(
                        pipes_lyr=pipes_lyr, nodes_lyr=nodes_lyr,
                        out_dir=out_input_dir, ora=i,
                        pressure_ref_pa=phys['pressure_ref_pa'],
                        temp_ref_k=phys['temp_ref_k'],
                        gas_comp_ref=phys['gas_comp_ref'],
                        roughness_m=phys['roughness_m'],
                        placeholder_flow=phys['placeholder_flow'],
                        f_pipe_id=_f_pipe_id,
                        f_node_a=_f_node_a,
                        f_node_b=_f_node_b,
                        f_length=_f_length,
                        f_diam=_f_diam,
                        f_diam_unit=_f_diam_unit,
                        f_node_id=_f_node_id,
                        f_altitude=_f_alt,
                        f_ref_flag=_f_ref_flag,
                        ref_flag_value=_ref_val,
                        f_flow=_f_flow,
                        flow_sep=self.cb_separator.currentData() or ';',
                    )
                    
                    if c_ref == 0:
                        self._log_run(f"ERRORE: Ora {i}: 0 nodi reference trovati!", 'red')
                        hourly_loads.append(0.0)
                        continue
                        
                    # Calcolo del carico totale della rete per l'ora corrente (Proxy proxy Cut-in)
                    import pandas as pd
                    try:
                        df_nodes = pd.read_csv(Path(out_input_dir) / 'sf_nodes.csv', sep=';')
                        if 'flow_sm3_per_s' in df_nodes.columns:
                            tot_load = pd.to_numeric(df_nodes['flow_sm3_per_s'], errors='coerce').sum() * 3600.0
                            hourly_loads.append(tot_load)
                        else:
                            hourly_loads.append(0.0)
                    except Exception:
                        hourly_loads.append(0.0)

                # --- FASE 2: Dispatching Day-Ahead (Isteresi MRT e Cut-In) ---
                compressor_schedule = [False] * 24
                if self.chk_enable_compressor.isChecked() and getattr(self, '_batch_pending_json', None):
                    self._log_run("🔧 Calcolo Dispacciamento Day-Ahead: applicazione Isteresi MRT (6h)...", 'orange')
                    UTILIZATION_FACTOR = 0.1152 # Snam 2018 (11.52% annuo)
                    MIN_RUN_TIME = 6
                    
                    sorted_loads = sorted(hourly_loads, reverse=True)
                    target_on_hours = max(1, int(24 * UTILIZATION_FACTOR))
                    cut_in_threshold = sorted_loads[target_on_hours - 1] if sorted_loads else 0
                    
                    hours_left_on = 0
                    for i in range(24):
                        if hourly_loads[i] >= cut_in_threshold and hourly_loads[i] > 0:
                            if hours_left_on == 0:
                                hours_left_on = MIN_RUN_TIME
                        if hours_left_on > 0:
                            compressor_schedule[i] = True
                            hours_left_on -= 1

                    try:
                        ts_path = Path(user_folder) / "enna_timesheet_day_ahead.csv"
                        df_ts = pd.DataFrame({
                            'Hour': range(24),
                            'Total_Load_Smc_h': hourly_loads,
                            'Compressor_ON': compressor_schedule
                        })
                        df_ts.to_csv(ts_path, index=False)
                        self._log_run(f"Timesheet salvato in: {ts_path.name}", 'green')
                    except Exception:
                        pass

                # --- FASE 3: Lancio Simulazioni (throttlato ai core fisici) ---
                # Prima si lanciavano sempre tutte e 24 le ore in un colpo solo,
                # a prescindere dai core disponibili: su macchine con pochi core
                # 24 processi si contendono la CPU e rallentano tutti insieme.
                # Ora si accodano e si lancia solo _max_parallel_sims() alla
                # volta; _on_sim_finished ne fa partire una nuova ogni volta che
                # se ne libera una, mantenendo la concorrenza al massimo utile
                # senza mai superarlo.
                max_parallel = self._max_parallel_sims()
                self._log_run(
                    tr("mapping.log_batch_concurrency",
                       n=max_parallel, logical=os.cpu_count()), '')
                for i in range(24):
                    out_input_dir = out_dirs[i]

                    if self.chk_enable_compressor.isChecked() and getattr(self, '_batch_pending_json', None):
                        if compressor_schedule[i]:
                            try:
                                import shutil
                                _dst = Path(out_input_dir) / '_pending_compressors.json'
                                shutil.copy2(self._batch_pending_json, str(_dst))
                            except Exception as _exc:
                                self._log_run(f"⚠ Ora {i}: impossibile iniettare compressore: {_exc}", 'orange')
                        else:
                            self._log_run(f"  [h{i}] Compressore in BYPASS (Fuori finestra MRT)", '')

                    params_i = self.get_params()
                    params_i['cartella'] = out_input_dir
                    params_i['ora'] = i
                    params_i['is_batch'] = True
                    self._batch_queue.append(params_i)

                self._launch_queued_batch_jobs()
                    
            except Exception as exc:
                import traceback
                self._log_run(f"ERRORE: {exc}", 'red')
                self._log_run(traceback.format_exc(), 'red')
                self._set_buttons_enabled(True)
                
            return

        user_folder = self.txt_prepare_folder.text().strip()
        if user_folder:
            run_dir, run_label = _next_run_subdir(user_folder)
            run_dir.mkdir(parents=True, exist_ok=True)
            out_input_dir = str(run_dir / "input")
        else:
            import tempfile
            run_label = "tmp"
            out_input_dir = str(Path(tempfile.mkdtemp(prefix="gasnetsim_")) / "input")
        self._last_input_dir = out_input_dir  # imposta subito, anche se fallisce

        sim_started = False
        self._set_buttons_enabled(False)
        self.txt_log_run.clear()
        self._log_run(f"(CSV in: {out_input_dir})")
        phys = self._phys_params()
        ora = self.spin_ora.value()

        try:
            from ..gis_integration.network_builder import (
                run_collapse_pipeline, run_nocollapse_pipeline, export_layers_to_csv)
            from qgis.core import QgsProject

            if not self.chk_already_collapsed.isChecked():
                pipe_layer = self.cb_pipes.currentData()
                if pipe_layer is None:
                    self._log_prepare("ERRORE: nessun layer condotte selezionato.")
                    return

                # Salva layer originali per backprojection risultati
                self._last_orig_pipes_lyr = pipe_layer
                self._last_orig_nodes_lyr = self.cb_nodes.currentData()

                _pipeline_fn = run_nocollapse_pipeline if self.chk_no_collapse.isChecked() \
                    else run_collapse_pipeline
                pipes_lyr, nodes_lyr, _, _, warnings = _pipeline_fn(
                    pipe_layer=pipe_layer,
                    out_dir=out_input_dir,
                    ora=ora,
                    dem_layer=self.cb_dem.currentData(),
                    nodes_layer=self.cb_nodes.currentData(),
                    diam_field=self.cb_diam_field.currentData() or 'Diametro_pollici',
                    diam_unit=self.cb_diam_unit.currentData() or 'in',
                    radius_m=self.spin_radius.value(),
                    log=self._log_prepare,
                    pressure_ref_pa=phys['pressure_ref_pa'],
                    temp_ref_k=phys['temp_ref_k'],
                    roughness_m=phys['roughness_m'],
                    gas_comp_ref=phys['gas_comp_ref'],
                    placeholder_flow=phys['placeholder_flow'],
                    loads_layer=self.cb_nodes.currentData(),
                    loads_field=self.cb_f_nodes_flow.currentData() or '',
                    ref_field=self.cb_f_nodes_ref.currentData() or '',
                    ref_value=self.txt_nodes_ref_val.text().strip(),
                    comp_field=self.cb_f_nodes_comp_field.currentData() or '' if self.chk_enable_compressor.isChecked() else '',
                    comp_value=self.txt_nodes_comp_val.text().strip() if self.chk_enable_compressor.isChecked() else '',
                    comp_pout_field=(self.cb_f_nodes_comp_pout.currentData() or self.cb_f_nodes_comp_pout.currentText().strip()) if self.chk_enable_compressor.isChecked() else '',
                    comp_use_pcm=self.chk_use_pcm.isChecked() if self.chk_enable_compressor.isChecked() else True,
                    flow_sep=self.cb_separator.currentData() or ';',
                )
                if warnings:
                    self._show_warnings_dialog(warnings, pipe_layer=pipe_layer)
                self._tab_repair.notify_islands(pipe_layer, warnings)
                if any('nessun nodo reference' in w.lower() for w in warnings):
                    self._log_prepare("Simulazione bloccata: nessun nodo reference trovato.")
                    return
                # Rinomina con numero progressivo
                _n = _next_layer_run_number()
                pipes_lyr.setName(f"Condotte #{_n}")
                nodes_lyr.setName(f"Nodi #{_n}")
                # Registra sempre nel progetto (serve per Modalità B)
                # ma l'utente ha richiesto di RIMUOVERE i layer temporanei per evitare confusione
                # quindi in Modalità Simulazione non li carichiamo in mappa e non passiamo a Mod B.
                # Se l'utente vuole usare la Modalità B manualmente, può usare "Solo Collassa".
                # QgsProject.instance().addMapLayer(pipes_lyr, False)
                # QgsProject.instance().addMapLayer(nodes_lyr, False)
                
                # if add_legend and self.iface is not None:
                #    self.iface.mapCanvas().refresh()
                
                # Pre-seleziona in Modalità B per eventuale ri-simulazione
                # self.chk_already_collapsed.setChecked(True)
                # self._restore(self.cb_coll_pipes, pipes_lyr)
                # self._restore(self.cb_coll_nodes, nodes_lyr)
                # self._on_coll_pipes_changed(self.cb_coll_pipes.currentIndex())
                # self._on_coll_nodes_changed(self.cb_coll_nodes.currentIndex())
            else:
                pipes_lyr = self.cb_coll_pipes.currentData()
                nodes_lyr = self.cb_coll_nodes.currentData()
                if pipes_lyr is None or nodes_lyr is None:
                    self._log_prepare(
                        "ERRORE: seleziona layer condotte E nodi collassati.")
                    return
                _, _, _, c_ref, _, _ = export_layers_to_csv(
                    pipes_lyr=pipes_lyr, nodes_lyr=nodes_lyr,
                    out_dir=out_input_dir, ora=ora,
                    pressure_ref_pa=phys['pressure_ref_pa'],
                    temp_ref_k=phys['temp_ref_k'],
                    gas_comp_ref=phys['gas_comp_ref'],
                    roughness_m=phys['roughness_m'],
                    placeholder_flow=phys['placeholder_flow'],
                    f_pipe_id=self.cb_f_pipe_id.currentData() or 'pipe_id',
                    f_node_a=self.cb_f_node_a.currentData() or 'node_a',
                    f_node_b=self.cb_f_node_b.currentData() or 'node_b',
                    f_length=self.cb_f_length.currentData() or 'length_m',
                    f_diam=self.cb_f_diam.currentData() or 'diameter_m',
                    f_diam_unit=self.cb_f_diam_unit.currentData() or 'm',
                    f_node_id=self.cb_f_node_id.currentData() or 'node_id',
                    f_altitude=self.cb_f_altitude.currentData() or 'altitude_m',
                    f_ref_flag=self.cb_f_ref_flag.currentData() or 'matched',
                    ref_flag_value=self.txt_ref_value.text().strip() or '1',
                    f_flow=self.cb_f_flow.currentData() or '',
                    flow_sep=self.cb_separator.currentData() or ';',
                )
                self._log_prepare(
                    f"Pipe: {pipes_lyr.featureCount()} | "
                    f"Nodi: {nodes_lyr.featureCount()} "
                    f"({c_ref} reference)")
                if c_ref == 0:
                    self._log_prepare(
                        "ERRORE: 0 nodi reference! Verifica il campo 'Flag reference' e il suo valore.")
                    QMessageBox.critical(
                        self, tr("mapping.no_ref_title"),
                        tr("mapping.no_ref_msg"))
                    return

            self._log_prepare("-" * 40)
            self._log_prepare("Avvio simulazione...")
            self._last_input_dir = out_input_dir
            # Memorizza i layer usati per la colorimetria post-simulazione
            self._last_nodes_lyr = nodes_lyr
            self._last_pipes_lyr = pipes_lyr
            params = self.get_params()  # include cartella = out_input_dir
            self._last_run_params = params
            # Avvia simulazione direttamente (simulate_ready connesso a _start_simulation in setup_ui)
            self.simulate_ready.emit(params)
            sim_started = True
            return  # _set_buttons_enabled(True) verra' chiamato da _on_sim_finished

        except Exception as exc:
            import traceback
            self._log_run(f"ERRORE: {exc}", 'red')
            self._log_run(traceback.format_exc(), 'red')
        finally:
            if not sim_started:
                self._set_buttons_enabled(True)

    # ─────────────────────────────────────────────────────────────────────────
    # API pubblica
    # ─────────────────────────────────────────────────────────────────────────

    def set_output_folder(self, folder: str):
        """Imposta la cartella dall'esterno (compatibilita' API)."""
        self._last_input_dir = folder

    def get_params(self) -> dict:
        """Ritorna tutti i parametri per SimWorker + export."""
        phys = self._phys_params()
        cartella = self._last_input_dir or self.txt_prepare_folder.text().strip()
        return {
            'cartella':         cartella,
            'ora':              self.spin_ora.value(),
            'pressure_pa':      phys['pressure_ref_pa'],
            'temperature_k':    phys['temp_ref_k'],
            'junction_flow':    self.spin_jflow.value(),
            'max_iter':         self.spin_maxiter.value(),
            'tol':              self.spin_tol.value(),
            'urf':              self.spin_urf.value(),
            'autocal':          self.chk_autocal.isChecked(),
            'refine':           self.chk_refine.isChecked(),
            'roughness_m':      phys['roughness_m'],
            'placeholder_flow': phys['placeholder_flow'],
            'gas_comp':         phys['gas_comp_ref'],
            'use_subprocess':   self.chk_multiprocess.isChecked(),
            'result_decimals':     self.spin_result_decimals.value(),
            'result_nodes_color':  self.cb_res_nodes_color.currentData(),
            'result_nodes_size':   self.cb_res_nodes_size.currentData(),
            'result_nodes_fields': [fid for fid, cb in self._res_node_checks
                                    if cb.isChecked()],
            'result_pipes_color':  self.cb_res_pipes_color.currentData(),
            'result_pipes_fields': [fid for fid, cb in self._res_pipe_checks
                                    if cb.isChecked()],
            'flow_arrows':         self.chk_flow_arrows.isChecked(),
        }

    # -------------------------------------------------------------------------
    # Simulazione self-contained
    # -------------------------------------------------------------------------

    def _is_sim_thread_running(self) -> bool:
        """True se esiste un QThread di simulazione ancora in esecuzione.

        _on_sim_finished() chiama thread.deleteLater(): l'oggetto C++ viene
        distrutto ma il wrapper Python in self._sim_thread resta appeso, e
        ogni accesso successivo (es. isRunning()) solleva
        RuntimeError: wrapped C/C++ object of type QThread has been deleted.
        Qui intercettiamo quel caso e ripuliamo il riferimento morto.
        """
        thread = getattr(self, '_sim_thread', None)
        if thread is None:
            return False
        try:
            return bool(thread.isRunning())
        except RuntimeError:
            # Oggetto C++ gia' distrutto -> riferimento stantio, lo azzeriamo.
            self._sim_thread = None
            self._sim_worker = None
            return False

    @staticmethod
    def _max_parallel_sims() -> int:
        """Stima quante simulazioni far girare in parallelo nel batch 24 ore.

        os.cpu_count() conta i core LOGICI: su CPU con hyperthreading (quasi
        tutte) sono il doppio dei core fisici. Per un carico CPU-bound come
        Newton-Raphson/numba i due thread di un core fisico si contendono le
        stesse unita' di calcolo, quindi non raddoppiano il throughput reale.
        Euristica: meta' dei core logici (arrotondato per difetto, minimo 1).
        Non e' precisa quanto psutil.cpu_count(logical=False) (non disponibile
        nell'ambiente Python di QGIS), ma evita di aggiungere una dipendenza
        solo per questo.
        """
        n_logical = os.cpu_count() or 4
        return max(1, n_logical // 2)

    def _launch_queued_batch_jobs(self):
        """Lancia simulazioni dalla coda batch (`self._batch_queue`) finche'
        non si raggiunge `_max_parallel_sims()` simulazioni attive insieme.
        Richiamata sia dopo aver accodato le 24 ore sia da _on_sim_finished
        ogni volta che una simulazione libera uno slot, cosi' la concorrenza
        resta sempre al massimo utile senza mai superarlo."""
        if getattr(self, '_batch_cancelled', False):
            return
        max_parallel = self._max_parallel_sims()
        while self._batch_queue and len(self._active_sim_threads) < max_parallel:
            params_i = self._batch_queue.pop(0)
            self._start_simulation(params_i, is_batch=True)
            self._batch_launched += 1

    def _start_simulation(self, params: dict, is_batch=False):
        """Avvia SimWorker in un QThread separato."""
        from .dashboard import SimWorker
        if not is_batch:
            if self._is_sim_thread_running():
                self._log_run("Simulazione già in corso. Attendere.", 'orange')
                return
            self._log_run("=" * 50)
            self._log_run(tr("mapping.log_single_start"))
            self._log_run("=" * 50)
            
        ora = params.get('ora', self.spin_ora.value())
        
        thread = QThread()
        worker = SimWorker(params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        
        def _log_wrap(msg, color='', hr=ora):
            if is_batch:
                self._log_run(f"[h{hr}] {msg}", color)
            else:
                self._log_run(msg, color)
                
        worker.log_line.connect(_log_wrap)
        
        worker.finished.connect(lambda conv, res, t=thread, w=worker, hr=ora, b=is_batch: self._on_sim_finished(conv, res, t, w, hr, b))
        
        if is_batch:
            if not hasattr(self, '_active_sim_threads'):
                self._active_sim_threads = []
            if not hasattr(self, '_active_sim_workers'):
                self._active_sim_workers = []
            self._active_sim_threads.append(thread)
            self._active_sim_workers.append(worker)   # tracciato per il tasto Ferma
        else:
            self._sim_thread = thread
            self._sim_worker = worker

        # Abilita Ferma mentre gira (sia corsa singola sia batch).
        if hasattr(self, 'btn_stop_sim'):
            self.btn_stop_sim.setEnabled(True)

        thread.start()

    def _stop_simulation(self):
        """Interrompe la/e simulazione/i in corso (uccide i sottoprocessi)."""
        self._log_run("⏹ Interruzione richiesta: chiusura dei processi...", 'orange')
        self._batch_cancelled = True
        # Svuota la coda: le ore non ancora avviate non partiranno piu'.
        self._batch_queue = []
        # Ferma anche la campagna: niente passaggio al giorno successivo.
        if getattr(self, '_campaign_active', False):
            self._campaign_active = False
            self._log_run("⏹ Campagna interrotta dall'utente.", 'orange')
            try:
                self.chk_only_export.setChecked(getattr(self, '_campaign_prev_only_export', False))
                self.chk_sim_24.setChecked(getattr(self, '_campaign_prev_sim24', False))
                self.txt_prepare_folder.setText(getattr(self, '_campaign_base_out', ''))
            except Exception:
                pass
        n = 0
        worker = getattr(self, '_sim_worker', None)
        if worker is not None:
            try:
                worker.cancel()
                n += 1
            except Exception:
                pass
        # Worker del batch (24 processi paralleli): ora sono tracciati.
        for w in getattr(self, '_active_sim_workers', []):
            try:
                w.cancel()
                n += 1
            except Exception:
                pass
        self._log_run(f"⏹ Segnale di stop inviato a {n} processo/i.", 'orange')
        if hasattr(self, 'btn_stop_sim'):
            self.btn_stop_sim.setEnabled(False)

    def _on_sim_finished(self, converged: bool, result, thread=None, worker=None, ora=None, is_batch=False):
        """Chiamato da SimWorker al termine: applica colorimetria ed emette simulation_done."""
        # Simulazione finita (o interrotta): il pulsante Ferma non serve piu'.
        if not is_batch and hasattr(self, 'btn_stop_sim'):
            self.btn_stop_sim.setEnabled(False)

        # Registra l'esito di convergenza di questa ora per il riepilogo batch.
        if is_batch:
            if not hasattr(self, '_batch_conv') or self._batch_conv is None:
                self._batch_conv = []
            self._batch_conv.append((ora, bool(converged)))

        is_last = False
        if thread is not None:
            thread.quit()
            thread.wait()
            worker.deleteLater()
            thread.deleteLater()

            # deleteLater() distrugge l'oggetto C++: se questo e' il thread
            # non-batch corrente dobbiamo azzerare i riferimenti, altrimenti
            # al lancio successivo self._sim_thread.isRunning() solleva
            # RuntimeError (wrapped C/C++ object has been deleted).
            if thread is getattr(self, '_sim_thread', None):
                self._sim_thread = None
                self._sim_worker = None

            if is_batch and hasattr(self, '_active_sim_threads'):
                if thread in self._active_sim_threads:
                    self._active_sim_threads.remove(thread)
                # Slot appena liberato: fa partire la prossima ora in coda,
                # se ce ne sono ancora (mantiene la concorrenza al massimo).
                if getattr(self, '_batch_queue', None):
                    self._launch_queued_batch_jobs()
                if len(self._active_sim_threads) == 0 and not getattr(self, '_batch_queue', []):
                    is_last = True
        elif self._sim_thread is not None:
            try:
                self._sim_thread.quit()
                self._sim_thread.wait()
            except RuntimeError:
                pass
            self._sim_thread = None
            self._sim_worker = None
            
        # Gestione opzione Solo Export
        if self.chk_only_export.isChecked():
            if is_batch:
                self._log_run(f"[h{ora}] Export CSV completato.", "green")
            else:
                self._log_run("Export CSV completato (caricamento mappa saltato).", "green")
        elif result is not None:
            nodes_lyr = self._last_nodes_lyr
            pipes_lyr = self._last_pipes_lyr
            params = self._last_run_params or {}
            if nodes_lyr is not None or pipes_lyr is not None:
                try:
                    from ..gis_integration.result_visualizer import apply_results_to_layers
                    res_nodes, res_pipes = apply_results_to_layers(
                        result=result,
                        nodes_lyr=nodes_lyr,
                        pipes_lyr=pipes_lyr,
                        log=lambda msg: self._log_run(f"[h{ora}] {msg}" if is_batch else msg, 'green'),
                        result_nodes_color=params.get('result_nodes_color', 'pressure_bar'),
                        result_nodes_size=params.get('result_nodes_size') or None,
                        result_nodes_fields=params.get('result_nodes_fields') or None,
                        result_pipes_color=params.get('result_pipes_color', 'flow_abs_sm3h'),
                        result_pipes_fields=params.get('result_pipes_fields') or None,
                        flow_arrows=params.get('flow_arrows', True),
                        decimals=params.get('result_decimals', 4),
                        orig_nodes_lyr=self._last_orig_nodes_lyr,
                        orig_pipes_lyr=self._last_orig_pipes_lyr,
                        show_orig_pipes_layer=self.chk_show_orig_pipes.isChecked(),
                    )
                    if self.iface is not None:
                        self.iface.mapCanvas().refresh()
                    # I GPKG vanno nella STESSA cartella h<NN>_<ESITO> dei CSV.
                    # `result` è la cartella di output restituita dal worker
                    # (già organizzata per ora ed esito): CSV e GPKG insieme, e
                    # il nome della cartella marca l'esito. Nessun suffisso: ogni
                    # ora ha la propria cartella, quindi niente collisioni fra i
                    # 24 processi del batch.
                    out_dir = str(result) if result else self.txt_prepare_folder.text().strip()
                    if out_dir:
                        if res_nodes is not None:
                            res_nodes = self._persist_result_layer(res_nodes, out_dir, "")
                        if res_pipes is not None:
                            res_pipes = self._persist_result_layer(res_pipes, out_dir, "")
                        if self.iface is not None:
                            self.iface.mapCanvas().refresh()
                    self._refresh_viz_combos()
                    self._select_viz_results(
                        res_nodes, res_pipes,
                        params.get('result_nodes_color', 'pressure_bar'),
                        params.get('result_pipes_color', 'flow_abs_sm3h'),
                    )
                    if not is_batch:
                        self.tabs.setCurrentIndex(2)
                except Exception as exc:
                    import traceback
                    self._log_run(f"Colorimetria: {exc}", 'orange')
        
        if not is_batch:
            self.simulation_done.emit(converged, result)
            self._set_buttons_enabled(True)
        else:
            if is_last:
                import time
                elapsed = time.time() - getattr(self, '_batch_start_time', time.time())
                conv = getattr(self, '_batch_conv', []) or []
                launched = getattr(self, '_batch_launched', len(conv)) or len(conv)
                n_conv = sum(1 for _o, c in conv if c)
                failed_hours = sorted(o for o, c in conv if not c and o is not None)
                skipped = 24 - launched
                _mm, _ss = divmod(elapsed, 60)
                _tstr = f"{int(_mm)}m {int(_ss):02d}s" if _mm >= 1 else f"{_ss:.1f}s"
                all_ok = (n_conv == launched and launched > 0)
                _c = "green" if all_ok else "orange"

                self._log_run("=" * 50, _c)
                self._log_run(tr("mapping.log_batch24_summary_title"), _c)
                self._log_run("=" * 50, _c)
                self._log_run(tr("mapping.log_batch24_converged", n=n_conv, tot=launched), _c)
                if failed_hours:
                    _fh = ", ".join(f"h{o}" for o in failed_hours)
                    self._log_run(tr("mapping.log_batch24_not_converged", hours=_fh), "orange")
                    self._log_run(tr("mapping.log_batch24_not_converged_note1"), "orange")
                    self._log_run(tr("mapping.log_batch24_not_converged_note2"), "orange")
                if skipped > 0:
                    self._log_run(tr("mapping.log_batch24_skipped", n=skipped), "orange")
                self._log_run(tr("mapping.log_batch24_total_time", t=_tstr), _c)
                self._log_run("=" * 50, _c)

                # --- _RIEPILOGO.csv nella cartella del giorno/batch -----------
                # Una riga per ora: ora, esito (OK/NONCONV), converso. La
                # cartella e' quella di output corrente (il giorno in campagna,
                # la base nel batch normale).
                try:
                    from pathlib import Path
                    import csv as _csv
                    _root = self.txt_prepare_folder.text().strip()
                    if _root:
                        _rc = sorted((o, c) for o, c in conv if o is not None)
                        with open(str(Path(_root) / '_RIEPILOGO.csv'),
                                  'w', newline='', encoding='utf-8') as _fh:
                            _w = _csv.writer(_fh, delimiter=';')
                            _w.writerow(['ora', 'esito', 'converso'])
                            for _o, _cc in _rc:
                                _w.writerow([f"h{_o:02d}",
                                             'OK' if _cc else 'NONCONV',
                                             1 if _cc else 0])
                            _w.writerow([])
                            _w.writerow(['TOTALE', f"{n_conv}/{launched}",
                                         'tutte OK' if all_ok else 'verificare NONCONV'])
                except Exception:
                    pass

                # --- Campagna: registra il giorno e passa al successivo -------
                if getattr(self, '_campaign_active', False):
                    day_name = getattr(self, '_campaign_day_name', '?')
                    self._campaign_summary.append(
                        (day_name, n_conv, launched, failed_hours, elapsed))
                    self._log_run(
                        f"  → Giorno '{day_name}': {n_conv}/{launched} converse.",
                        _c)
                    # Rimuovi il layer-giorno dal progetto (evita accumulo).
                    try:
                        from qgis.core import QgsProject
                        _lid = getattr(self, '_campaign_layer_id', None)
                        if _lid:
                            QgsProject.instance().removeMapLayer(_lid)
                            self._campaign_layer_id = None
                    except Exception:
                        pass
                    self._campaign_idx += 1
                    self._schedule_next_campaign_day()
                    return

                self.simulation_done.emit(all_ok, None)
                self._set_buttons_enabled(True)

    def _persist_result_layer(self, lyr, out_dir: str, unique_suffix: str = ""):
        """Salva il layer in memoria come GeoPackage nella cartella out_dir.
        Copia lo stile, rimuove il layer temporaneo dal progetto e carica
        quello su file. Restituisce il nuovo layer (o l'originale se fallisce).
        unique_suffix (es. 'h08') viene aggiunto al nome del file per evitare
        collisioni fra i processi paralleli del batch."""
        try:
            import re as _re
            from pathlib import Path
            from qgis.core import (
                QgsProject, QgsVectorFileWriter,
                QgsCoordinateTransformContext, QgsVectorLayer,
            )
            safe_name = _re.sub(r'[^\w\-]', '_', lyr.name()).strip('_')
            if unique_suffix:
                safe_name = f"{safe_name}_{unique_suffix}"
            gpkg_path = str(Path(out_dir) / f"{safe_name}.gpkg")
            
            if Path(gpkg_path).exists():
                try:
                    Path(gpkg_path).unlink()
                except Exception:
                    pass

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.fileEncoding = "UTF-8"
            options.layerName = safe_name

            error, msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
                lyr, gpkg_path, QgsCoordinateTransformContext(), options)
            if error != QgsVectorFileWriter.NoError:
                self._log_run(f"⚠ Salvataggio '{lyr.name()}' fallito: {msg}", 'orange')
                return lyr

            # Clona renderer per preservare lo stile
            renderer_clone = lyr.renderer().clone() if lyr.renderer() else None

            # Rimuovi il layer in memoria
            layer_name = lyr.name()
            QgsProject.instance().removeMapLayer(lyr.id())

            # Carica il file GeoPackage
            new_lyr = QgsVectorLayer(
                f"{gpkg_path}|layername={safe_name}", layer_name, "ogr")
            if not new_lyr.isValid():
                self._log_run(f"⚠ GeoPackage scritto ma non ricaricato: {gpkg_path}", 'orange')
                return lyr
            if renderer_clone:
                new_lyr.setRenderer(renderer_clone)
            QgsProject.instance().addMapLayer(new_lyr)
            self._log_run(f"💾 Salvato: {gpkg_path}", 'green')
            return new_lyr
        except Exception as exc:
            self._log_run(f"⚠ Errore salvataggio layer: {exc}", 'orange')
            return lyr

    def _on_layer_verified(self, layer):
        """Seleziona il layer verificato nel combo condotte di Tab 1 e switcha."""
        if layer is None:
            return
        self.reload_layers()
        for i in range(self.cb_pipes.count()):
            if self.cb_pipes.itemData(i) is layer:
                self.cb_pipes.setCurrentIndex(i)
                break
        # Popola anche il combo nodi dal layer selezionato in Tab 0
        nodes_lyr = self._tab_repair.cb_nodes.currentData()
        if nodes_lyr is not None:
            for i in range(self.cb_nodes.count()):
                if self.cb_nodes.itemData(i) is nodes_lyr:
                    self.cb_nodes.setCurrentIndex(i)
                    break
        self.tabs.setCurrentIndex(1)

    def _on_analysis_ok(self, pipes_lyr, nodes_lyr):
        """Pre-popola i combo di Tab 1 dopo analisi senza problemi topologici."""
        self.reload_layers()
        # Seleziona condotte
        for i in range(self.cb_pipes.count()):
            if self.cb_pipes.itemData(i) is pipes_lyr:
                self.cb_pipes.setCurrentIndex(i)
                break
        # Seleziona nodi (se disponibile)
        if nodes_lyr is not None:
            for i in range(self.cb_nodes.count()):
                if self.cb_nodes.itemData(i) is nodes_lyr:
                    self.cb_nodes.setCurrentIndex(i)
                    break

    # -------------------------------------------------------------------------
    # Tab 2 – Viz helpers
    # -------------------------------------------------------------------------

    def _select_viz_results(self, res_nodes, res_pipes, nodes_color, pipes_color):
        """Dopo la simulazione: seleziona i layer risultato e i campi di colore nel tab Viz."""
        def _sel_layer(combo, lyr):
            if lyr is None:
                return False
            lyr_id = lyr.id()
            for i in range(combo.count()):
                if combo.itemData(i) == lyr_id:
                    combo.setCurrentIndex(i)
                    return True
            return False

        def _sel_field(combo, field_id):
            for i in range(combo.count()):
                if combo.itemData(i) == field_id:
                    combo.setCurrentIndex(i)
                    return

        if _sel_layer(self.cb_viz_nodes_lyr, res_nodes):
            self._on_viz_nodes_lyr_changed()
            _sel_field(self.cb_viz_nodes_field, nodes_color)
        if _sel_layer(self.cb_viz_pipes_lyr, res_pipes):
            self._on_viz_pipes_lyr_changed()
            _sel_field(self.cb_viz_pipes_field, pipes_color)

    def _refresh_viz_combos(self):
        """Aggiorna i combo layer nella tab Visualizzazione Risultati.
        Mostra solo i layer vettoriali presenti nella legenda: R-N-/R-P- in cima,
        poi tutti gli altri per geometria (punti -> nodi, linee -> condotte)."""
        try:
            from qgis.core import QgsProject, QgsWkbTypes, QgsMapLayer
            proj = QgsProject.instance()
            tree_ids = {n.layerId() for n in proj.layerTreeRoot().findLayers()}
            
            nodes_res, nodes_other = [], []
            pipes_res, pipes_other = [], []
            for lyr in proj.mapLayers().values():
                if lyr.id() not in tree_ids:
                    continue
                if lyr.type() != QgsMapLayer.VectorLayer:
                    continue
                # Salta layer non validi (es. sorgente cancellata, simulazioni pregresse)
                if not lyr.isValid():
                    continue
                # Salta layer senza features (layer vuoti o placeholder)
                try:
                    if lyr.featureCount() == 0:
                        continue
                except Exception:
                    continue
                try:
                    gt = lyr.geometryType()
                    is_res = lyr.name().startswith('R-N-') or lyr.name().startswith('R-P-')
                    if gt == QgsWkbTypes.PointGeometry:
                        (nodes_res if is_res else nodes_other).append(lyr)
                    elif gt == QgsWkbTypes.LineGeometry:
                        (pipes_res if is_res else pipes_other).append(lyr)
                except Exception:
                    pass

            nodes_lyrs = sorted(nodes_res, key=lambda l: l.name()) + \
                         sorted(nodes_other, key=lambda l: l.name())
            pipes_lyrs = sorted(pipes_res, key=lambda l: l.name()) + \
                         sorted(pipes_other, key=lambda l: l.name())

            def _fill(combo, layers):
                prev = combo.currentData()
                combo.blockSignals(True)
                combo.clear()
                combo.addItem(tr("mapping.none_item"), None)
                for l in layers:
                    combo.addItem(l.name(), l.id())
                combo.blockSignals(False)
                if prev:
                    for i in range(combo.count()):
                        if combo.itemData(i) == prev:
                            combo.setCurrentIndex(i)
                            return
                combo.currentIndexChanged.emit(combo.currentIndex())

            _fill(self.cb_viz_nodes_lyr, nodes_lyrs)
            _fill(self.cb_viz_pipes_lyr, pipes_lyrs)
            all_lyrs = sorted(nodes_lyrs + pipes_lyrs, key=lambda l: l.name())
            _fill(self.cb_viz_export_lyr, all_lyrs)
            self._on_viz_nodes_lyr_changed()
            self._on_viz_pipes_lyr_changed()
        except Exception:
            pass

    def _on_viz_nodes_lyr_changed(self):
        _node_candidates = [
            ('pressure_bar', tr("mapping.fs_pressure")), ('volumetric_flow_sm3s', tr("mapping.fs_vol_flow")),
            ('energy_flow_mw', tr("mapping.fs_energy_flow")), ('temperature_k', tr("mapping.fs_temp")),
            ('sp_gravity', tr("mapping.fs_sp_gravity")), ('z_factor', tr("mapping.f_z_factor")),
            ('hhv_mj_sm3', tr("mapping.fs_hhv")), ('wobbe_mj_sm3', tr("mapping.fs_wobbe")),
            ('density_kg_m3', tr("mapping.fs_density")), ('std_density_kg_sm3', tr("mapping.fs_std_density")),
            ('molar_mass', tr("mapping.fs_mm")), ('h2_pct', tr("mapping.f_h2_pct")),
            ('throughput_sm3h', tr("mapping.fs_throughput"))]
        self._fill_viz_field_combo(
            self.cb_viz_nodes_field, self.cb_viz_nodes_lyr, _node_candidates)
        # Combo dimensione: stesse opzioni + "-- nessuno --" in testa
        prev_size = self.cb_viz_nodes_size.currentData()
        self.cb_viz_nodes_size.blockSignals(True)
        self.cb_viz_nodes_size.clear()
        self.cb_viz_nodes_size.addItem(tr("mapping.none_item"), None)
        lyr_id = self.cb_viz_nodes_lyr.currentData()
        if lyr_id:
            try:
                from qgis.core import QgsProject
                lyr = QgsProject.instance().mapLayer(lyr_id)
                if lyr:
                    lyr_fields = {f.name() for f in lyr.fields()}
                    for fid, flabel in _node_candidates:
                        if fid in lyr_fields:
                            self.cb_viz_nodes_size.addItem(flabel, fid)
            except Exception:
                pass
        self.cb_viz_nodes_size.blockSignals(False)
        if prev_size:
            for i in range(self.cb_viz_nodes_size.count()):
                if self.cb_viz_nodes_size.itemData(i) == prev_size:
                    self.cb_viz_nodes_size.setCurrentIndex(i)
                    break

    def _on_viz_pipes_lyr_changed(self):
        self._fill_viz_field_combo(
            self.cb_viz_pipes_field, self.cb_viz_pipes_lyr,
            [('flow_abs_sm3h', tr("mapping.fps_flow_abs")), ('flow_sm3h', tr("mapping.fps_flow_signed")),
             ('velocity_m_s', tr("mapping.fps_velocity")), ('avg_pressure_bar', tr("mapping.fps_avg_pressure")),
             ('sp_gravity', tr("mapping.fs_sp_gravity")), ('z_factor', tr("mapping.f_z_factor")),
             ('density_kg_m3', tr("mapping.fps_density"))])

    def _fill_viz_field_combo(self, field_combo, lyr_combo, candidates):
        """Popola field_combo con i campi risultato noti del layer.
        Se nessun campo noto è presente (es. layer non-risultato), mostra
        tutti i campi numerici del layer come fallback."""
        prev = field_combo.currentData()
        field_combo.blockSignals(True)
        field_combo.clear()
        lyr_id = lyr_combo.currentData()
        if lyr_id:
            try:
                from qgis.core import QgsProject
                from PyQt5.QtCore import QVariant
                lyr = QgsProject.instance().mapLayer(lyr_id)
                if lyr:
                    lyr_fields = {f.name() for f in lyr.fields()}
                    # Prima prova i campi risultato noti
                    added = []
                    for fid, flabel in candidates:
                        if fid in lyr_fields:
                            field_combo.addItem(flabel, fid)
                            added.append(fid)
                    # Fallback: se nessun campo risultato trovato, mostra tutti i numerici
                    if not added:
                        _numeric = {QVariant.Int, QVariant.LongLong,
                                    QVariant.Double, QVariant.UInt, QVariant.ULongLong}
                        for f in lyr.fields():
                            if f.type() in _numeric:
                                field_combo.addItem(f.name(), f.name())
            except Exception:
                pass
        field_combo.blockSignals(False)
        if prev:
            for i in range(field_combo.count()):
                if field_combo.itemData(i) == prev:
                    field_combo.setCurrentIndex(i)
                    return

    def _apply_viz_recolor(self):
        """Applica colorimetria ai layer [Risultati] selezionati senza ri-simulare."""
        try:
            from ..gis_integration.result_visualizer import recolor_result_layer
            from qgis.core import QgsProject
        except ImportError:
            return
        lyr_id = self.cb_viz_nodes_lyr.currentData()
        if lyr_id:
            lyr = QgsProject.instance().mapLayer(lyr_id)
            field = self.cb_viz_nodes_field.currentData()
            if lyr and field:
                size_field = self.cb_viz_nodes_size.currentData() or None
                recolor_result_layer(lyr, field, add_arrows=False, size_field=size_field)
        lyr_id = self.cb_viz_pipes_lyr.currentData()
        if lyr_id:
            lyr = QgsProject.instance().mapLayer(lyr_id)
            field = self.cb_viz_pipes_field.currentData()
            if lyr and field:
                recolor_result_layer(lyr, field,
                                     add_arrows=self.chk_viz_arrows.isChecked())
        try:
            if self.iface is not None:
                self.iface.mapCanvas().refresh()
        except Exception:
            pass

    def _export_viz_csv(self):
        """Esporta il layer [Risultati] selezionato in un file CSV."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        lyr_id = self.cb_viz_export_lyr.currentData()
        if not lyr_id:
            QMessageBox.warning(self, tr("mapping.export_no_layer_title"),
                                tr("mapping.export_no_layer_msg"))
            return
        try:
            from qgis.core import QgsProject
            lyr = QgsProject.instance().mapLayer(lyr_id)
        except Exception:
            lyr = None
        if lyr is None:
            QMessageBox.warning(self, tr("mapping.export_layer_not_found_title"),
                                tr("mapping.export_layer_not_found_msg"))
            return
        default_name = (lyr.name().replace('R-N-', '').replace('R-P-orig-', '').replace('R-P-', '')).replace(' ', '_') + '.csv'
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr("mapping.export_csv_dialog_title"), default_name, "CSV (*.csv)")
        if not filepath:
            return
        decimals = self.spin_viz_decimals.value()
        try:
            from ..gis_integration.result_visualizer import export_layer_to_csv
            export_layer_to_csv(lyr, filepath, decimals)
            QMessageBox.information(
                self, tr("mapping.export_done_title"),
                tr("mapping.export_done_msg", decimals=decimals, filepath=filepath))
        except Exception as e:
            QMessageBox.critical(self, tr("mapping.export_error_title"), str(e))
