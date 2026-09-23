# -*- coding: utf-8 -*-
"""Resa tipografica della Guida: Markdown -> HTML + foglio di stile.

Perche' non `QTextBrowser.setMarkdown()`: quel percorso costruisce il
documento con la formattazione interna di Qt, non influenzabile da un foglio
di stile. Ne risultano tabelle senza spaziatura fra le celle, titoli quasi
indistinguibili dal corpo del testo e blocchi di codice non evidenziati.
Convertendo qui in HTML si passa invece per il parser CSS di Qt, che supporta
il sottoinsieme necessario (margini, bordi, colori, spaziature, monospazio).

Il convertitore copre esattamente i costrutti usati nella Guida — titoli,
paragrafi, tabelle, elenchi, blocchi di codice, citazioni, righe orizzontali e
la formattazione in linea — senza dipendere da librerie esterne, che
nell'ambiente Python di QGIS non sono garantite.

I colori non sono fissati: derivano dalla palette del widget, cosi' la resa
resta corretta sia con tema chiaro sia con tema scuro di QGIS.
"""
import re

# ── Formattazione in linea ───────────────────────────────────────────────────

_URL_RE = re.compile(r'(?<![\w(])(https?://[^\s<>)]+)')


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _inline(text: str) -> str:
    """Applica grassetto, corsivo, codice e collegamenti.

    Le porzioni fra apici inversi sono protette per prime: al loro interno
    asterischi e trattini bassi restano caratteri letterali.
    """
    out = []
    for i, chunk in enumerate(text.split("`")):
        if i % 2:                                    # dentro `codice`
            out.append(f"<code>{_escape(chunk)}</code>")
            continue
        s = _escape(chunk)
        s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
        s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<i>\1</i>', s)
        s = _URL_RE.sub(r'<a href="\1">\1</a>', s)
        out.append(s)
    return "".join(out)


# ── Blocchi ──────────────────────────────────────────────────────────────────

def _table_html(rows):
    """rows: righe grezze che iniziano con '|'. La seconda e' il separatore."""
    def cells(row):
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    if not rows:
        return ""
    header = cells(rows[0])
    aligns = []
    body = rows[1:]
    if len(rows) > 1 and set(rows[1].replace("|", "").strip()) <= set("-: "):
        for spec in cells(rows[1]):
            spec = spec.strip()
            if spec.startswith(":") and spec.endswith(":"):
                aligns.append("center")
            elif spec.endswith(":"):
                aligns.append("right")
            else:
                aligns.append("left")
        body = rows[2:]

    def align_of(i):
        return aligns[i] if i < len(aligns) else "left"

    html = ['<table width="100%" cellspacing="0" cellpadding="6">']
    html.append("<tr>")
    for i, c in enumerate(header):
        html.append(f'<th align="{align_of(i)}">{_inline(c)}</th>')
    html.append("</tr>")
    for row in body:
        html.append("<tr>")
        for i, c in enumerate(cells(row)):
            html.append(f'<td align="{align_of(i)}">{_inline(c)}</td>')
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)


def _list_html(items, ordered):
    tag = "ol" if ordered else "ul"
    out = [f"<{tag}>"]
    for text, sub in items:
        out.append(f"<li>{_inline(text)}")
        if sub:
            out.append(_list_html(sub, ordered=False))
        out.append("</li>")
    out.append(f"</{tag}>")
    return "".join(out)


_H_RE = re.compile(r'^(#{1,4})\s+(.*)$')
_OL_RE = re.compile(r'^(\s*)(\d+)\.\s+(.*)$')
_UL_RE = re.compile(r'^(\s*)[-*]\s+(.*)$')


def markdown_to_body(md: str) -> str:
    """Converte il Markdown della Guida nel corpo HTML corrispondente."""
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    para, table, quote = [], [], []
    list_items, list_ordered = [], False
    code, in_code = [], False
    indented = []          # blocco di codice indentato (4 spazi), es. equazioni

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def flush_table():
        if table:
            out.append(_table_html(list(table)))
            table.clear()

    def flush_quote():
        if quote:
            out.append("<blockquote>" + _inline(" ".join(quote).strip())
                       + "</blockquote>")
            quote.clear()

    def flush_list():
        if list_items:
            out.append(_list_html(list(list_items), list_ordered))
            list_items.clear()

    def flush_indented():
        # Le equazioni della Guida sono scritte come blocchi indentati: vanno
        # rese in monospazio, altrimenti perdono allineamento e numerazione.
        while indented and not indented[-1].strip():
            indented.pop()
        if indented:
            out.append("<pre>" + _escape("\n".join(indented)) + "</pre>")
            indented.clear()

    def flush_all():
        flush_indented(); flush_para(); flush_table(); flush_quote(); flush_list()

    for raw in lines:
        line = raw.rstrip()

        # Blocchi di codice: tutto letterale fino alla chiusura.
        if line.lstrip().startswith("```"):
            if in_code:
                out.append("<pre>" + _escape("\n".join(code)) + "</pre>")
                code.clear()
                in_code = False
            else:
                flush_all()
                in_code = True
            continue
        if in_code:
            code.append(raw)
            continue

        if not line.strip():
            if indented:           # righe vuote interne al blocco: conservate
                indented.append("")
            else:
                flush_all()
            continue

        # Blocco indentato (4+ spazi) fuori da un elenco: codice/equazione.
        if re.match(r'^(\s{4,}|\t)', raw) and not list_items and not para:
            flush_table(); flush_quote()
            indented.append(re.sub(r'^(\s{4}|\t)', '', raw.rstrip()))
            continue
        if indented:
            flush_indented()

        if line.strip() in ("---", "***", "___"):
            flush_all()
            out.append("<hr/>")
            continue

        m = _H_RE.match(line)
        if m:
            flush_all()
            level = min(len(m.group(1)), 4)
            out.append(f"<h{level}>{_inline(m.group(2).strip())}</h{level}>")
            continue

        if line.lstrip().startswith(">"):
            flush_para(); flush_table(); flush_list()
            quote.append(line.lstrip()[1:].strip())
            continue

        if line.startswith("|"):
            flush_para(); flush_quote(); flush_list()
            table.append(line)
            continue

        m_ol, m_ul = _OL_RE.match(line), _UL_RE.match(line)
        if m_ol or m_ul:
            indent = len((m_ol or m_ul).group(1))
            text = (m_ol.group(3) if m_ol else m_ul.group(2)).strip()
            ordered = bool(m_ol)
            flush_para(); flush_table(); flush_quote()
            if indent >= 2 and list_items:          # elemento annidato
                list_items[-1][1].append([text, []])
            else:
                if list_items and ordered != list_ordered:
                    flush_list()
                list_ordered = ordered
                list_items.append([text, []])
            continue

        # Riga indentata che prosegue l'ultimo elemento di elenco.
        if (raw.startswith("  ") or raw.startswith("\t")) and list_items:
            target = (list_items[-1][1][-1] if list_items[-1][1] else list_items[-1])
            target[0] = target[0] + " " + line.strip()
            continue

        flush_table(); flush_quote(); flush_list()
        para.append(line.strip())

    if in_code and code:
        out.append("<pre>" + _escape("\n".join(code)) + "</pre>")
    flush_all()
    flush_indented()
    return "\n".join(out)


