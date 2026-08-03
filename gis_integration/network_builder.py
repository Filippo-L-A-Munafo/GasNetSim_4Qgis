# -*- coding: utf-8 -*-
"""
gis_integration/network_builder.py
Collasso rete gas e generazione CSV GasNetSim da layer QGIS.

Adattato da:
  - _moduli/Semplificazione della rete/collapse_rnt_qgis.py
  - _moduli/simulazione_cascade/export_qgis_to_csv.py

Funzioni pure (nessuna UI):
  - build_graph, collapse_undirected, find_diameter_change_nodes,
    prune_dangling, split_network_at_user_nodes, match_user_nodes,
    make_memory_layers, export_layers_to_csv

Pipeline completa:
  - run_collapse_pipeline(pipe_layer, ...) → (pipes_lyr, nodes_lyr, nodes_csv, pipes_csv)
"""

import csv
from collections import defaultdict
from pathlib import Path

# ── Costanti ─────────────────────────────────────────────────────────────────
CRS_DEFAULT     = "EPSG:25833"
FRICTION_METHOD = "chen"
ROUGHNESS_M     = 0.00005
PRESSURE_REF_PA = 2_400_000.0   # 24 bar
TEMP_REF_K      = 288.15         # 15°C — condizioni standard italiane (Sm³ per UNI EN ISO 13443)
GAS_COMP_REF    = "SNAM_MAZARA_GAS"  # gas algerino via Tunisia (punto di consegna principale Sicilia)
PLACEHOLDER_FLOW = 1e-6

NODES_HEADER = [
    "node_index", "pressure_pa", "flow_MW", "flow_sm3_per_s",
    "altitude_m", "temperature_k", "gas_composition",
    "node_type", "latitude", "longitude", "flow_type",
]
PIPES_HEADER = [
    "pipeline_index", "inlet_index", "outlet_index",
    "diameter_m", "length_m", "friction_method", "roughness_m",
]
COMPRESSORS_HEADER = [
    "compressor_index", "inlet", "outlet",
    "compression_ratio", "efficiency", "thermodynamic_process",
    "control_mode", "p_out_target",
]

# Default GasNetSim per i parametri del compressore
COMP_RATIO_DEFAULT = 1.1
COMP_EFF_DEFAULT   = 0.85
COMP_PROC_DEFAULT  = "isentropic"


# ── Utility ───────────────────────────────────────────────────────────────────

def _parse_smc_ora(smc_str, ora: int, sep: str = ';'):
    """Parsing flusso orario da stringa sep-separated (Smc/h → Sm³/s).

    Unità: SEMPRE Smc/h. Il segno determina il tipo:
      valore POSITIVO  → consumo (REMI, utenza)   → Sm³/s > 0
      valore NEGATIVO  → immissione in rete        → Sm³/s < 0
      valore ~0        → usa PLACEHOLDER_FLOW

    Il valore viene sempre diviso per 3600 indipendentemente dal segno.
    """
    if not smc_str or str(smc_str).upper() in ("NULL", "NONE", "NAN", ""):
        return PLACEHOLDER_FLOW
    try:
        vals = [v.strip() for v in str(smc_str).split(sep) if v.strip()]
        if not vals:
            return PLACEHOLDER_FLOW
        idx = min(ora, len(vals) - 1)
        val = float(vals[idx])
        if abs(val) < 1e-10:
            return PLACEHOLDER_FLOW
        return round(val / 3600.0, 8)
    except (ValueError, IndexError):
        return PLACEHOLDER_FLOW


# ── Geometria ─────────────────────────────────────────────────────────────────

def get_coords(geom):
    """Ritorna lista di (x,y) o (x,y,z) dai vertici della polilinea."""
    verts = list(geom.vertices())
    is3d = geom.constGet().is3D()
    if is3d:
        return [(v.x(), v.y(), v.z()) for v in verts]
    return [(v.x(), v.y()) for v in verts]


def coords_to_qgsgeom(coords):
    """Converte lista di (x,y) o (x,y,z) in QgsGeometry LineString."""
    from qgis.core import QgsPoint, QgsLineString, QgsGeometry
    if len(coords[0]) == 3:
        pts = [QgsPoint(x, y, z) for x, y, z in coords]
    else:
        pts = [QgsPoint(x, y) for x, y in coords]
    return QgsGeometry(QgsLineString(pts))


def round_coord(c):
    return (round(c[0], 1), round(c[1], 1))


def path_length_3d(coords):
    """Lunghezza reale percorso (somma segmenti, con Z se presente)."""
    total = 0.0
    for i in range(len(coords) - 1):
        dx = coords[i + 1][0] - coords[i][0]
        dy = coords[i + 1][1] - coords[i][1]
        dz = (coords[i + 1][2] - coords[i][2]) if len(coords[i]) == 3 else 0.0
        total += (dx**2 + dy**2 + dz**2) ** 0.5
    return total


# ── Grafo ─────────────────────────────────────────────────────────────────────

def build_graph(layer):
    """
    Costruisce grafo NON direzionato dalla layer.
    Ritorna: (archi, nodo_xy)
      - archi: list of dict {id, a, b, coords, attrs}
      - nodo_xy: dict {node_id: coord_tuple}
    """
    nodo_xy = {}
    coord_to_id = {}
    counter = [0]

    def get_node(coord):
        k = round_coord(coord)
        if k not in coord_to_id:
            coord_to_id[k] = counter[0]
            nodo_xy[counter[0]] = coord
            counter[0] += 1
        return coord_to_id[k]

    archi = []
    skipped_null = 0
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isNull() or geom.isEmpty() or geom.constGet() is None:
            skipped_null += 1
            continue
        coords = get_coords(geom)
        if len(coords) < 2:
            skipped_null += 1
            continue
        a = get_node(coords[0])
        b = get_node(coords[-1])
        attrs = dict(zip([f.name() for f in layer.fields()], feat.attributes()))
        # src_fids: i fid ORIGINALI del layer condotte che compongono questo
        # arco. All'inizio uno solo; il collasso grado-2 li accumula quando
        # fonde una catena. Serve a ritrovare, DOPO il collasso, quali condotte
        # originali modificare (es. per allargare un diametro).
        archi.append({'id': feat.id(), 'a': a, 'b': b, 'coords': coords,
                      'attrs': attrs, 'src_fids': [feat.id()]})

    return archi, nodo_xy, skipped_null


# ── Smoothing Topologico ──────────────────────────────────────────────────────

def apply_topological_laplacian_smoothing(archi, nodo_xy, log=print, slope_threshold=10.0, z_error_threshold=15.0, window_m=250.0):
    """
    Applica il Laplacian Smoothing Contestuale Topologico ai nodi di grado 2
    per correggere falsi picchi o falsi burroni generati dal campionamento del DEM.
    Utilizza una 'finestra spaziale' di window_m metri attraversando il grafo per trovare 
    una macro-pendenza stabile, diventando immune alla fitta frammentazione vettoriale.
    """
    from collections import defaultdict
    if log is None: log = print
    
    adj = defaultdict(list)
    for i, e in enumerate(archi):
        adj[e['a']].append(i)
        adj[e['b']].append(i)
        
    to_check = [nid for nid, idxs in adj.items() if len(idxs) == 2]
    anomalies_fixed = 0
    
    def traverse_for_z(start_node, initial_edge_idx):
        """
        Esplora il grafo partendo da start_node, andando lungo initial_edge_idx,
        fino a percorrere window_m metri. Restituisce la Z al target e la distanza percorsa.
        """
        acc_dist = 0.0
        curr_node = start_node
        curr_edge_idx = initial_edge_idx
        
        while True:
            e = archi[curr_edge_idx]
            L = path_length_3d(e['coords'])
            next_node = e['b'] if e['a'] == curr_node else e['a']
            
            if acc_dist + L >= window_m:
                # Abbiamo raggiunto o superato i 250m in questo segmento. 
                # Interpoliamo la Z esatta a 250m.
                overshoot = (window_m - acc_dist) / L if L > 0 else 1.0
                z_curr = e['coords'][0][2] if e['a'] == curr_node else e['coords'][-1][2]
                z_next = e['coords'][-1][2] if e['a'] == curr_node else e['coords'][0][2]
                z_target = z_curr + (z_next - z_curr) * overshoot
                acc_dist = window_m
                return z_target, acc_dist
                
            acc_dist += L
            curr_node = next_node
            
            # Se colpiamo una giunzione o un estremo prima dei 250m, ci fermiamo lì.
            if len(adj[curr_node]) != 2:
                z_end = nodo_xy[curr_node][2] if len(nodo_xy[curr_node]) == 3 else 0.0
                return z_end, acc_dist
                
            # Proseguiamo nel grafo
            next_edges = adj[curr_node]
            curr_edge_idx = next_edges[0] if next_edges[0] != curr_edge_idx else next_edges[1]
            
    for nid in to_check:
        i1, i2 = adj[nid]
        p1 = archi[i1]
        p2 = archi[i2]
        
        c1 = p1['coords']
        c2 = p2['coords']
        
        # Saltiamo se non abbiamo dati 3D (nessun DEM)
        if len(c1[0]) < 3 or len(c2[0]) < 3:
            continue
            
        z_node = nodo_xy[nid][2] if len(nodo_xy[nid]) == 3 else 0.0
        
        # Esplorazione a ritroso (lungo p1)
        z_prev, L1 = traverse_for_z(nid, i1)
        dz1 = z_node - z_prev
        p1_is_towards = (p1['b'] == nid)
            
        # Esplorazione in avanti (lungo p2)
        z_next, L2 = traverse_for_z(nid, i2)
        dz2 = z_next - z_node
        p2_is_from = (p2['a'] == nid)
            
        slope1_to_node = (dz1 / L1 * 100) if L1 > 0 else 0
        slope2_from_node = (dz2 / L2 * 100) if L2 > 0 else 0
        
        # Z attesa (Laplaciano puro ponderato sulle distanze macroscopiche)
        if (L1 + L2) > 0:
            z_interp = z_prev + (z_next - z_prev) * (L1 / (L1 + L2))
        else:
            z_interp = z_prev
            
        error_z = z_node - z_interp
        
        # Condizione anomalia topologica macroscopica
        if abs(error_z) > z_error_threshold and (abs(slope1_to_node) > slope_threshold or abs(slope2_from_node) > slope_threshold):
            # Controllo se le macro-pendenze hanno segno opposto (picco o burrone)
            if slope1_to_node * slope2_from_node < 0:
                # Applica correzione solo se la pendenza è irrealistica
                old_xy = nodo_xy[nid]
                nodo_xy[nid] = (old_xy[0], old_xy[1], z_interp)
                
                # Aggiorna l'array coords di p1
                if p1_is_towards:
                    c1[-1] = (c1[-1][0], c1[-1][1], z_interp)
                else:
                    c1[0] = (c1[0][0], c1[0][1], z_interp)
                    
                # Aggiorna l'array coords di p2
                if p2_is_from:
                    c2[0] = (c2[0][0], c2[0][1], z_interp)
                else:
                    c2[-1] = (c2[-1][0], c2[-1][1], z_interp)
                    
                anomalies_fixed += 1

    if anomalies_fixed > 0:
        log(f"  [Topological Smoothing Window={window_m}m] Corretti {anomalies_fixed} nodi intermedi con anomalie Z (>{z_error_threshold}m)")
        
    return archi, nodo_xy



# ── Algoritmi di collasso ─────────────────────────────────────────────────────

def collapse_undirected(archi, protected=None):
    """Collasso iterativo con grafo NON direzionato dei nodi grado-2."""
    if protected is None:
        protected = set()
    while True:
        adj = defaultdict(list)
        for i, e in enumerate(archi):
            adj[e['a']].append(i)
            adj[e['b']].append(i)

        to_collapse = [nid for nid, idxs in adj.items()
                       if len(idxs) == 2 and nid not in protected]
        if not to_collapse:
            break

        edges_to_remove = set()
        new_edges = []
        for nid in to_collapse:
            i1, i2 = adj[nid]
            if i1 in edges_to_remove or i2 in edges_to_remove:
                continue
            e1, e2 = archi[i1], archi[i2]
            a_end = e1['b'] if e1['a'] == nid else e1['a']
            b_end = e2['b'] if e2['a'] == nid else e2['a']
            c1 = list(e1['coords'])
            if e1['a'] == nid:
                c1 = list(reversed(c1))
            c2 = list(e2['coords'])
            if e2['b'] == nid:
                c2 = list(reversed(c2))
            new_edges.append({
                'id': max(e['id'] for e in archi) + len(new_edges) + 1,
                'a': a_end, 'b': b_end,
                'coords': c1 + c2[1:],
                'attrs': e1['attrs'].copy(),
                # accumula i fid originali dei due archi fusi
                'src_fids': list(e1.get('src_fids', [e1['id']]))
                            + list(e2.get('src_fids', [e2['id']])),
            })
            edges_to_remove.add(i1)
            edges_to_remove.add(i2)

        archi = [e for i, e in enumerate(archi) if i not in edges_to_remove] + new_edges
    return archi


