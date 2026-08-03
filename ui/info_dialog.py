# -*- coding: utf-8 -*-
import configparser
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser,
)
from PyQt5.QtCore import Qt

from .i18n import tr, register

register({
    "info.title": {"it": "Informazioni", "en": "About"},
    "info.manual_missing": {
        "it": "Manuale non trovato ({path}).",
        "en": "Manual not found ({path}).",
    },
    "info.close": {"it": "Chiudi", "en": "Close"},
    "info.version": {"it": "Versione {version}", "en": "Version {version}"},
    "info.author": {"it": "Autore: {author}", "en": "Author: {author}"},
    "info.repository": {"it": "Repository:", "en": "Repository:"},
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


class InfoDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.setWindowTitle(tr("info.title"))
        self.resize(720, 640)
        self._build_ui()

    def _build_ui(self):
        meta = _read_metadata(self.plugin_dir)
        layout = QVBoxLayout(self)

        header = QLabel(meta["name"])
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        sub = QLabel(tr("info.version", version=meta["version"]))
        sub.setStyleSheet("color: gray;")
        layout.addWidget(sub)

        if meta["description"]:
            desc = QLabel(meta["description"])
            desc.setWordWrap(True)
            layout.addWidget(desc)

        if meta["author"]:
            author = QLabel(tr("info.author", author=meta["author"]))
            layout.addWidget(author)

        if meta["repository"]:
            repo_row = QHBoxLayout()
            repo_row.addWidget(QLabel(tr("info.repository")))
            repo_link = QLabel(
                f'<a href="{meta["repository"]}">{meta["repository"]}</a>')
            repo_link.setOpenExternalLinks(True)
            repo_row.addWidget(repo_link)
            repo_row.addStretch()
            layout.addLayout(repo_row)

        self.manual_view = QTextBrowser()
        self.manual_view.setOpenExternalLinks(True)
        self._load_manual()
        layout.addWidget(self.manual_view, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton(tr("info.close"))
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _load_manual(self):
        from .i18n import get_language
        if get_language() == "en":
            candidates = ["MANUALE.en.md", "MANUALE.md"]
        else:
            candidates = ["MANUALE.md"]
        for name in candidates:
            path = os.path.join(self.plugin_dir, name)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.manual_view.setMarkdown(f.read())
                return
        path = os.path.join(self.plugin_dir, candidates[0])
        self.manual_view.setPlainText(tr("info.manual_missing", path=path))
