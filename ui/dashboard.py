# -*- coding: utf-8 -*-
import ast
import traceback
from pathlib import Path

import pandas as pd
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton


# ---------------------------------------------------------------------------
# Worker — gira in QThread per non bloccare la UI di QGIS
# ---------------------------------------------------------------------------
class SimWorker(QObject):
    log_line = pyqtSignal(str, str)   # (testo, colore: '' | 'green' | 'red' | 'orange')
    finished = pyqtSignal(bool, object)  # (converged, network_results | None)

    def __init__(self, params: dict):
        super().__init__()
        self._p = params
        self._proc = None          # sottoprocesso in esecuzione (se use_subprocess)
        self._cancelled = False    # True se l'utente ha premuto Ferma

    def cancel(self):
        """Richiesta di interruzione dal thread della UI.

        Uccide il sottoprocesso se attivo. Il ciclo di lettura in
        _run_in_subprocess se ne accorge, esce, ed emette finished(False).
        Sicuro da chiamare piu' volte.
        """
        self._cancelled = True
        proc = self._proc
        if proc is not None and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    def run(self):
        import traceback
        try:
            use_sub = self._p.get('use_subprocess', False)
            if use_sub:
                self._run_in_subprocess()
            else:
                self._run_native()
        except Exception as e:
            self.log_line.emit(f"Errore fatale in SimWorker:\n{traceback.format_exc()}", 'red')
            self.finished.emit(False, None)
            
    def _run_native(self):
        from .worker_logic import run_simulation
        import traceback
        
        def log(msg, color=''):
            self.log_line.emit(str(msg), color)
            
        try:
            res = run_simulation(self._p, log)
            if res is not None:
                self.finished.emit(True, res)
            else:
                self.finished.emit(False, None)
        except Exception as e:
            log(f"Errore:\n{traceback.format_exc()}", 'red')
            self.finished.emit(False, None)
            
    def _run_in_subprocess(self):
        import sys, os, json, subprocess
        from pathlib import Path
        
        folder = Path(self._p['cartella'])
        params_file = folder / 'params.json'
        with open(params_file, 'w', encoding='utf-8') as f:
            json.dump(self._p, f)
            
        script_file = folder / 'run_worker.py'
        plugin_root = str(Path(__file__).parent.parent.parent).replace('\\', '/')
        
        script_code = f"""
import sys
import json
from pathlib import Path

sys.path.insert(0, r\"\"\"{plugin_root}\"\"\")

try:
    from GasNetSim_4Qgis.ui.worker_logic import run_simulation
except ImportError as e:
    print("LOG::red::ImportError: " + str(e))
    sys.exit(1)

def log_func(msg, color=''):
    print(f"LOG::{{color}}::{{msg}}")

try:
    with open(r\"\"\"{str(params_file)}\"\"\", 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    res = run_simulation(params, log_func)
    if res:
        with open(r\"\"\"{str(folder / "success.json")}\"\"\", 'w', encoding='utf-8') as f:
            json.dump({{"success": True, "out_folder": str(res)}}, f)
    else:
        with open(r\"\"\"{str(folder / "success.json")}\"\"\", 'w', encoding='utf-8') as f:
            json.dump({{"success": False}}, f)
except Exception as e:
    import traceback
    print("LOG::red::Exception: " + str(e) + "\\n" + traceback.format_exc())
    sys.exit(1)
"""
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_code)
            
        python_exe = os.path.join(sys.base_exec_prefix, 'python.exe')
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # ── Anti-oversubscription dei thread BLAS ────────────────────────────
        # numpy/scipy (spsolve, np.linalg.solve) aprono di default un thread di
        # algebra lineare PER CORE. Con N sottoprocessi in parallelo diventano
        # N × n_core thread in contesa sugli stessi core (es. 24 × 36 = 864),
        # che si accavallano e rallentano TUTTO. Forzando 1 thread per processo,
        # gli N processi usano N core in modo pulito. E' lo standard per il
        # calcolo numerico parallelo a processi.
        _env = dict(os.environ)
        for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                   'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
            _env[_v] = '1'

        proc = subprocess.Popen([python_exe, str(script_file)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                startupinfo=startupinfo,
                                env=_env)
        self._proc = proc  # esposto a cancel()

        # Se l'utente ha premuto Ferma prima ancora dell'avvio del ciclo.
        if self._cancelled:
            try:
                proc.kill()
            except Exception:
                pass

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            if line.startswith('LOG::'):
                parts = line.split('::', 2)
                if len(parts) == 3:
                    self.log_line.emit(parts[2], parts[1])
                else:
                    self.log_line.emit(line, '')
            else:
                self.log_line.emit(line, '')

        proc.wait()

        if self._cancelled:
            self.log_line.emit("⏹ Simulazione interrotta dall'utente.", 'orange')
            self.finished.emit(False, None)
            return

        success_file = folder / 'success.json'
        if success_file.exists():
            with open(success_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('success'):
                self.finished.emit(True, data.get('out_folder'))
            else:
                self.finished.emit(False, None)
        else:
            self.log_line.emit("Errore: Subprocess non ha generato success.json", 'red')
            self.finished.emit(False, None)



# ---------------------------------------------------------------------------
# Dashboard widget
# ---------------------------------------------------------------------------
class Dashboard(QWidget):
    simulation_done = pyqtSignal(bool, object)  # (converged, result)

    def __init__(self, iface, parent=None):
        super(Dashboard, self).__init__(parent)
        self.iface = iface
        self._thread = None
        self._worker = None
        self.last_result = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel("Log Simulazione")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background:#1e1e1e; color:#d4d4d4; font-family:Consolas,monospace; font-size:11px;")
        self.txt_log.setText("Motore GasNetSim pronto.\nSeleziona la cartella input e premi 'Avvia Simulazione'.\n")
        self.txt_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_log.customContextMenuRequested.connect(self._show_log_context_menu)
        layout.addWidget(self.txt_log)

        btn_row = QHBoxLayout()
        self.btn_snapshot = QPushButton("\U0001f4cc  Salva snapshot risultati")
        self.btn_snapshot.setToolTip(
            "Rinomina i layer [Risultati] correnti in [Run #N] per\n"
            "conservarli. La prossima simulazione crea nuovi [Risultati]\n"
            "senza sovrascrivere lo snapshot.")
        self.btn_snapshot.clicked.connect(self._snapshot_results)
        btn_row.addWidget(self.btn_snapshot)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _show_log_context_menu(self, pos):
        menu = self.txt_log.createStandardContextMenu()
        menu.addSeparator()
        act_clear = menu.addAction("\U0001f5d1  Svuota log")
        act_clear.triggered.connect(self.txt_log.clear)
        menu.exec_(self.txt_log.mapToGlobal(pos))

    def _append(self, text, color=''):
        cursor = self.txt_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = cursor.charFormat()
        if color == 'green':
            fmt.setForeground(QColor('#4ec94e'))
        elif color == 'red':
            fmt.setForeground(QColor('#f44747'))
        elif color == 'orange':
            fmt.setForeground(QColor('#ce9178'))
        else:
            fmt.setForeground(QColor('#d4d4d4'))
        cursor.setCharFormat(fmt)
        cursor.insertText(text + '\n')
        self.txt_log.setTextCursor(cursor)
        self.txt_log.ensureCursorVisible()

    def run_simulation(self, params: dict):
        """Chiamato da main_dialog quando l'utente preme Avvia Simulazione."""
        if not params.get('cartella'):
            self._append("⚠ Nessuna cartella selezionata.", 'orange')
            return
        csv_ok = (Path(params['cartella']) / 'sf_nodes.csv').exists() and \
                 (Path(params['cartella']) / 'sf_pipelines.csv').exists()
        if not csv_ok:
            self._append("⚠ sf_nodes.csv o sf_pipelines.csv non trovati nella cartella.", 'red')
            return

        self.txt_log.clear()
        self._append("Avvio simulazione in background...", '')

        self._worker = SimWorker(params)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log_line.connect(self._append)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _snapshot_results(self):
        """Rinomina i layer [Risultati] correnti in [Run #N] per conservarli."""
        try:
            from qgis.core import QgsProject
            proj = QgsProject.instance()
            result_layers = [lyr for lyr in proj.mapLayers().values()
                             if lyr.name().startswith('[Risultati]')]
            if not result_layers:
                self._append("Nessun layer [Risultati] attivo da salvare come snapshot.", 'orange')
                return
            existing_names = {lyr.name() for lyr in proj.mapLayers().values()}
            n = 1
            while any(f'[Run #{n}]' in nm for nm in existing_names):
                n += 1
            for lyr in result_layers:
                lyr.setName(lyr.name().replace('[Risultati]', f'[Run #{n}]', 1))
            self._append(f"Snapshot salvato: [Run #{n}]  ({len(result_layers)} layer).", 'green')
            if self.iface:
                self.iface.mapCanvas().refresh()
        except Exception as exc:
            self._append(f"Errore snapshot: {exc}", 'red')

    def _on_finished(self, converged: bool, result):
        self.last_result = result
        status = "CONVERGENZA OK" if converged else "Non conversa"
        self._append(f"\nStato finale: {status}", 'green' if converged else 'orange')
        self.simulation_done.emit(converged, result)
