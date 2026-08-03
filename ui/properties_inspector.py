# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QCheckBox, QSpinBox,
)
from PyQt5.QtCore import Qt

from .i18n import tr, register

register({
    "props.title": {"it": "Visualizzazione Risultati", "en": "Results Display"},
    "props.hint": {
        "it": "<i style='color:gray;font-size:10px;'>"
              "Modifica la colorimetria dei layer risultato<br>"
              "senza rieseguire la simulazione.</i>",
        "en": "<i style='color:gray;font-size:10px;'>"
              "Change the result layers' colouring<br>"
              "without re-running the simulation.</i>",
    },
    "props.nodes_group": {"it": "Nodi", "en": "Nodes"},
    "props.pipes_group": {"it": "Condotte", "en": "Pipelines"},
    "props.layer_row": {"it": "Layer:", "en": "Layer:"},
    "props.color_by_row": {"it": "Colora per:", "en": "Colour by:"},
    "props.flow_arrows": {"it": "Frecce direzione flusso", "en": "Flow direction arrows"},
    "props.refresh_tooltip": {
        "it": "Aggiorna la lista dei layer risultato presenti nel progetto",
        "en": "Refresh the list of result layers present in the project",
    },
    "props.apply_button": {"it": "▶  Applica colorimetria", "en": "▶  Apply colouring"},
    "props.export_group": {"it": "Esporta dati", "en": "Export data"},
    "props.decimals_row": {"it": "Decimali:", "en": "Decimals:"},
    "props.decimals_tooltip": {
        "it": "Cifre decimali per i valori numerici nel CSV",
        "en": "Decimal digits for numeric values in the CSV",
    },
    "props.export_button": {"it": "Esporta CSV", "en": "Export CSV"},
    "props.none_item": {"it": "— nessuno —", "en": "— none —"},
    "props.no_layer_title": {"it": "Nessun layer", "en": "No layer"},
    "props.no_layer_msg": {
        "it": "Seleziona un layer da esportare.",
        "en": "Select a layer to export.",
    },
    "props.layer_not_found_title": {"it": "Layer non trovato", "en": "Layer not found"},
    "props.layer_not_found_msg": {
        "it": "Il layer selezionato non è più disponibile.",
        "en": "The selected layer is no longer available.",
    },
    "props.export_dialog_title": {"it": "Esporta CSV", "en": "Export CSV"},
    "props.export_done_title": {"it": "Esportazione completata", "en": "Export complete"},
    "props.export_done_msg": {
        "it": "Layer esportato con {decimals} decimali:\n{filepath}",
        "en": "Layer exported with {decimals} decimals:\n{filepath}",
    },
    "props.export_error_title": {"it": "Errore esportazione", "en": "Export error"},
})

# Campi risultato nodi con etichette human-readable
_NODE_FIELDS = [
    ('pressure_bar',       {'it': 'Pressione (bar)', 'en': 'Pressure (bar)'}),
    ('temperature_k',      {'it': 'Temperatura (K)', 'en': 'Temperature (K)'}),
    ('sp_gravity',         {'it': 'Spec. gravity', 'en': 'Spec. gravity'}),
    ('z_factor',           {'it': 'Z-factor', 'en': 'Z-factor'}),
    ('hhv_mj_sm3',         {'it': 'HHV (MJ/sm3)', 'en': 'HHV (MJ/sm3)'}),
    ('wobbe_mj_sm3',       {'it': 'Wobbe (MJ/sm3)', 'en': 'Wobbe (MJ/sm3)'}),
    ('density_kg_m3',      {'it': 'Densità (kg/m3)', 'en': 'Density (kg/m3)'}),
    ('std_density_kg_sm3', {'it': 'Dens. std (kg/sm3)', 'en': 'Std density (kg/sm3)'}),
    ('molar_mass',         {'it': 'Massa molare (g/mol)', 'en': 'Molar mass (g/mol)'}),
]

# Campi risultato condotte con etichette human-readable
_PIPE_FIELDS = [
    ('flow_abs_sm3h',    {'it': 'Portata assoluta (Smc/h)', 'en': 'Absolute flow (Sm3/h)'}),
    ('flow_sm3h',        {'it': 'Portata con segno (Smc/h)', 'en': 'Signed flow (Sm3/h)'}),
    ('velocity_m_s',     {'it': 'Velocità (m/s)', 'en': 'Velocity (m/s)'}),
    ('avg_pressure_bar', {'it': 'Press. media (bar)', 'en': 'Avg. pressure (bar)'}),
    ('sp_gravity',       {'it': 'Spec. gravity', 'en': 'Spec. gravity'}),
    ('z_factor',          {'it': 'Z-factor', 'en': 'Z-factor'}),
    ('density_kg_m3',    {'it': 'Densità (kg/m3)', 'en': 'Density (kg/m3)'}),
]


