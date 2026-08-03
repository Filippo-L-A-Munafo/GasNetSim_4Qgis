# -*- coding: utf-8 -*-
"""
Tab 0 — Verifica Condotte
Analisi topologica, snap endpoint e gestione isole.
Widget autonomo: si connette direttamente ai segnali di QgsProject.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QComboBox, QPushButton, QTextEdit,
    QRadioButton, QButtonGroup, QDoubleSpinBox, QCheckBox,
    QScrollArea, QMessageBox, QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor

from .i18n import tr, register

register({
    "verifica.layer_group": {"it": "Layer", "en": "Layer"},
    "verifica.pipes_row": {"it": "Condotte:", "en": "Pipelines:"},
    "verifica.none_item": {"it": "-- nessuno --", "en": "-- none --"},
    "verifica.nodes_row": {"it": "Nodi (opz.):", "en": "Nodes (opt.):"},
    "verifica.nodes_tooltip": {
        "it": "Layer di nodi opzionale.\n"
              "Se selezionato, lo snap aggancia gli endpoint delle condotte\n"
              "ai nodi esistenti entro la tolleranza (priorità sul centroide).",
        "en": "Optional node layer.\n"
              "If selected, snapping attaches pipeline endpoints to existing\n"
              "nodes within tolerance (takes priority over the centroid).",
    },
    "verifica.analysis_group": {"it": "1. Analisi rete", "en": "1. Network analysis"},
    "verifica.analysis_desc": {
        "it": "Rileva: geometrie nulle · duplicati · condotte sconnesse (isole).\n"
              "Non modifica nulla — solo lettura.",
        "en": "Detects: null geometries · duplicates · disconnected pipelines (islands).\n"
              "Does not modify anything — read-only.",
    },
    "verifica.auto_color": {
        "it": "Crea layer colorato automaticamente se isole trovate",
        "en": "Automatically create a coloured layer if islands are found",
    },
    "verifica.analyze_button": {"it": "\U0001f50d  Analizza rete", "en": "\U0001f50d  Analyze network"},
    "verifica.select_bad_button": {"it": "⚠  Seleziona problematici", "en": "⚠  Select problem pipelines"},
    "verifica.select_bad_tooltip": {
        "it": "Seleziona nel layer condotte le pipe duplicate o sovrapposte\n"
              "rilevate dall'ultima analisi.",
        "en": "Selects the duplicate or overlapping pipelines found by the\n"
              "last analysis in the pipelines layer.",
    },
    "verifica.snap_group": {"it": "2. Snap endpoint", "en": "2. Snap endpoints"},
    "verifica.snap_desc": {
        "it": "Unisce endpoint entro la tolleranza.\n"
              "Se un layer nodi è selezionato, ha priorità sul centroide pipe-to-pipe.",
        "en": "Merges endpoints within tolerance.\n"
              "If a node layer is selected, it takes priority over the pipe-to-pipe centroid.",
    },
    "verifica.tolerance_row": {"it": "Tolleranza:", "en": "Tolerance:"},
    "verifica.tolerance_tooltip": {
        "it": "Distanza massima (unità del CRS) entro cui due endpoint vengono uniti.\n"
              "Per CRS in gradi usa valori piccoli (es. 0.0001 ≈ 11 m).",
        "en": "Maximum distance (CRS units) within which two endpoints are merged.\n"
              "For degree-based CRS use small values (e.g. 0.0001 ≈ 11 m).",
    },
    "verifica.strategy_centroid": {
        "it": "Punto medio  (tutti gli endpoint del cluster → centroide)",
        "en": "Midpoint  (all endpoints in the cluster → centroid)",
    },
    "verifica.strategy_first": {
        "it": "Ancora al primo  (un endpoint rimane fisso, gli altri si avvicinano)",
        "en": "Anchor to first  (one endpoint stays fixed, the others move to it)",
    },
    "verifica.strategy_row": {"it": "Strategia:", "en": "Strategy:"},
    "verifica.output_new_layer": {
        "it": "Crea nuovo layer  (copia snappata aggiunta al progetto)",
        "en": "Create new layer  (snapped copy added to the project)",
    },
    "verifica.output_overwrite": {
        "it": "Modifica layer originale  (⚠ irreversibile se su file)",
        "en": "Modify original layer  (⚠ irreversible if file-based)",
    },
    "verifica.output_row": {"it": "Output:", "en": "Output:"},
    "verifica.snap_button": {"it": "⚡  Applica snap", "en": "⚡  Apply snap"},
    "verifica.islands_group": {"it": "3. Isole e ri-analisi", "en": "3. Islands and re-analysis"},
    "verifica.islands_desc": {
        "it": "Attivo dopo ‘Analizza’ se ci sono componenti sconnesse.\n"
              "Seleziona o visualizza le isole, intervieni manualmente nel canvas,\n"
              "poi ri-analizza per verificare il risultato.",
        "en": "Enabled after ‘Analyze’ if there are disconnected components.\n"
              "Select or view the islands, fix them manually on the canvas,\n"
              "then re-analyze to check the result.",
    },
    "verifica.select_islands_button": {"it": "⚠  Seleziona isole", "en": "⚠  Select islands"},
    "verifica.select_islands_tooltip": {
        "it": "Seleziona nel layer sorgente le condotte\n"
              "appartenenti a componenti sconnesse dalla rete principale.",
        "en": "Selects, in the source layer, the pipelines\n"
              "belonging to components disconnected from the main network.",
    },
    "verifica.color_islands_button": {"it": "\U0001f3a8  Crea layer colorato", "en": "\U0001f3a8  Create coloured layer"},
    "verifica.color_islands_tooltip": {
        "it": "Crea un layer temporaneo in cui ogni isola\n"
              "è colorata con un colore diverso per distinguerle visivamente.",
        "en": "Creates a temporary layer where each island\n"
              "is coloured differently so they can be told apart visually.",
    },
    "verifica.reanalyze_button": {"it": "\U0001f50d  Ri-analizza rete corrente", "en": "\U0001f50d  Re-analyze current network"},
    "verifica.reanalyze_tooltip": {
        "it": "Ri-analizza il layer risultato dell'ultimo snap (se esiste),\n"
              "altrimenti il layer selezionato nel combo condotte.\n"
              "I combo restano modificabili per scegliere un layer diverso.",
        "en": "Re-analyzes the layer resulting from the last snap (if any),\n"
              "otherwise the layer selected in the pipelines combo.\n"
              "The combos stay editable to pick a different layer.",
    },
    "verifica.log_label": {"it": "Log:", "en": "Log:"},
    "verifica.clear_log_action": {"it": "\U0001f5d1  Svuota log", "en": "\U0001f5d1  Clear log"},
    "verifica.overwrite_confirm_title": {
        "it": "Conferma modifica layer originale",
        "en": "Confirm original layer modification",
    },
    "verifica.overwrite_confirm_msg": {
        "it": "Stai per modificare direttamente '{layer_name}'.\n"
              "Se il layer è su file, l'operazione NON può essere annullata.\n\n"
              "Continuare?",
        "en": "You are about to directly modify '{layer_name}'.\n"
              "If the layer is file-based, this operation CANNOT be undone.\n\n"
              "Continue?",
    },
})


class VerificaTab(QWidget):
    """Tab autonomo per la verifica e riparazione delle condotte."""

    layer_verified = pyqtSignal(object)           # emesso dopo snap riuscito: (new_layer)
    analysis_ok    = pyqtSignal(object, object)   # emesso dopo analisi senza problemi: (pipes_lyr, nodes_lyr)
    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self._last_island_fids = []
        self._last_island_source_lyr = None
        self._last_snap_layer = None      # layer risultato dell'ultimo snap
        self._last_problem_ids = set()    # ID originali condotte problematiche (dup/overlap)
        self._last_problem_pipe_lyr = None  # layer sorgente per selezione problematici
        self._proj_connections = []       # segnali QgsProject da disconnettere
        self._build_ui()
        self._connect_project_signals()

    # ── Segnali progetto ─────────────────────────────────────────────────────

    def _connect_project_signals(self):
        try:
            from qgis.core import QgsProject
            proj = QgsProject.instance()
            self._proj_connections = [
                proj.layersAdded.connect(lambda _: self._refresh_combos()),
                proj.layersRemoved.connect(lambda _: self._refresh_combos()),
            ]
            self._refresh_combos()
        except Exception:
            pass

    def _refresh_combos(self):
        """Aggiorna i combo con i layer del progetto corrente.
        Mostra solo i layer visibili nella legenda (layer-tree),
        escludendo quelli aggiunti al registro ma nascosti (es. Condotte #N)."""
        try:
            from qgis.core import QgsProject, QgsWkbTypes
            proj = QgsProject.instance()
            # Filtra: solo layer presenti nell'albero della legenda
            tree_ids = {n.layerId() for n in proj.layerTreeRoot().findLayers()}
            all_layers = [
                l for l in proj.mapLayers().values()
                if l.id() in tree_ids
            ]
            line_lys = [
                l for l in all_layers
                if hasattr(l, 'wkbType') and
                QgsWkbTypes.geometryType(l.wkbType()) == QgsWkbTypes.LineGeometry
            ]
            pt_lys = [
                l for l in all_layers
                if hasattr(l, 'wkbType') and
                QgsWkbTypes.geometryType(l.wkbType()) == QgsWkbTypes.PointGeometry
            ]

            prev_pipes = self.cb_pipes.currentData()
            self.cb_pipes.blockSignals(True)
            self.cb_pipes.clear()
            for l in line_lys:
                self.cb_pipes.addItem(f"{l.name()}  [{l.featureCount()}]", l)
            self.cb_pipes.blockSignals(False)
            for i in range(self.cb_pipes.count()):
                if self.cb_pipes.itemData(i) is prev_pipes:
                    self.cb_pipes.setCurrentIndex(i)
                    break

            prev_nodes = self.cb_nodes.currentData()
            self.cb_nodes.blockSignals(True)
            self.cb_nodes.clear()
            self.cb_nodes.addItem(tr("verifica.none_item"), None)
            for l in pt_lys:
                self.cb_nodes.addItem(f"{l.name()}  [{l.featureCount()}]", l)
            self.cb_nodes.blockSignals(False)
            for i in range(self.cb_nodes.count()):
                if self.cb_nodes.itemData(i) is prev_nodes:
                    self.cb_nodes.setCurrentIndex(i)
                    break
        except Exception:
            pass

    # ── Costruzione UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        _root = QVBoxLayout(self)
        _root.setContentsMargins(4, 6, 4, 4)
        _root.setSpacing(0)
        h_main = QSplitter(Qt.Horizontal)
        h_main.setHandleWidth(4)
        _root.addWidget(h_main)

        # Colonna sinistra: form (scorrevole)
        left_content = QWidget()
        layout = QVBoxLayout(left_content)
        layout.setContentsMargins(2, 2, 6, 2)
        layout.setSpacing(6)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setWidget(left_content)
        h_main.addWidget(left_scroll)

        # Colonna destra: log
        right_panel = QWidget()
        right_panel.setMinimumWidth(160)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(2, 2, 2, 2)
        right_layout.setSpacing(4)
        h_main.addWidget(right_panel)
        h_main.setStretchFactor(0, 3)
        h_main.setStretchFactor(1, 2)
        h_main.setSizes([300, 200])   # rapporto iniziale 60/40
        h_main.setCollapsible(0, False)
        h_main.setCollapsible(1, False)

        # ── Layer ────────────────────────────────────────────────────────────
        grp_lyr = QGroupBox(tr("verifica.layer_group"))
        fl = QFormLayout(grp_lyr)
        fl.setLabelAlignment(Qt.AlignRight)

        self.cb_pipes = QComboBox()
        self.cb_pipes.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        fl.addRow(tr("verifica.pipes_row"), self.cb_pipes)

        self.cb_nodes = QComboBox()
        self.cb_nodes.addItem(tr("verifica.none_item"), None)
        self.cb_nodes.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.cb_nodes.setToolTip(tr("verifica.nodes_tooltip"))
        fl.addRow(tr("verifica.nodes_row"), self.cb_nodes)
        layout.addWidget(grp_lyr)

        # ── 1. Analisi ───────────────────────────────────────────────────────
        grp_check = QGroupBox(tr("verifica.analysis_group"))
        vb_c = QVBoxLayout(grp_check)
        vb_c.setSpacing(6)

        lbl_c = QLabel(tr("verifica.analysis_desc"))
        lbl_c.setStyleSheet("color: #aaa; font-size: 10px;")
        vb_c.addWidget(lbl_c)

        self.chk_auto_color = QCheckBox(tr("verifica.auto_color"))
        self.chk_auto_color.setChecked(True)
        vb_c.addWidget(self.chk_auto_color)

        self.btn_analyze = QPushButton(tr("verifica.analyze_button"))
        self.btn_analyze.setStyleSheet(
            "QPushButton { background-color: #7a5c1e; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_analyze.clicked.connect(lambda _: self._run_analysis())
        vb_c.addWidget(self.btn_analyze)

        self.btn_select_bad = QPushButton(tr("verifica.select_bad_button"))
        self.btn_select_bad.setEnabled(False)
        self.btn_select_bad.setStyleSheet(
            "QPushButton { background-color: #6a1e6a; color: white; "
            "font-weight: bold; padding: 5px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_select_bad.setToolTip(tr("verifica.select_bad_tooltip"))
        self.btn_select_bad.clicked.connect(self._select_bad_pipes)
        vb_c.addWidget(self.btn_select_bad)
        layout.addWidget(grp_check)

        # ── 2. Snap endpoint ─────────────────────────────────────────────────
        grp_snap = QGroupBox(tr("verifica.snap_group"))
        fl_s = QFormLayout(grp_snap)
        fl_s.setLabelAlignment(Qt.AlignRight)
        fl_s.setVerticalSpacing(8)

        lbl_s = QLabel(tr("verifica.snap_desc"))
        lbl_s.setStyleSheet("color: #aaa; font-size: 10px;")
        fl_s.addRow("", lbl_s)

        self.spin_tol = QDoubleSpinBox()
        self.spin_tol.setRange(0.001, 100_000.0)
        self.spin_tol.setValue(1.0)
        self.spin_tol.setDecimals(3)
        self.spin_tol.setSuffix(" m")
        self.spin_tol.setToolTip(tr("verifica.tolerance_tooltip"))
        fl_s.addRow(tr("verifica.tolerance_row"), self.spin_tol)

        strat_w = QWidget()
        strat_l = QVBoxLayout(strat_w)
        strat_l.setContentsMargins(0, 0, 0, 0)
        strat_l.setSpacing(3)
        self._strat_grp = QButtonGroup(self)
        self.rb_centroid = QRadioButton(tr("verifica.strategy_centroid"))
        self.rb_centroid.setChecked(True)
        self._strat_grp.addButton(self.rb_centroid, 0)
        strat_l.addWidget(self.rb_centroid)
        self.rb_first = QRadioButton(tr("verifica.strategy_first"))
        self._strat_grp.addButton(self.rb_first, 1)
        strat_l.addWidget(self.rb_first)
        fl_s.addRow(tr("verifica.strategy_row"), strat_w)

        out_w = QWidget()
        out_l = QVBoxLayout(out_w)
        out_l.setContentsMargins(0, 0, 0, 0)
        out_l.setSpacing(3)
        self._out_grp = QButtonGroup(self)
        self.rb_new_layer = QRadioButton(tr("verifica.output_new_layer"))
        self.rb_new_layer.setChecked(True)
        self._out_grp.addButton(self.rb_new_layer, 0)
        out_l.addWidget(self.rb_new_layer)
        self.rb_overwrite = QRadioButton(tr("verifica.output_overwrite"))
        self._out_grp.addButton(self.rb_overwrite, 1)
        out_l.addWidget(self.rb_overwrite)
        fl_s.addRow(tr("verifica.output_row"), out_w)

        self.btn_snap = QPushButton(tr("verifica.snap_button"))
        self.btn_snap.setStyleSheet(
            "QPushButton { background-color: #6a1010; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_snap.clicked.connect(self._run_snap)
        fl_s.addRow("", self.btn_snap)
        layout.addWidget(grp_snap)

        # ── 3. Isole e ri-analisi ────────────────────────────────────────────
        grp_isl = QGroupBox(tr("verifica.islands_group"))
        vb_i = QVBoxLayout(grp_isl)
        vb_i.setSpacing(6)

        lbl_i = QLabel(tr("verifica.islands_desc"))
        lbl_i.setStyleSheet("color: #aaa; font-size: 10px;")
        vb_i.addWidget(lbl_i)

        isl_row = QHBoxLayout()
        self.btn_select = QPushButton(tr("verifica.select_islands_button"))
        self.btn_select.setEnabled(False)
        self.btn_select.setStyleSheet(
            "QPushButton { background-color: #b8860b; color: white; "
            "font-weight: bold; padding: 5px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_select.clicked.connect(self._select_islands)
        self.btn_select.setToolTip(tr("verifica.select_islands_tooltip"))
        isl_row.addWidget(self.btn_select)

        self.btn_color = QPushButton(tr("verifica.color_islands_button"))
        self.btn_color.setEnabled(False)
        self.btn_color.setStyleSheet(
            "QPushButton { background-color: #2e5980; color: white; "
            "font-weight: bold; padding: 5px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_color.clicked.connect(self._color_islands)
        self.btn_color.setToolTip(tr("verifica.color_islands_tooltip"))
        isl_row.addWidget(self.btn_color)
        vb_i.addLayout(isl_row)

        self.btn_reanalyze = QPushButton(tr("verifica.reanalyze_button"))
        self.btn_reanalyze.setStyleSheet(
            "QPushButton { background-color: #3a3a6a; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_reanalyze.clicked.connect(self._reanalyze)
        self.btn_reanalyze.setToolTip(tr("verifica.reanalyze_tooltip"))
        vb_i.addWidget(self.btn_reanalyze)
        layout.addWidget(grp_isl)
        layout.addStretch()

        # Colonna destra: log
        lbl_log = QLabel(tr("verifica.log_label"))
        lbl_log.setStyleSheet("font-weight: bold; margin-top: 8px;")
        right_layout.addWidget(lbl_log)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_log.customContextMenuRequested.connect(self._show_log_context_menu)
        right_layout.addWidget(self.txt_log, 1)

    # ── Log helper ───────────────────────────────────────────────────────────

    def _show_log_context_menu(self, pos):
        menu = self.txt_log.createStandardContextMenu()
        menu.addSeparator()
        act_clear = menu.addAction(tr("verifica.clear_log_action"))
        act_clear.triggered.connect(self.txt_log.clear)
        menu.exec_(self.txt_log.mapToGlobal(pos))

    def _log(self, msg: str, color: str = ''):
        from PyQt5.QtCore import QCoreApplication
        cursor = self.txt_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        if color == 'green':
            fmt.setForeground(QColor('#1a7a1a'))
        elif color == 'red':
            fmt.setForeground(QColor('#cc0000'))
        elif color == 'orange':
            fmt.setForeground(QColor('#b85c00'))
        else:
            fmt.setForeground(self.txt_log.palette().text().color())
        cursor.setCharFormat(fmt)
        cursor.insertText(msg + '\n')
        self.txt_log.setTextCursor(cursor)
        self.txt_log.ensureCursorVisible()
        QCoreApplication.processEvents()

    # ── Analisi ──────────────────────────────────────────────────────────────
    # NOTA: i messaggi di log qui sotto (self._log(...)) restano in italiano
    # deliberatamente — sono diagnostica dinamica, non interfaccia statica.
    # Vedi commento in cima al modulo i18n.py.

    def _run_analysis(self, pipe_layer=None, clear_log=True):
        """Analisi topologica. pipe_layer opzionale per ri-analisi su layer diverso."""
        if pipe_layer is None:
            pipe_layer = self.cb_pipes.currentData()
        if pipe_layer is None:
            self._log("ERRORE: nessun layer condotte selezionato.")
            return

        if pipe_layer.featureCount() == 0:
            if clear_log:
                self.txt_log.clear()
            self._log(
                f"⚠ Il layer '{pipe_layer.name()}' è VUOTO (0 feature).\n"
                "  Seleziona il layer condotte corretto prima di eseguire l'analisi.")
            return

        if clear_log:
            self.txt_log.clear()
        self._log(
            f"Analisi rete: {pipe_layer.name()} "
            f"({pipe_layer.featureCount()} feature) ...")
        try:
            import processing as _proc
            from PyQt5.QtCore import QCoreApplication
            from ..gis_integration.network_builder import build_graph, check_pipe_issues

            self._log("  Fix geometrie ...")
            fixed = _proc.run("native:fixgeometries", {
                'INPUT': pipe_layer, 'METHOD': 1,
                'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
            QCoreApplication.processEvents()

            self._log("  Esplosione polilinee ...")
            exploded = _proc.run("native:explodelines", {
                'INPUT': fixed, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
            QCoreApplication.processEvents()
            self._log(f"  Segmenti dopo esplosione: {exploded.featureCount()}")

            archi, _, skipped_null = build_graph(exploded)
            self._log(
                f"  Archi nel grafo: {len(archi)}  "
                f"(scartati null/degenerate: {skipped_null})")

            warnings, bad_ids = check_pipe_issues(archi, skipped_null=skipped_null)
            self._last_problem_ids = bad_ids
            self._last_problem_pipe_lyr = pipe_layer
            self.btn_select_bad.setEnabled(bool(bad_ids))
            if warnings:
                for w in warnings:
                    self._log(f"⚠ {w}")
            else:
                self._log("[OK] Nessun problema topologico rilevato.")
                # Notifica il pannello principale di pre-popolare Tab 1
                self.analysis_ok.emit(pipe_layer, self.cb_nodes.currentData())

            self._update_island_state(pipe_layer, warnings)

            if self.chk_auto_color.isChecked() and self._last_island_fids:
                self._color_islands()

        except Exception as exc:
            import traceback
            self._log(f"ERRORE: {exc}")
            self._log(traceback.format_exc())

    def _select_bad_pipes(self):
        """Seleziona nel layer sorgente le condotte con duplicati o sovrapposizioni."""
        if not self._last_problem_ids or self._last_problem_pipe_lyr is None:
            return
        lyr = self._last_problem_pipe_lyr
        field_names = {f.name() for f in lyr.fields()}
        id_field = next(
            (f for f in ('pipe_id', 'fid', 'FID', 'id', 'OBJECTID') if f in field_names),
            None)
        if id_field is None:
            self._log("⚠ Nessun campo ID (pipe_id/fid/id) trovato nel layer.", 'orange')
            return
        vals = ', '.join(str(v) for v in sorted(self._last_problem_ids))
        lyr.selectByExpression(f'"{id_field}" IN ({vals})')
        n = lyr.selectedFeatureCount()
        self._log(
            f"Selezionate {n} condotte problematiche nel layer '{lyr.name()}' "
            f"(campo: {id_field}).")
        if self.iface is not None:
            self.iface.mapCanvas().zoomToSelected(lyr)

    def _select_in_pipes_combo(self, layer):
        """Seleziona *layer* nel combo condotte, se presente."""
        for i in range(self.cb_pipes.count()):
            if self.cb_pipes.itemData(i) is layer:
                self.cb_pipes.blockSignals(True)
                self.cb_pipes.setCurrentIndex(i)
                self.cb_pipes.blockSignals(False)
                break

    def _reanalyze(self):
        """Ri-analizza usando l'ultimo layer snappato, o il combo se non disponibile."""
        if self._last_snap_layer is not None:
            layer = self._last_snap_layer
            self._select_in_pipes_combo(layer)
        else:
            layer = self.cb_pipes.currentData()

        if layer is None:
            self._log("ERRORE: nessun layer disponibile per la ri-analisi.")
            return

        self.txt_log.clear()
        self._log(f"--- Ri-analisi su: {layer.name()} ---")
        self._run_analysis(pipe_layer=layer, clear_log=False)

    # ── Isole ────────────────────────────────────────────────────────────────

    def notify_islands(self, pipe_layer, warnings):
        """Chiamato dal pannello principale per aggiornare lo stato isole
        (es. dopo un collasso/check eseguito negli altri tab)."""
        self._update_island_state(pipe_layer, warnings)

    def _update_island_state(self, pipe_layer, warnings):
        # ATTENZIONE: questo controllo rilegge il TESTO ITALIANO dei warning
        # generati da check_pipe_issues() in network_builder.py. NON tradurre
        # ne' questa stringa ne' quella sorgente senza aggiornarle insieme,
        # altrimenti il rilevamento isole smette di funzionare silenziosamente.
        has_islands = any(
            'isole' in w.lower() or 'sconnessa' in w.lower()
            for w in warnings
        )
        if has_islands and pipe_layer is not None:
            try:
                from ..gis_integration.network_builder import find_island_fids
                self._last_island_fids = find_island_fids(pipe_layer)
                self._last_island_source_lyr = pipe_layer
            except Exception:
                self._last_island_fids = []
                self._last_island_source_lyr = None
        else:
            self._last_island_fids = []
            self._last_island_source_lyr = None
        has = bool(self._last_island_fids)
        self.btn_select.setEnabled(has)
        self.btn_color.setEnabled(has)

        if has:
            n_pipes = sum(len(g) for g in self._last_island_fids)
            n_isl   = len(self._last_island_fids)
            self._log(
                f"⚠ ATTENZIONE: {n_pipes} condotta/e in {n_isl} isola/e "
                "NON SARANNO SIMULATE — non sono collegate alla rete principale.\n"
                "  → Correggile con Snap + Ri-analizza prima del collasso.\n"
                "  → Le condotte isolate sono ora selezionate nel layer sorgente."
            )
            # Seleziona automaticamente le condotte isolate nel layer sorgente
            all_fids = [fid for grp in self._last_island_fids for fid in grp]
            self._last_island_source_lyr.selectByIds(all_fids)

    def _select_islands(self):
        if not self._last_island_fids or self._last_island_source_lyr is None:
            return
        lyr = self._last_island_source_lyr
        all_fids = [fid for group in self._last_island_fids for fid in group]
        lyr.selectByIds(all_fids)
        n_comp = len(self._last_island_fids)
        self._log(
            f"Selezionate {len(all_fids)} condotte in {n_comp} isola/e — "
            "usa 'Zoom alla selezione' per vederle.")
        for ci, fids in enumerate(self._last_island_fids):
            self._log(
                f"  Isola {ci+1}: {len(fids)} condotte "
                f"(FID: {fids[:5]}{'...' if len(fids) > 5 else ''})")
        if self.iface is not None:
            self.iface.mapCanvas().zoomToSelected(lyr)

    def _color_islands(self):
        if not self._last_island_fids or self._last_island_source_lyr is None:
            self._log("ERRORE: esegui prima ‘Analizza rete’.")
            return
        try:
            from qgis.core import (
                QgsVectorLayer, QgsFeature, QgsProject,
                QgsCategorizedSymbolRenderer, QgsRendererCategory,
                QgsSymbol, QgsField, QgsWkbTypes,
            )
            from PyQt5.QtCore import QVariant
            from PyQt5.QtGui import QColor

            src_lyr = self._last_island_source_lyr
            crs_str = src_lyr.crs().authid()
            geom_str = QgsWkbTypes.displayString(src_lyr.wkbType())
            mem_lyr = QgsVectorLayer(
                f"{geom_str}?crs={crs_str}",
                f"Verifica connessione – {src_lyr.name()}",
                "memory",
            )
            dp = mem_lyr.dataProvider()
            dp.addAttributes(src_lyr.fields().toList())
            dp.addAttributes([QgsField("comp_id", QVariant.Int)])
            mem_lyr.updateFields()

            # Mappa fid -> comp_id (0 = componente principale, 1+ = isole)
            fid_to_comp = {}
            for comp_idx, fid_group in enumerate(self._last_island_fids):
                for fid in fid_group:
                    fid_to_comp[fid] = comp_idx + 1

            # Inserisce TUTTE le feature del layer sorgente
            new_feats = []
            for feat in src_lyr.getFeatures():
                nf = QgsFeature(mem_lyr.fields())
                nf.setGeometry(feat.geometry())
                for field in src_lyr.fields():
                    nf[field.name()] = feat[field.name()]
                nf["comp_id"] = fid_to_comp.get(feat.id(), 0)
                new_feats.append(nf)
            dp.addFeatures(new_feats)
            mem_lyr.updateExtents()

            _colors = [
                "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
                "#42d4f4", "#f032e6", "#bfef45", "#469990", "#9a6324",
            ]
            categories = []
            # Categoria 0: componente principale (grigio neutro)
            sym_main = QgsSymbol.defaultSymbol(mem_lyr.geometryType())
            sym_main.setColor(QColor("#888888"))
            n_main = src_lyr.featureCount() - sum(
                len(g) for g in self._last_island_fids)
            categories.append(
                QgsRendererCategory(0, sym_main,
                                    f"Rete principale  ({n_main} condotte)"))
            # Categorie 1+: isole
            for comp_idx, fid_group in enumerate(self._last_island_fids):
                color = _colors[comp_idx % len(_colors)]
                sym = QgsSymbol.defaultSymbol(mem_lyr.geometryType())
                sym.setColor(QColor(color))
                label = f"Isola {comp_idx + 1}  ({len(fid_group)} condotte)"
                categories.append(QgsRendererCategory(comp_idx + 1, sym, label))
            mem_lyr.setRenderer(QgsCategorizedSymbolRenderer("comp_id", categories))
            QgsProject.instance().addMapLayer(mem_lyr)
            self._log(
                f"[OK] Layer ‘Verifica connessione – {src_lyr.name()}’ "
                f"aggiunto: {src_lyr.featureCount()} condotte totali, "
                f"{len(self._last_island_fids)} isola/e colorata/e.")
            for ci, fids in enumerate(self._last_island_fids):
                self._log(f"  Isola {ci+1}: {len(fids)} condotte")
        except Exception as exc:
            import traceback
            self._log(f"ERRORE colora isole: {exc}")
            self._log(traceback.format_exc())

    # ── Snap ─────────────────────────────────────────────────────────────────

    def _run_snap(self):
        pipe_layer = self.cb_pipes.currentData()
        if pipe_layer is None:
            self._log("ERRORE: nessun layer condotte selezionato.")
            return

        tolerance   = self.spin_tol.value()
        strategy    = 'centroid' if self.rb_centroid.isChecked() else 'first'
        overwrite   = self.rb_overwrite.isChecked()
        nodes_layer = self.cb_nodes.currentData()

        if overwrite:
            ret = QMessageBox.question(
                self, tr("verifica.overwrite_confirm_title"),
                tr("verifica.overwrite_confirm_msg", layer_name=pipe_layer.name()),
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret != QMessageBox.Yes:
                return

        self._log(
            f"Snap endpoint: tolleranza={tolerance} m, "
            f"strategia='{'centroid' if strategy == 'centroid' else 'first'}', "
            f"output={'sovrascrittura' if overwrite else 'nuovo layer'} ...")
        try:
            from ..gis_integration.network_builder import snap_pipe_endpoints
            new_layer, modified_geoms = snap_pipe_endpoints(
                pipe_layer, tolerance, strategy=strategy,
                nodes_layer=nodes_layer, log=self._log)

            if not modified_geoms:
                self._log(
                    "[OK] Nessun endpoint entro la tolleranza — "
                    "rete già connessa o tolleranza troppo piccola.")
                self._last_snap_layer = None
                return

            if overwrite:
                if not pipe_layer.isEditable():
                    pipe_layer.startEditing()
                for fid, geom in modified_geoms.items():
                    pipe_layer.changeGeometry(fid, geom)
                ok = pipe_layer.commitChanges()
                if ok:
                    pipe_layer.triggerRepaint()
                    self._last_snap_layer = pipe_layer
                    self._select_in_pipes_combo(pipe_layer)
                    self._log(
                        f"[OK] Layer '{pipe_layer.name()}' aggiornato: "
                        f"{len(modified_geoms)} condotte modificate.", 'green')
                    self.layer_verified.emit(pipe_layer)
                else:
                    self._log(
                        "ERRORE: commit fallito — il layer potrebbe non supportare "
                        "la modifica diretta.")
                    pipe_layer.rollBack()
                    self._last_snap_layer = None
            else:
                from qgis.core import QgsProject
                QgsProject.instance().addMapLayer(new_layer)
                self._last_snap_layer = new_layer
                self._select_in_pipes_combo(new_layer)
                self._log(
                    f"[OK] Nuovo layer '{new_layer.name()}' aggiunto al progetto "
                    f"({len(modified_geoms)} condotte modificate su "
                    f"{pipe_layer.featureCount()} totali).", 'green')
                self._log(
                    "  → Clicca 'Ri-analizza' per verificare il risultato.")
                self.layer_verified.emit(new_layer)

        except Exception as exc:
            import traceback
            self._log(f"ERRORE: {exc}")
            self._log(traceback.format_exc())
