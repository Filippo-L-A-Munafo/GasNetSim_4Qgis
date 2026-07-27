# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from .layer_mapping_panel import LayerMappingPanel


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

        header = QLabel("GasNetSim 4Qgis \u2014 Simulatore Idraulico Reti Gas")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        main_layout.addWidget(header)

        self.mapping_panel = LayerMappingPanel(self.iface)
        main_layout.addWidget(self.mapping_panel)

        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(self.close)
        footer.addWidget(btn_close)
        main_layout.addLayout(footer)
        # Aggiorna il pannello di visualizzazione con i nuovi layer risultato
        try:
            self.inspector.refresh_layers()
        except Exception:
            pass
