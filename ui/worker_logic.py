# -*- coding: utf-8 -*-
import ast
import time
import traceback
from pathlib import Path
import pandas as pd
import GasNetSim as gns

def run_simulation(params: dict, log_func):
    """
    Esegue la logica computazionale di GasNetSim isolata dalla UI.
    Ritorna una tupla (out_folder, converged):
      - out_folder: cartella di output ('Path') se i CSV sono stati prodotti,
        altrimenti None in caso di errore;
      - converged: True se la simulazione è realmente conversa, False se è
        stato estratto solo il miglior iterato (soluzione non convergente).
    """
    def log(msg, color=''):
        log_func(str(msg), color)

    converged = False
    result = None
    _t0 = time.time()          # cronometro totale della simulazione

    # In batch: azzera alla radice il flusso di log di GasNetSim verso lo
    # stdout. Ogni riga di log emessa dai 24 sottoprocessi viene letta e
    # mostrata dal thread UNICO della UI di QGIS; il diluvio di DEBUG per
    # iterazione bloccava i processi in attesa di I/O (il vero motivo per cui
    # "24 in parallelo" erano piu' lente di "24 in fila"). Tagliando la
    # propagazione dell'intero albero "GasNetSim" i sottoprocessi smettono di
    # aspettare e tornano a calcolare. I messaggi importanti passano comunque
    # via log_func (print "LOG::..."), non via logging.
    if params.get('is_batch'):
        import logging as _lg
        _gns_logger = _lg.getLogger("GasNetSim")
        _gns_logger.setLevel(_lg.WARNING)
        _gns_logger.propagate = False

    try:
        folder = Path(params['cartella'])
        log(f"{'='*50}", '')
        log(f"  GasNetSim — Avvio Simulazione", '')
        # Identificazione del codice: il numero di versione del plugin e quello
        # del motore sono indipendenti, quindi entrambi vanno registrati.
        try:
            from .version import build_stamp
            log(f"  {build_stamp()}", '')
        except Exception:
            pass
        log(f"  Cartella: {folder}", '')
        log(f"{'='*50}", '')

        # --- Patch sf_nodes.csv ---
        nodes_csv = str(folder / 'sf_nodes.csv')
        df = pd.read_csv(nodes_csv, sep=';', dtype=str)
        mask_ref = df['node_type'].fillna('').str.lower().str.strip() == 'reference'
        comp = {'methane': 1.0}
        if mask_ref.any():
            try:
                _raw = df.loc[mask_ref, 'gas_composition'].values[0]
                try:
                    import json as _json
                    comp = _json.loads(_raw)   # JSON con virgolette doppie
                except Exception:
                    comp = ast.literal_eval(_raw)  # Python con virgolette singole (legacy)
            except Exception:
                pass
            df.loc[mask_ref, 'temperature_k'] = str(params['temperature_k'])
            df.loc[mask_ref, 'gas_composition'] = str(comp)
            df.loc[mask_ref, 'flow_sm3_per_s'] = ''
            if params.get('pressure_pa') is not None:
                df.loc[mask_ref, 'pressure_pa'] = str(int(params['pressure_pa']))
                log(f"Pressione reference: {params['pressure_pa']/1e5:.1f} bar", '')

        jf = str(params['junction_flow'])
        df.loc[~mask_ref, 'flow_sm3_per_s'] = (
            df.loc[~mask_ref, 'flow_sm3_per_s'].fillna(jf).replace('', jf).replace('0', jf)
        )
        df['altitude_m'] = pd.to_numeric(df['altitude_m'], errors='coerce').fillna(0.0)
        for col, default in [('flow_type', 'volumetric'), ('flow_MW', '')]:
            if col not in df.columns:
                df[col] = default
        df.to_csv(nodes_csv, index=False, sep=';', na_rep='')
        log(f"CSV nodi validato. Miscela: {comp}", '')

        # --- Patch sf_pipelines.csv ---
        pipes_csv = str(folder / 'sf_pipelines.csv')
        dfp = pd.read_csv(pipes_csv, sep=';', dtype=str)
        if 'friction_method' not in dfp.columns:
            dfp['friction_method'] = 'chen'
        else:
            dfp['friction_method'] = (dfp['friction_method']
                .fillna('chen').replace('', 'chen').replace('hagen-poiseuille', 'chen'))
        dfp.to_csv(pipes_csv, index=False, sep=';', na_rep='')
        log("CSV condotte validato.", '')

        # --- Two-pass per compressori (se richiesto dalla UI) ---
        # Pressioni della baseline (rete SENZA compressore), usate per
        # warm-startare la simulazione aumentata: sono gia' vicine alla
        # soluzione finale su quasi tutti i 340 nodi (l'unica differenza vera
        # e' attorno al compressore), quindi Newton parte molto piu' vicino e
        # le iterazioni interne scendono da ~18 a ~6-8. E' un warm start
        # AUTOCONTENUTO: ogni ora usa la propria baseline, senza soluzioni
        # condivise ne' corse fra i processi paralleli.
        _baseline_pressures = None
        pending_json = folder / '_pending_compressors.json'
        compressors_csv = folder / 'sf_compressors.csv'
        if pending_json.exists() and not compressors_csv.exists():
            import json
            try:
                with open(pending_json, 'r', encoding='utf-8') as fh:
                    comp_specs = json.load(fh)
            except Exception as exc:
                log(f"[compressori] impossibile leggere {pending_json.name}: {exc}", 'orange')
                comp_specs = []
            if comp_specs:
                log(f"\n[compressori] {len(comp_specs)} nodi marcati. "
                    f"Eseguo simulazione baseline per classificare le direzioni...", 'orange')
                try:
                    base_net = gns.create_network_from_folder(folder, base_composition=comp)
                    try:
                        # La baseline serve SOLO a leggere i segni di flusso alle
                        # condotte del compressore (quali entrano, quali escono).
                        # Quei segni si stabiliscono nelle prime iterazioni, molto
                        # prima della convergenza fine: non serve risolverla a
                        # tol=0.001. Con una tolleranza lasca e poche iterazioni
                        # la classificazione e' identica ma la baseline scende da
                        # ~18 a ~6-8 passi, dimezzando l'overhead del compressore
                        # per ogni ora del batch.
                        #
                        # Se la rete converge prima, tanto meglio; se non
                        # converge entro il cap, l'except sotto usa comunque lo
                        # stato raggiunto (i segni sono gia' corretti).
                        # Le direzioni di flusso alle condotte del compressore
                        # (DN1200 con portate enormi, mai borderline) sono gia'
                        # corrette dopo 4-5 iterazioni. La baseline STANDARD
                        # invece STALLA verso l'iterazione 12-15 sui nodi
                        # terminali, e ogni iterazione in stallo costa 40
                        # dimezzamenti della line search (40 valutazioni). Si
                        # cappa quindi PRIMA della zona di stallo: bastano ~6
                        # iterazioni per una classificazione corretta, e si
                        # evita del tutto la coda costosa.
                        _tol_base = max(float(params['tol']), 1.0)
                        _maxit_base = 6
                        _ts_base = time.time()
                        base_res = base_net.simulation(
                            max_iter=_maxit_base,
                            tol=_tol_base,
                            underrelaxation_factor=float(params['urf']),
                        )
                        log(f"[compressori]    ⏱ baseline: {time.time() - _ts_base:.1f}s", '')
                    except RuntimeError:
                        base_res = base_net
                        log(f"[compressori]    ⏱ baseline (cap raggiunto): "
                            f"{time.time() - _ts_base:.1f}s", '')
                    tmp_results = folder / '_baseline_results_pipes.csv'
                    rows = []
                    for pid, pipe in base_res.pipelines.items():
                        fr = vars(pipe).get('flow_rate')
                        rows.append({
                            'pipe_id': pid,
                            'flow_sm3h': float(fr) * 3600.0 if fr is not None else 0.0,
                        })
                    pd.DataFrame(rows).to_csv(str(tmp_results), index=False, sep=';')
                    
                    tmp_nodes = folder / '_baseline_results_nodes.csv'
                    rows_nodes = []
                    _baseline_pressures = {}
                    for nid, node in base_res.nodes.items():
                        p = vars(node).get('pressure')
                        rows_nodes.append({
                            'node_id': nid,
                            'pressure_bar': float(p) / 100000.0 if p is not None else 0.0,
                        })
                        if p is not None:
                            _baseline_pressures[nid] = float(p)  # Pa
                    pd.DataFrame(rows_nodes).to_csv(str(tmp_nodes), index=False, sep=';')

                    from GasNetSim_4Qgis.gis_integration.network_builder import inject_compressors_into_csvs
                    rename_map, _ = inject_compressors_into_csvs(
                        nodes_csv, pipes_csv, comp_specs, 
                        results_pipes_csv=str(tmp_results), 
                        results_nodes_csv=str(tmp_nodes),
                        log=log)
                    log(f"[compressori] sf_compressors.csv creato ({len(rename_map)} nodi splittati).", 'green')
                    try:
                        tmp_results.unlink()
                        tmp_nodes.unlink()
                        pending_json.unlink()
                    except Exception:
                        pass
                except Exception:
                    log(f"[compressori] errore nel workflow due-pass:\n{traceback.format_exc()}", 'red')

        # --- Carica rete ---
        log("\nCaricamento rete...", '')
        network = gns.create_network_from_folder(folder, base_composition=comp)
        log(f"Rete: {len(network.nodes)} nodi, {len(network.pipelines)} condotte", '')

        # --- Seed warm start (soluzione conversa di una run precedente) ------
        # Il compressore lavora a regimi molto simili da un'ora all'altra: una
        # soluzione gia' conversa sulla STESSA rete (altra ora/scenario) e' un
        # punto di partenza quasi perfetto. Caricata come warm start, il solve
        # diretto converge in pochi giri — niente rampa, niente oscillazioni.
        # Il file e' un results_nodes.csv (colonne node_id;pressure_bar), per
        # default condiviso da tutta la campagna nella cartella "nonna" (radice
        # comune a tutte le ore); si puo' forzare un percorso con
        # params['seed_csv']. La scrittura avviene solo dopo una convergenza
        # (vedi piu' sotto), cosi il seed migliora di corsa in corsa.
        _seed_out_path = folder.parent.parent / '_warmstart_seed.csv'
        _seed_pressures = {}
        # SICUREZZA: nel batch NON si legge il seed automatico condiviso. Le 24
        # ore hanno regimi molto diversi (notte vs punta): un seed preso da
        # un'ora starved (es. serale con pressioni a 16 bar) avvelenerebbe le ore
        # facili, che partirebbero da pressioni assurde e non riuscirebbero a
        # risalire. Nel batch ogni ora usa il warm-start della propria baseline.
        # Un seed esplicito (params['seed_csv']) resta consentito (lo chiede
        # l'utente apposta).
        _seed_allowed = bool(params.get('seed_csv')) or not params.get('is_batch')
        try:
            _seed_path = Path(params['seed_csv']) if params.get('seed_csv') else _seed_out_path
            if _seed_allowed and _seed_path and _seed_path.exists():
                _df_seed = pd.read_csv(str(_seed_path), sep=';', dtype=str)
                for _, _r in _df_seed.iterrows():
                    try:
                        _nid = int(_r['node_id'])
                        _pb = float(_r['pressure_bar'])
                    except (TypeError, ValueError, KeyError):
                        continue
                    if _pb > 0:
                        _seed_pressures[_nid] = _pb * 1e5   # bar -> Pa
                if _seed_pressures:
                    log(f"Seed warm start: {len(_seed_pressures)} pressioni da "
                        f"'{_seed_path.name}' (soluzione conversa precedente).", 'green')
        except Exception:
            _seed_pressures = {}

        # --- Warm start dalla baseline -----------------------------------
        # Se abbiamo le pressioni della baseline (rete senza compressore), le
        # scriviamo sui nodi della rete aumentata come punto di partenza.
        # I nodi originali ereditano la loro pressione; il nodo di mandata del
        # compressore (nuovo, non presente in baseline) parte dalla pressione
        # del nodo di aspirazione da cui e' stato splittato — entrambi vicini
        # alla soluzione, cosi Newton non riparte da freddo.
        _use_warm_start = False
        if _baseline_pressures or _seed_pressures:
            _ref = set(getattr(network, 'reference_nodes', []) or [])
            # Pressione di ripiego per i nodi non presenti in baseline (es. la
            # mandata del compressore, nodo nuovo creato dallo split): la
            # pressione di riferimento della rete (~70 bar). Per la mandata e'
            # gia' il suo valore di soluzione.
            try:
                _p_fallback = float(params.get('pressure_pa') or 7.0e6)
            except Exception:
                _p_fallback = 7.0e6

            _set = 0
            _from_seed = 0
            for nid, node in network.nodes.items():
                if nid in _ref:
                    continue  # i reference hanno pressione imposta
                # Il seed (soluzione conversa completa, compreso il nodo di
                # mandata del compressore) ha priorita' sulla baseline: e' piu'
                # vicino al punto di lavoro finale.
                if nid in _seed_pressures:
                    node.pressure = _seed_pressures[nid]
                    _set += 1
                    _from_seed += 1
                elif _baseline_pressures and nid in _baseline_pressures:
                    node.pressure = _baseline_pressures[nid]
                    _set += 1

            # CRITICO: con warm_start=True l'inizializzazione delle pressioni
            # viene SALTATA, quindi ogni nodo DEVE gia' avere una pressione
            # valida. I nodi non toccati sopra (mandata compressore) avrebbero
            # pressione None -> GERG2008 crasha su None/1000. Si riempie ogni
            # pressione mancante con il ripiego.
            _filled = 0
            for nid, node in network.nodes.items():
                if getattr(node, 'pressure', None) is None:
                    node.pressure = _p_fallback
                    _filled += 1

            # Warm start solo se ora TUTTI i nodi hanno pressione valida.
            if _set > 0 and all(
                getattr(n, 'pressure', None) is not None
                for n in network.nodes.values()
            ):
                _use_warm_start = True
                if _from_seed:
                    _src = (f"{_from_seed} dal seed"
                            + (f" + {_set - _from_seed} dalla baseline"
                               if _set - _from_seed else ""))
                else:
                    _src = f"{_set} pressioni dalla baseline"
                log(f"Warm start: {_src}"
                    + (f" + {_filled} di ripiego" if _filled else "")
                    + " (Newton parte vicino alla soluzione).", 'green')

        _multi_comp = False
        try:
            _df_nc = pd.read_csv(str(folder / 'sf_nodes.csv'), sep=';', dtype=str)
            _mask_nonref = _df_nc['node_type'].fillna('').str.lower().str.strip() != 'reference'
            _nonref_comp = _df_nc.loc[_mask_nonref, 'gas_composition'].fillna('').str.strip()
            if (_nonref_comp != '').any():
                _multi_comp = True
        except Exception:
            pass
        if _multi_comp:
            log("Composizioni multiple rilevate → StaggeredStrategy (pressure+composition)", 'orange')

        tol = float(params['tol'])
        urf = float(params['urf'])
        if params.get('autocal'):
            n = len(network.nodes)
            if n < 100:
                tol, urf = 0.1, 1.5
            elif n < 500:
                tol, urf = 1.0, 2.0
            elif n < 2000:
                tol, urf = 5.0, 2.5
            else:
                tol, urf = 10.0, 3.0
            log(f"Auto-calibra ({n} nodi) → tol={tol}  urf={urf}", 'orange')

        _AUTOCAL_LADDER = [(0.1, 1.5), (1.0, 2.0), (5.0, 2.5), (10.0, 3.0)]

        def _run_sim(net, max_iter, tol, urf, warm_start=None):
            # warm_start=None → usa il default (_use_warm_start): la PRIMA
            # solve parte dalle pressioni della baseline; le solve successive
            # (affinamento, ladder) mantengono comunque le pressioni gia'
            # calcolate, quindi warm start resta vantaggioso.
            if warm_start is None:
                warm_start = _use_warm_start
            import logging
            nr_logger = logging.getLogger("GasNetSim.simulation.solvers.newton_raphson")
            old_level = nr_logger.level
            old_propagate = nr_logger.propagate
            fh = None

            # ── I/O: la causa principale della lentezza in parallelo ─────────
            # Il solver logga OGNI iterazione di Newton al livello DEBUG. In un
            # batch di 24 processi questo diluvio, propagato allo stdout (che il
            # thread unico della UI di QGIS deve leggere riga per riga) e scritto
            # su un file su OneDrive, BLOCCA i sottoprocessi in attesa di I/O:
            # non calcolano, aspettano di scrivere i log. Da qui "24 in parallelo
            # piu' lente di 24 in fila".
            #
            # In modalita' batch quindi:
            #   * si TAGLIA la propagazione allo stdout (propagate = False);
            #   * NON si scrive il convergence_log.txt su OneDrive.
            # Nei run singoli si mantiene tutto (utile per il debug interattivo).
            _is_batch = bool(params.get('is_batch'))
            # Il logging DEBUG per-iterazione del solver, scritto su file in
            # OneDrive e RI-scritto a ogni solve, e' un forte collo di bottiglia
            # I/O — trascurabile con 1 solve (rete senza compressore), pesante
            # col compressore che esegue molti solve (baseline + tentativo +
            # rampa a 8 passi + affinamento). Di default lo si TAGLIA (come in
            # batch): il solver non genera nemmeno le stringhe DEBUG. Il
            # convergence_log.txt dettagliato resta attivabile a richiesta con
            # params['debug_convergence'] = True per il debug interattivo.
            _want_conv_log = bool(params.get('debug_convergence')) and not _is_batch
            if not _want_conv_log:
                nr_logger.propagate = False
                nr_logger.setLevel(logging.WARNING)  # niente DEBUG/INFO
            else:
                out_folder = folder.parent / 'output'
                out_folder.mkdir(parents=True, exist_ok=True)
                fh = logging.FileHandler(
                    str(out_folder / "convergence_log.txt"), mode='w')
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(logging.Formatter('%(message)s'))
                nr_logger.addHandler(fh)
                nr_logger.setLevel(logging.DEBUG)

            _ts = time.time()
            try:
                # Assemblaggio sparso dello Jacobiano, attivabile con
                # GNS_SPARSE=1. Il solutore Newton converte comunque in CSC
                # prima di spsolve; questo evita di costruire prima la matrice
                # densa 340x340. Non cambia il risultato, solo il percorso.
                import os as _os_sp
                _sparse = _os_sp.environ.get('GNS_SPARSE', '0') not in ('0', '', 'false', 'False')
                if _multi_comp:
                    _res = net.simulation(
                        max_iter=max_iter,
                        tol=tol,
                        underrelaxation_factor=urf,
                        tracking_method='simple_mixing',
                        coupling_strategy='staggered',
                        coupling_max_iter=max_iter,
                        coupling_tol=tol * 1e-2,
                        warm_start=warm_start,
                        sparse_matrix=_sparse,
                    )
                else:
                    _res = net.simulation(
                        max_iter=max_iter,
                        tol=tol,
                        underrelaxation_factor=urf,
                        warm_start=warm_start,
                    )
                _its = getattr(_res, 'last_iterations', '?')
                log(f"   ⏱ solve: {time.time() - _ts:.1f}s "
                    f"(iter={_its}, max_iter={max_iter}, tol={tol:g}, urf={urf:g})", '')
                return _res
            except Exception:
                log(f"   ⏱ solve NON converso: {time.time() - _ts:.1f}s "
                    f"(max_iter={max_iter}, tol={tol:g}, urf={urf:g})", 'orange')
                raise
            finally:
                if fh is not None:
                    nr_logger.removeHandler(fh)
                    fh.close()
                nr_logger.setLevel(old_level)
                nr_logger.propagate = old_propagate

        log(f"\nParametri: max_iter={params['max_iter']}  tol={tol}  urf={urf}", '')
        try:
            result = _run_sim(network, int(params['max_iter']), tol, urf)
            converged = True
            iters = getattr(result, 'last_iterations', '?')
            log(f"\n✓ SIMULAZIONE CONVERSA in {iters} iterazioni!", 'green')
        except RuntimeError as exc:
            if 'not converged' not in str(exc).lower():
                raise
            if params.get('autocal'):
                log(f"\n⚠ Non converso con tol={tol}  urf={urf} — provo parametri più laschi...", 'orange')
                for fb_tol, fb_urf in _AUTOCAL_LADDER:
                    if fb_tol <= tol:
                        continue
                    log(f"   → tol={fb_tol}  urf={fb_urf}", 'orange')
                    try:
                        result = _run_sim(network, int(params['max_iter']), fb_tol, fb_urf)
                        converged = True
                        tol, urf = fb_tol, fb_urf
                        iters = getattr(result, 'last_iterations', '?')
                        log(f"\n✓ SIMULAZIONE CONVERSA (tol={fb_tol}  urf={fb_urf}) in {iters} iterazioni!", 'green')
                        break
                    except RuntimeError as exc2:
                        if 'not converged' in str(exc2).lower():
                            continue
                        raise
            # --- Rampa sul target dei compressori (continuazione) ---------
            # Una stazione che impone una pressione di mandata puo' chiedere
            # alla rete di monte molta piu' portata di quanta ne transiti
            # naturalmente, e in una rete magliata induce ricircolo negli
            # anelli. Attaccare direttamente il punto di lavoro finale e' un
            # salto grosso rispetto allo stato iniziale.
            #
            # Si parte allora dal compressore SPENTO — target pari alla
            # pressione che il nodo di aspirazione assume da solo, cioe' la
            # soluzione senza compressore, che converge — e si sale al target
            # nominale a piccoli passi, ognuno warm-started dal precedente.
            # Stessa tecnica dell'affinamento sulla tolleranza, applicata al
            # parametro di controllo.
            if not converged and getattr(network, 'compressors', None):
                comps = network.compressors
                target0 = {cid: getattr(c, 'p_out_target', None)
                           for cid, c in comps.items()}
                if any(target0.values()):
                    n_passi = 8
                    mode0 = {cid: getattr(c, 'control_mode', 'ratio')
                             for cid, c in comps.items()}
                    ratio0 = {cid: float(getattr(c, 'compression_ratio', 1.0))
                              for cid, c in comps.items()}

                    log(f"\nRampa ADATTIVA sui compressori "
                        f"(passo iniziale 1/{n_passi}, bisezione sui punti duri) "
                        f"— parto da rapporto 1.00 (compressore trasparente)...",
                        'orange')

                    # Si rampa il RAPPORTO, non la pressione di mandata.
                    #
                    # A rapporto 1.0 il compressore impone p_out = p_in: e'
                    # trasparente, e la rete coincide con il baseline senza
                    # compressore, che converge. E' un punto di partenza noto
                    # e indipendente dallo stato in cui ci troviamo — mentre
                    # partire dalla "pressione naturale di aspirazione"
                    # significa leggerla dallo stato sporco lasciato dai
                    # tentativi falliti, che e' proprio l'errore che faceva
                    # fallire il primo passo.
                    #
                    # Salito il rapporto fino al valore nominale, si chiude
                    # con un solve in controllo di pressione sul target vero.
                    ok_rampa = True
                    for cid, c in comps.items():
                        c.control_mode = 'ratio'

                    # Rampa ADATTIVA: invece di n_passi fissi che si arrendono
                    # al primo livello che non converge, il passo si DIMEZZA
                    # (bisezione) su quel livello e riprende dall'ultimo stato
                    # buono. Cosi' la continuazione striscia oltre i punti duri
                    # (es. rapporto ~1.02 ad alto boost del compressore) invece
                    # di fermarsi. Dopo un passo liscio il passo si ri-allarga.
                    def _snap_p():
                        return {nid: n.pressure for nid, n in network.nodes.items()}

                    def _restore_p(snap):
                        for _nid, _p in snap.items():
                            network.nodes[_nid].pressure = _p

                    fr = 0.0                       # frazione raggiunta (0=trasparente, 1=nominale)
                    step = 1.0 / n_passi           # passo iniziale
                    _MIN_STEP = step / 16.0        # passo minimo prima di arrendersi
                    good_snap = _snap_p()          # ultimo stato convergente
                    while fr < 1.0 - 1e-9:
                        trial = min(fr + step, 1.0)
                        for cid, c in comps.items():
                            r_nom = ratio0.get(cid, 1.0)
                            c.compression_ratio = 1.0 + (r_nom - 1.0) * trial
                        try:
                            result = _run_sim(network, int(params['max_iter']),
                                              tol, urf)
                            fr = trial
                            good_snap = _snap_p()
                            log(f"   → {fr*100:.0f}%  (rapporto "
                                f"{c.compression_ratio:.4f}) ✓", 'green')
                            # un passo andato liscio: ri-allarga (ma non oltre l'iniziale)
                            step = min(step * 1.5, 1.0 / n_passi)
                        except RuntimeError as exc3:
                            if 'not converged' not in str(exc3).lower():
                                raise
                            _restore_p(good_snap)   # torna all'ultimo stato buono
                            step *= 0.5             # biseziona
                            log(f"   → {trial*100:.0f}% ✗ — dimezzo il passo "
                                f"(ora {step*100:.2f}%)", 'orange')
                            if step < _MIN_STEP:
                                log("   → passo minimo raggiunto: rampa "
                                    "interrotta.", 'orange')
                                ok_rampa = False
                                break

                    # Passo finale: controllo di pressione sul target nominale,
                    # partendo dalla soluzione a rapporto nominale.
                    if ok_rampa:
                        for cid, c in comps.items():
                            c.control_mode = mode0.get(cid, 'ratio')
                            if target0.get(cid) is not None:
                                c.p_out_target = target0[cid]
                        try:
                            result = _run_sim(network, int(params['max_iter']),
                                              tol, urf)
                            log("   → controllo di pressione sul target "
                                "nominale ✓", 'green')
                        except RuntimeError as exc4:
                            if 'not converged' not in str(exc4).lower():
                                raise
                            log("   → controllo di pressione sul target "
                                "nominale ✗", 'orange')
                            ok_rampa = False

                    if ok_rampa:
                        converged = True
                        iters = getattr(result, 'last_iterations', '?')
                        log(f"\n✓ SIMULAZIONE CONVERSA con rampa compressori "
                            f"in {iters} iterazioni!", 'green')
                    else:
                        # Ripristina i parametri nominali: i risultati estratti
                        # devono riferirsi al compressore vero, non a uno
                        # depotenziato dalla rampa.
                        for cid, c in comps.items():
                            c.control_mode = mode0.get(cid, 'ratio')
                            c.compression_ratio = ratio0.get(cid, 1.0)
                            if target0.get(cid) is not None:
                                c.p_out_target = target0[cid]

            if not converged:
                log(f"\n⚠ {exc}", 'orange')
                log("Estraggo l'ultima soluzione calcolata...", 'orange')
                result = network

        if converged and params.get('refine'):
            log("\nAffinamento precisione in corso...", 'orange')
            best_tol = tol
            best_result = result
            _MIN_TOL = 1e-4

            # NOTA su _run_sim: DEVE passare di li', non chiamare
            # network.simulation() direttamente. Senza coupling_strategy il
            # default e' "direct", quindi l'affinamento risolverebbe un
            # problema DIVERSO da quello principale (composizione tracciata
            # dentro il loop di Newton invece che nel loop esterno staggered),
            # reintroducendo la discontinuita' che il congelamento delle
            # miscele elimina.
            #
            # STRATEGIA: bisezione invece del salto x10.
            # Il vecchio schema andava a fattori di 10 (0.1 -> 0.01 -> ...):
            # se 0.01 falliva ci si fermava a 0.1, buttando via tutto
            # l'intervallo intermedio, dove spesso c'e' un valore
            # raggiungibile. Ora, quando un tentativo fallisce, si prova a
            # META' strada (in scala log) fra l'ultimo valore riuscito e
            # quello fallito, e si continua a stringere la forchetta finche'
            # i due estremi non sono abbastanza vicini. Il risultato e' il
            # MIGLIOR tol effettivamente ottenibile, non l'ultimo multiplo di
            # 10 riuscito.
            import math as _math

            def _tenta(t):
                """True se la rete converge a tolleranza t (e aggiorna il best)."""
                nonlocal best_tol, best_result
                try:
                    best_result = _run_sim(network, int(params['max_iter']),
                                           t, urf)
                    best_tol = t
                    log(f"   tol={t:.4g} ✓", 'green')
                    return True
                except RuntimeError as exc2:
                    if 'not converged' in str(exc2).lower():
                        log(f"   tol={t:.4g} ✗", 'orange')
                        return False
                    raise

            # Fase 1: discesa a fattori di 10 finche' si riesce.
            tol_ok = tol            # ultimo valore CONVERGENTE
            tol_ko = None           # primo valore FALLITO (None = mai fallito)
            t = tol
            while t > _MIN_TOL:
                t = max(t / 10.0, _MIN_TOL)
                if _tenta(t):
                    tol_ok = t
                else:
                    tol_ko = t
                    break

            # Fase 2: bisezione fra l'ultimo riuscito e il primo fallito.
            # Ci si ferma quando i due estremi distano meno di un fattore ~1.3
            # (0.1 in scala log10): oltre non vale la pena, la differenza e'
            # fisicamente trascurabile.
            if tol_ko is not None:
                # Pochi passi: ogni tentativo fallito costa un solve intero
                # che ora si ferma per stallo, ma resta lavoro. 4 bisezioni
                # portano la forchetta da un fattore 10 a un fattore ~1.8,
                # piu' che sufficiente.
                for _ in range(4):
                    if _math.log10(tol_ok / tol_ko) < 0.15:
                        break
                    t = 10 ** ((_math.log10(tol_ok) + _math.log10(tol_ko)) / 2.0)
                    if _tenta(t):
                        tol_ok = t
                    else:
                        tol_ko = t

                # La rete potrebbe essere rimasta nello stato di un tentativo
                # fallito: si rifa' un solve all'ultimo tol riuscito per
                # riportarla su uno stato valido (network.simulation() muta la
                # rete in-place).
                # Consolida SEMPRE: la rete potrebbe essere rimasta nello stato
                # di un tentativo di bisezione fallito, quindi si rifà un solve
                # all'ultimo tol riuscito per riportarla su uno stato valido.
                if True:
                    log(f"   consolido la soluzione a tol={tol_ok:.4g}", 'green')
                    try:
                        _run_sim(network, int(params['max_iter']), tol_ok, urf)
                        best_tol = tol_ok
                    except RuntimeError:
                        log("   ⚠ consolidamento non riuscito: i risultati "
                            "potrebbero non essere convergenti", 'orange')

            result = best_result
            log(f"Affinamento: tol finale = {best_tol:.4g} Sm³/s  |  urf = {urf}", 'green')

        # --- Risultati ---
        if result is not None:
            pp = [vars(n).get('pressure') for n in result.nodes.values()]
            pp = [p / 1e5 for p in pp if p is not None]
            if pp:
                log(f"\nPressioni [bar]:  min={min(pp):.2f}  max={max(pp):.2f}  media={sum(pp)/len(pp):.2f}",
                    'green' if converged else 'orange')

            try:
                _node_throughput_csv = {}
                try:
                    for _pid, _pipe in result.pipelines.items():
                        _fr = vars(_pipe).get('flow_rate')
                        if _fr is None:
                            continue
                        _frh = float(_fr) * 3600.0
                        _a = getattr(_pipe, 'inlet_index', None)
                        _b = getattr(_pipe, 'outlet_index', None)
                        if _a is None or _b is None:
                            continue
                        if _frh > 0:
                            _node_throughput_csv[_b] = _node_throughput_csv.get(_b, 0.0) + _frh
                        elif _frh < 0:
                            _node_throughput_csv[_a] = _node_throughput_csv.get(_a, 0.0) + abs(_frh)
                except Exception:
                    pass
                rows_n = []
                for nid, node in result.nodes.items():
                    row = {'node_id': nid}
                    try:
                        p = node.pressure
                        row['pressure_bar'] = round(float(p) / 1e5, 6) if p is not None else ''
                    except Exception:
                        row['pressure_bar'] = ''
                    try:
                        t = node.temperature
                        row['temperature_k'] = round(float(t), 4) if t is not None else ''
                    except Exception:
                        row['temperature_k'] = ''
                    try:
                        gm = node.gas_mixture
                        if gm is not None:
                            def _safe(fn):
                                try: v = fn(); return v
                                except Exception: return None
                            sg  = _safe(lambda: gm.specific_gravity)
                            z   = _safe(lambda: gm.compressibility)
                            hhv = _safe(lambda: gm.HHV_J_per_sm3)
                            rho = _safe(lambda: gm.density)
                            mm  = _safe(lambda: gm.molar_mass)
                            std = _safe(lambda: gm.standard_density)
                            row['sp_gravity']        = round(float(sg),  6) if sg  is not None else ''
                            row['z_factor']          = round(float(z),   6) if z   is not None else ''
                            row['hhv_mj_sm3']        = round(float(hhv) / 1e6, 4) if hhv is not None else ''
                            row['density_kg_m3']     = round(float(rho), 4) if rho is not None else ''
                            row['molar_mass']        = round(float(mm),  4) if mm  is not None else ''
                            row['std_density_kg_sm3']= round(float(std), 6) if std is not None else ''
                            try:
                                if row['hhv_mj_sm3'] != '' and row['sp_gravity'] not in ('', 0):
                                    row['wobbe_mj_sm3'] = round(
                                        float(row['hhv_mj_sm3']) / float(row['sp_gravity']) ** 0.5, 4)
                                else:
                                    row['wobbe_mj_sm3'] = ''
                            except Exception:
                                row['wobbe_mj_sm3'] = ''
                            try:
                                comp_gm = gm.composition
                                if comp_gm is not None and not hasattr(comp_gm, 'items'):
                                    try:
                                        from GasNetSim.components.gas_mixture.GERG2008.gerg2008 import convert_gerg2008_to_dictionary
                                        comp_gm = convert_gerg2008_to_dictionary(comp_gm)
                                    except Exception:
                                        comp_gm = None
                                if comp_gm is not None and hasattr(comp_gm, 'items'):
                                    row['gas_comp'] = ';'.join(
                                        f"{k}={round(float(v), 5)}"
                                        for k, v in comp_gm.items() if float(v) > 0.0001
                                    )
                                    row['h2_pct'] = round(float(comp_gm.get('hydrogen', 0)) * 100.0, 5)
                                else:
                                    row['gas_comp'] = ''
                                    row['h2_pct'] = 0.0
                            except Exception:
                                row['gas_comp'] = ''
                                row['h2_pct'] = ''
                        else:
                            for c in ('sp_gravity','z_factor','hhv_mj_sm3','density_kg_m3',
                                      'molar_mass','std_density_kg_sm3','wobbe_mj_sm3',
                                      'gas_comp','h2_pct'):
                                row[c] = ''
                    except Exception:
                        for c in ('sp_gravity','z_factor','hhv_mj_sm3','density_kg_m3',
                                  'molar_mass','std_density_kg_sm3','wobbe_mj_sm3',
                                  'gas_comp','h2_pct'):
                            row[c] = ''
                    try:
                        tp = _node_throughput_csv.get(int(nid))
                        row['throughput_sm3h'] = round(tp, 2) if tp is not None else ''
                    except Exception:
                        row['throughput_sm3h'] = ''
                    rows_n.append(row)
                # --- Cartella di output organizzata: <root>/h<NN>_<ESITO> -----
                # Stessa struttura per singola, batch e campagna. <root> e' la
                # cartella "madre" (il run_XXX per singola/batch, o il giorno
                # per la campagna). L'esito (OK/NONCONV) e' nel NOME.
                _esito = 'OK' if converged else 'NONCONV'
                _root = folder.parent
                _ora = params.get('ora')
                try:
                    _ora_i = int(_ora) if _ora is not None else None
                except (TypeError, ValueError):
                    _ora_i = None
                if _ora_i is not None:
                    out_folder = _root / f"h{_ora_i:02d}_{_esito}"
                    _other = _root / f"h{_ora_i:02d}_{'NONCONV' if converged else 'OK'}"
                else:
                    out_folder = _root / f"run_{_esito}"
                    _other = _root / f"run_{'NONCONV' if converged else 'OK'}"
                # Rimuovi la cartella dell'esito OPPOSTO per la stessa ora (una
                # run precedente convergeva e ora no, o viceversa): niente doppioni.
                try:
                    import shutil
                    if _other.exists():
                        shutil.rmtree(str(_other), ignore_errors=True)
                except Exception:
                    pass
                out_folder.mkdir(parents=True, exist_ok=True)
                if rows_n:
                    pd.DataFrame(rows_n).to_csv(
                        str(out_folder / 'results_nodes.csv'), index=False, sep=';')

                    # Salva questa soluzione come seed condiviso per le prossime
                    # ore/scenari. Solo se conversa e SOLO fuori dal batch: in
                    # parallelo 24 processi scriverebbero lo stesso file in corsa.
                    # Flusso previsto: un'ora "di riferimento" singola crea il
                    # seed, poi il batch lo riusa (piu' veloce, niente rampa).
                    if converged and not params.get('is_batch', False):
                        try:
                            _seed_rows = [
                                r for r in rows_n
                                if r.get('pressure_bar') not in ('', None)
                            ]
                            # SALVAGUARDIA: non salvare un seed da una soluzione
                            # STARVED (qualche nodo a pressione bassa). Un seed
                            # con pressioni a 16 bar, riusato su ore facili, le
                            # avvelena. Si scrive solo se la soluzione e' "sana"
                            # (minimo sopra ~25 bar).
                            _pmin = min((float(r['pressure_bar']) for r in _seed_rows),
                                        default=0.0)
                            if _seed_rows and _pmin < 25.0:
                                log(f"Seed NON salvato: soluzione starved "
                                    f"(min {_pmin:.1f} bar < 25). Eviterebbe di "
                                    f"avvelenare le ore facili.", 'orange')
                                _seed_rows = []
                            if _seed_rows:
                                pd.DataFrame(
                                    [{'node_id': r['node_id'],
                                      'pressure_bar': r['pressure_bar']}
                                     for r in _seed_rows]
                                ).to_csv(str(_seed_out_path), index=False, sep=';')
                                log(f"Seed warm start aggiornato "
                                    f"({len(_seed_rows)} pressioni) → "
                                    f"'{_seed_out_path.name}'.", '')
                        except Exception:
                            pass

                rows_p = []
                for pid, pipe in result.pipelines.items():
                    row = {'pipe_id': pid}
                    try:
                        fr = vars(pipe).get('flow_rate')
                        if fr is not None:
                            row['flow_sm3h']     = round(float(fr) * 3600.0, 4)
                            row['flow_abs_sm3h'] = round(abs(float(fr)) * 3600.0, 4)
                        else:
                            row['flow_sm3h'] = ''
                            row['flow_abs_sm3h'] = ''
                    except Exception:
                        row['flow_sm3h'] = ''
                        row['flow_abs_sm3h'] = ''
                    try:
                        vel = pipe.calc_flow_velocity()
                        row['velocity_m_s'] = round(abs(float(vel)), 6) if vel is not None else ''
                    except Exception:
                        row['velocity_m_s'] = ''
                    try:
                        p_avg = pipe.calc_average_pressure()
                        row['avg_pressure_bar'] = round(float(p_avg) / 1e5, 6) if p_avg is not None else ''
                    except Exception:
                        row['avg_pressure_bar'] = ''
                    try:
                        gm = pipe.gas_mixture
                        if gm is not None:
                            def _safe(fn):
                                try: v = fn(); return v
                                except Exception: return None
                            sg  = _safe(lambda: gm.specific_gravity)
                            z   = _safe(lambda: gm.compressibility)
                            rho = _safe(lambda: gm.density)
                            row['sp_gravity']    = round(float(sg),  6) if sg  is not None else ''
                            row['z_factor']      = round(float(z),   6) if z   is not None else ''
                            row['density_kg_m3'] = round(float(rho), 4) if rho is not None else ''
                        else:
                            row['sp_gravity'] = ''
                            row['z_factor']   = ''
                            row['density_kg_m3'] = ''
                    except Exception:
                        row['sp_gravity'] = ''
                        row['z_factor']   = ''
                        row['density_kg_m3'] = ''
                    rows_p.append(row)
                if rows_p:
                    pd.DataFrame(rows_p).to_csv(
                        str(out_folder / 'results_pipes.csv'), index=False, sep=';')

                # --- Potenza reale dei compressori --------------------------
                # A convergenza calcoliamo la potenza isentropica assorbita da
                # ogni stazione con i VALORI FINALI (non quelli congelati in
                # __init__, che sono stantii durante il solve aumentato):
                #   T inlet, cp/cv dalla miscela d'ingresso, rapporto = p_out/p_in
                #   e portata massica dalla portata volumetrica conversa.
                # Formula isentropica (compressor.calculate_power, MW):
                #   P = cp·T·(r^((n-1)/n) − 1)·ṁ / η / 1e6
                _comps = getattr(result, 'compressors', None) or {}
                if _comps:
                    _dt_h = float(params.get('time_step_s', 3600.0)) / 3600.0
                    rows_c = []
                    _tot_mw = 0.0
                    for cid, comp_obj in _comps.items():
                        row = {'compressor_index': cid}
                        try:
                            _in = comp_obj.inlet
                            _out = comp_obj.outlet
                            row['inlet_node'] = getattr(_in, 'index', '')
                            row['outlet_node'] = getattr(_out, 'index', '')
                            p_in = getattr(_in, 'pressure', None)
                            p_out = getattr(_out, 'pressure', None)
                            row['inlet_pressure_bar'] = (
                                round(float(p_in) / 1e5, 4) if p_in else '')
                            row['outlet_pressure_bar'] = (
                                round(float(p_out) / 1e5, 4) if p_out else '')
                            # Rapporto di compressione EFFETTIVO a convergenza.
                            ratio = (float(p_out) / float(p_in)
                                     if p_in and p_out and float(p_in) > 0 else 1.0)
                            row['compression_ratio'] = round(ratio, 5)

                            # Portata volumetrica conversa (Sm³/s) → massica.
                            q = comp_obj.flow_rate
                            if q is None:
                                q = comp_obj.calc_flow_rate()
                            q = float(q) if q is not None else 0.0
                            gm_c = getattr(comp_obj, 'gas_mixture', None) or getattr(
                                _in, 'gas_mixture', None)
                            std_rho = getattr(gm_c, 'standard_density', 0.8) or 0.8
                            row['flow_sm3h'] = round(q * 3600.0, 2)
                            row['mass_flow_kg_s'] = round(q * float(std_rho), 4)

                            # Aggiorna i parametri stantii con lo stato finale
                            # PRIMA di chiamare calculate_power().
                            comp_obj.T1 = getattr(_in, 'temperature', comp_obj.T1)
                            _cp = getattr(gm_c, 'cp', None)
                            _cv = getattr(gm_c, 'cv', None)
                            if _cp:
                                comp_obj.cp = float(_cp)
                            if _cv:
                                comp_obj.cv = float(_cv)
                            # Isentropico: n=cp/cv. Isotermo (n==1): invariato.
                            if abs(float(getattr(comp_obj, 'n', 1.3)) - 1.0) > 1e-9 \
                                    and comp_obj.cv:
                                comp_obj.n = comp_obj.cp / comp_obj.cv
                            comp_obj.compression_ratio = ratio
                            comp_obj.flow_rate = q
                            comp_obj.mass_flow_rate = q * float(std_rho)

                            raw_mw = float(comp_obj.calculate_power() or 0.0)
                            # Un compressore assorbe potenza ≥ 0; con ratio ≤ 1
                            # (stazione trasparente/riduttrice) il lavoro di
                            # compressione e' nullo.
                            power_mw = max(raw_mw, 0.0) if ratio > 1.0 else 0.0
                            row['power_MW'] = round(power_mw, 4)
                            row['energy_MWh'] = round(power_mw * _dt_h, 4)
                            _tot_mw += power_mw
                        except Exception:
                            for _k in ('power_MW', 'energy_MWh'):
                                row.setdefault(_k, '')
                        rows_c.append(row)
                    if rows_c:
                        pd.DataFrame(rows_c).to_csv(
                            str(out_folder / 'results_compressors.csv'),
                            index=False, sep=';')
                        log(f"Potenza compressori: {len(rows_c)} stazione/i, "
                            f"totale {_tot_mw:.3f} MW "
                            f"(energia {_tot_mw * _dt_h:.3f} MWh nell'ora simulata).",
                            'green')

                # --- Provenienza: chi ha prodotto questi risultati -----------
                # Versione del plugin, versione/commit del motore e parametri
                # effettivamente usati. Scritto in un file a parte per non
                # alterare l'intestazione dei CSV, che restano leggibili da
                # qualunque parser senza opzioni aggiuntive.
                try:
                    import json as _json
                    from .version import provenance
                    _iters = getattr(result, 'last_iterations', None)
                    _info = provenance(params=params, converged=converged,
                                       iterations=_iters,
                                       elapsed_s=time.time() - _t0)
                    with open(str(out_folder / 'run_info.json'), 'w',
                              encoding='utf-8') as _fh:
                        _json.dump(_info, _fh, indent=2, ensure_ascii=False)
                except Exception:
                    pass

                log(f"CSV risultati salvati in {out_folder}", 'green' if converged else 'orange')
            except Exception:
                log(f"Attenzione: impossibile salvare CSV risultati.\n{traceback.format_exc()}", 'orange')

        _elapsed = time.time() - _t0
        _mm, _ss = divmod(_elapsed, 60)
        _tempo_str = (f"{int(_mm)}m {_ss:.1f}s" if _mm else f"{_ss:.1f}s")
        _col = 'green' if converged else 'orange'
        if params.get('is_batch', False):
            log(f"⏱ Tempo totale simulazione: {_tempo_str}", _col)
        else:
            log(f"\n{'='*50}", '')
            log("  Elaborazione terminata.", '')
            log(f"  ⏱ Tempo totale: {_tempo_str}", _col)
            log(f"{'='*50}", '')

        return out_folder, converged

    except Exception:
        log(f"\n[ERRORE]\n{traceback.format_exc()}", 'red')
        return None, False
