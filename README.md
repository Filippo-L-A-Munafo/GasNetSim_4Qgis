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
::    close to the drive root - e.g. C:\gasnetsim. Windows has a 260-char
::    path limit, and some files in this repo have long nested paths, so
::    cloning deep inside OneDrive or another long path can fail with
::    "Filename too long".
git clone --branch improvement/modular-simulation-architecture https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv.git C:\gasnetsim

:: 2. Then, from the OSGeo4W Shell / QGIS Python environment:
pip install --no-deps -e C:\gasnetsim
```

On macOS/Linux, `git` is normally already on `PATH`, so
`pip install "git+https://github.com/Filippo-L-A-Munafo/GasNetSim_4Qgis-venv.git@improvement/modular-simulation-architecture"`
works directly with the QGIS Python from step 2.

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
