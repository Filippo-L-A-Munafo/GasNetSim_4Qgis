# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QPushButton,
)

from .i18n import tr, get_language, set_language, register

register({
    "settings.title": {"it": "Impostazioni", "en": "Settings"},
    "settings.language": {"it": "Lingua:", "en": "Language:"},
    "settings.note": {
        "it": "La lingua selezionata si applica alla prossima apertura "
              "di GasNetSim 4Qgis.",
        "en": "The selected language applies the next time you open "
              "GasNetSim 4Qgis.",
    },
    "settings.save": {"it": "Salva", "en": "Save"},
    "settings.cancel": {"it": "Annulla", "en": "Cancel"},
})

_LANG_LABELS = [("it", "Italiano"), ("en", "English")]


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings.title"))
        self.setMinimumWidth(320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.cb_lang = QComboBox()
        for code, label in _LANG_LABELS:
            self.cb_lang.addItem(label, code)
        current = get_language()
        idx = self.cb_lang.findData(current)
        if idx >= 0:
            self.cb_lang.setCurrentIndex(idx)
        form.addRow(tr("settings.language"), self.cb_lang)
        layout.addLayout(form)

        note = QLabel(tr("settings.note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(note)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton(tr("settings.cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_save = QPushButton(tr("settings.save"))
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self):
        set_language(self.cb_lang.currentData())
        self.accept()
