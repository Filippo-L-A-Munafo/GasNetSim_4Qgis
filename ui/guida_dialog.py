# -*- coding: utf-8 -*-
"""Finestra "Guida" — manuale d'uso completo del plugin, sezione per sezione.

Diversa dal pulsante "Info" (che mostra versione/licenza/crediti + il
vecchio MANUALE.md): questa Guida è pensata per un utente non esperto,
spiega ogni singolo campo dell'interfaccia E la fisica che c'è dietro,
ed è organizzata in sezioni navigabili da un elenco a sinistra.

I contenuti vivono come file Markdown in ``guida/<id>.<lang>.md`` accanto
a questo modulo, cosi' si possono aggiornare senza toccare il codice.
"""
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QTextBrowser, QSplitter,
)
from PyQt5.QtCore import Qt

from .i18n import tr, get_language, register

register({
    "guida.title": {"it": "Guida", "en": "Guide"},
    "guida.close": {"it": "Chiudi", "en": "Close"},
    "guida.missing": {
        "it": "Questa sezione è ancora in preparazione.",
        "en": "This section is still being written.",
    },
})

# Indice della guida: (id_file, {lingua: titolo})
# L'ordine qui definisce l'ordine nella lista a sinistra.
SECTIONS = [
    ("00_introduzione", {
        "it": "Introduzione", "en": "Introduction"}),
    ("01_fisica_di_base", {
        "it": "Concetti fisici di base", "en": "Basic physics concepts"}),
    ("02_interfaccia", {
        "it": "L'interfaccia del plugin", "en": "The plugin interface"}),
    ("03_prepara_rete", {
        "it": "Tab 1 — Prepara Rete", "en": "Tab 1 — Prepare Network"}),
    ("04_parametri_simulazione", {
        "it": "Tab 2 — Parametri Simulazione",
        "en": "Tab 2 — Simulation Parameters"}),
    ("05_avvio_simulazione", {
        "it": "Avvio della simulazione", "en": "Running the simulation"}),
    ("06_risultati_nodi", {
        "it": "Risultati — Nodi", "en": "Results — Nodes"}),
    ("07_risultati_condotte", {
        "it": "Risultati — Condotte", "en": "Results — Pipes"}),
    ("08_layer_output", {
        "it": "Layer di output e file CSV", "en": "Output layers and CSV files"}),
    ("09_riferimenti_tecnici", {
        "it": "Riferimenti tecnici e normativa",
        "en": "Technical references & standards"}),
    ("10_risoluzione_problemi", {
        "it": "Risoluzione dei problemi comuni", "en": "Troubleshooting"}),
    ("11_glossario", {
        "it": "Glossario", "en": "Glossary"}),
]


class GuidaDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.guida_dir = os.path.join(plugin_dir, "guida")
        self.setWindowTitle(tr("guida.title"))
        self.resize(980, 720)
        self._build_ui()
        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(280)
        lang = get_language()
        for section_id, titles in SECTIONS:
            title = titles.get(lang, titles.get("it", section_id))
            self.list_widget.addItem(title)
        self.list_widget.currentRowChanged.connect(self._show_section)
        splitter.addWidget(self.list_widget)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        splitter.addWidget(self.text_browser)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton(tr("guida.close"))
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _show_section(self, row):
        if row < 0 or row >= len(SECTIONS):
            return
        section_id, _titles = SECTIONS[row]
        lang = get_language()
        text = self._read_section(section_id, lang)
        self.text_browser.setMarkdown(text)
        self.text_browser.verticalScrollBar().setValue(0)

    def _read_section(self, section_id, lang):
        candidates = [lang, "it"] if lang != "it" else ["it"]
        for candidate in candidates:
            path = os.path.join(self.guida_dir, f"{section_id}.{candidate}.md")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        return f"# {section_id}\n\n{tr('guida.missing')}"
