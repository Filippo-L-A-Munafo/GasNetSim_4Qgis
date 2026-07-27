# -*- coding: utf-8 -*-
"""
Visualizzazione colorimetrica dei risultati di simulazione GasNetSim su QGIS.

Dopo una simulazione conversa, chiama apply_results_to_layers() per creare
layer di risultati nel progetto QGIS con colorimetria graduata.

Campi disponibili per i nodi:
  pressure_bar   — pressione (bar)
  temperature_k  — temperatura (K)
  sp_gravity     — peso specifico del gas (adimensionale)
  z_factor       — fattore di compressibilità Z (adimensionale)
  hhv_mj_sm3     — potere calorifico superiore (MJ/sm3)
  density_kg_m3  — densità del gas (kg/m3)

Campi disponibili per le condotte:
  flow_sm3s        — portata volumetrica (sm3/s, positiva o negativa)
  flow_abs_sm3s    — portata assoluta (sm3/s, sempre >= 0)
  velocity_m_s     — velocità media del gas (m/s)
  avg_pressure_bar — pressione media nella condotta (bar)
  sp_gravity       — peso specifico del gas (adimensionale)
"""

from qgis.core import (
    QgsVectorLayer, QgsField, QgsFeature, QgsProject,
    QgsGraduatedSymbolRenderer, QgsSingleSymbolRenderer,
    QgsStyle, QgsSymbol,
    QgsWkbTypes, QgsSimpleLineSymbolLayer,
    QgsMarkerLineSymbolLayer, QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase, QgsMarkerSymbol, QgsGeometry,
    QgsProperty, QgsSymbolLayer, QgsUnitTypes,
    QgsPalLayerSettings, QgsVectorLayerSimpleLabeling, QgsTextFormat,
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor, QFont
import re as _re

# Rimuove parole di tipo ridondanti (nodi/condotte) dal nome del layer sorgente
_STRIP_TYPE_RE = _re.compile(
    r'^(nodi|condotte|nodes?|pipes?)[\s_\-]+|[\s_\-]+(nodi|condotte|nodes?|pipes?)$',
    _re.IGNORECASE,
)


def _clean_layer_name(name):
    """Rimuove il termine di tipo (nodi/condotte) dal nome del layer per evitare
    ridondanza con il prefisso R-N-/R-P-."""
    cleaned = _STRIP_TYPE_RE.sub('', name).strip(' _-')
    return cleaned or name  # fallback al nome originale se risulta vuoto


# Ramp predefinita per ogni campo risultato: blu (basso) → rosso (alto)
_RAMP = ('RdBu', True)   # RdBu con reverse=True → blu=min, rosso=max
_RAMP_FOR_FIELD = {
    'pressure_bar':          _RAMP,
    'temperature_k':         _RAMP,
    'sp_gravity':            _RAMP,
    'z_factor':              _RAMP,
    'hhv_mj_sm3':            _RAMP,
    'density_kg_m3':         _RAMP,
    'molar_mass':            _RAMP,
    'std_density_kg_sm3':    _RAMP,
    'wobbe_mj_sm3':          _RAMP,
    'flow_abs_sm3h':         _RAMP,
    'flow_sm3h':             _RAMP,
    'velocity_m_s':          _RAMP,
    'avg_pressure_bar':      _RAMP,
    'volumetric_flow_sm3s':  _RAMP,
    'energy_flow_mw':        _RAMP,
    'throughput_sm3h':       _RAMP,
    'h2_pct':                ('YlOrRd', False),  # bianco/giallo (0%) → rosso (alto%)
}


# ─────────────────────────────────────────────────────────────────────────────
# Frecce direzionali
# ─────────────────────────────────────────────────────────────────────────────

def _add_arrow_markers_to_renderer(layer, log=None):
    """
    Aggiunge una freccia direzionale per condotta al renderer.

    Posiziona UNA freccia al punto centrale di ogni segmento (CentralPoint),
    con forma Arrow (punta aperta), orientata dal segno di flow_sm3s.
    La dimensione è in mm su schermo, quindi rimane costante con lo zoom.
    """
    def _log(msg):
        if log:
            log(msg)
    try:
        layer.setLabelsEnabled(False)

        # ── Testa di freccia (forma Arrow, punta aperta) ─────────────────
        arrow_head = QgsSimpleMarkerSymbolLayer()
        # Usa ArrowHead (punta aperta) o Triangle come fallback.
        # NON usare 'Arrow': in QGIS punta a destra (est) a 0°, causando frecce perpendicolari.
        for shape_name in ('ArrowHead', 'ArrowHeadFilled', 'Triangle'):
            shape = getattr(QgsSimpleMarkerSymbolLayerBase, shape_name, None)
            if shape is not None:
                arrow_head.setShape(shape)
                break

        arrow_head.setSize(5.0)
        arrow_head.setColor(QColor(255, 255, 255, 220))
        arrow_head.setStrokeColor(QColor(20, 20, 20))
        arrow_head.setStrokeWidth(0.5)

        # Rotazione data-driven: 0° = lungo flusso, 180° = contro flusso
        try:
            arrow_head.setDataDefinedProperty(
                QgsSymbolLayer.PropertyAngle,
                QgsProperty.fromExpression('if("flow_sm3h" >= 0, 0, 180)')
            )
        except Exception as e:
            _log(f"[arrows] data-defined angle: {e}")

        marker_sym = QgsMarkerSymbol()
        marker_sym.deleteSymbolLayer(0)
        marker_sym.appendSymbolLayer(arrow_head)

        # ── Una freccia per condotta, al punto centrale ───────────────────
        marker_line = QgsMarkerLineSymbolLayer()
        # CentralPoint = una sola freccia per segmento, al centro
        central = getattr(QgsMarkerLineSymbolLayer, 'CentralPoint', None)
        if central is None:
            central = getattr(QgsMarkerLineSymbolLayer, 'Interval', 3)
        try:
            marker_line.setPlacements(central)
        except (AttributeError, TypeError):
            try:
                marker_line.setPlacement(central)
            except Exception:
                pass
        marker_line.setSubSymbol(marker_sym)
        marker_line.setRotateMarker(True)

        # ── Aggiunge la freccia a ogni classe del renderer graduato ──────
        renderer = layer.renderer()
        if renderer is None:
            _log("[arrows] renderer None, skip")
            return
        if hasattr(renderer, 'ranges'):
            for i, rng in enumerate(renderer.ranges()):
                sym = rng.symbol()
                if sym is not None:
                    sym_clone = sym.clone()
                    sym_clone.appendSymbolLayer(marker_line.clone())
                    renderer.updateRangeSymbol(i, sym_clone)
            _log(f"[arrows] frecce centrali aggiunte a {len(renderer.ranges())} classi")
        elif hasattr(renderer, 'symbol') and callable(renderer.symbol):
            sym = renderer.symbol()
            if sym is not None:
                sym.appendSymbolLayer(marker_line.clone())
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        _log("[arrows] frecce direzionali attivate (1 per condotta, al centro)")
    except Exception as e:
        import traceback
        _log(f"[arrows] errore: {e}\n{traceback.format_exc()}")


def _add_flow_arrows(res_pipes, log=None):
    """
    Aggiunge frecce direzionali al layer condotte tramite expression data-driven.
    Le geometrie NON vengono modificate.
    """
    _add_arrow_markers_to_renderer(res_pipes, log=log)


def _next_result_idx(base_name):
    """Restituisce il prossimo indice #N disponibile per un nome base risultato."""
    existing = {lyr.name() for lyr in QgsProject.instance().mapLayers().values()}
    n = 1
    while f"{base_name} #{n}" in existing:
        n += 1
    return n


def apply_results_to_layers(
    result,
    nodes_lyr,
    pipes_lyr,
    log=None,
    result_nodes_color='pressure_bar',
    result_nodes_fields=None,
    result_nodes_size=None,
    result_pipes_color='flow_abs_sm3h',
    result_pipes_fields=None,
    flow_arrows=True,
    decimals=4,
    orig_nodes_lyr=None,
    orig_pipes_lyr=None,
    show_orig_pipes_layer=True,
):
    """
    Estrae i risultati dal network GasNetSim e crea layer di visualizzazione
    con colorimetria graduata nel progetto QGIS corrente.

    Parameters
    ----------
    result                : oggetto rete GasNetSim post-simulazione
    nodes_lyr             : QgsVectorLayer (punti) usato per la simulazione
    pipes_lyr             : QgsVectorLayer (linee) usato per la simulazione
    log                   : callable(str) per messaggi, opzionale
    result_nodes_color    : campo su cui applicare la colorimetria dei nodi
    result_nodes_fields   : lista di campi da includere nel layer nodi
                            (None = tutti disponibili)
    result_pipes_color    : campo su cui applicare la colorimetria condotte
    result_pipes_fields   : lista di campi da includere nel layer condotte
                            (None = tutti disponibili)
    decimals              : cifre decimali per i valori nei layer risultato
                            (default 4)
    orig_nodes_lyr        : QgsVectorLayer (punti) layer nodi originale pre-collasso
                            (opzionale): se fornito, i suoi campi vengono uniti
                            al layer risultato tramite fid_ut
    orig_pipes_lyr        : QgsVectorLayer (linee) layer condotte originale non collassate
                            (opzionale): se fornito, crea un layer risultato aggiuntivo
                            con le geometrie originali e i risultati proiettati

    Returns
    -------
    (res_nodes_lyr, res_pipes_lyr)  — possono essere None
    """
    def _log(msg):
        if log:
            log(msg)

    # Default: se non specificato, includi tutti i campi
    if result_nodes_fields is None:
        result_nodes_fields = [
            'pressure_bar', 'temperature_k', 'sp_gravity',
            'z_factor', 'hhv_mj_sm3', 'wobbe_mj_sm3',
            'density_kg_m3', 'std_density_kg_sm3', 'molar_mass',
            'h2_pct', 'gas_comp', 'throughput_sm3h',
            'volumetric_flow_sm3s', 'energy_flow_mw',
        ]
    # Assicura che il campo dimensione sia sempre incluso nel layer
    if result_nodes_size and result_nodes_size not in result_nodes_fields:
        result_nodes_fields = list(result_nodes_fields) + [result_nodes_size]
    if result_pipes_fields is None:
        result_pipes_fields = [
            'flow_sm3h', 'flow_abs_sm3h', 'velocity_m_s',
            'avg_pressure_bar', 'sp_gravity', 'z_factor', 'density_kg_m3',
        ]

    # ── Estrazione dati nodi ──────────────────────────────────────────────
    node_data = _extract_node_data(result)
    # ── Estrazione dati condotte ─────────────────────────────────────────
    pipe_data = _extract_pipe_data(result)

    _log(f"Risultati estratti: {len(node_data)} nodi, {len(pipe_data)} condotte")

    res_nodes = None
    res_pipes = None

    # ── Debug: mostra sample chiavi per diagnostica ───────────────────────
    if node_data:
        sample_keys = list(node_data.keys())[:3]
        _log(f"[DEBUG] node_data: {len(node_data)} nodi, chiavi es: {sample_keys}")
    else:
        _log("[DEBUG] node_data: VUOTO — nessun risultato estratto dai nodi")
    if pipe_data:
        sample_keys_p = list(pipe_data.keys())[:3]
        _log(f"[DEBUG] pipe_data: {len(pipe_data)} condotte, chiavi es: {sample_keys_p}")
    else:
        _log("[DEBUG] pipe_data: VUOTO — nessun risultato estratto dalle condotte")

    if nodes_lyr is not None:
        node_id_idx = nodes_lyr.fields().indexOf('node_id')
        if node_id_idx >= 0:
            sample_feat_keys = []
            for feat in nodes_lyr.getFeatures():
                sample_feat_keys.append(str(feat['node_id']))
                if len(sample_feat_keys) >= 3:
                    break
            _log(f"[DEBUG] nodes_lyr '{nodes_lyr.name()}': node_id field idx={node_id_idx}, "
                 f"es feat_key: {sample_feat_keys}")
        else:
            _log(f"[DEBUG] nodes_lyr '{nodes_lyr.name()}': campo 'node_id' NON TROVATO. "
                 f"Campi disponibili: {[f.name() for f in nodes_lyr.fields()]}")

    if pipes_lyr is not None:
        pipe_id_idx = pipes_lyr.fields().indexOf('pipe_id')
        if pipe_id_idx >= 0:
            sample_feat_keys_p = []
            for feat in pipes_lyr.getFeatures():
                sample_feat_keys_p.append(str(feat['pipe_id']))
                if len(sample_feat_keys_p) >= 3:
                    break
            _log(f"[DEBUG] pipes_lyr '{pipes_lyr.name()}': pipe_id field idx={pipe_id_idx}, "
                 f"es feat_key: {sample_feat_keys_p}")
        else:
            _log(f"[DEBUG] pipes_lyr '{pipes_lyr.name()}': campo 'pipe_id' NON TROVATO. "
                 f"Campi disponibili: {[f.name() for f in pipes_lyr.fields()]}")

    # ── Layer nodi ────────────────────────────────────────────────────────
    if nodes_lyr is not None and node_data:
        available_n = _available_fields(node_data, result_nodes_fields)
        if available_n:
            color_field = result_nodes_color if result_nodes_color in available_n \
                          else available_n[0]
            try:
                _orig_n = orig_nodes_lyr.name() if orig_nodes_lyr is not None else nodes_lyr.name()
                _base_n = f"R-N-{_clean_layer_name(_orig_n)}"
                name = f"{_base_n} #{_next_result_idx(_base_n)}"
                res_nodes = _make_multi_field_layer(
                    source_lyr=nodes_lyr,
                    data_dict=node_data,
                    fields=available_n,
                    id_field='node_id',
                    layer_name=name,
                    decimals=decimals,
                )
                _log(f"[DEBUG] layer nodi creato: {res_nodes.featureCount()} features, "
                     f"campi: {[f.name() for f in res_nodes.fields()]}")
                ramp_name, reverse = _RAMP_FOR_FIELD.get(
                    color_field, ('RdYlGn', False))
                _apply_graduated(res_nodes, color_field,
                                 ramp_name=ramp_name, reverse=reverse)
                if result_nodes_size and result_nodes_size in available_n:
                    _apply_node_proportional_size(res_nodes, result_nodes_size)
                # Arricchisce con i campi del layer nodi originale (pre-collasso)
                if orig_nodes_lyr is not None:
                    try:
                        _enrich_with_orig(res_nodes, orig_nodes_lyr)
                        _log("[OK] Campi nodi originali aggiunti al layer risultato")
                    except Exception as _e:
                        _log(f"[warn] enrich orig nodes: {_e}")
                QgsProject.instance().addMapLayer(res_nodes)
                _log(f"[OK] {name}  ({res_nodes.featureCount()} nodi, "
                     f"colora per: {color_field})")

            except Exception as exc:
                import traceback
                _log(f"Errore layer nodi: {exc}\n{traceback.format_exc()}")
        else:
            _log(f"[DEBUG] available_n vuoto. result_nodes_fields={result_nodes_fields}")

    # ── Layer condotte ────────────────────────────────────────────────────
    if pipes_lyr is not None and pipe_data:
        # Assicura che flow_abs_sm3s sia incluso (serve per spessore linea)
        fields_pipes = list(result_pipes_fields)
        first_pipe = pipe_data.get(next(iter(pipe_data)), {})
        if 'flow_sm3h' in first_pipe and 'flow_abs_sm3h' not in fields_pipes:
            fields_pipes.append('flow_abs_sm3h')
        available_p = _available_fields(pipe_data, fields_pipes)
        if available_p:
            color_field = result_pipes_color if result_pipes_color in available_p \
                          else available_p[0]
            try:
                _orig_p = orig_pipes_lyr.name() if orig_pipes_lyr is not None else pipes_lyr.name()
                _base_p = f"R-P-{_clean_layer_name(_orig_p)}"
                name = f"{_base_p} #{_next_result_idx(_base_p)}"
                res_pipes = _make_multi_field_layer(
                    source_lyr=pipes_lyr,
                    data_dict=pipe_data,
                    fields=available_p,
                    id_field='pipe_id',
                    layer_name=name,
                    decimals=decimals,
                )
                _log(f"[DEBUG] layer condotte creato: {res_pipes.featureCount()} features")
                ramp_name, reverse = _RAMP_FOR_FIELD.get(
                    color_field, ('Blues', False))
                _apply_graduated(res_pipes, color_field,
                                 ramp_name=ramp_name, reverse=reverse)
                width_field = 'flow_abs_sm3h' if 'flow_abs_sm3h' in available_p \
                              else (color_field if color_field != 'sp_gravity' else None)
                if width_field:
                    _set_line_width_expression(res_pipes, width_field)
                if flow_arrows:
                    _add_flow_arrows(res_pipes, log=_log)
                QgsProject.instance().addMapLayer(res_pipes)
                _log(f"[OK] {name}  ({res_pipes.featureCount()} condotte, "
                     f"colora per: {color_field})")
                # Layer risultato su condotte originali (non collassate)
                if show_orig_pipes_layer and orig_pipes_lyr is not None and orig_pipes_lyr is not pipes_lyr:
                    try:
                        apply_results_to_orig_pipes(
                            result=result,
                            orig_pipes_lyr=orig_pipes_lyr,
                            collapsed_pipes_lyr=pipes_lyr,
                            decimals=decimals,
                            log=_log,
                            result_pipes_color=result_pipes_color,
                            result_pipes_fields=result_pipes_fields,
                            flow_arrows=flow_arrows,
                        )
                    except Exception as _e:
                        _log(f"[warn] orig pipes layer: {_e}")
            except Exception as exc:
                import traceback
                _log(f"Errore layer condotte: {exc}\n{traceback.format_exc()}")
        else:
            _log(f"[DEBUG] available_p vuoto. result_pipes_fields={result_pipes_fields}")

    return res_nodes, res_pipes


def recolor_result_layer(layer, field_name, add_arrows=False, size_field=None, log=None):
    """
    Riapplica la colorimetria graduata su un layer risultato esistente.
    Non modifica le geometrie. Usata dal pannello di visualizzazione
    per cambiare il campo di colore senza rieseguire la simulazione.
    """
    ramp_name, reverse = _RAMP_FOR_FIELD.get(field_name, _RAMP)
    _apply_graduated(layer, field_name, ramp_name=ramp_name, reverse=reverse)
    if size_field:
        _apply_node_proportional_size(layer, size_field)
    if add_arrows:
        _add_arrow_markers_to_renderer(layer, log=(log or (lambda m: None)))
    else:
        layer.setLabelsEnabled(False)
    layer.triggerRepaint()


def _apply_node_proportional_size(layer, size_field, min_mm=2.0, max_mm=12.0):
    """
    Imposta il diametro del simbolo nodo proporzionale al valore assoluto di
    size_field, scalato linearmente da min_mm (valore 0) a max_mm (massimo).
    Funziona sia su renderer graduated che single-symbol.
    Il valore massimo viene pre-calcolato in Python per evitare problemi con
    le funzioni aggregate QGIS nelle data-defined properties.
    """
    try:
        renderer = layer.renderer()
        if renderer is None:
            return
        # Pre-calcola il massimo valore assoluto del campo
        max_val = 0.0
        idx = layer.fields().indexOf(size_field)
        if idx < 0:
            return  # campo non trovato
        for feat in layer.getFeatures():
            v = feat.attributes()[idx]
            if v is not None and v != '' and str(v).upper() != 'NULL':
                try:
                    max_val = max(max_val, abs(float(v)))
                except (TypeError, ValueError):
                    pass
        if max_val == 0.0:
            return  # tutti zero, nessun dimensionamento

        expr = (
            f'scale_linear(abs("{size_field}"), 0, {max_val}, {min_mm}, {max_mm})'
        )
        dd_prop = QgsProperty.fromExpression(expr)

        def _apply_to_sym(sym):
            for i in range(sym.symbolLayerCount()):
                sl = sym.symbolLayer(i)
                if isinstance(sl, QgsSimpleMarkerSymbolLayer):
                    sl.setDataDefinedProperty(
                        QgsSymbolLayer.PropertySize, dd_prop)

        if isinstance(renderer, QgsGraduatedSymbolRenderer):
            for rng in renderer.ranges():
                if rng.symbol() is not None:
                    _apply_to_sym(rng.symbol())
        elif isinstance(renderer, QgsSingleSymbolRenderer):
            if renderer.symbol() is not None:
                _apply_to_sym(renderer.symbol())
        layer.triggerRepaint()
    except Exception:
        import traceback
        traceback.print_exc()


def _enrich_with_orig(result_lyr, orig_lyr):
    """
    Arricchisce il layer risultato nodi con tutti i campi del layer sorgente
    originale (pre-collasso), usando il campo 'fid_ut' come chiave di join.
    I campi già presenti nel layer risultato vengono ignorati.
    """
    try:
        prov = result_lyr.dataProvider()
        # Campi già presenti
        existing = {f.name().lower() for f in result_lyr.fields()}
        # Campi da aggiungere (tutti quelli di orig_lyr non già presenti)
        new_fields = [
            f for f in orig_lyr.fields()
            if f.name().lower() not in existing
        ]
        if not new_fields:
            return
        # Prefissa con 'orig_' per evitare collisioni future
        from qgis.core import QgsField
        from PyQt5.QtCore import QVariant
        added_fields = []
        for f in new_fields:
            fname = f'orig_{f.name()}'
            if fname.lower() in existing:
                continue
            added_fields.append((f.name(), fname, f.type()))
            prov.addAttributes([QgsField(fname, f.type(), f.typeName(), f.length(), f.precision())])
        result_lyr.updateFields()
        if not added_fields:
            return

        # Build fid → feature dict from orig_lyr.
        # IMPORTANT: fid_ut in the result layer stores the VALUE of the 'fid'
        # field from the original user-nodes layer (set in make_memory_layers).
        # We must look up by that field value, NOT by the QGIS internal .id()
        # (which is a separate auto-assigned integer and does NOT match 'fid').
        fid_field_idx = orig_lyr.fields().indexOf('fid')
        if fid_field_idx >= 0:
            orig_by_fid = {}
            for feat in orig_lyr.getFeatures():
                try:
                    v = feat.attributes()[fid_field_idx]
                    key = int(v) if v is not None and str(v).upper() not in ('NULL', '') else int(feat.id())
                    orig_by_fid[key] = feat
                except (TypeError, ValueError):
                    orig_by_fid[feat.id()] = feat
        else:
            # Nessun campo 'fid' — usa l'ID interno QGIS (coerente con make_memory_layers)
            orig_by_fid = {feat.id(): feat for feat in orig_lyr.getFeatures()}

        fid_ut_idx = result_lyr.fields().indexOf('fid_ut')
        if fid_ut_idx < 0:
            return  # nessun campo di join disponibile

        # Aggiorna attributi
        result_lyr.startEditing()
        for feat in result_lyr.getFeatures():
            fid_ut = feat.attributes()[fid_ut_idx]
            if fid_ut is None or fid_ut == -1:
                continue
            try:
                orig_feat = orig_by_fid.get(int(fid_ut))
            except (TypeError, ValueError):
                continue
            if orig_feat is None:
                continue
            for src_name, dst_name, _ in added_fields:
                dst_idx = result_lyr.fields().indexOf(dst_name)
                if dst_idx >= 0:
                    try:
                        val = orig_feat[src_name]
                        result_lyr.changeAttributeValue(feat.id(), dst_idx, val)
                    except Exception:
                        pass
        result_lyr.commitChanges()
    except Exception:
        import traceback
        traceback.print_exc()


def apply_results_to_orig_pipes(result, orig_pipes_lyr, collapsed_pipes_lyr,
                                 decimals=4, log=None,
                                 result_pipes_color='flow_abs_sm3h',
                                 result_pipes_fields=None,
                                 flow_arrows=True):
    """
    Crea un layer risultato sulle condotte originali (non collassate)
    proiettando i risultati di simulazione dalle condotte collassate tramite
    corrispondenza geometrica per punto medio.

    Parameters
    ----------
    result              : oggetto rete GasNetSim post-simulazione
    orig_pipes_lyr      : QgsVectorLayer (linee) — condotte originali non collassate
    collapsed_pipes_lyr : QgsVectorLayer (linee) — condotte collassate usate nella simulazione
    decimals            : cifre decimali per i valori
    log                 : callable(str) per messaggi, opzionale
    result_pipes_color  : campo per la colorimetria
    result_pipes_fields : lista campi da includere (None = tutti disponibili)
    flow_arrows         : aggiunge frecce direzionali

    Returns
    -------
    QgsVectorLayer o None
    """
    def _log(msg):
        if log:
            log(msg)

    try:
        from qgis.core import QgsSpatialIndex, QgsGeometry
        pipe_data = _extract_pipe_data(result)
        if not pipe_data:
            _log("[orig_pipes] nessun dato condotte disponibile")
            return None

        if result_pipes_fields is None:
            result_pipes_fields = [
                'flow_sm3h', 'flow_abs_sm3h', 'velocity_m_s',
                'avg_pressure_bar', 'sp_gravity', 'z_factor', 'density_kg_m3',
            ]
        # Assicura flow_abs_sm3h
        fields_pipes = list(result_pipes_fields)
        if 'flow_abs_sm3h' not in fields_pipes:
            fields_pipes.append('flow_abs_sm3h')
        available_p = _available_fields(pipe_data, fields_pipes)
        if not available_p:
            _log("[orig_pipes] nessun campo risultato disponibile")
            return None

        # Build spatial index sui punti medi delle condotte collassate
        # mapping: feature_id → pipe_id (campo 'pipe_id' del layer collassato)
        collapsed_midpoints = {}   # feat_id → midpoint QgsGeometry
        collapsed_fid_to_pipeid = {}  # feat_id → str(pipe_id)
        for feat in collapsed_pipes_lyr.getFeatures():
            geom = feat.geometry()
            if geom is None or geom.isNull():
                continue
            mid = geom.interpolate(geom.length() / 2.0)
            collapsed_midpoints[feat.id()] = mid
            pid = feat.attribute('pipe_id')
            if pid is not None:
                collapsed_fid_to_pipeid[feat.id()] = str(pid)

        if not collapsed_midpoints:
            _log("[orig_pipes] layer condotte collassate senza geometrie valide")
            return None

        # Costruisci indice spaziale per i punti medi collassati
        spatial_idx = QgsSpatialIndex()
        # Crea feature fittizie per l'indice (solo geometrie punto)
        from qgis.core import QgsFeature as _QF
        tmp_feats = []
        for fid, mid_geom in collapsed_midpoints.items():
            tmp = _QF()
            tmp.setId(fid)
            tmp.setGeometry(mid_geom)
            tmp_feats.append(tmp)
        spatial_idx.addFeatures(tmp_feats)

        # Per ogni condotta originale: trova la condotta collassata più vicina
        # data_dict keyed by str(orig_feat_id)
        orig_data_dict = {}
        for orig_feat in orig_pipes_lyr.getFeatures():
            geom = orig_feat.geometry()
            if geom is None or geom.isNull():
                continue
            orig_mid = geom.interpolate(geom.length() / 2.0)
            nearest = spatial_idx.nearestNeighbor(orig_mid.asPoint(), 1)
            if not nearest:
                continue
            collapsed_fid = nearest[0]
            pipe_id_str = collapsed_fid_to_pipeid.get(collapsed_fid)
            if pipe_id_str and pipe_id_str in pipe_data:
                orig_data_dict[str(orig_feat.id())] = pipe_data[pipe_id_str]

        if not orig_data_dict:
            _log("[orig_pipes] nessuna corrispondenza trovata tra condotte originali e collassate")
            return None

        # Usa _make_multi_field_layer con id_field = 'fid' (usare feature id)
        # Ma i feature id non sono un attributo — usiamo un campo ausiliario
        # Aggiungiamo temporaneamente 'orig_fid' al layer originale in memoria
        from qgis.core import QgsVectorLayer, QgsField
        from PyQt5.QtCore import QVariant

        # Clona il layer originale in memoria per aggiungere il campo fid temporaneo
        crs_str = orig_pipes_lyr.crs().authid()
        geom_type_str = 'LineString'
        mem_src = QgsVectorLayer(f"{geom_type_str}?crs={crs_str}", "_tmp_src", "memory")
        mp = mem_src.dataProvider()
        mp.addAttributes(orig_pipes_lyr.fields().toList())
        mp.addAttributes([QgsField('_orig_fid', QVariant.String)])
        mem_src.updateFields()
        feats_to_add = []
        for orig_feat in orig_pipes_lyr.getFeatures():
            nf = _QF(mem_src.fields())
            nf.setGeometry(orig_feat.geometry())
            for f in orig_pipes_lyr.fields():
                try:
                    nf.setAttribute(f.name(), orig_feat[f.name()])
                except Exception:
                    pass
            nf.setAttribute('_orig_fid', str(orig_feat.id()))
            feats_to_add.append(nf)
        mp.addFeatures(feats_to_add)
        mem_src.updateExtents()

        # Rinomina le chiavi di orig_data_dict con la stringa dell'id originale
        # (già lo sono, perché usiamo str(orig_feat.id()) come chiave)

        color_field = result_pipes_color if result_pipes_color in available_p else available_p[0]
        _base_po = f"R-P-orig-{_clean_layer_name(orig_pipes_lyr.name())}"
        name = f"{_base_po} #{_next_result_idx(_base_po)}"
        res_orig = _make_multi_field_layer(
            source_lyr=mem_src,
            data_dict=orig_data_dict,
            fields=available_p,
            id_field='_orig_fid',
            layer_name=name,
            decimals=decimals,
        )
        ramp_name, reverse = _RAMP_FOR_FIELD.get(color_field, ('Blues', False))
        _apply_graduated(res_orig, color_field, ramp_name=ramp_name, reverse=reverse)
        width_field = 'flow_abs_sm3h' if 'flow_abs_sm3h' in available_p else color_field
        if width_field:
            _set_line_width_expression(res_orig, width_field)
        if flow_arrows:
            _add_flow_arrows(res_orig, log=_log)
        QgsProject.instance().addMapLayer(res_orig)
        _log(f"[OK] {name}  ({res_orig.featureCount()} condotte, colora per: {color_field})")
        return res_orig
    except Exception as exc:
        import traceback
        _log(f"[orig_pipes] errore: {exc}\n{traceback.format_exc()}")
        return None


def export_layer_to_csv(layer, filepath, decimals=4):
    """
    Esporta tutti gli attributi del layer in un file CSV separato da punto e virgola.
    I valori float vengono arrotondati a `decimals` cifre decimali.

    Parameters
    ----------
    layer    : QgsVectorLayer  — layer da esportare
    filepath : str             — percorso del file .csv di destinazione
    decimals : int             — cifre decimali per i valori float (default 4)
    """
    import csv
    fields = [f.name() for f in layer.fields()]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(fields)
        for feat in layer.getFeatures():
            row = []
            for val in feat.attributes():
                if isinstance(val, float):
                    row.append(round(val, decimals))
                elif val is None:
                    row.append('')
                else:
                    row.append(val)
            writer.writerow(row)


# ─────────────────────────────────────────────────────────────────────────────
# Estrazione dati dal network GasNetSim
# ─────────────────────────────────────────────────────────────────────────────

def _extract_node_data(result):
    """Ritorna {str(node_id): {field: value}} con tutti i campi disponibili."""
    from pathlib import Path
    if isinstance(result, (str, Path)):
        import pandas as pd
        csv_file = Path(result) / 'results_nodes.csv'
        if not csv_file.exists():
            return {}
        try:
            df = pd.read_csv(csv_file, sep=';', dtype=str)
            data = {}
            for _, row in df.iterrows():
                if pd.isna(row.get('node_id')): continue
                nid = str(row['node_id'])
                entry = {}
                for col in df.columns:
                    if col == 'node_id' or pd.isna(row[col]) or str(row[col]).strip() == '':
                        continue
                    if col in ('gas_comp', 'node_type'):
                        entry[col] = str(row[col])
                    else:
                        try:
                            entry[col] = float(row[col])
                        except ValueError:
                            entry[col] = str(row[col])
                data[nid] = entry
            return data
        except Exception:
            return {}

    # Pre-calcola throughput per nodo: somma flussi entranti dalle pipe connesse
    # Per un nodo passante: throughput = portata della pipe
    # Per un nodo di diramazione: throughput = somma dei flussi entranti (Smc/h)
    _node_throughput = {}   # nid (int) -> float Smc/h
    try:
        for pid, pipe in result.pipelines.items():
            fr = vars(pipe).get('flow_rate')
            if fr is None:
                continue
            fr_h = float(fr) * 3600.0
            a = getattr(pipe, 'inlet_index', None)
            b = getattr(pipe, 'outlet_index', None)
            if a is None or b is None:
                continue
            # Flusso positivo: va da a verso b
            # Contributo entrante in b = fr_h se > 0; in a = -fr_h se < 0
            if fr_h > 0:
                _node_throughput[b] = _node_throughput.get(b, 0.0) + fr_h
            elif fr_h < 0:
                _node_throughput[a] = _node_throughput.get(a, 0.0) + abs(fr_h)
    except Exception:
        pass

    node_data = {}
    for nid, node in result.nodes.items():
        entry = {}
        try:
            p = node.pressure
            if p is not None:
                entry['pressure_bar'] = float(p) / 1e5
        except Exception:
            pass
        try:
            t = node.temperature
            if t is not None:
                entry['temperature_k'] = float(t)
        except Exception:
            pass
        try:
            gm = node.gas_mixture
            if gm is not None:
                try:
                    sg = gm.specific_gravity
                    if sg is not None:
                        entry['sp_gravity'] = float(sg)
                except Exception:
                    pass
                try:
                    z = gm.compressibility
                    if z is not None:
                        entry['z_factor'] = float(z)
                except Exception:
                    pass
                try:
                    hhv = gm.HHV_J_per_sm3
                    if hhv is not None:
                        entry['hhv_mj_sm3'] = float(hhv) / 1e6
                except Exception:
                    pass
                try:
                    rho = gm.density
                    if rho is not None:
                        entry['density_kg_m3'] = float(rho)
                except Exception:
                    pass
                try:
                    mm = gm.molar_mass
                    if mm is not None:
                        entry['molar_mass'] = float(mm)
                except Exception:
                    pass
                try:
                    std_rho = gm.standard_density
                    if std_rho is not None:
                        entry['std_density_kg_sm3'] = float(std_rho)
                except Exception:
                    pass
                try:
                    hhv_v = entry.get('hhv_mj_sm3')
                    sg_v = entry.get('sp_gravity')
                    if hhv_v is not None and sg_v and sg_v > 0:
                        entry['wobbe_mj_sm3'] = hhv_v / (sg_v ** 0.5)
                except Exception:
                    pass
                try:
                    comp = gm.composition
                    # Se dopo staggered è un numpy array, riconvertilo in dict
                    if comp is not None and not hasattr(comp, 'items'):
                        try:
                            from GasNetSim.components.gas_mixture.GERG2008.gerg2008 import convert_gerg2008_to_dictionary
                            comp = convert_gerg2008_to_dictionary(comp)
                        except Exception:
                            comp = None
                    if comp is not None and hasattr(comp, 'items'):
                        entry['gas_comp'] = ';'.join(
                            f"{k}={round(float(v), 5)}"
                            for k, v in comp.items() if float(v) > 0.0001
                        )
                        entry['h2_pct'] = round(float(comp.get('hydrogen', 0)) * 100.0, 5)
                except Exception:
                    pass
        except Exception:
            pass
        # Flusso nodale (consumo/immissione)
        try:
            vf = node.volumetric_flow
            if vf is not None:
                entry['volumetric_flow_sm3s'] = float(vf)
        except Exception:
            pass
        try:
            ef = node.energy_flow
            if ef is not None:
                entry['energy_flow_mw'] = float(ef)
        except Exception:
            pass
        # Tipo nodo
        try:
            nt = node.node_type
            if nt is not None:
                entry['node_type'] = str(nt)
        except Exception:
            pass
        # Throughput nodale dalle pipe (flusso che transita per il nodo)
        try:
            tp = _node_throughput.get(int(nid))
            if tp is not None:
                entry['throughput_sm3h'] = round(tp, 2)
        except Exception:
            pass
        if entry:
            node_data[str(nid)] = entry
    return node_data


def _extract_pipe_data(result):
    """Ritorna {str(pipe_id): {field: value}} con tutti i campi disponibili."""
    from pathlib import Path
    if isinstance(result, (str, Path)):
        import pandas as pd
        csv_file = Path(result) / 'results_pipes.csv'
        if not csv_file.exists():
            return {}
        try:
            df = pd.read_csv(csv_file, sep=';', dtype=str)
            data = {}
            for _, row in df.iterrows():
                if pd.isna(row.get('pipe_id')): continue
                pid = str(row['pipe_id'])
                entry = {}
                for col in df.columns:
                    if col == 'pipe_id' or pd.isna(row[col]) or str(row[col]).strip() == '':
                        continue
                    try:
                        entry[col] = float(row[col])
                    except ValueError:
                        entry[col] = str(row[col])
                data[pid] = entry
            return data
        except Exception:
            return {}

    pipe_data = {}
    for pid, pipe in result.pipelines.items():
        entry = {}
        fr = vars(pipe).get('flow_rate')
        if fr is not None:
            entry['flow_sm3h'] = round(float(fr) * 3600.0, 4)      # Smc/h
            entry['flow_abs_sm3h'] = round(abs(float(fr)) * 3600.0, 4)  # Smc/h
            try:
                vel = pipe.calc_flow_velocity()
                if vel is not None:
                    entry['velocity_m_s'] = abs(float(vel))
            except Exception:
                pass
            try:
                p_avg = pipe.calc_average_pressure()
                if p_avg is not None:
                    entry['avg_pressure_bar'] = float(p_avg) / 1e5
            except Exception:
                pass
            try:
                gm = pipe.gas_mixture
                if gm is not None:
                    try:
                        sg = gm.specific_gravity
                        if sg is not None:
                            entry['sp_gravity'] = float(sg)
                    except Exception:
                        pass
                    try:
                        z = gm.compressibility
                        if z is not None:
                            entry['z_factor'] = float(z)
                    except Exception:
                        pass
                    try:
                        rho = gm.density
                        if rho is not None:
                            entry['density_kg_m3'] = float(rho)
                    except Exception:
                        pass
            except Exception:
                pass
        if entry:
            pipe_data[str(pid)] = entry
    return pipe_data


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _remove_old_result_layers():
    """Rimuove dal progetto tutti i layer il cui nome inizia con 'R-N-' o 'R-P-'."""
    try:
        proj = QgsProject.instance()
        to_remove = [
            lid for lid, lyr in proj.mapLayers().items()
            if lyr.name().startswith('R-N-') or lyr.name().startswith('R-P-')
        ]
        if to_remove:
            proj.removeMapLayers(to_remove)
    except Exception:
        pass


def _available_fields(data_dict, requested_fields):
    """
    Ritorna la lista dei campi in requested_fields che sono effettivamente
    presenti in almeno un elemento del dizionario dati.
    """
    if not data_dict:
        return []
    all_keys = set()
    for v in data_dict.values():
        all_keys.update(v.keys())
    return [f for f in requested_fields if f in all_keys]


def _make_multi_field_layer(source_lyr, data_dict, fields, id_field, layer_name, decimals=4):
    """
    Clona il layer sorgente in memoria, aggiunge tutti i campi risultato
    e popola i valori tramite corrispondenza con id_field.
    """
    # Campi che devono essere trattati come stringa anziché double
    _STRING_FIELDS = {'gas_comp', 'node_type'}

    geom_type_str = {
        QgsWkbTypes.PointGeometry:   'Point',
        QgsWkbTypes.LineGeometry:    'LineString',
        QgsWkbTypes.PolygonGeometry: 'Polygon',
    }.get(source_lyr.geometryType(), 'Point')

    crs_str = source_lyr.crs().authid()
    mem_lyr = QgsVectorLayer(
        f"{geom_type_str}?crs={crs_str}", layer_name, 'memory')
    prov = mem_lyr.dataProvider()

    prov.addAttributes(source_lyr.fields().toList())
    for fname in fields:
        if fname in _STRING_FIELDS:
            prov.addAttributes([QgsField(fname, QVariant.String, 'string', 500)])
        else:
            prov.addAttributes(
                [QgsField(fname, QVariant.Double, 'double', 14, decimals)])
    mem_lyr.updateFields()

    id_src_idx = source_lyr.fields().indexOf(id_field)

    feats = []
    for src_feat in source_lyr.getFeatures():
        new_feat = QgsFeature(mem_lyr.fields())
        new_feat.setGeometry(src_feat.geometry())
        for field in source_lyr.fields():
            try:
                new_feat.setAttribute(field.name(), src_feat[field.name()])
            except Exception:
                pass
        if id_src_idx >= 0:
            raw_id = src_feat[id_field]
            # Prova sia come stringa diretta sia come int/float per sicurezza
            feat_key = str(raw_id)
            row = data_dict.get(feat_key)
            if row is None:
                # Fallback: prova conversione int (numpy.int64 vs Python int)
                try:
                    row = data_dict.get(str(int(raw_id)))
                except Exception:
                    pass
            if row is None:
                row = {}
            for fname in fields:
                val = row.get(fname)
                if val is not None:
                    try:
                        if fname in _STRING_FIELDS:
                            new_feat.setAttribute(fname, str(val))
                        else:
                            new_feat.setAttribute(fname, round(float(val), decimals))
                    except Exception:
                        pass
        feats.append(new_feat)

    ok, _ = prov.addFeatures(feats)
    mem_lyr.updateExtents()
    return mem_lyr


def _apply_graduated(layer, field_name, ramp_name='RdYlGn',
                     n_classes=5, reverse=False):
    """
    Applica QgsGraduatedSymbolRenderer con colori da ramp_name (Quantile).
    Se il renderer graduated fallisce, imposta comunque un renderer di default
    visibile in modo che il layer sia sempre renderizzato.
    """
    applied = False
    try:
        style = QgsStyle.defaultStyle()
        ramp = style.colorRamp(ramp_name)
        if ramp is None:
            from qgis.core import QgsGradientColorRamp
            ramp = QgsGradientColorRamp(QColor('#2166ac'), QColor('#d73027'))
        if reverse:
            ramp.invert()
        default_sym = QgsSymbol.defaultSymbol(layer.geometryType())
        renderer = QgsGraduatedSymbolRenderer.createRenderer(
            layer, field_name, n_classes,
            QgsGraduatedSymbolRenderer.Quantile,
            default_sym, ramp,
        )
        if renderer is not None and len(renderer.ranges()) > 0:
            layer.setRenderer(renderer)
            applied = True
    except Exception:
        pass
    if not applied:
        # Fallback: renderer singolo colore sempre visibile
        from qgis.core import QgsSingleSymbolRenderer
        fallback_sym = QgsSymbol.defaultSymbol(layer.geometryType())
        layer.setRenderer(QgsSingleSymbolRenderer(fallback_sym))
    layer.triggerRepaint()


def _set_line_width_expression(layer, width_field):
    """
    Imposta lo spessore della linea proporzionale al campo indicato.
    """
    try:
        renderer = layer.renderer()
        if renderer is None:
            return
        expr = (
            f"scale_linear("
            f"  \"{width_field}\","
            f"  minimum(\"{width_field}\"),"
            f"  maximum(\"{width_field}\"),"
            f"  0.3, 2.0"
            f")"
        )
        from qgis.core import QgsProperty
        dd_prop = QgsProperty.fromExpression(expr)
        for rng in renderer.ranges():
            sym = rng.symbol()
            if sym is not None:
                for i in range(sym.symbolLayerCount()):
                    sl = sym.symbolLayer(i)
                    if isinstance(sl, QgsSimpleLineSymbolLayer):
                        sl.setDataDefinedProperty(
                            QgsSimpleLineSymbolLayer.PropertyStrokeWidth,
                            dd_prop,
                        )
    except Exception:
        pass
