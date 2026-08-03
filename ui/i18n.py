# -*- coding: utf-8 -*-
"""Infrastruttura minima di internazionalizzazione (IT/EN) per la UI statica
del plugin (bottoni, titoli, tooltip, etichette).

Deliberatamente NON copre i messaggi di log/diagnostica generati a runtime
(con testo interpolato) né le stringhe che il codice rilegge per logica
interna (es. controlli tipo `'isole' in msg.lower()`): tradurle richiede
anche aggiornare quella logica, ed e' un lavoro separato.

Uso:
    from .i18n import tr
    label = QLabel(tr("main.header"))
"""
from PyQt5.QtCore import QSettings

_SETTINGS_KEY = "GasNetSim_4Qgis/language"
_DEFAULT_LANG = "it"
_SUPPORTED_LANGS = ("it", "en")

STRINGS = {}


def register(strings: dict):
    """Aggiunge un blocco di traduzioni al dizionario globale.

    Ogni modulo UI chiama `register({...})` con le proprie chiavi al
    momento dell'import, cosi' le stringhe restano vicine a chi le usa
    invece che tutte ammassate in questo file.
    """
    STRINGS.update(strings)


def get_language() -> str:
    lang = QSettings().value(_SETTINGS_KEY, _DEFAULT_LANG)
    return lang if lang in _SUPPORTED_LANGS else _DEFAULT_LANG


def set_language(lang: str):
    if lang not in _SUPPORTED_LANGS:
        raise ValueError(f"Lingua non supportata: {lang!r}")
    QSettings().setValue(_SETTINGS_KEY, lang)


def tr(key: str, **kwargs) -> str:
    """Restituisce la stringa tradotta per `key` nella lingua corrente.

    Fallback: lingua corrente mancante -> italiano -> la chiave stessa
    (cosi' una chiave non ancora tradotta e' comunque visibile/debuggabile
    invece di sollevare un'eccezione).
    """
    entry = STRINGS.get(key)
    if entry is None:
        return key
    lang = get_language()
    text = entry.get(lang, entry.get(_DEFAULT_LANG, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