# ── Foglio di stile ──────────────────────────────────────────────────────────

def build_stylesheet(text, base, accent, border, code_bg, muted,
                     header_bg, base_pt=10):
    """CSS per QTextDocument. Solo proprieta' supportate dal parser di Qt."""
    return f"""
    body {{ color: {text}; background-color: {base};
            font-size: {base_pt}pt; }}
    p    {{ margin-top: 6px; margin-bottom: 6px; }}
    h1   {{ font-size: {base_pt + 7}pt; font-weight: bold; color: {accent};
            margin-top: 2px; margin-bottom: 14px;
            padding-bottom: 6px; border-bottom: 2px solid {accent}; }}
    h2   {{ font-size: {base_pt + 3}pt; font-weight: bold; color: {text};
            margin-top: 22px; margin-bottom: 8px;
            padding-bottom: 3px; border-bottom: 1px solid {border}; }}
    h3   {{ font-size: {base_pt + 1}pt; font-weight: bold; color: {accent};
            margin-top: 16px; margin-bottom: 6px; }}
    h4   {{ font-size: {base_pt}pt; font-weight: bold; color: {text};
            margin-top: 12px; margin-bottom: 4px; }}
    table {{ border: 1px solid {border}; margin-top: 10px; margin-bottom: 14px; }}
    th   {{ background-color: {header_bg}; color: {text}; font-weight: bold;
            border: 1px solid {border}; }}
    td   {{ border: 1px solid {border}; }}
    pre  {{ background-color: {code_bg}; color: {text};
            font-family: 'Consolas', 'DejaVu Sans Mono', monospace;
            font-size: {base_pt - 1}pt;
            margin-top: 10px; margin-bottom: 12px;
            padding: 10px; border: 1px solid {border}; }}
    code {{ background-color: {code_bg};
            font-family: 'Consolas', 'DejaVu Sans Mono', monospace;
            font-size: {base_pt - 1}pt; }}
    blockquote {{ color: {muted}; margin-left: 14px; margin-right: 14px;
                  margin-top: 10px; margin-bottom: 10px;
                  padding-left: 12px; border-left: 3px solid {border}; }}
    li   {{ margin-top: 3px; margin-bottom: 3px; }}
    hr   {{ border: 1px solid {border}; }}
    a    {{ color: {accent}; }}
    """


def _mix(c1, c2, ratio):
    """Miscela due QColor: ratio=0 -> c1, ratio=1 -> c2."""
    return type(c1)(
        int(c1.red() * (1 - ratio) + c2.red() * ratio),
        int(c1.green() * (1 - ratio) + c2.green() * ratio),
        int(c1.blue() * (1 - ratio) + c2.blue() * ratio),
    )


def stylesheet_from_palette(palette, base_pt=10):
    """Costruisce il CSS a partire dalla palette corrente del widget.

    I colori sono derivati, non fissati: la Guida resta leggibile sia con il
    tema chiaro sia con quello scuro di QGIS.
    """
    from PyQt5.QtGui import QPalette

    text = palette.color(QPalette.Text)
    base = palette.color(QPalette.Base)
    accent = palette.color(QPalette.Highlight)

    # Un accento troppo vicino allo sfondo risulterebbe illeggibile: in quel
    # caso si ripiega sul colore del testo.
    if abs(accent.lightness() - base.lightness()) < 60:
        accent = _mix(text, accent, 0.35)

    return build_stylesheet(
        text=text.name(),
        base=base.name(),
        accent=accent.name(),
        border=_mix(base, text, 0.32).name(),
        code_bg=_mix(base, text, 0.07).name(),
        muted=_mix(text, base, 0.35).name(),
        header_bg=_mix(base, text, 0.13).name(),
        base_pt=base_pt,
    )


def markdown_to_html(md: str) -> str:
    """Documento HTML completo, da passare a QTextBrowser.setHtml()."""
    return "<html><body>" + markdown_to_body(md) + "</body></html>"