def find_diameter_change_nodes(archi, diam_field='Diametro_pollici', diam_unit='in'):
    """Trova i nodi di cambio diametro (da proteggere dal collasso)."""
    adj = defaultdict(list)
    for e in archi:
        adj[e['a']].append(e)
        adj[e['b']].append(e)
    protected = set()
    for nid, edges in adj.items():
        if len(edges) != 2:
            continue
        d1 = edges[0]['attrs'].get(diam_field)
        d2 = edges[1]['attrs'].get(diam_field)
        if d1 is None or d2 is None:
            continue
        try:
            if float(d1) != float(d2):
                protected.add(nid)
        except (ValueError, TypeError):
            if str(d1) != str(d2):
                protected.add(nid)
    return protected


def prune_dangling(archi, protected=None):
    """Rimuove iterativamente i rami pendenti (nodi grado-1 non protetti)."""
    if protected is None:
        protected = set()
    while True:
        adj = defaultdict(list)
        for i, e in enumerate(archi):
            adj[e['a']].append(i)
            adj[e['b']].append(i)
        dangling = [nid for nid, idxs in adj.items()
                    if len(idxs) == 1 and nid not in protected]
        if not dangling:
            break
        edges_to_remove = set()
        for nid in dangling:
            edges_to_remove.add(adj[nid][0])
        archi = [e for i, e in enumerate(archi) if i not in edges_to_remove]
    return archi


# ── Verifica quote e re-draping pre-simulazione ────────────────────────────────

def verify_and_redrape_nodes(nodo_xy, remaining_ids, dem_layer, pipe_crs,
                             log=print, warnings=None, z_missing_tol=1e-6):
    """
    Verifica le quote dei nodi finali PRIMA della simulazione e ripara i buchi.

    Un nodo puo' restare senza quota per due motivi:
      1) il suo vertice e' caduto su una cella nodata del DEM (o fuori
         estensione) durante il draping iniziale → z=0;
      2) e' un nodo inserito manualmente DOPO il draping (es. cabine,
         compressori come Enna) che il DEM non aveva mai campionato.

    Per ogni nodo con quota mancante (assente o ~0) si ricampiona il DEM
    direttamente alle coordinate FINALI del nodo (secondo tentativo di
    draping), con eventuale trasformazione di CRS. Se anche il secondo
    campionamento non restituisce una quota valida (nodata/fuori estensione),
    il nodo viene segnalato come ERRORE all'utente, ma la pipeline prosegue:
    la simulazione viene comunque avviata.

    Aggiorna nodo_xy in-place.
    Ritorna: (n_recuperati, lista_nodi_ancora_mancanti)
    """
    if warnings is None:
        warnings = []
    if dem_layer is None:
        return 0, []

    from qgis.core import QgsCoordinateTransform, QgsProject, QgsPointXY

    prov = dem_layer.dataProvider()
    xform = None
    if pipe_crs != dem_layer.crs():
        xform = QgsCoordinateTransform(pipe_crs, dem_layer.crs(),
                                       QgsProject.instance())

    def _has_z(c):
        return len(c) == 3 and c[2] is not None and abs(c[2]) > z_missing_tol

    to_fix = [nid for nid in remaining_ids if not _has_z(nodo_xy[nid])]
    if not to_fix:
        log(f"  Check quote: OK, tutti i {len(remaining_ids)} nodi finali "
            f"hanno quota valida")
        return 0, []

    log(f"  Check quote: {len(to_fix)} nodi senza quota → 2° tentativo di "
        f"draping dal DEM...")

    recovered = 0
    still_missing = []
    for nid in to_fix:
        c = nodo_xy[nid]
        p = QgsPointXY(c[0], c[1])
        if xform is not None:
            p = xform.transform(p)
        try:
            val, ok = prov.sample(p, 1)   # banda 1
        except Exception:
            val, ok = None, False
        if ok and val is not None:
            z = float(val)
            nodo_xy[nid] = (c[0], c[1], z)
            if abs(z) > z_missing_tol:
                recovered += 1
            # z valida == 0 → quota reale a livello del mare, non e' un errore
        else:
            # nodata / fuori estensione anche al 2° tentativo
            nodo_xy[nid] = (c[0], c[1], 0.0)
            still_missing.append(nid)

    log(f"  Re-draping: {recovered} quote recuperate, "
        f"{len(still_missing)} ancora mancanti")

    if still_missing:
        msg = (f"ERRORE QUOTE: {len(still_missing)} nodo/i senza quota valida "
               f"anche dopo il re-draping (DEM nodata o fuori estensione): "
               f"{', '.join(str(n) for n in still_missing[:15])}"
               + (" ..." if len(still_missing) > 15 else "")
               + ". Simulazione avviata comunque: il termine idrostatico "
                 "(rho*g*dz) su questi nodi NON e' fisicamente attendibile.")
        log(f"  ❌ {msg}")
        warnings.append(msg)

    return recovered, still_missing


# ── Layer QGIS ────────────────────────────────────────────────────────────────

def split_network_at_user_nodes(work_lyr, user_layer, radius_m, crs=CRS_DEFAULT):
    """
    Spezza i segmenti più vicini ai nodi utente nel punto di proiezione ortogonale.
    Ritorna: (out_layer, n_splits)
    """
    from qgis.core import (QgsVectorLayer, QgsFeature, QgsSpatialIndex,
                            QgsRectangle, QgsCoordinateTransform,
                            QgsProject, QgsGeometry, QgsWkbTypes)
    feats = list(work_lyr.getFeatures())
    has_z = work_lyr.wkbType() in (QgsWkbTypes.LineStringZ,
                                    QgsWkbTypes.MultiLineStringZ,
                                    QgsWkbTypes.LineString25D)
    geom_type = f"LineStringZ?crs={crs}" if has_z else f"LineString?crs={crs}"

    idx = QgsSpatialIndex()
    feat_map = {}
    for f in feats:
        idx.insertFeature(f)
        feat_map[f.id()] = f

    new_feats = list(feats)
    next_id = max(f.id() for f in feats) + 1 if feats else 1
    splits_done = 0

    src_crs = user_layer.crs()
    dst_crs = work_lyr.crs()
    xform = None
    if src_crs != dst_crs:
        xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

    for user_feat in user_layer.getFeatures():
        geom_pt = user_feat.geometry()
        if geom_pt.isEmpty():
            continue
        if xform is not None:
            geom_pt = QgsGeometry(geom_pt)
            geom_pt.transform(xform)
        pt = geom_pt.asPoint()
        px, py = pt.x(), pt.y()
        search_rect = QgsRectangle(px - radius_m, py - radius_m,
                                   px + radius_m, py + radius_m)
        candidates = idx.intersects(search_rect)
        if not candidates:
            continue

        best_fid, best_t, best_dist, best_proj = None, None, radius_m, None
        for fid in candidates:
            f = feat_map.get(fid)
            if f is None:
                continue
            coords = get_coords(f.geometry())
            if len(coords) < 2:
                continue
            ax, ay = coords[0][0], coords[0][1]
            bx, by = coords[1][0], coords[1][1]
            dx, dy = bx - ax, by - ay
            seg_len2 = dx * dx + dy * dy
            if seg_len2 < 1e-10:
                continue
            t = ((px - ax) * dx + (py - ay) * dy) / seg_len2
            t = max(0.0, min(1.0, t))
            projx, projy = ax + t * dx, ay + t * dy
            dist = ((px - projx)**2 + (py - projy)**2) ** 0.5
            if dist < best_dist and 1e-4 < t < 1 - 1e-4:
                best_dist, best_fid, best_t, best_proj = dist, fid, t, (projx, projy)

        if best_fid is None:
            continue

        f = feat_map[best_fid]
        coords = get_coords(f.geometry())
        ax, ay = coords[0][0], coords[0][1]
        bx, by = coords[1][0], coords[1][1]
        projx, projy = best_proj

        if has_z:
            az = coords[0][2] if len(coords[0]) == 3 else 0.0
            bz = coords[1][2] if len(coords[1]) == 3 else 0.0
            projz = az + best_t * (bz - az)
            c1 = [(ax, ay, az), (projx, projy, projz)]
            c2 = [(projx, projy, projz), (bx, by, bz)]
        else:
            c1 = [(ax, ay), (projx, projy)]
            c2 = [(projx, projy), (bx, by)]

        g1, g2 = coords_to_qgsgeom(c1), coords_to_qgsgeom(c2)
        f1 = QgsFeature(f.fields()); f1.setId(next_id)
        f1.setGeometry(g1); f1.setAttributes(f.attributes())
        f2 = QgsFeature(f.fields()); f2.setId(next_id + 1)
        f2.setGeometry(g2); f2.setAttributes(f.attributes())
        next_id += 2

        new_feats = [x for x in new_feats if x.id() != best_fid]
        del feat_map[best_fid]
        idx.deleteFeature(f)
        new_feats += [f1, f2]
        feat_map[f1.id()] = f1
        feat_map[f2.id()] = f2
        idx.insertFeature(f1)
        idx.insertFeature(f2)
        splits_done += 1

    out = QgsVectorLayer(geom_type, "exploded_split", "memory")
    out.dataProvider().addAttributes(work_lyr.fields().toList())
    out.updateFields()
    out.dataProvider().addFeatures(new_feats)
    return out, splits_done


def match_user_nodes(nodo_xy, user_layer, radius_m=50.0, crs=CRS_DEFAULT):
    """
    Aggancia nodi utente ai nodi topologici entro radius_m.
    Ritorna: {node_id: QgsFeature}
    """
    from qgis.core import (QgsCoordinateReferenceSystem,
                            QgsCoordinateTransform, QgsProject, QgsGeometry)
    dst_crs = QgsCoordinateReferenceSystem(crs)
    src_crs = user_layer.crs()
    xform = None
    if src_crs != dst_crs:
        xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

    matched = {}
    for feat in user_layer.getFeatures():
        geom = feat.geometry()
        if geom.isEmpty():
            continue
        if xform is not None:
            geom = QgsGeometry(geom)
            geom.transform(xform)
        pt = geom.asPoint()
        best_id, best_dist = None, radius_m
        for nid, coord in nodo_xy.items():
            dx, dy = coord[0] - pt.x(), coord[1] - pt.y()
            dist = (dx**2 + dy**2) ** 0.5
            if dist < best_dist:
                best_dist, best_id = dist, nid
        if best_id is not None:
            matched[best_id] = feat
    return matched


def find_unmatched_user_nodes(nodo_xy, user_layer, radius_m=50.0, crs=CRS_DEFAULT):
    """
    Trova i nodi utente che NON hanno nessun nodo grafo entro radius_m.
    Ritorna lista di etichette (nome/id feature) dei nodi non connessi.
    """
    from qgis.core import (QgsCoordinateReferenceSystem,
                            QgsCoordinateTransform, QgsProject, QgsGeometry)
    dst_crs = QgsCoordinateReferenceSystem(crs)
    src_crs = user_layer.crs()
    xform = None
    if src_crs != dst_crs:
        xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

    nodo_coords = list(nodo_xy.values())
    r2 = radius_m ** 2
    _NAME_FIELDS = ('name', 'Name', 'nome', 'id', 'ID', 'node_id', 'NodeID', 'label')

    unmatched = []
    for feat in user_layer.getFeatures():
        geom = feat.geometry()
        if geom.isEmpty():
            continue
        if xform is not None:
            geom = QgsGeometry(geom)
            geom.transform(xform)
        pt = geom.asPoint()
        found = any(
            (c[0] - pt.x()) ** 2 + (c[1] - pt.y()) ** 2 <= r2
            for c in nodo_coords
        )
        if not found:
            label = f"FID={feat.id()}"
            for fn in _NAME_FIELDS:
                if feat.fields().indexOf(fn) >= 0:
                    val = feat.attribute(fn)
                    if val is not None and str(val).strip():
                        label = str(val)
                        break
            unmatched.append(label)
    return unmatched


