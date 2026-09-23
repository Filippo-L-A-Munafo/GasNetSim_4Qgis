# -*- coding: utf-8 -*-
"""Finestra "Guida" — manuale d'uso completo del plugin, sezione per sezione.

Diversa dal pulsante "Info" (che mostra versione, motore e licenze): questa
Guida e' il manuale, organizzato in sezioni navigabili da un elenco a sinistra.

I contenuti vivono come file Markdown in ``guida/<id>.<lang>.md`` accanto a
questo modulo, cosi' si possono aggiornare senza toccare il codice. La resa
tipografica passa da markdown_view: conversione in HTML e foglio di stile
derivato dalla palette, perche' QTextBrowser.setMarkdown() non e' governabile
da CSS.

NOTA: l'ordine di lettura e' quello della lista SECTIONS qui sotto, NON la
numerazione dei nomi file (che e' storica: i file sono stati riusati per non
lasciare in giro contenuti obsoleti).
"""
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QTextBrowser, QSplitter, QAbstractItemView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .i18n import tr, get_language, register
from .markdown_view import markdown_to_html, stylesheet_from_palette

register({
    "guida.title": {"it": "Guida", "en": "Guide"},
    "guida.close": {"it": "Chiudi", "en": "Close"},
    "guida.missing": {
        "it": "Questa sezione è ancora in preparazione.",
        "en": "This section is still being written.",
    },
})

# Indice della guida: (id_file, {lingua: titolo}). L'ordine è quello di lettura.
SECTIONS = [
    ("00_introduzione", {
        "it": "1 · Introduzione e ambito",
        "en": "1 · Introduction and scope"}),
    ("01_fisica_di_base", {
        "it": "2 · Formulazione del modello",
        "en": "2 · Model formulation"}),
    ("02_interfaccia", {
        "it": "3 · Architettura dell'interfaccia",
        "en": "3 · Interface architecture"}),
    ("13_verifica_condotte", {
        "it": "4 · Tab 0 — Verifica topologica",
        "en": "4 · Tab 0 — Topological check"}),
    ("03_prepara_rete", {
        "it": "5 · Tab 1 — Dati e mappatura",
        "en": "5 · Tab 1 — Input data and field mapping"}),
    ("04_parametri_simulazione", {
        "it": "6 · Tab 1 — Parametri di calcolo",
        "en": "6 · Tab 1 — Physical and numerical parameters"}),
    ("05_avvio_simulazione", {
        "it": "7 · Esecuzione e file prodotti",
        "en": "7 · Execution and output files"}),
    ("08_layer_output", {
        "it": "8 · Tab 2 — Post-processing",
        "en": "8 · Tab 2 — Post-processing"}),
    ("06_risultati_nodi", {
        "it": "9 · Grandezze ai nodi",
        "en": "9 · Nodal quantities"}),
    ("07_risultati_condotte", {
        "it": "10 · Grandezze su condotte e compressori",
        "en": "10 · Pipeline and compressor quantities"}),
    ("12_tutorial", {
        "it": "11 · Caso di verifica",
        "en": "11 · Reproducible verification case"}),
    ("10_risoluzione_problemi", {
        "it": "12 · Diagnostica della convergenza",
        "en": "12 · Convergence diagnostics"}),
    ("09_riferimenti_tecnici", {
        "it": "13 · Riferimenti tecnici e normativi",
        "en": "13 · Technical and regulatory references"}),
    ("11_glossario", {
        "it": "14 · Nomenclatura e glossario",
        "en": "14 · Nomenclature and glossary"}),
]

# Margine interno del documento: il testo non deve toccare il bordo del
# riquadro, altrimenti tabelle e titoli risultano compressi.
_DOC_MARGIN = 20


class GuidaDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.guida_dir = os.path.join(plugin_dir, "guida")
        self.setWindowTitle(tr("guida.title"))
        self.resize(1080, 780)
        self._build_ui()
        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        # ── Indice ──────────────────────────────────────────────────────────
        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(240)
        self.list_widget.setMaximumWidth(330)
        self.list_widget.setWordWrap(True)          # i titoli lunghi vanno a capo
        self.list_widget.setSpacing(2)
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        lang = get_language()
        for section_id, titles in SECTIONS:
            item = QListWidgetItem(titles.get(lang, titles.get("it", section_id)))
            self.list_widget.addItem(item)
        self.list_widget.currentRowChanged.connect(self._show_section)
        splitter.addWidget(self.list_widget)

        # ── Testo ───────────────────────────────────────────────────────────
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.document().setDocumentMargin(_DOC_MARGIN)
        # Il foglio di stile va assegnato al documento PRIMA del contenuto:
        # viene applicato in fase di analisi dell'HTML.
        self._css = stylesheet_from_palette(self.text_browser.palette())
        self.text_browser.document().setDefaultStyleSheet(self._css)
        font = self.text_browser.font()
        font.setStyleHint(QFont.SansSerif)
        self.text_browser.setFont(font)
        splitter.addWidget(self.text_browser)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 800])
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
        markdown = self._read_section(section_id, get_language())
        try:
            html = markdown_to_html(markdown)
        except Exception:
            # Una sezione malformata non deve impedire la consultazione delle
            # altre: si ripiega sulla resa predefinita di Qt.
            self.text_browser.setMarkdown(markdown)
            return
        self.text_browser.document().setDefaultStyleSheet(self._css)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(0)

    def _read_section(self, section_id, lang):
        candidates = [lang, "it"] if lang != "it" else ["it"]
        for candidate in candidates:
            path = os.path.join(self.guida_dir, f"{section_id}.{candidate}.md")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        return f"# {section_id}\n\n{tr('guida.missing')}"
