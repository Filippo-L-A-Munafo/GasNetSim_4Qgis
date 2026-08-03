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

This also installs the GasNetSim engine fork straight from GitHub (see the
comments in `requirements.txt` for the exact command if you need to run it
separately, or want to point it at a local clone for development instead).

### 3. Enable the plugin in QGIS

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