def find_island_fids(pipe_layer):
    """
    Dato un layer condotte, trova le componenti connesse usando gli endpoint
    della geometria come nodi del grafo.

    Ritorna list[list[int]]: una lista per ogni componente MINORE (tutte
    tranne la più grande), ordinate per dimensione crescente.
    Ritorna [] se la rete è connessa (una sola componente).
    """
    parent = {}
    fid_to_a = {}   # fid -> endpoint arrotondato (per Union-Find)

    def _rk(vx, vy):
        # Stessa precisione di round_coord (1 decimale = 0.1 m) per coerenza
        # con build_graph + check_pipe_issues che usano round_coord
        return round_coord((vx, vy))

    def _find(x):
        if x not in parent:
            parent[x] = x
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def _union(x, y):
        px, py = _find(x), _find(y)
        if px != py:
            parent[px] = py

    for feat in pipe_layer.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isNull() or geom.isEmpty():
            continue
        verts = list(geom.vertices())
        if len(verts) < 2:
            continue
        # Considera TUTTI i vertici consecutivi (come build_graph dopo explodelines)
        first_k = _rk(verts[0].x(), verts[0].y())
        prev_k = first_k
        for v in verts[1:]:
            k = _rk(v.x(), v.y())
            _union(prev_k, k)
            prev_k = k
        fid_to_a[feat.id()] = first_k

    if not fid_to_a:
        return []

    comp_fids = defaultdict(list)
    for fid, a in fid_to_a.items():
        comp_fids[_find(a)].append(fid)

    if len(comp_fids) <= 1:
        return []

    # Ordina per dimensione decrescente, salta la componente principale
    sorted_comps = sorted(comp_fids.values(), key=len, reverse=True)
    return sorted_comps[1:]


def snap_pipe_endpoints(pipe_layer, tolerance_m, strategy='centroid',
                        nodes_layer=None, log=None):
    """
    Snappa gli endpoint delle condotte entro tolerance_m l'uno dall'altro.
    Se nodes_layer è fornito, gli endpoint vicini a un nodo vengono agganciati
    alla posizione esatta del nodo (priorità sul centroide pipe-to-pipe).

    Parameters
    ----------
    pipe_layer   : QgsVectorLayer  (LineString/MultiLineString)
    tolerance_m  : float  distanza massima di snap (unità CRS del layer)
    strategy     : 'centroid' — tutti gli endpoint del cluster si spostano
                               nel baricentro del gruppo
                   'first'    — il primo endpoint trovato rimane fisso,
                               gli altri si spostano verso di lui
    nodes_layer  : QgsVectorLayer (Point) opzionale — se fornito, gli endpoint
                   entro tolerance_m da un nodo vengono agganciati al nodo
                   più vicino (ha priorità rispetto al centroide pipe-to-pipe)
    log          : callable per logging (default=print)

    Returns
    -------
    (new_layer, modified_geoms)
        new_layer     : QgsVectorLayer memory con geometrie aggiornate
                        (None se nessun endpoint modificato)
        modified_geoms: dict {fid: QgsGeometry}  solo le feature modificate
    """
    if log is None:
        log = print

    # ── Raccogli tutti i vertici ──────────────────────────────────────────
    # all_pts[i] = (x, y, fid, pos)
    #   fid=feat.id(), pos=0/-1  → start/end (mobile, viene spostato)
    #   fid=None,      pos=None  → vertice intermedio (ancora, non viene spostato)
    all_pts = []
    feat_coords = {}    # fid -> list of (x,y) or (x,y,z)
    for feat in pipe_layer.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isNull() or geom.isEmpty():
            continue
        coords = get_coords(geom)
        if len(coords) < 2:
            continue
        feat_coords[feat.id()] = coords
        all_pts.append((coords[0][0],  coords[0][1],  feat.id(), 0))    # start
        all_pts.append((coords[-1][0], coords[-1][1], feat.id(), -1))   # end
        for vi in range(1, len(coords) - 1):
            all_pts.append((coords[vi][0], coords[vi][1], None, None))  # intermedi

    if not all_pts:
        return None, {}

    n_endpoints = sum(1 for (_, _, f, _) in all_pts if f is not None)
    n_anchors   = len(all_pts) - n_endpoints
    log(f"  Vertici: {len(all_pts)} totali  "
        f"({n_endpoints} endpoint mobili, {n_anchors} vertici intermedi) "
        f"da {len(feat_coords)} condotte")

    # ── Union-Find con grid bucketing (O(n) medio) ───────────────────────
    n = len(all_pts)
    parent = list(range(n))

    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path compression
            x = parent[x]
        return x

    def _union(a, b):
        pa, pb = _find(a), _find(b)
        if pa != pb:
            parent[pa] = pb

    cell = max(tolerance_m, 1e-9)
    tol2 = tolerance_m * tolerance_m

    grid = defaultdict(list)
    for i, (x, y, _, _) in enumerate(all_pts):
        grid[(int(x / cell), int(y / cell))].append(i)

    for i, (x1, y1, _, _) in enumerate(all_pts):
        cx, cy = int(x1 / cell), int(y1 / cell)
        for dcx in (-1, 0, 1):
            for dcy in (-1, 0, 1):
                for j in grid.get((cx + dcx, cy + dcy), []):
                    if j <= i:
                        continue
                    x2, y2, _, _ = all_pts[j]
                    if (x2 - x1) ** 2 + (y2 - y1) ** 2 <= tol2:
                        _union(i, j)

    # ── Calcola snap point per ogni cluster ─────────────────────────────
    clusters = defaultdict(list)
    for i, (x, y, _, _) in enumerate(all_pts):
        clusters[_find(i)].append((i, x, y))

    snap_pt = {}    # cluster root -> (snap_x, snap_y)
    for root, members in clusters.items():
        if len(members) < 2:
            continue
        # Se il cluster contiene vertici intermedi (ancore), gli endpoint
        # si agganciano alla loro posizione (priorità su centroid/first)
        anchor_xy = [(x, y) for (mi, x, y) in members if all_pts[mi][2] is None]
        if anchor_xy:
            snap_pt[root] = (
                sum(a[0] for a in anchor_xy) / len(anchor_xy),
                sum(a[1] for a in anchor_xy) / len(anchor_xy),
            )
        elif strategy == 'centroid':
            snap_pt[root] = (
                sum(m[1] for m in members) / len(members),
                sum(m[2] for m in members) / len(members),
            )
        else:  # 'first'
            snap_pt[root] = (members[0][1], members[0][2])

    # ── Snap a nodi (priorità rispetto al centroide pipe-to-pipe) ────────
    if nodes_layer is not None:
        node_pts = []
        for nfeat in nodes_layer.getFeatures():
            ng = nfeat.geometry()
            if ng is None or ng.isNull():
                continue
            pt = ng.asPoint()
            node_pts.append((pt.x(), pt.y()))
        if node_pts:
            node_grid_snap = defaultdict(list)
            for ni, (nx_n, ny_n) in enumerate(node_pts):
                node_grid_snap[(int(nx_n / cell), int(ny_n / cell))].append(ni)
            root_best = {}   # root -> (dist2, snap_x, snap_y)
            for i, (x1, y1, fid_i, _) in enumerate(all_pts):
                if fid_i is None:   # vertice intermedio: non agganciato a nodi
                    continue
                root = _find(i)
                cx_i, cy_i = int(x1 / cell), int(y1 / cell)
                for dcx in (-1, 0, 1):
                    for dcy in (-1, 0, 1):
                        for ni in node_grid_snap.get(
                                (cx_i + dcx, cy_i + dcy), []):
                            nx_n, ny_n = node_pts[ni]
                            d2 = (nx_n - x1) ** 2 + (ny_n - y1) ** 2
                            if d2 <= tol2:
                                if (root not in root_best
                                        or d2 < root_best[root][0]):
                                    root_best[root] = (d2, nx_n, ny_n)
            for root, (_, sx, sy) in root_best.items():
                snap_pt[root] = (sx, sy)
            log(f"  Snap a nodi: {len(root_best)} cluster agganciati "
                f"a nodi ({len(node_pts)} nodi)")

    # ── Mappa (fid, pos) -> nuovo punto (solo start/end, non ancore) ────
    moved = {}   # (fid, pos) -> (new_x, new_y)
    for i, (x, y, fid, pos) in enumerate(all_pts):
        if fid is None:   # vertice intermedio (ancora), non viene spostato
            continue
        root = _find(i)
        if root in snap_pt:
            nx, ny = snap_pt[root]
            if abs(nx - x) > 1e-9 or abs(ny - y) > 1e-9:
                moved[(fid, pos)] = (nx, ny)

    log(f"  Endpoint da spostare: {len(moved)} in {len(snap_pt)} cluster")

    if not moved:
        return None, {}

    # ── Aggiorna geometrie ───────────────────────────────────────────────
    from qgis.core import (
        QgsVectorLayer, QgsFeature, QgsWkbTypes,
        QgsPoint, QgsLineString, QgsGeometry,
    )

    crs_str  = pipe_layer.crs().authid()
    has_z    = QgsWkbTypes.hasZ(pipe_layer.wkbType())
    geom_type = 'LineStringZ' if has_z else 'LineString'

    new_layer = QgsVectorLayer(
        f"{geom_type}?crs={crs_str}",
        f"{pipe_layer.name()} [snappato]",
        "memory",
    )
    dp = new_layer.dataProvider()
    dp.addAttributes(pipe_layer.fields().toList())
    new_layer.updateFields()

    n_modified   = 0
    modified_geoms = {}   # fid -> QgsGeometry (solo feature modificate)
    new_feats    = []

    for feat in pipe_layer.getFeatures():
        fid = feat.id()
        if fid not in feat_coords:
            new_feats.append(QgsFeature(feat))
            continue

        coords     = feat_coords[fid]
        new_coords = list(coords)
        modified   = False

        if (fid, 0) in moved:
            nx, ny = moved[(fid, 0)]
            c0 = coords[0]
            new_coords[0] = (nx, ny, c0[2]) if (has_z and len(c0) > 2) else (nx, ny)
            modified = True

        if (fid, -1) in moved:
            nx, ny = moved[(fid, -1)]
            cl = coords[-1]
            new_coords[-1] = (nx, ny, cl[2]) if (has_z and len(cl) > 2) else (nx, ny)
            modified = True

        if modified:
            n_modified += 1
            if has_z:
                pts = [QgsPoint(c[0], c[1], c[2] if len(c) > 2 else 0.0)
                       for c in new_coords]
            else:
                pts = [QgsPoint(c[0], c[1]) for c in new_coords]
            new_geom = QgsGeometry(QgsLineString(pts))
            nf = QgsFeature(feat)
            nf.setGeometry(new_geom)
            modified_geoms[fid] = new_geom
            new_feats.append(nf)
        else:
            new_feats.append(QgsFeature(feat))

    dp.addFeatures(new_feats)
    new_layer.updateExtents()
    log(f"  Snap completato: {n_modified}/{len(feat_coords)} condotte modificate")
    return new_layer, modified_geoms


def _arc_label(arc):
    """Restituisce l'identificatore significativo dell'arco (dal campo fid/pipe_id
    del layer originale, ereditato dopo explodelines)."""
    for field in ('fid', 'FID', 'pipe_id', 'id', 'OBJECTID'):
        val = arc['attrs'].get(field)
        if val is not None:
            return val
    return arc['id']