def _lang_label(labels: dict) -> str:
    from .i18n import get_language
    lang = get_language()
    return labels.get(lang, labels.get('it'))


class PropertiesInspector(QWidget):
    """
    Pannello di controllo della visualizzazione risultati.
    Permette di cambiare il campo di colorimetria sui layer [Risultati]
    già presenti nel progetto senza rieseguire la simulazione.
    """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel(tr("props.title"))
        title.setStyleSheet(
            "font-weight: bold; font-size: 11px; padding-bottom: 2px;")
        layout.addWidget(title)

        hint = QLabel(tr("props.hint"))
        hint.setTextFormat(Qt.RichText)
        layout.addWidget(hint)

        # ── Layer Nodi ─────────────────────────────────────────────────────
        grp_n = QGroupBox(tr("props.nodes_group"))
        fl_n = QFormLayout(grp_n)
        fl_n.setLabelAlignment(Qt.AlignRight)
        fl_n.setSpacing(4)

        self.cb_nodes_lyr = QComboBox()
        self.cb_nodes_lyr.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLength)
        self.cb_nodes_lyr.currentIndexChanged.connect(
            lambda _: self._on_nodes_layer_changed())
        fl_n.addRow(tr("props.layer_row"), self.cb_nodes_lyr)

        self.cb_nodes_field = QComboBox()
        fl_n.addRow(tr("props.color_by_row"), self.cb_nodes_field)

        layout.addWidget(grp_n)

        # ── Layer Condotte ─────────────────────────────────────────────────
        grp_p = QGroupBox(tr("props.pipes_group"))
        fl_p = QFormLayout(grp_p)
        fl_p.setLabelAlignment(Qt.AlignRight)
        fl_p.setSpacing(4)

        self.cb_pipes_lyr = QComboBox()
        self.cb_pipes_lyr.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLength)
        self.cb_pipes_lyr.currentIndexChanged.connect(
            lambda _: self._on_pipes_layer_changed())
        fl_p.addRow(tr("props.layer_row"), self.cb_pipes_lyr)

        self.cb_pipes_field = QComboBox()
        fl_p.addRow(tr("props.color_by_row"), self.cb_pipes_field)

        self.chk_arrows = QCheckBox(tr("props.flow_arrows"))
        self.chk_arrows.setChecked(True)
        fl_p.addRow("", self.chk_arrows)

        layout.addWidget(grp_p)

        # ── Pulsanti ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()

        btn_refresh = QPushButton("↺")
        btn_refresh.setFixedWidth(32)
        btn_refresh.setToolTip(tr("props.refresh_tooltip"))
        btn_refresh.clicked.connect(self.refresh_layers)
        btn_row.addWidget(btn_refresh)

        self.btn_apply = QPushButton(tr("props.apply_button"))
        self.btn_apply.setStyleSheet(
            "QPushButton { background-color: #0078d7; color: white; "
            "font-weight: bold; padding: 5px; border-radius: 3px; }"
            "QPushButton:disabled { background-color: #666; color: #aaa; }")
        self.btn_apply.clicked.connect(self._apply_recolor)
        btn_row.addWidget(self.btn_apply)

        layout.addLayout(btn_row)

        # ── Esporta dati ────────────────────────────────────────────────
        grp_exp = QGroupBox(tr("props.export_group"))
        fl_exp = QFormLayout(grp_exp)
        fl_exp.setLabelAlignment(Qt.AlignRight)
        fl_exp.setSpacing(4)

        self.cb_export_lyr = QComboBox()
        self.cb_export_lyr.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLength)
        fl_exp.addRow(tr("props.layer_row"), self.cb_export_lyr)

        self.sb_decimals = QSpinBox()
        self.sb_decimals.setRange(0, 10)
        self.sb_decimals.setValue(4)
        self.sb_decimals.setToolTip(tr("props.decimals_tooltip"))
        fl_exp.addRow(tr("props.decimals_row"), self.sb_decimals)

        btn_export = QPushButton(tr("props.export_button"))
        btn_export.clicked.connect(self._export_csv)
        fl_exp.addRow("", btn_export)

        layout.addWidget(grp_exp)
        layout.addStretch()

        # Prima popolazione
        self.refresh_layers()

    # ── API pubblica ────────────────────────────────────────────────────────

    def refresh_layers(self):
        """
        Rileva i layer [Risultati] presenti nel progetto QGIS e
        aggiorna i combobox di selezione.
        """
        try:
            from qgis.core import QgsProject, QgsWkbTypes
            proj = QgsProject.instance()
            nodes_lyrs, pipes_lyrs = [], []
            for lyr in proj.mapLayers().values():
                if not (lyr.name().startswith('R-N-') or lyr.name().startswith('R-P-')):
                    continue
                try:
                    gt = lyr.geometryType()
                    if gt == QgsWkbTypes.PointGeometry:
                        nodes_lyrs.append(lyr)
                    elif gt == QgsWkbTypes.LineGeometry:
                        pipes_lyrs.append(lyr)
                except Exception:
                    pass
            self._fill_layer_combo(self.cb_nodes_lyr, nodes_lyrs)
            self._fill_layer_combo(self.cb_pipes_lyr, pipes_lyrs)
            all_lyrs = sorted(nodes_lyrs + pipes_lyrs, key=lambda l: l.name())
            self._fill_layer_combo(self.cb_export_lyr, all_lyrs)
        except Exception:
            pass

    # ── Helpers privati ─────────────────────────────────────────────────────

    def _fill_layer_combo(self, combo, layers):
        prev_id = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(tr("props.none_item"), None)
        for lyr in layers:
            combo.addItem(lyr.name(), lyr.id())
        combo.blockSignals(False)
        restored = False
        if prev_id:
            for i in range(combo.count()):
                if combo.itemData(i) == prev_id:
                    combo.setCurrentIndex(i)
                    restored = True
                    break
        if not restored:
            combo.currentIndexChanged.emit(combo.currentIndex())

    def _get_layer(self, combo):
        layer_id = combo.currentData()
        if not layer_id:
            return None
        try:
            from qgis.core import QgsProject
            return QgsProject.instance().mapLayer(layer_id)
        except Exception:
            return None

    def _fill_field_combo(self, combo, layer, candidates):
        prev = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        if layer is not None:
            layer_fields = {f.name() for f in layer.fields()}
            for fid, flabels in candidates:
                if fid in layer_fields:
                    combo.addItem(_lang_label(flabels), fid)
        combo.blockSignals(False)
        if prev:
            for i in range(combo.count()):
                if combo.itemData(i) == prev:
                    combo.setCurrentIndex(i)
                    return

    def _on_nodes_layer_changed(self):
        self._fill_field_combo(
            self.cb_nodes_field,
            self._get_layer(self.cb_nodes_lyr),
            _NODE_FIELDS)

    def _on_pipes_layer_changed(self):
        self._fill_field_combo(
            self.cb_pipes_field,
            self._get_layer(self.cb_pipes_lyr),
            _PIPE_FIELDS)

    def _apply_recolor(self):
        """Riapplica la colorimetria ai layer risultato selezionati."""
        try:
            from ..gis_integration.result_visualizer import recolor_result_layer
        except ImportError:
            return

        nodes_lyr = self._get_layer(self.cb_nodes_lyr)
        nodes_field = self.cb_nodes_field.currentData()
        if nodes_lyr is not None and nodes_field:
            recolor_result_layer(nodes_lyr, nodes_field, add_arrows=False)

        pipes_lyr = self._get_layer(self.cb_pipes_lyr)
        pipes_field = self.cb_pipes_field.currentData()
        if pipes_lyr is not None and pipes_field:
            recolor_result_layer(
                pipes_lyr, pipes_field,
                add_arrows=self.chk_arrows.isChecked())

        try:
            if self.iface is not None:
                self.iface.mapCanvas().refresh()
        except Exception:
            pass

    def _export_csv(self):
        """Esporta il layer selezionato in CSV con precisione configurabile."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        lyr_id = self.cb_export_lyr.currentData()
        if not lyr_id:
            QMessageBox.warning(self, tr("props.no_layer_title"),
                                tr("props.no_layer_msg"))
            return

        try:
            from qgis.core import QgsProject
            lyr = QgsProject.instance().mapLayer(lyr_id)
        except Exception:
            lyr = None
        if lyr is None:
            QMessageBox.warning(self, tr("props.layer_not_found_title"),
                                tr("props.layer_not_found_msg"))
            return

        default_name = (
            lyr.name()
            .replace('R-N-', '').replace('R-P-orig-', '').replace('R-P-', '')
            .replace(' ', '_') + '.csv'
        )
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr("props.export_dialog_title"), default_name, "CSV (*.csv)")
        if not filepath:
            return

        decimals = self.sb_decimals.value()
        try:
            from ..gis_integration.result_visualizer import export_layer_to_csv
            export_layer_to_csv(lyr, filepath, decimals)
            QMessageBox.information(
                self, tr("props.export_done_title"),
                tr("props.export_done_msg", decimals=decimals, filepath=filepath))
        except Exception as e:
            QMessageBox.critical(self, tr("props.export_error_title"), str(e))
