# -*- coding: utf-8 -*-
"""Finestra "Info" — identificazione del plugin, crediti e licenze.

NON contiene il manuale: il manuale d'uso e' la Guida (pulsante Guida,
modulo guida_dialog.py), che lo presenta in sezioni navigabili. Fino alla
versione 1.0.0 questa finestra caricava l'intero MANUALE.md, duplicando lo
stesso contenuto in due punti dell'interfaccia.
"""
import configparser
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt5.QtCore import Qt

from .i18n import tr, register

register({
    "info.title": {"it": "Informazioni", "en": "About"},
    "info.close": {"it": "Chiudi", "en": "Close"},
    "info.version": {"it": "Versione {version}", "en": "Version {version}"},
    "info.author": {"it": "Autore: {author}", "en": "Author: {author}"},
    "info.repository": {"it": "Repository:", "en": "Repository:"},
    "info.engine_title": {"it": "Motore di calcolo", "en": "Calculation engine"},
    "info.engine_detected": {
        "it": "Rilevato: {engine}",
        "en": "Detected: {engine}",
    },
    "info.engine_note": {
        "it": "La versione del plugin è indipendente da quella del motore. "
              "Versione e commit del motore effettivamente usato vengono "
              "registrati nel log e nel file run_info.json salvato accanto a "
              "ogni serie di risultati.",
        "en": "The plugin version is independent of the engine version. The "
              "version and commit of the engine actually used are recorded in "
              "the log and in the run_info.json file saved alongside every set "
              "of results.",
    },
    "info.license_title": {"it": "Licenze", "en": "Licences"},
    "info.license_plugin": {
        "it": "Plugin GasNetSim 4Qgis — licenza MIT.",
        "en": "GasNetSim 4Qgis plugin — MIT licence.",
    },
    "info.license_engine": {
        "it": "Motore di calcolo GasNetSim — licenza MPL-2.0, sviluppato da "
              "ICE-1: Energy Systems Engineering, Forschungszentrum Jülich GmbH.",
        "en": "GasNetSim calculation engine — MPL-2.0 licence, developed by "
              "ICE-1: Energy Systems Engineering, Forschungszentrum Jülich GmbH.",
    },
    "info.citation_title": {"it": "Citazione", "en": "Citation"},
    "info.citation_text": {
        "it": "Per citare questo software si utilizzino i metadati contenuti "
              "nel file CITATION.cff del repository.",
        "en": "To cite this software, use the metadata contained in the "
              "CITATION.cff file of the repository.",
    },
    "info.manual_title": {"it": "Manuale d'uso", "en": "User manual"},
    "info.manual_text": {
        "it": "Il manuale completo — formulazione del modello, descrizione di "
              "ogni comando, caso di verifica riproducibile — è disponibile nella "
              "Guida, organizzata in sezioni navigabili.",
        "en": "The complete manual — model formulation, description of every "
              "control, reproducible verification case — is available in the "
              "Guide, organised into navigable sections.",
    },
    "info.open_guide": {"it": "Apri la Guida", "en": "Open the Guide"},
})


def _read_metadata(plugin_dir):
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(plugin_dir, "metadata.txt"), encoding="utf-8")
    general = cfg["general"] if cfg.has_section("general") else {}
    return {
        "name": general.get("name", "GasNetSim_4Qgis"),
        "version": general.get("version", "?"),
        "description": general.get("about", general.get("description", "")),
        "author": general.get("author", ""),
        "repository": general.get("repository", ""),
    }


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


def _section_title(text):
    lbl = QLabel(text)
    lbl.setStyleSheet("font-weight: bold; margin-top: 6px;")
    return lbl


def _body(text):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    return lbl


class InfoDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.setWindowTitle(tr("info.title"))
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self):
        meta = _read_metadata(self.plugin_dir)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QLabel(meta["name"])
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        sub = QLabel(tr("info.version", version=meta["version"]))
        sub.setStyleSheet("color: gray;")
        layout.addWidget(sub)

        if meta["description"]:
            layout.addWidget(_body(meta["description"]))

        if meta["author"]:
            layout.addWidget(QLabel(tr("info.author", author=meta["author"])))

        if meta["repository"]:
            repo_row = QHBoxLayout()
            repo_row.addWidget(QLabel(tr("info.repository")))
            repo_link = QLabel(
                f'<a href="{meta["repository"]}">{meta["repository"]}</a>')
            repo_link.setOpenExternalLinks(True)
            repo_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
            repo_row.addWidget(repo_link)
            repo_row.addStretch()
            layout.addLayout(repo_row)

        layout.addWidget(_separator())

        # ── Manuale: rimanda alla Guida, non lo duplica ──────────────────────
        layout.addWidget(_section_title(tr("info.manual_title")))
        layout.addWidget(_body(tr("info.manual_text")))
        btn_guide_row = QHBoxLayout()
        btn_guide = QPushButton(tr("info.open_guide"))
        try:
            from PyQt5.QtWidgets import QStyle
            btn_guide.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
        except Exception:
            pass
        btn_guide.clicked.connect(self._open_guide)
        btn_guide_row.addWidget(btn_guide)
        btn_guide_row.addStretch()
        layout.addLayout(btn_guide_row)

        layout.addWidget(_separator())

        layout.addWidget(_section_title(tr("info.license_title")))
        layout.addWidget(_body(tr("info.license_plugin")))
        layout.addWidget(_body(tr("info.license_engine")))

        layout.addWidget(_section_title(tr("info.citation_title")))
        layout.addWidget(_body(tr("info.citation_text")))

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton(tr("info.close"))
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _open_guide(self):
        from .guida_dialog import GuidaDialog
        self.accept()
        GuidaDialog(self.plugin_dir, self.parent()).exec_()