def check_pipe_issues(archi, skipped_null=0):
    """
    Controlla problemi topologici nelle condotte:
      - Elementi con geometria nulla o degenere (da build_graph)
      - Condotte duplicate (stessa coppia nodi A-B)
      - Condotte sovrapposte geometricamente
      - Rete sconnessa (isole / componenti separate)

    Ritorna (warnings, bad_ids):
      - warnings  : lista di stringhe di avviso
      - bad_ids   : set di valori ID originali (campo fid/pipe_id) delle condotte
                    problematiche, da usare per la selezione nel layer sorgente.
    """
    warnings = []
    bad_ids = set()

    # ── Geometria nulla ──────────────────────────────────────────────────────
    if skipped_null:
        warnings.append(
            f"{skipped_null} condotta/e con geometria nulla o degenere "
            f"(< 2 vertici) — ignorate")

    if not archi:
        return warnings, bad_ids

    # ── Duplicati topologici ─────────────────────────────────────────────────
    seen = {}  # (min_a, max_b) -> arc dict
    dups = []
    for e in archi:
        key = (min(e['a'], e['b']), max(e['a'], e['b']))
        if key in seen:
            dups.append((seen[key], e))
        else:
            seen[key] = e
    if dups:
        def _dup_info(a, b):
            label_a = _arc_label(a)
            label_b = _arc_label(b)
            # Punto medio della prima condotta per permettere localizzazione
            try:
                coords = a['coords']
                mid = coords[len(coords) // 2]
                return (f"(condotta {label_a} e condotta {label_b})"
                        f" — punto medio ≈ ({mid[0]:.0f}, {mid[1]:.0f})")
            except Exception:
                return f"(condotta {label_a} e condotta {label_b})"
        examples = ', '.join(_dup_info(a, b) for a, b in dups[:5])
        warnings.append(
            f"{len(dups)} condotta/e duplicata/e (stessa coppia nodi A-B): "
            f"{examples}" +
            (" ..." if len(dups) > 5 else ""))
        for a, b in dups:
            bad_ids.add(_arc_label(a))
            bad_ids.add(_arc_label(b))

    # ── Sovrapposizione geometrica ───────────────────────────────────────────
    seen_geom = {}
    overlaps = []
    for e in archi:
        c0 = round_coord(e['coords'][0])
        c1 = round_coord(e['coords'][-1])
        key = (min(c0, c1, key=str), max(c0, c1, key=str))
        if key in seen_geom:
            overlaps.append((seen_geom[key], e))
        else:
            seen_geom[key] = e
    if overlaps:
        def _ovlp_info(a, b):
            label_b = _arc_label(b)
            # Punto medio + coordinate estreme per localizzazione
            try:
                coords = b['coords']
                mid = coords[len(coords) // 2]
                c0, c1 = coords[0], coords[-1]
                return (f"condotta {label_b}"
                        f" [({c0[0]:.0f},{c0[1]:.0f})→({c1[0]:.0f},{c1[1]:.0f})]"
                        f" punto medio ≈ ({mid[0]:.0f},{mid[1]:.0f})")
            except Exception:
                return f"condotta {label_b}"
        examples = ', '.join(_ovlp_info(a, b) for a, b in overlaps[:5])
        warnings.append(
            f"{len(overlaps)} condotta/e sovrapposta/e geometricamente: "
            f"{examples}" +
            (" ..." if len(overlaps) > 5 else ""))
        for a, b in overlaps:
            bad_ids.add(_arc_label(a))
            bad_ids.add(_arc_label(b))

    # ── Componenti connesse (isole) ──────────────────────────────────────────
    parent = {}

    def _find(x):
        if x not in parent:
            parent[x] = x
        # path compression iterativa (evita ricorsione su reti grandi)
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def _union(x, y):
        px, py = _find(x), _find(y)
        if px != py:
            parent[px] = py

    for e in archi:
        _union(e['a'], e['b'])

    comp_nodes = defaultdict(set)
    comp_edges = defaultdict(int)
    for e in archi:
        root = _find(e['a'])
        comp_nodes[root].add(e['a'])
        comp_nodes[root].add(e['b'])
        comp_edges[root] += 1

    n_components = len(comp_nodes)
    if n_components > 1:
        # Ordina componenti dalla più grande alla più piccola (per numero di nodi)
        sorted_roots = sorted(comp_nodes.keys(),
                              key=lambda r: len(comp_nodes[r]), reverse=True)
        sizes = [(len(comp_nodes[r]), comp_edges[r]) for r in sorted_roots]
        size_str = ', '.join(f"{n}n/{e}c" for n, e in sizes[:6])
        msg = (f"Rete sconnessa: {n_components} componenti separate (isole). "
               f"Dimensioni (nodi/condotte): {size_str}"
               + (" ..." if n_components > 6 else "") + ".")

        # Per le isole minori (tutte tranne la principale) elenca i FID
        # delle condotte se sono poche, altrimenti fornisce l'espressione QGIS
        minor_roots = sorted_roots[1:]  # escludi la componente più grande
        for root in minor_roots:
            fids = sorted(e['id'] for e in archi if _find(e['a']) == root)
            n_pipes = len(fids)
            if n_pipes <= 30:
                fid_list = ', '.join(str(f) for f in fids)
                msg += (f"\n  Isola ({len(comp_nodes[root])}n/{n_pipes}c) — "
                        f"seleziona in QGIS: $id IN ({fid_list})")
            else:
                msg += (f"\n  Isola ({len(comp_nodes[root])}n/{n_pipes}c) — "
                        f"troppi FID da listare ({n_pipes}), usa lo strumento "
                        f"di selezione spaziale su QGIS.")
        msg += ("\n\u26a0 CORREGGERE LE ISOLE PRIMA DEL COLLASSO: "
                "usare 'Snap endpoint' in Tab 0, poi ri-analizzare. "
                "La simulazione usa solo la componente col nodo reference.")
        warnings.append(msg)

    return warnings, bad_ids


def make_memory_layers(archi, nodo_xy, matched=None,
                        diam_field='Diametro_pollici', diam_unit='in',
                        crs=CRS_DEFAULT,
                        fid_map=None):
    """
    Crea layer pipe e nodi in memoria QGIS.
    - Pipe: segmento retto tra endpoint, lunghezza misurata sul percorso reale.
    - Nodi: matched=1 se agganciato a nodo utente (→ reference per simulazione).
    - fid_map: dict {nid: QgsFeature} con TUTTI i nodi utente agganciati (non solo
               i reference) — usato esclusivamente per impostare fid_ut.
               Se None, viene usato matched anche per fid_ut.
    Ritorna: (pipes_lyr, nodes_lyr)
    """
    from qgis.core import (QgsVectorLayer, QgsField, QgsFeature,
                            QgsGeometry, QgsPoint, QgsPointXY)
    from PyQt5.QtCore import QVariant

    remaining_nodes = set()
    for e in archi:
        remaining_nodes.add(e['a'])
        remaining_nodes.add(e['b'])

    has_z = bool(nodo_xy) and len(next(iter(nodo_xy.values()))) == 3

    # ── Layer pipe ────────────────────────────────────────────────────────────
    geom_type_line = f"LineStringZ?crs={crs}" if has_z else f"LineString?crs={crs}"
    pipes_lyr = QgsVectorLayer(geom_type_line, "RNT_Pipe_Collassate", "memory")
    pp = pipes_lyr.dataProvider()
    pp.addAttributes([
        QgsField("pipe_id",    QVariant.Int),
        QgsField("node_a",     QVariant.Int),
        QgsField("node_b",     QVariant.Int),
        QgsField("length_m",   QVariant.Double),
        QgsField("diameter_m", QVariant.Double),
        QgsField("src_fids",   QVariant.String),
    ])
    pipes_lyr.updateFields()

    pipe_feats = []
    for i, e in enumerate(archi, 1):
        real_len = path_length_3d(e['coords'])
        straight_coords = [e['coords'][0], e['coords'][-1]]
        geom = coords_to_qgsgeom(straight_coords)
        raw_diam = e['attrs'].get(diam_field, None)
        try:
            _rd = float(raw_diam)
            if diam_unit == 'in':
                diam_m = _rd * 0.0254
            elif diam_unit == 'cm':
                diam_m = _rd * 0.01
            else:  # 'm'
                diam_m = _rd
        except (TypeError, ValueError):
            diam_m = None
        _src = ','.join(str(x) for x in e.get('src_fids', [e['id']]))
        f = QgsFeature()
        f.setGeometry(geom)
        f.setAttributes([i, e['a'], e['b'], round(real_len, 2),
                          round(diam_m, 6) if diam_m is not None else None,
                          _src])
        pipe_feats.append(f)
    pp.addFeatures(pipe_feats)

    # ── Layer nodi ────────────────────────────────────────────────────────────
    geom_type_pt = f"PointZ?crs={crs}" if has_z else f"Point?crs={crs}"
    nodes_lyr = QgsVectorLayer(geom_type_pt, "RNT_Nodi_Collassati", "memory")
    np_ = nodes_lyr.dataProvider()
    if has_z:
        fields_def = [
            QgsField("node_id",    QVariant.Int),
            QgsField("x_utm",      QVariant.Double),
            QgsField("y_utm",      QVariant.Double),
            QgsField("z_m",        QVariant.Double),
            QgsField("altitude_m", QVariant.Double),
            QgsField("matched",    QVariant.Int),
            QgsField("fid_ut",     QVariant.Int),
            QgsField("label_ut",   QVariant.String),
        ]
    else:
        fields_def = [
            QgsField("node_id",  QVariant.Int),
            QgsField("x_utm",    QVariant.Double),
            QgsField("y_utm",    QVariant.Double),
            QgsField("z_m",      QVariant.Double),
            QgsField("matched",  QVariant.Int),
            QgsField("fid_ut",   QVariant.Int),
            QgsField("label_ut", QVariant.String),
        ]
    np_.addAttributes(fields_def)
    nodes_lyr.updateFields()

    node_feats = []
    for nid in sorted(remaining_nodes):
        coord = nodo_xy[nid]
        x, y = coord[0], coord[1]
        z = coord[2] if has_z else 0.0
        user_feat = (matched or {}).get(nid)
        # Per fid_ut usa fid_map se disponibile (tutti i nodi utente),
        # altrimenti cade su matched (solo i reference)
        fid_feat = (fid_map or matched or {}).get(nid) if fid_map is not None else user_feat
        is_matched = 1 if user_feat is not None else 0
        fid_ut, label_ut = -1, ""
        if fid_feat is not None:
            fid_idx = fid_feat.fields().indexOf('fid')
            if fid_idx >= 0:
                v = fid_feat.attributes()[fid_idx]
                if v is not None and str(v).upper() not in ('NULL', ''):
                    try:
                        fid_ut = int(v)
                    except Exception:
                        pass
            # Fallback: usa l'ID interno QGIS se non c'è campo 'fid'
            if fid_ut == -1:
                try:
                    fid_ut = int(fid_feat.id())
                except Exception:
                    pass
        if fid_feat is not None or user_feat is not None:
            src = fid_feat if fid_feat is not None else user_feat
            for fi in src.fields():
                if fi.type() == QVariant.String:
                    v = src.attribute(fi.name())
                    if v is not None and str(v).upper() not in ('NULL', ''):
                        label_ut = str(v)[:80]
                        break
        f = QgsFeature()
        if has_z:
            f.setGeometry(QgsGeometry(QgsPoint(x, y, z)))
            f.setAttributes([nid, x, y, z, z, is_matched, fid_ut, label_ut])
        else:
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
            f.setAttributes([nid, x, y, z, is_matched, fid_ut, label_ut])
        node_feats.append(f)
    np_.addFeatures(node_feats)

    return pipes_lyr, nodes_lyr


# ── Export a CSV ──────────────────────────────────────────────────────────────

def extract_compressor_specs(matched, comp_field, comp_value,
                             ratio_field=None, eff_field=None, proc_field=None,
                             p_out_field=None, use_pcm=True):
    """
    Dai nodi-utente già agganciati alla rete (dict {nid: QgsFeature}), estrae le
    specifiche compressore per quelli con feat[comp_field] == comp_value.

    Ritorna: list[dict] con chiavi 'nid', 'ratio', 'eff', 'proc' e
    opzionalmente 'p_out_bar' (se p_out_field è valorizzato per quel nodo).
    Lista vuota se comp_field/comp_value non specificati o nessun nodo combacia.
    """
    specs = []
    if not matched or not comp_field or not comp_value:
        return specs
    target = str(comp_value).strip().lower()
    for nid, feat in matched.items():
        try:
            val = str(feat.attribute(comp_field) or '').strip().lower()
        except Exception:
            val = ''
        if val != target:
            continue

        def _read(field, default):
            if not field:
                return default
            try:
                raw = feat.attribute(field)
            except Exception:
                return default
            if raw is None or str(raw).strip() == '':
                return default
            return raw

        try:
            ratio = float(_read(ratio_field, COMP_RATIO_DEFAULT))
        except (TypeError, ValueError):
            ratio = COMP_RATIO_DEFAULT
        try:
            eff = float(_read(eff_field, COMP_EFF_DEFAULT))
        except (TypeError, ValueError):
            eff = COMP_EFF_DEFAULT
        proc = str(_read(proc_field, COMP_PROC_DEFAULT)).strip() or COMP_PROC_DEFAULT

        # p_out opzionale (bar): se presente, vince sul ratio (verra' tradotto
        # in ratio dinamicamente usando la p_in baseline in inject_*).
        p_out_bar = None
        if p_out_field:
            # L'utente puo' aver inserito un nome campo o direttamente un valore numerico fisso
            try:
                p_out_bar = float(p_out_field)
            except ValueError:
                try:
                    raw_pout = feat.attribute(p_out_field)
                except Exception:
                    raw_pout = None
                if raw_pout is not None and str(raw_pout).strip() != '':
                    try:
                        p_out_bar = float(raw_pout)
                    except (TypeError, ValueError):
                        p_out_bar = None

        spec = {
            'nid':   int(nid),
            'ratio': ratio,
            'eff':   eff,
            'proc':  proc,
            'use_pcm': use_pcm,
        }
        if p_out_bar is not None:
            spec['p_out_bar'] = p_out_bar
        specs.append(spec)
    return specs


def _read_pipe_flow_signs(results_pipes_csv):
    """Legge results_pipes.csv → dict {pipe_id: signed_flow_sm3s}.

    Il segno è quello della convenzione GasNetSim:
      flow > 0  → gas va da inlet_index a outlet_index della pipeline
      flow < 0  → gas va in verso opposto
    """
    import csv as _csv
    signs = {}
    try:
        with open(results_pipes_csv, 'r', encoding='utf-8') as f:
            reader = _csv.DictReader(f, delimiter=';')
            for row in reader:
                try:
                    pid = int(row['pipe_id'])
                    val = float(row['flow_sm3h'])
                except (TypeError, ValueError, KeyError):
                    continue
                signs[pid] = val
    except FileNotFoundError:
        pass
    return signs


def _read_node_pressures_bar(results_nodes_csv):
    """Legge results_nodes.csv → dict {node_id: pressure_bar}."""
    import csv as _csv
    pressures = {}
    try:
        with open(results_nodes_csv, 'r', encoding='utf-8') as f:
            reader = _csv.DictReader(f, delimiter=';')
            for row in reader:
                try:
                    nid = int(row['node_id'])
                    val = float(row['pressure_bar'])
                except (TypeError, ValueError, KeyError):
                    continue
                pressures[nid] = val
    except FileNotFoundError:
        pass
    return pressures


def inject_compressors_into_csvs(nodes_csv_path, pipes_csv_path,
                                 comp_specs, results_pipes_csv,
                                 results_nodes_csv=None,
                                 log=None):
    """
    Inietta i compressori nei CSV GasNetSim sdoppiando il nodo originale e
    riassegnando le pipeline incidenti in base al SEGNO del flusso ottenuto
    da una simulazione base (results_pipes.csv).

    Per ogni compressore in comp_specs:
      1. Trova le pipe incidenti al nid (da sf_pipelines.csv).
      2. Classifica ciascuna pipe in 'IN' (flusso entrante in nid) o
         'OUT' (uscente), tenendo conto del segno e del verso geometrico
         (inlet_index/outlet_index).
      3. Crea un nuovo nodo new_nid (duplicato del nid: coord, quota, ecc.,
         con demand 0 e node_type vuoto).
      4. Per ogni pipe del set OUT: sostituisce il nid con new_nid
         all'estremità che era il nid.
      5. Aggiunge una riga in sf_compressors.csv: idx;nid;new_nid;ratio;eff;proc.

    Scrive in-place i CSV nodi e pipe; crea/sovrascrive sf_compressors.csv
    nella stessa cartella.

    Ritorna: dict {nid_originale: new_nid} e path a sf_compressors.csv.
    """
    import csv as _csv
    if log is None:
        log = print

    nodes_csv_path = Path(nodes_csv_path)
    pipes_csv_path = Path(pipes_csv_path)
    out_dir = nodes_csv_path.parent

    if not comp_specs:
        return {}, None

    # ── Carica nodi e pipe ──
    with open(nodes_csv_path, 'r', encoding='utf-8') as f:
        nodes_reader = _csv.DictReader(f, delimiter=';')
        nodes_rows = list(nodes_reader)
        nodes_fields = nodes_reader.fieldnames or NODES_HEADER

    with open(pipes_csv_path, 'r', encoding='utf-8') as f:
        pipes_reader = _csv.DictReader(f, delimiter=';')
        pipes_rows = list(pipes_reader)
        pipes_fields = pipes_reader.fieldnames or PIPES_HEADER

    # Index nodi per id
    nodes_by_id = {}
    max_nid = -1
    for r in nodes_rows:
        try:
            nid = int(r['node_index'])
        except (TypeError, ValueError):
            continue
        nodes_by_id[nid] = r
        if nid > max_nid:
            max_nid = nid

    # Flow signs dalla simulazione base
    flow_signs = _read_pipe_flow_signs(results_pipes_csv)
    if not flow_signs:
        log(f"  ⚠ Nessun segno di flusso disponibile in {results_pipes_csv}; "
            "i compressori NON saranno iniettati.")
        return {}, None

    # Pressioni nodi baseline (per spec con p_out_bar target)
    node_pressures_bar = {}
    if results_nodes_csv:
        node_pressures_bar = _read_node_pressures_bar(results_nodes_csv)

    rename_map = {}        # nid_originale -> new_nid
    comp_rows = []
    next_nid = max_nid + 1
    next_comp_idx = 1

    for spec in comp_specs:
        nid = spec['nid']
        if nid not in nodes_by_id:
            log(f"  ⚠ Compressore: nodo {nid} non trovato nei nodi, skip.")
            continue

        # Trova pipe incidenti
        incident = []
        for prow in pipes_rows:
            try:
                a = int(prow['inlet_index']); b = int(prow['outlet_index'])
                pid = int(prow['pipeline_index'])
            except (TypeError, ValueError, KeyError):
                continue
            if nid == a or nid == b:
                incident.append((pid, prow, a, b))

        if len(incident) < 2:
            log(f"  ⚠ Compressore su nodo {nid}: solo {len(incident)} pipe "
                "incidente/i, impossibile classificare. Skip.")
            continue

        in_set, out_set, unknown = [], [], []
        for pid, prow, a, b in incident:
            flow = flow_signs.get(pid)
            if flow is None or abs(flow) < 1e-9:
                unknown.append((pid, prow, a, b))
                continue
            # Segno positivo: da a verso b
            # Caso nid == b: flow>0 entra in nid
            # Caso nid == a: flow>0 esce da nid
            if nid == b:
                (in_set if flow > 0 else out_set).append((pid, prow, a, b))
            else:  # nid == a
                (out_set if flow > 0 else in_set).append((pid, prow, a, b))

        if not in_set or not out_set:
            log(f"  ⚠ Compressore su nodo {nid}: classificazione degenerata "
                f"(IN={len(in_set)}, OUT={len(out_set)}, ambigui={len(unknown)}). "
                "Verifica i risultati base. Skip.")
            continue

        # Pipe con flusso ~0: alloca al lato OUT per default (scelta neutra
        # — segnaliamo all'utente).
        for tup in unknown:
            out_set.append(tup)
            log(f"  ⚠ Pipe {tup[0]} su compressore {nid}: flusso ~0, "
                "assegnata al lato OUT per default.")

        # Se l'utente ha specificato un p_out target (bar), calcola il ratio
        # dinamicamente usando la p_in (= pressione del nodo nid nella
        # simulazione baseline). Approssimazione di primo ordine: dopo
        # l'iniezione del compressore la p_in cambierà leggermente, ma il
        # valore di partenza è sufficientemente vicino al target.
        ratio_used = spec['ratio']
        control_mode = "ratio"
        if spec.get('p_out_bar') is not None:
            # Test impl: Se p_out_bar è specificato, usiamo PCM di default per il test
            if spec.get('use_pcm', True):
                control_mode = "pressure"
                # Il ratio_used è calcolato in modo fittizio, il PCM lo ignorerà in parte
                p_in_bar = node_pressures_bar.get(nid)
                if p_in_bar and p_in_bar > 0:
                    ratio_used = float(spec['p_out_bar']) / float(p_in_bar)
            else:
                p_in_bar = node_pressures_bar.get(nid)
                if p_in_bar is None or p_in_bar <= 0:
                    log(f"  ⚠ Compressore su nodo {nid}: p_out={spec['p_out_bar']} bar "
                        f"richiesto ma p_in baseline non disponibile. Uso ratio={ratio_used:.3f}.")
                else:
                    ratio_used = float(spec['p_out_bar']) / float(p_in_bar)
                    if ratio_used < 1.0:
                        fallback_ratio = max(1.1, float(spec.get('ratio', 1.1)))
                        log(f"  ⚠ Compressore su nodo {nid}: p_out={spec['p_out_bar']} bar "
                            f"<= p_in={p_in_bar:.2f} bar. (Baseline anomala o stallo). "
                            f"Per non bloccare la rete, forzo ratio={fallback_ratio:.3f} di emergenza.")
                        ratio_used = fallback_ratio

        # Crea nuovo nodo (duplicato del nid, demand 0, node_type vuoto)
        new_nid = next_nid
        next_nid += 1
        rename_map[nid] = new_nid

        src = nodes_by_id[nid]
        dup = {k: src.get(k, '') for k in nodes_fields}
        dup['node_index']     = str(new_nid)
        dup['flow_sm3_per_s'] = str(PLACEHOLDER_FLOW)
        dup['flow_MW']        = ''
        
        # Il nodo di uscita del compressore e' SEMPRE una giunzione normale
        # (node_type vuoto, nessuna pressione imposta), sia in controllo di
        # pressione (PCM) sia in controllo di rapporto.
        #
        # In PCM la pressione di mandata NON viene imposta rendendo il nodo un
        # 'reference' (che avrebbe portata libera e agirebbe da sorgente
        # illimitata in mezzo alla rete, scollegando i tronconi a monte e a
        # valle): e' imposta da una riga di vincolo  p_out - p_out_target = 0
        # nella formulazione aumentata (PressureProblem._augment), con la
        # portata del compressore come incognita del sistema. p_out_target
        # resta in sf_compressors.csv: e' li' che il vincolo va a leggerlo.
        dup['node_type']   = ''
        dup['pressure_pa'] = ''

        nodes_rows.append(dup)
        nodes_by_id[new_nid] = dup

        # Il nodo originale resta sul lato IN: forza demand 0 e node_type vuoto
        # (qualunque etichetta precedente è incompatibile col ruolo "lato inlet
        # compressore"). Non tocchiamo coordinate/altitudine.
        src['flow_sm3_per_s'] = str(PLACEHOLDER_FLOW)
        src['flow_MW']        = ''
        if (src.get('node_type') or '').strip().lower() not in ('', 'reference'):
            src['node_type'] = ''

        # Riassegna pipe OUT al new_nid
        for pid, prow, a, b in out_set:
            if a == nid:
                prow['inlet_index'] = str(new_nid)
            if b == nid:
                prow['outlet_index'] = str(new_nid)

        comp_rows.append({
            'compressor_index':      next_comp_idx,
            'inlet':                 nid,
            'outlet':                new_nid,
            'compression_ratio':     ratio_used,
            'efficiency':            spec['eff'],
            'thermodynamic_process': spec['proc'],
            'control_mode':          control_mode,
            'p_out_target':          (spec.get('p_out_bar', 0) * 1e5) if control_mode == "pressure" else ""
        })
        next_comp_idx += 1
        
        if control_mode == "pressure":
            log(f"  ✓ Compressore {comp_rows[-1]['compressor_index']}: nodo {nid} "
                f"→ controllo di pressione, OUT nodo {new_nid} "
                f"(giunzione, p_out target {spec['p_out_bar']:.2f} bar)")
        elif spec.get('p_out_bar') is not None:
            log(f"  ✓ Compressore {comp_rows[-1]['compressor_index']}: nodo {nid} "
                f"→ split in {nid} (IN, {len(in_set)} pipe) e {new_nid} "
                f"(OUT, {len(out_set)} pipe), p_out_target={spec['p_out_bar']:.2f} bar "
                f"→ ratio={ratio_used:.3f}")
        else:
            log(f"  ✓ Compressore {comp_rows[-1]['compressor_index']}: nodo {nid} "
                f"→ split in {nid} (IN, {len(in_set)} pipe) e {new_nid} "
                f"(OUT, {len(out_set)} pipe), ratio={ratio_used:.3f}")

    if not comp_rows:
        return {}, None

    # ── Riscrivi nodi e pipe ──
    with open(nodes_csv_path, 'w', newline='', encoding='utf-8') as f:
        w = _csv.DictWriter(f, fieldnames=nodes_fields, delimiter=';')
        w.writeheader()
        w.writerows(nodes_rows)

    with open(pipes_csv_path, 'w', newline='', encoding='utf-8') as f:
        w = _csv.DictWriter(f, fieldnames=pipes_fields, delimiter=';')
        w.writeheader()
        w.writerows(pipes_rows)

    # ── Scrivi sf_compressors.csv ──
    comp_csv = out_dir / 'sf_compressors.csv'
    with open(comp_csv, 'w', newline='', encoding='utf-8') as f:
        w = _csv.DictWriter(f, fieldnames=COMPRESSORS_HEADER, delimiter=';')
        w.writeheader()
        w.writerows(comp_rows)

    return rename_map, comp_csv


def export_layers_to_csv(pipes_lyr, nodes_lyr, out_dir, ora=0,
                          pressure_ref_pa=PRESSURE_REF_PA,
                          temp_ref_k=TEMP_REF_K,
                          gas_comp_ref=GAS_COMP_REF,
                          roughness_m=ROUGHNESS_M,
                          placeholder_flow=PLACEHOLDER_FLOW,
                          # Pipe field mapping
                          f_pipe_id='pipe_id', f_node_a='node_a',
                          f_node_b='node_b', f_length='length_m',
                          f_diam='diameter_m', f_diam_unit='m',
                          # Node field mapping
                          f_node_id='node_id', f_altitude='altitude_m',
                          f_ref_flag='matched', ref_flag_value='1',
                          f_flow='Totale_Smc',
                          flow_sep=';',
                          # Domanda da layer esterno {node_id_int: flow_sm3s}
                          demands_dict=None):
    """
    Converte i layer QGIS (memoria o file) in sf_nodes.csv + sf_pipelines.csv.

    Field mapping (default: output di make_memory_layers / collasso):
      Pipe : f_pipe_id, f_node_a, f_node_b, f_length, f_diam + f_diam_unit
      Nodi : f_node_id, f_altitude, f_ref_flag + ref_flag_value, f_flow

    f_ref_flag / ref_flag_value:
      Il campo il cui valore (convertito in str) == ref_flag_value
      identifica i nodi reference (pressione nota).
      Es. campo 'matched', valore '1'  →  matched == 1
          campo 'Type',    valore 'reference'  →  Type == 'reference'

    f_flow:
      Campo con flussi orari (stringa sep=';' in Smc/ora).
      Se '' o None: tutti i nodi junction usano placeholder_flow.

    Ritorna: (nodes_path, pipes_path, n_nodes, c_ref, c_junc, n_pipes)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── sf_nodes.csv ──────────────────────────────────────────────────────────
    rows_nodes = []
    node_fields = [f.name() for f in nodes_lyr.fields()]

    for feat in nodes_lyr.getFeatures():
        attrs = dict(zip(node_fields, feat.attributes()))
        node_index = attrs.get(f_node_id)
        if node_index is None:
            continue

        flag_raw = attrs.get(f_ref_flag, '')
        s_val = str(flag_raw).strip()
        s_ref = str(ref_flag_value).strip()
        is_ref = (s_val == s_ref)
        if not is_ref:
            try:
                is_ref = (float(s_val) == float(s_ref))
            except (ValueError, TypeError):
                pass

        alt = attrs.get(f_altitude) or attrs.get('z_m') or 0.0
        try:
            alt = float(alt) if alt is not None else 0.0
        except (TypeError, ValueError):
            alt = 0.0

        if is_ref:
            row = {
                "node_index":      int(node_index),
                "pressure_pa":     pressure_ref_pa,
                "flow_MW":         "",
                "flow_sm3_per_s":  "",
                "altitude_m":      alt,
                "temperature_k":   temp_ref_k,
                "gas_composition": gas_comp_ref,
                "node_type":       "reference",
                "latitude":        "",
                "longitude":       "",
                "flow_type":       "volumetric",
            }
        else:
            # Domanda: 1) layer esterno (demands_dict), 2) campo f_flow, 3) placeholder
            nid_int = None
            try:
                nid_int = int(node_index)
            except (TypeError, ValueError):
                pass
            if demands_dict is not None and nid_int in demands_dict:
                flow = demands_dict[nid_int]
            else:
                smc_str = (attrs.get(f_flow, '') or '') if f_flow else ''
                if smc_str:
                    parsed = _parse_smc_ora(str(smc_str), ora, sep=flow_sep)
                    flow = parsed if parsed != PLACEHOLDER_FLOW else placeholder_flow
                else:
                    flow = placeholder_flow
            # Composizione gas per-nodo: campo 'gas_comp' nel layer (opzionale)
            node_gas_comp = str(attrs.get('gas_comp', '') or '').strip()
            row = {
                "node_index":      int(node_index),
                "pressure_pa":     "",
                "flow_MW":         "",
                "flow_sm3_per_s":  flow,
                "altitude_m":      alt,
                "temperature_k":   "",
                "gas_composition": node_gas_comp,
                "node_type":       "",
                "latitude":        "",
                "longitude":       "",
                "flow_type":       "volumetric",
            }
        rows_nodes.append(row)

    nodes_path = out_dir / "sf_nodes.csv"
    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=NODES_HEADER, delimiter=";")
        writer.writeheader()
        writer.writerows(rows_nodes)

    # ── sf_pipelines.csv ──────────────────────────────────────────────────────
    rows_pipes = []
    seen_keys: set = set()
    pipe_fields = [f.name() for f in pipes_lyr.fields()]

    for feat in pipes_lyr.getFeatures():
        attrs = dict(zip(pipe_fields, feat.attributes()))
        pipe_id = attrs.get(f_pipe_id)
        na      = attrs.get(f_node_a)
        nb      = attrs.get(f_node_b)
        if any(v is None for v in [pipe_id, na, nb]):
            continue

        raw_diam = attrs.get(f_diam)
        try:
            _rd = float(raw_diam)
            if f_diam_unit == 'in':
                diam_m = _rd * 0.0254
            elif f_diam_unit == 'cm':
                diam_m = _rd * 0.01
            else:  # 'm'
                diam_m = _rd
        except (TypeError, ValueError):
            diam_m = 0.305

        try:
            length_m = float(attrs.get(f_length) or 0)
        except (TypeError, ValueError):
            length_m = 0.0

        key = (frozenset({int(na), int(nb)}), round(length_m, 2), round(diam_m, 4))
        if key in seen_keys:
            continue
        seen_keys.add(key)

        rows_pipes.append({
            "pipeline_index": int(pipe_id),
            "inlet_index":    int(na),
            "outlet_index":   int(nb),
            "diameter_m":     diam_m,
            "length_m":       length_m,
            "friction_method": FRICTION_METHOD,
            "roughness_m":    roughness_m,
        })

    pipes_path = out_dir / "sf_pipelines.csv"
    with open(pipes_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PIPES_HEADER, delimiter=";")
        writer.writeheader()
        writer.writerows(rows_pipes)

    c_ref = sum(1 for r in rows_nodes if r.get('node_type') == 'reference')
    c_junc = len(rows_nodes) - c_ref

    return nodes_path, pipes_path, len(rows_nodes), c_ref, c_junc, len(rows_pipes)


# ── Pipeline completa ─────────────────────────────────────────────────────────

def run_collapse_pipeline(pipe_layer, out_dir, ora=0,
                           dem_layer=None, nodes_layer=None,
                           diam_field='Diametro_pollici', diam_unit='in',
                           radius_m=50.0, log=None,
                           pressure_ref_pa=PRESSURE_REF_PA,
                           temp_ref_k=TEMP_REF_K,
                           roughness_m=ROUGHNESS_M,
                           gas_comp_ref=GAS_COMP_REF,
                           placeholder_flow=PLACEHOLDER_FLOW,
                           loads_layer=None, loads_field=None,
                           ref_field=None, ref_value=None,
                           comp_field=None, comp_value=None,
                           comp_pout_field=None, comp_use_pcm=True,
                           flow_sep=';'):
    """
    Pipeline completa: QGIS layer → collasso → CSV GasNetSim.

    Parametri:
        pipe_layer      : QgsVectorLayer (LineString) — condotte
        out_dir         : cartella dove scrivere i CSV (verrà creata)
        ora             : ora del giorno 0-23 per flussi orari
        dem_layer       : QgsRasterLayer opzionale per draping Z
        nodes_layer     : QgsVectorLayer opzionale (Point) nodi reference
        diam_field      : nome campo diametro nel pipe_layer
        diam_unit       : 'in' (pollici) o 'm' (metri)
        radius_m        : raggio aggancio nodi (m)
        log             : callable(msg: str) per logging, default=print
        pressure_ref_pa : pressione reference [Pa] per i nodi agganciati
        temp_ref_k      : temperatura reference [K]

    Ritorna:
        (pipes_lyr, nodes_lyr, nodes_csv_path, pipes_csv_path)
        pipes_lyr / nodes_lyr = layer QGIS in memoria (NON ancora aggiunti al progetto)
    """
    import processing as _proc
    from PyQt5.QtCore import QCoreApplication

    if log is None:
        log = print

    warnings = []  # Avvisi da mostrare all'utente
    log(f"Layer: {pipe_layer.name()} ({pipe_layer.featureCount()} feature)")

    # Step 1a: Correggi geometrie invalide
    log("Step 1a: Correzione geometrie...")
    fixed = _proc.run("native:fixgeometries", {
        'INPUT': pipe_layer, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']
    QCoreApplication.processEvents()
    log(f"  → {fixed.featureCount()} geometrie")

    # Step 1b: Esplodi polilinee in segmenti elementari
    log("Step 1b: Esplosione polilinee...")
    exploded = _proc.run("native:explodelines", {
        'INPUT': fixed, 'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']
    QCoreApplication.processEvents()
    log(f"  → {exploded.featureCount()} segmenti")

    # Step 2: Draping su DEM (opzionale)
    if dem_layer is not None:
        log(f"Step 2: Draping su DEM '{dem_layer.name()}'...")
        draped = _proc.run("native:setzfromraster", {
            'INPUT': exploded, 'RASTER': dem_layer,
            'BAND': 1, 'NODATA': 0, 'SCALE': 1,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        QCoreApplication.processEvents()
        log("  → draping completato")
        work_lyr = draped
    else:
        log("Step 2: Draping saltato (nessun DEM)")
        work_lyr = exploded

    # Step 2b: Split ai nodi utente (opzionale)
    if nodes_layer is not None:
        log(f"Step 2b: Split ai nodi utente (raggio {radius_m} m)...")
        work_lyr, n_splits = split_network_at_user_nodes(
            work_lyr, nodes_layer, radius_m, crs=pipe_layer.crs().authid())
        QCoreApplication.processEvents()
        log(f"  → {n_splits} split, {work_lyr.featureCount()} segmenti totali")

    # Step 3: Build grafo e collasso
    log("Step 3: Build grafo...")
    archi, nodo_xy, skipped_null = build_graph(work_lyr)
    log(f"  Iniziale: {len(nodo_xy)} nodi, {len(archi)} archi")
    
    if dem_layer is not None:
        archi, nodo_xy = apply_topological_laplacian_smoothing(archi, nodo_xy, log)
    # Controllo pipe: geometria nulla, duplicati, sovrapposizioni, isole
    pipe_warns, _ = check_pipe_issues(archi, skipped_null=skipped_null)
    for w in pipe_warns:
        log(f"  \u26a0 {w}")
        warnings.append(w)

    # Step 4: Aggancio e protezione nodi reference
    matched = {}
    protected = set()
    if nodes_layer is not None:
        matched = match_user_nodes(nodo_xy, nodes_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
        protected = set(matched.keys())
        log(f"  Nodi agganciati: {len(matched)}/{nodes_layer.featureCount()}")
        # Controlla nodi non connessi
        unmatched_labels = find_unmatched_user_nodes(nodo_xy, nodes_layer, radius_m=radius_m)
        if unmatched_labels:
            msg = (f"{len(unmatched_labels)} nodo/i NON connesso/i alla rete "
                   f"(fuori dal raggio {radius_m} m): "
                   f"{', '.join(unmatched_labels[:10])}"
                   + (" ..." if len(unmatched_labels) > 10 else ""))
            log(f"  ⚠ {msg}")
            warnings.append(msg)

    # Filtra quali nodi agganciati sono "reference" (pressione nota)
    # Se ref_field/ref_value specificati: solo quelli con feat[ref_field]==ref_value
    # Altrimenti: tutti i nodi agganciati sono reference
    if matched and ref_field and ref_value:
        reference = {nid: feat for nid, feat in matched.items()
                     if str(feat.attribute(ref_field) or '').strip() == str(ref_value).strip()}
        log(f"  Nodi reference (campo '{ref_field}'='{ref_value}'): {len(reference)}")
    else:
        reference = matched

    diam_protected = find_diameter_change_nodes(
        archi, diam_field=diam_field, diam_unit=diam_unit)
    protected |= diam_protected
    log(f"  Nodi cambio diametro protetti: {len(diam_protected)}")

    log("Step 3b: Collasso nodi grado-2...")
    archi = collapse_undirected(archi, protected=protected)
    log(f"  → {len(archi)} archi")

    log("Step 3c: Potatura rami pendenti...")
    archi = prune_dangling(archi, protected=protected)
    log(f"  → {len(archi)} archi")

    log("Step 3d: Collasso post-potatura...")
    archi = collapse_undirected(archi, protected=protected)
    log(f"  → {len(archi)} archi")
    QCoreApplication.processEvents()

    # Controllo sezioni isolate (componenti disconnesse)
    _adj = {}
    for _e in archi:
        _adj.setdefault(_e['a'], set()).add(_e['b'])
        _adj.setdefault(_e['b'], set()).add(_e['a'])
    _all_nodes = set(_adj.keys())
    _visited = set()
    _components = []
    for _start in sorted(_all_nodes):
        if _start in _visited:
            continue
        _comp = set()
        _stack = [_start]
        while _stack:
            _n = _stack.pop()
            if _n in _visited:
                continue
            _visited.add(_n)
            _comp.add(_n)
            _stack.extend(_adj[_n] - _visited)
        _components.append(_comp)
    if len(_components) > 1:
        _sizes = sorted([len(c) for c in _components], reverse=True)
        w = (f"Rete non connessa: {len(_components)} sezioni isolate. "
             f"Dimensioni (nodi): {_sizes}")
        log(f"  ⚠ {w}")
        warnings.append(w)
    else:
        log(f"  OK: rete connessa ({len(_all_nodes)} nodi)")

    # Verifica integrità nodi reference
    remaining = {e['a'] for e in archi} | {e['b'] for e in archi}
    missing = set(reference.keys()) - remaining
    if missing:
        log(f"  ATTENZIONE: {len(missing)} nodi reference mancanti nel grafo finale")
    else:
        log(f"  OK: tutti {len(reference)} nodi reference presenti")

    # Step 4b: Verifica quote e re-draping dei nodi finali (pre-simulazione)
    if dem_layer is not None:
        log("Step 4b: Verifica quote nodi finali...")
        verify_and_redrape_nodes(nodo_xy, remaining, dem_layer,
                                 work_lyr.crs(), log=log, warnings=warnings)

    # Step 5: Crea layer memoria QGIS
    log("Step 5: Creazione layer risultato...")
    # matched (reference) -> is_matched/node_type; matched_all -> fid_ut per tutti i nodi
    pipes_lyr, nodes_lyr = make_memory_layers(
        archi, nodo_xy, reference,
        diam_field=diam_field, diam_unit=diam_unit,
        crs=pipe_layer.crs().authid(),
        fid_map=matched)
    log(f"  Pipe: {pipes_lyr.featureCount()}, Nodi: {nodes_lyr.featureCount()}")

    # Step 5b: Mappa collasso → fid originali. Ogni condotta collassata
    # (pipeline_index) elenca i fid delle condotte ORIGINALI che la compongono,
    # con diametro e lunghezza: cosi, individuato un collo di bottiglia sul
    # modello collassato, si sa esattamente quali condotte modificare nel layer
    # di partenza.
    try:
        import csv as _csv
        from pathlib import Path as _P
        _P(out_dir).mkdir(parents=True, exist_ok=True)   # la cartella potrebbe non esistere ancora
        _map = _P(out_dir) / 'collapse_map.csv'
        with open(str(_map), 'w', newline='', encoding='utf-8') as _fh:
            _w = _csv.writer(_fh, delimiter=';')
            _w.writerow(['pipeline_index', 'node_a', 'node_b',
                         'diameter_m', 'length_m', 'n_orig', 'src_fids'])
            for _i, _e in enumerate(archi, 1):
                _rd = _e['attrs'].get(diam_field, None)
                try:
                    _rd = float(_rd)
                    _dm = _rd * 0.0254 if diam_unit == 'in' else (
                        _rd * 0.01 if diam_unit == 'cm' else _rd)
                except (TypeError, ValueError):
                    _dm = ''
                _src = _e.get('src_fids', [_e['id']])
                _w.writerow([_i, _e['a'], _e['b'],
                             round(_dm, 6) if _dm != '' else '',
                             round(path_length_3d(_e['coords']), 2),
                             len(_src), ','.join(str(x) for x in _src)])
        log(f"  Mappa collasso→fid originali: {_map.name}")
    except Exception as _exc:
        log(f"  (mappa collasso non scritta: {_exc})")

    # Step 6: Export CSV
    log(f"Step 6: Export CSV (ora={ora})...")
    # Step 6b: Costruisci demands_dict da loads_layer (opzionale)
    demands_dict = None
    raw_smc_dict = {}   # stringhe grezze 24 valori, per campo load_smc_h
    if loads_layer is not None and loads_field:
        lf = loads_field
        load_fields = [f.name() for f in loads_layer.fields()]
        if lf in load_fields:
            matched_loads = match_user_nodes(nodo_xy, loads_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
            demands_dict = {}
            for nid, feat in matched_loads.items():
                attrs_l = dict(zip(load_fields, feat.attributes()))
                smc_str = str(attrs_l.get(lf, '') or '')
                if smc_str:
                    parsed = _parse_smc_ora(smc_str, ora, sep=flow_sep)
                    demands_dict[nid] = parsed
                    raw_smc_dict[nid] = smc_str
            log(f"  Consumi agganciati: {len(demands_dict)} nodi")
        else:
            log(f"  ATTENZIONE: campo '{lf}' non trovato nel layer consumi")

    # Aggiungi campo 'load_smc_h' ai nodi collassati (per riuso in Modalità B)
    if raw_smc_dict:
        from qgis.core import QgsField
        from PyQt5.QtCore import QVariant
        nodes_lyr.dataProvider().addAttributes([QgsField('load_smc_h', QVariant.String)])
        nodes_lyr.updateFields()
        fld_idx = nodes_lyr.fields().indexOf('load_smc_h')
        nodes_lyr.startEditing()
        for feat in nodes_lyr.getFeatures():
            nid = feat['node_id']
            if nid is not None:
                try:
                    smc = raw_smc_dict.get(int(nid), '')
                    nodes_lyr.changeAttributeValue(feat.id(), fld_idx, smc)
                except (TypeError, ValueError):
                    pass
        nodes_lyr.commitChanges()
        log(f"  Campo 'load_smc_h' aggiunto ai nodi ({len(raw_smc_dict)} valori)")

    # Aggiungi campo 'gas_comp' al layer collassato leggendolo dal layer utente
    if loads_layer is not None:
        from qgis.core import QgsField
        from PyQt5.QtCore import QVariant
        user_fields = [f.name() for f in loads_layer.fields()]
        if 'gas_comp' in user_fields:
            matched_gc = match_user_nodes(nodo_xy, loads_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
            gc_dict = {}
            for nid, feat in matched_gc.items():
                attrs_gc = dict(zip(user_fields, feat.attributes()))
                val = str(attrs_gc.get('gas_comp', '') or '').strip()
                if val:
                    gc_dict[nid] = val
            if gc_dict:
                nodes_lyr.dataProvider().addAttributes([QgsField('gas_comp', QVariant.String)])
                nodes_lyr.updateFields()
                gc_idx = nodes_lyr.fields().indexOf('gas_comp')
                nodes_lyr.startEditing()
                for feat in nodes_lyr.getFeatures():
                    nid = feat['node_id']
                    if nid is not None:
                        try:
                            nodes_lyr.changeAttributeValue(feat.id(), gc_idx, gc_dict.get(int(nid), ''))
                        except (TypeError, ValueError):
                            pass
                nodes_lyr.commitChanges()
                log(f"  Campo 'gas_comp' propagato ({len(gc_dict)} nodi con composizione custom)")

    nodes_path, pipes_path, n_nodes, c_ref, c_junc, n_pipes = export_layers_to_csv(
        pipes_lyr, nodes_lyr, out_dir, ora=ora,
        pressure_ref_pa=pressure_ref_pa, temp_ref_k=temp_ref_k,
        gas_comp_ref=gas_comp_ref, roughness_m=roughness_m,
        placeholder_flow=placeholder_flow, demands_dict=demands_dict,
        flow_sep=flow_sep)
    log(f"  sf_nodes.csv:    {n_nodes} nodi ({c_ref} reference, {c_junc} junction)")
    log(f"  sf_pipelines.csv: {n_pipes} pipe")
    log(f"  Output: {out_dir}")

    if c_ref == 0:
        warnings.append(
            "Nessun nodo reference trovato nel layer nodi. "
            "La simulazione fallirà senza almeno un nodo a pressione fissa. "
            "Verifica il campo 'Flag reference' e il suo valore.")

    # ── Compressori: estrai specifiche dai nodi-utente con flag e salva
    #    in _pending_compressors.json per il SimWorker (due-pass: la prima
    #    sim dà i segni di flusso, la seconda usa sf_compressors.csv).
    _dump_pending_compressors(
        matched, comp_field, comp_value,
        out_dir, log,
        p_out_field=comp_pout_field,
        use_pcm=comp_use_pcm)

    return pipes_lyr, nodes_lyr, nodes_path, pipes_path, warnings


def _dump_pending_compressors(matched, comp_field, comp_value,
                              out_dir, log,
                              p_out_field=None, use_pcm=True):
    """Estrae comp_specs e li scrive in <out_dir>/_pending_compressors.json.
    Rimuove un eventuale file preesistente se non ci sono più compressori.
    """
    import json as _json
    pending_path = Path(out_dir) / '_pending_compressors.json'
    specs = extract_compressor_specs(
        matched, comp_field, comp_value,
        p_out_field=p_out_field,
        use_pcm=use_pcm
    )
    if specs:
        with open(pending_path, 'w', encoding='utf-8') as f:
            _json.dump(specs, f, indent=2)
        log(f"  Compressori marcati: {len(specs)} "
            f"(scritto {pending_path.name})")
    elif pending_path.exists():
        try:
            pending_path.unlink()
        except OSError:
            pass

def run_nocollapse_pipeline(pipe_layer, out_dir, ora=0,
                             dem_layer=None, nodes_layer=None,
                             diam_field='Diametro_pollici', diam_unit='in',
                             radius_m=50.0, log=None,
                             pressure_ref_pa=PRESSURE_REF_PA,
                             temp_ref_k=TEMP_REF_K,
                             roughness_m=ROUGHNESS_M,
                             gas_comp_ref=GAS_COMP_REF,
                             placeholder_flow=PLACEHOLDER_FLOW,
                             loads_layer=None, loads_field=None,
                             ref_field=None, ref_value=None,
                             comp_field=None, comp_value=None,
                             comp_pout_field=None, comp_use_pcm=True,
                             flow_sep=';'):
    """
    Pipeline senza collasso topologico: conserva TUTTI i nodi intermedi.
    Usa l'elevazione reale dal DEM per ogni nodo della rete originale.
    Identico a run_collapse_pipeline ma salta i passi di collasso e potatura
    dei nodi di grado 2.

    Utile quando si vuole preservare la topologia completa e le quote reali
    derivate dal raster DEM.

    Ritorna: (pipes_lyr, nodes_lyr, nodes_csv_path, pipes_csv_path, warnings)
    """
    import processing as _proc
    from PyQt5.QtCore import QCoreApplication

    if log is None:
        log = print

    warnings = []
    log(f"Layer: {pipe_layer.name()} ({pipe_layer.featureCount()} feature)")
    log("[MODALITA'] Nodi intermedi PRESERVATI (nessun collasso topologico)")

    # Step 1a: Correggi geometrie invalide
    log("Step 1a: Correzione geometrie...")
    fixed = _proc.run("native:fixgeometries", {
        'INPUT': pipe_layer, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']
    QCoreApplication.processEvents()
    log(f"  -> {fixed.featureCount()} geometrie")

    # Step 1b: Esplodi polilinee in segmenti elementari
    log("Step 1b: Esplosione polilinee...")
    exploded = _proc.run("native:explodelines", {
        'INPUT': fixed, 'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']
    QCoreApplication.processEvents()
    log(f"  -> {exploded.featureCount()} segmenti")

    # Step 2: Draping su DEM (necessario per quote reali ai nodi)
    if dem_layer is not None:
        log(f"Step 2: Draping su DEM '{dem_layer.name()}'...")
        draped = _proc.run("native:setzfromraster", {
            'INPUT': exploded, 'RASTER': dem_layer,
            'BAND': 1, 'NODATA': 0, 'SCALE': 1,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        QCoreApplication.processEvents()
        log("  -> draping completato (quota reale da raster)")
        work_lyr = draped
    else:
        log("Step 2: Draping saltato (nessun DEM -- quota sara' 0)")
        work_lyr = exploded

    # Step 2b: Split ai nodi utente (opzionale)
    if nodes_layer is not None:
        log(f"Step 2b: Split ai nodi utente (raggio {radius_m} m)...")
        work_lyr, n_splits = split_network_at_user_nodes(
            work_lyr, nodes_layer, radius_m, crs=pipe_layer.crs().authid())
        QCoreApplication.processEvents()
        log(f"  -> {n_splits} split, {work_lyr.featureCount()} segmenti totali")

    # Step 3: Build grafo -- NESSUN COLLASSO
    log("Step 3: Build grafo (senza collasso)...")
    archi, nodo_xy, skipped_null = build_graph(work_lyr)
    log(f"  Iniziale: {len(nodo_xy)} nodi, {len(archi)} archi")
    
    if dem_layer is not None:
        archi, nodo_xy = apply_topological_laplacian_smoothing(archi, nodo_xy, log)
    pipe_warns, _ = check_pipe_issues(archi, skipped_null=skipped_null)
    for w in pipe_warns:
        log(f"  {w}")
        warnings.append(w)

    # Step 4: Aggancio nodi reference
    matched = {}
    if nodes_layer is not None:
        matched = match_user_nodes(nodo_xy, nodes_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
        log(f"  Nodi agganciati: {len(matched)}/{nodes_layer.featureCount()}")
        unmatched_labels = find_unmatched_user_nodes(nodo_xy, nodes_layer, radius_m=radius_m)
        if unmatched_labels:
            msg = (f"{len(unmatched_labels)} nodo/i NON connesso/i alla rete "
                   f"(fuori dal raggio {radius_m} m): "
                   f"{', '.join(unmatched_labels[:10])}"
                   + (" ..." if len(unmatched_labels) > 10 else ""))
            log(f"  {msg}")
            warnings.append(msg)

    # Filtra reference
    if matched and ref_field and ref_value:
        reference = {nid: feat for nid, feat in matched.items()
                     if str(feat.attribute(ref_field) or '').strip() == str(ref_value).strip()}
        log(f"  Nodi reference (campo '{ref_field}'='{ref_value}'): {len(reference)}")
    else:
        reference = matched

    # Controllo connettivita'
    _adj = {}
    for _e in archi:
        _adj.setdefault(_e['a'], set()).add(_e['b'])
        _adj.setdefault(_e['b'], set()).add(_e['a'])
    _all_nodes = set(_adj.keys())
    _visited = set()
    _components = []
    for _start in sorted(_all_nodes):
        if _start in _visited:
            continue
        _comp = set()
        _stack = [_start]
        while _stack:
            _n = _stack.pop()
            if _n in _visited:
                continue
            _visited.add(_n)
            _comp.add(_n)
            _stack.extend(_adj[_n] - _visited)
        _components.append(_comp)
    if len(_components) > 1:
        _sizes = sorted([len(c) for c in _components], reverse=True)
        w = (f"Rete non connessa: {len(_components)} sezioni isolate. "
             f"Dimensioni (nodi): {_sizes}")
        log(f"  {w}")
        warnings.append(w)
    else:
        log(f"  OK: rete connessa ({len(_all_nodes)} nodi, {len(archi)} archi)")

    # Step 4b: Verifica quote e re-draping dei nodi finali (pre-simulazione)
    if dem_layer is not None:
        log("Step 4b: Verifica quote nodi finali...")
        verify_and_redrape_nodes(nodo_xy, _all_nodes, dem_layer,
                                 work_lyr.crs(), log=log, warnings=warnings)

    # Step 5: Crea layer memoria QGIS
    log("Step 5: Creazione layer risultato (rete completa)...")
    # matched (reference) -> is_matched/node_type; matched_all -> fid_ut per tutti i nodi
    pipes_lyr, nodes_lyr = make_memory_layers(
        archi, nodo_xy, reference,
        diam_field=diam_field, diam_unit=diam_unit,
        crs=pipe_layer.crs().authid(),
        fid_map=matched)
    pipes_lyr.setName("RNT_Pipe_Complete")
    nodes_lyr.setName("RNT_Nodi_Complete")
    log(f"  Pipe: {pipes_lyr.featureCount()}, Nodi: {nodes_lyr.featureCount()}")

    # Step 5b: Mappa collasso → fid originali. Ogni condotta collassata
    # (pipeline_index) elenca i fid delle condotte ORIGINALI che la compongono,
    # con diametro e lunghezza: cosi, individuato un collo di bottiglia sul
    # modello collassato, si sa esattamente quali condotte modificare nel layer
    # di partenza.
    try:
        import csv as _csv
        from pathlib import Path as _P
        _P(out_dir).mkdir(parents=True, exist_ok=True)   # la cartella potrebbe non esistere ancora
        _map = _P(out_dir) / 'collapse_map.csv'
        with open(str(_map), 'w', newline='', encoding='utf-8') as _fh:
            _w = _csv.writer(_fh, delimiter=';')
            _w.writerow(['pipeline_index', 'node_a', 'node_b',
                         'diameter_m', 'length_m', 'n_orig', 'src_fids'])
            for _i, _e in enumerate(archi, 1):
                _rd = _e['attrs'].get(diam_field, None)
                try:
                    _rd = float(_rd)
                    _dm = _rd * 0.0254 if diam_unit == 'in' else (
                        _rd * 0.01 if diam_unit == 'cm' else _rd)
                except (TypeError, ValueError):
                    _dm = ''
                _src = _e.get('src_fids', [_e['id']])
                _w.writerow([_i, _e['a'], _e['b'],
                             round(_dm, 6) if _dm != '' else '',
                             round(path_length_3d(_e['coords']), 2),
                             len(_src), ','.join(str(x) for x in _src)])
        log(f"  Mappa collasso→fid originali: {_map.name}")
    except Exception as _exc:
        log(f"  (mappa collasso non scritta: {_exc})")

    # Step 6: Export CSV
    log(f"Step 6: Export CSV (ora={ora})...")
    demands_dict = None
    raw_smc_dict = {}
    if loads_layer is not None and loads_field:
        lf = loads_field
        load_fields = [f.name() for f in loads_layer.fields()]
        if lf in load_fields:
            matched_loads = match_user_nodes(nodo_xy, loads_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
            demands_dict = {}
            for nid, feat in matched_loads.items():
                attrs_l = dict(zip(load_fields, feat.attributes()))
                smc_str = str(attrs_l.get(lf, '') or '')
                if smc_str:
                    parsed = _parse_smc_ora(smc_str, ora, sep=flow_sep)
                    demands_dict[nid] = parsed
                    raw_smc_dict[nid] = smc_str
            log(f"  Consumi agganciati: {len(demands_dict)} nodi")
        else:
            log(f"  ATTENZIONE: campo '{lf}' non trovato nel layer consumi")

    if raw_smc_dict:
        from qgis.core import QgsField
        from PyQt5.QtCore import QVariant
        nodes_lyr.dataProvider().addAttributes([QgsField('load_smc_h', QVariant.String)])
        nodes_lyr.updateFields()
        fld_idx = nodes_lyr.fields().indexOf('load_smc_h')
        nodes_lyr.startEditing()
        for feat in nodes_lyr.getFeatures():
            nid = feat['node_id']
            if nid is not None:
                try:
                    smc = raw_smc_dict.get(int(nid), '')
                    nodes_lyr.changeAttributeValue(feat.id(), fld_idx, smc)
                except (TypeError, ValueError):
                    pass
        nodes_lyr.commitChanges()
        log(f"  Campo 'load_smc_h' aggiunto ai nodi ({len(raw_smc_dict)} valori)")

    # Aggiungi campo 'gas_comp' al layer collassato leggendolo dal layer utente
    if loads_layer is not None:
        from qgis.core import QgsField
        from PyQt5.QtCore import QVariant
        user_fields = [f.name() for f in loads_layer.fields()]
        if 'gas_comp' in user_fields:
            matched_gc = match_user_nodes(nodo_xy, loads_layer, radius_m=radius_m, crs=pipe_layer.crs().authid())
            gc_dict = {}
            for nid, feat in matched_gc.items():
                attrs_gc = dict(zip(user_fields, feat.attributes()))
                val = str(attrs_gc.get('gas_comp', '') or '').strip()
                if val:
                    gc_dict[nid] = val
            if gc_dict:
                nodes_lyr.dataProvider().addAttributes([QgsField('gas_comp', QVariant.String)])
                nodes_lyr.updateFields()
                gc_idx = nodes_lyr.fields().indexOf('gas_comp')
                nodes_lyr.startEditing()
                for feat in nodes_lyr.getFeatures():
                    nid = feat['node_id']
                    if nid is not None:
                        try:
                            nodes_lyr.changeAttributeValue(feat.id(), gc_idx, gc_dict.get(int(nid), ''))
                        except (TypeError, ValueError):
                            pass
                nodes_lyr.commitChanges()
                log(f"  Campo 'gas_comp' propagato ({len(gc_dict)} nodi con composizione custom)")

    nodes_path, pipes_path, n_nodes, c_ref, c_junc, n_pipes = export_layers_to_csv(
        pipes_lyr, nodes_lyr, out_dir, ora=ora,
        pressure_ref_pa=pressure_ref_pa, temp_ref_k=temp_ref_k,
        gas_comp_ref=gas_comp_ref, roughness_m=roughness_m,
        placeholder_flow=placeholder_flow, demands_dict=demands_dict,
        flow_sep=flow_sep)
    log(f"  sf_nodes.csv:    {n_nodes} nodi ({c_ref} reference, {c_junc} junction)")
    log(f"  sf_pipelines.csv: {n_pipes} pipe")
    log(f"  Output: {out_dir}")

    if c_ref == 0:
        warnings.append(
            "Nessun nodo reference trovato nel layer nodi. "
            "La simulazione fallira' senza almeno un nodo a pressione fissa. "
            "Verifica il campo 'Flag reference' e il suo valore.")

    _dump_pending_compressors(
        matched, comp_field, comp_value,
        out_dir, log,
        p_out_field=comp_pout_field,
        use_pcm=comp_use_pcm)

    return pipes_lyr, nodes_lyr, nodes_path, pipes_path, warnings
