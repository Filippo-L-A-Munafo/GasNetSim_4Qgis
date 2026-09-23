# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QWidget, QToolButton, QStyle,
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

from .layer_mapping_panel import LayerMappingPanel
from .i18n import tr, register
from .settings_dialog import SettingsDialog
from .info_dialog import InfoDialog
from .guida_dialog import GuidaDialog

register({
    "main.header": {
        "it": "GasNetSim 4Qgis — Simulatore Idraulico Reti Gas",
        "en": "GasNetSim 4Qgis — Gas Network Hydraulic Simulator",
    },
    "main.close": {"it": "Chiudi", "en": "Close"},
    "main.menu_toggle": {"it": "Menu", "en": "Menu"},
    "main.settings_button": {"it": "Impostazioni", "en": "Settings"},
    "main.guida_button": {"it": "Guida", "en": "Guide"},
    "main.info_button": {"it": "Info", "en": "About"},
    "main.settings_tooltip": {
        "it": "Lingua dell'interfaccia",
        "en": "Interface language",
    },
    "main.guida_tooltip": {
        "it": "Manuale d'uso completo, in sezioni navigabili",
        "en": "Complete user manual, in navigable sections",
    },
    "main.info_tooltip": {
        "it": "Versione, motore di calcolo, licenze",
        "en": "Version, calculation engine, licences",
    },
})

_SIDEBAR_WIDTH = 190


class GasNetSimMainDialog(QDialog):
    def __init__(self, iface, plugin_dir, parent=None):
        super(GasNetSimMainDialog, self).__init__(parent)
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.setWindowTitle("GasNetSim 4Qgis")
        self.resize(1100, 820)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        top_bar = QHBoxLayout()
        self.btn_menu = QToolButton()
        self.btn_menu.setText("☰")
        self.btn_menu.setToolTip(tr("main.menu_toggle"))
        self.btn_menu.setFixedSize(28, 28)
        self.btn_menu.clicked.connect(self._toggle_sidebar)
        top_bar.addWidget(self.btn_menu)

        header = QLabel(tr("main.header"))
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        top_bar.addWidget(header)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        body = QHBoxLayout()
        body.setSpacing(0)

        self.sidebar = self._build_sidebar()
        self.sidebar.setMaximumWidth(0)  # nascosta all'apertura
        body.addWidget(self.sidebar)

        self.mapping_panel = LayerMappingPanel(self.iface)
        body.addWidget(self.mapping_panel, 1)
        main_layout.addLayout(body, 1)

        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton(tr("main.close"))
        btn_close.clicked.connect(self.close)
        footer.addWidget(btn_close)
        main_layout.addLayout(footer)

    def _build_sidebar(self):
        panel = QWidget()
        # Il foglio di stile e' vincolato al solo pannello tramite selettore di
        # objectName: senza selettore Qt lo propaga ai widget figli, i pulsanti
        # perdono la cornice nativa (apparendo fusi fra loro) e mantengono il
        # colore di testo del tema, illeggibile sul fondo cosi' imposto.
        panel.setObjectName("gnsSidebar")
        panel.setStyleSheet(
            "#gnsSidebar { background-color: rgba(127, 127, 127, 28); "
            "border-right: 1px solid rgba(127, 127, 127, 90); }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        style = self.style()
        for key, tip, callback, icon in (
                ("main.settings_button", "main.settings_tooltip",
                 self._open_settings, QStyle.SP_FileDialogDetailedView),
                ("main.guida_button", "main.guida_tooltip",
                 self._open_guida, QStyle.SP_DialogHelpButton),
                ("main.info_button", "main.info_tooltip",
                 self._open_info, QStyle.SP_MessageBoxInformation)):
            btn = QPushButton(tr(key))
            btn.setToolTip(tr(tip))
            # Icone del tema corrente: sempre disponibili, a differenza degli
            # emoji, che dipendono dai font installati.
            try:
                btn.setIcon(style.standardIcon(icon))
            except Exception:
                pass
            btn.setMinimumHeight(30)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        layout.addStretch()
        return panel

    def _toggle_sidebar(self):
        collapsed = self.sidebar.maximumWidth() == 0
        target = _SIDEBAR_WIDTH if collapsed else 0
        anim = QPropertyAnimation(self.sidebar, b"maximumWidth", self)
        anim.setDuration(150)
        anim.setStartValue(self.sidebar.maximumWidth())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._sidebar_anim = anim  # mantiene un riferimento vivo durante l'animazione

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def _open_info(self):
        dlg = InfoDialog(self.plugin_dir, self)
        dlg.exec_()

    def _open_guida(self):
        dlg = GuidaDialog(self.plugin_dir, self)
        dlg.exec_()
