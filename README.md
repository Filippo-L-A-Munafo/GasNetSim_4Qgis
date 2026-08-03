# GasNetSim_4Qgis

A QGIS plugin to run steady-state hydraulic simulations of gas networks
(pipelines, nodes, compressors) directly from QGIS vector layers, using the
[GasNetSim](https://jugit.fz-juelich.de/iek-10/public/simulation/gasnetsim)
simulation engine.

The plugin reads pipeline/node vector layers from your QGIS project, exports
them to the CSV format GasNetSim expects, runs the hydraulic simulation in a
background thread, and writes the results (pressures, flow rates, velocities)
back into new colour-coded QGIS layers.

For a detailed guide to the interface (currently in Italian), see
[MANUALE.md](MANUALE.md).

## Requirements

- QGIS >= 3.10 (tested on 3.36 / 3.40)
- Python 3.10+ (the interpreter bundled with QGIS)
- The Python packages listed in [requirements.txt](requirements.txt)
- The [GasNetSim engine fork](https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv)
  used by this plugin (adds compressor support and solver fixes on top of
  upstream GasNetSim) — see installation below

## Installation

### 1. Install the plugin

Download or clone this repository, then copy (or symlink) the
`GasNetSim_4Qgis` folder into your QGIS profile's `plugins` directory:

- **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
- **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

### 2. Install the Python dependencies

Open a terminal that uses QGIS's own Python environment:

- **Windows**: open the "OSGeo4W Shell" from the Start menu (matching the
  QGIS version you use), then run:
  ```
  pip install -r requirements.txt
  ```
- **macOS**: use the Python bundled inside QGIS.app, e.g.:
  ```
  /Applications/QGIS.app/Contents/MacOS/bin/pip3 install -r requirements.txt
  ```
- **Linux**: use the `pip` associated with the Python QGIS was built against
  (often the system `pip3`, or the one from your QGIS package/conda env).

### 3. Install the GasNetSim engine

This plugin needs the [GasNetSim engine fork](https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv)
(adds compressor support and solver fixes on top of upstream GasNetSim).

> **Windows note**: the OSGeo4W Shell resets its `PATH` on startup, so `git`
> is normally **not** reachable from it even if Git for Windows is installed
> system-wide — `pip install git+https://...` will fail there with
> `Cannot find command 'git'`. Clone the repo from a regular terminal first,
> then install it from the local path:

```
:: 1. In a regular terminal (not the OSGeo4W Shell), clone to a SHORT path
::    under your user folder - e.g. C:\Users\<you>\GasNetSim_4Qgis-engine.
::    Do NOT use bare C:\ (untidy) or Program Files (you won't have write
::    access there without admin rights) - and do NOT nest it inside the
::    QGIS plugin folder or a deep OneDrive path either, see the path
::    length note below.
git clone --branch improvement/modular-simulation-architecture https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv.git C:\Users\<you>\GasNetSim_4Qgis-engine

:: 2. Then, from the OSGeo4W Shell / QGIS Python environment:
pip install --no-deps -e C:\Users\<you>\GasNetSim_4Qgis-engine
```

On macOS/Linux, `git` is normally already on `PATH`, so
`pip install "git+https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv.git@improvement/modular-simulation-architecture"`
works directly with the QGIS Python from step 2.

> **Why the path has to be short**: Windows caps full paths at 260
> characters. The source files in this repo are short enough on their own
> (88 characters at most), but `numba` (used for JIT-compiled gas mixture
> functions) writes its own cache files at import time with much longer
> generated names — e.g. `lucas.LucasViscosityCalculator._calculate_
> polarity_correction-28.py312.nbi.tmp.<hash>`, ~168 characters by itself.
> Verified: cloning straight into the QGIS plugin's own install folder
> (`...\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\GasNetSim_4Qgis\`,
> already 89 characters before adding anything — a fixed QGIS convention,
> not something you can shorten) blows past the limit and crashes the
> plugin at import time with a `numba` `FileNotFoundError`. A short path
> under your user folder (~30-40 characters) leaves enough headroom.

> **Version note**: upstream GasNetSim requires `geopandas>=1.0.1` and
> `openpyxl>=3.1.5`; some QGIS versions bundle slightly older ones (e.g. QGIS
> 3.40.2 ships geopandas 1.0.0 / openpyxl 3.1.2). `pip` will print an
> incompatibility warning; the plugin has been verified to work regardless,
> but upgrade those two packages if you run into geopandas/openpyxl errors.

### 4. Enable the plugin in QGIS

Restart QGIS, then go to **Plugins -> Manage and Install Plugins ->
Installed**, and check **GasNetSim_4Qgis**.

## License

This plugin is released under the [MIT License](LICENSE).

It depends at runtime on [GasNetSim](https://jugit.fz-juelich.de/iek-10/public/simulation/gasnetsim),
developed by ICE-1: Energy Systems Engineering, Forschungszentrum Julich
GmbH, released under MPL-2.0. All credit for the underlying simulation
engine belongs to its original authors — see the
[fork's README](https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv)
for the full acknowledgment and citation.

## Issues

Please report bugs or feature requests via the
[GitHub issue tracker](https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis/issues).
