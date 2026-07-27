# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


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
            out_folder, converged = run_simulation(self._p, log)
            if out_folder is not None:
                self.finished.emit(bool(converged), out_folder)
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
    
    out_folder, converged = run_simulation(params, log_func)
    if out_folder:
        with open(r\"\"\"{str(folder / "success.json")}\"\"\", 'w', encoding='utf-8') as f:
            json.dump({{"success": True, "converged": bool(converged), "out_folder": str(out_folder)}}, f)
    else:
        with open(r\"\"\"{str(folder / "success.json")}\"\"\", 'w', encoding='utf-8') as f:
            json.dump({{"success": False, "converged": False}}, f)
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
                self.finished.emit(bool(data.get('converged', True)), data.get('out_folder'))
            else:
                self.finished.emit(False, None)
        else:
            self.log_line.emit("Errore: Subprocess non ha generato success.json", 'red')
            self.finished.emit(False, None)
