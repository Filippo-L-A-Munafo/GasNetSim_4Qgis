# 7. Execution and output files

## 7.1 Commands

The commands are located in the right-hand column of Tab 1.

| Command | Function |
|---------|----------|
| **↺ Reload layers** | Refreshes the project layer lists. |
| **> Generate CSV** | Performs model construction and mapping and writes the input files, without running the solver. In Mode B it is named *Generate CSV from Layer*. |
| **CSV export only** | Option: results are written to file but no layers are created in QGIS. It appreciably reduces execution time on large networks. |
| **▶ Start Simulation** | Generates the input files and runs the solver. |
| **⏹ Stop** | Interrupts the running computation. |
| **Campaign** | Sequential execution of the hourly batch over a series of days (§7.4). |

Without an output folder, a single simulation uses a temporary system folder;
*Generate CSV* and parallel execution require one explicitly.

## 7.2 Preliminary checks

### 7.2.1 Blocking conditions

- Mode A: pipeline layer not selected.
- Mode B: collapsed pipeline layer or collapsed node layer not selected.
- Both: absence of reference nodes at the end of model construction.

### 7.2.2 Warning conditions

The following conditions produce a warning with a request for confirmation;
continuation is permitted but in each case the results are compromised:

| Condition | Consequence |
|-----------|-------------|
| Node layer not selected | No boundary conditions: indeterminate system |
| *Reference flag* field not assigned | All nodes treated as reference |
| Empty reference flag value | All snapped nodes treated as reference |
| Compressors enabled without *Pressure OUT* | Fallback ratio 1.1 (§6.1.2) |

## 7.3 Execution

The computation runs in a separate thread and, with *Force Multiprocess*
enabled, in independent processes: the QGIS interface remains usable.

The log reports, in order:

1. working folder and reference pressure applied;
2. the outcome of input file validation, with the composition adopted. At this
   stage the plugin: writes temperature, pressure and composition on the
   reference nodes; replaces null or missing demands with the fallback flow;
   sets missing elevations to zero; imposes `friction_method = chen`;
3. any messages concerning compressors and multiple compositions;
4. the numerical parameters actually adopted;
5. the outcome: `✓ SIMULAZIONE CONVERSA in N iterazioni!` or a non-convergence
   notice followed by `Estraggo l'ultima soluzione calcolata…`;
6. the path to the results and the elapsed time.

At the end of a single simulation the result layers are created and the
interface switches automatically to Tab 2.

### 7.3.1 Hourly batch

The **Simulate 24 hours in parallel** option runs the 24 hourly scenarios
simultaneously. The degree of parallelism is set from the estimated number of
physical cores and is stated in the log. The final summary reports the number
of converged hours, the list of those that did not converge and the total time.

## 7.4 Multi-day campaign

The **Campaign** command repeats the hourly batch over a series of days. The
network (pipeline layer) is common; what varies are the node layers,
representing the demand profiles of individual days.

The procedure requires: the source of the days (files on disk in `.geojson`,
`.shp` or equivalent format, or layers already loaded in the project); the
output folder; and confirmation, with the total number of simulations
(days × 24).

During a campaign the *CSV export only* option is forced and dialogs are
suppressed: a day failing the checks of §7.2 is skipped and recorded in the
log, without interrupting the run. The final summary reports days completed,
days with 24 converged hours out of 24, total converged simulations and overall
time.

## 7.5 Outcome of the simulation

The solver returns a result even when convergence fails (§2.7.1). That result
is the last computed iterate: **it does not satisfy the nodal balances and does
not represent a physically admissible state**, despite having the appearance of
an ordinary solution.

The outcome is declared in three ways: the log message, the colour of the
closing line and — the decisive element — the **suffix of the results folder
name**, `_OK` or `_NONCONV`. Checking that suffix must precede any use of the
values produced.

## 7.6 Organisation of the output files

Each run generates a progressive subfolder; no file is ever overwritten.

```
<output folder>/
├─ _warmstart_seed.csv              pressures of the last converged solution
├─ run_001/
│  ├─ input/
│  │  ├─ sf_nodes.csv               generated input data (§5.8)
│  │  ├─ sf_pipelines.csv
│  │  └─ sf_compressors.csv         if compressor stations are present
│  ├─ output/
│  │  └─ convergence_log.txt        per-iteration diagnostics (§12.10)
│  └─ h00_OK/                       results for hour 0, converged
│     ├─ results_nodes.csv
│     ├─ results_pipes.csv
│     ├─ results_compressors.csv
│     ├─ run_info.json           provenance of the run (§7.8)
│     ├─ R-N-<name>_#1.gpkg
│     └─ R-P-<name>_#1.gpkg
└─ run_002/ …
```

Notes:

- result files use `;` as separator;
- re-running the same hour with a different outcome removes the folder
  corresponding to the previous outcome, preventing contradictory results from
  coexisting;
- result layers are persisted as **GeoPackage** in the same folder: the layer
  present in QGIS refers to that file and survives closing the project;
- the file `_warmstart_seed.csv`, written at the end of each converged single
  simulation, is reused as the initial state by subsequent runs (§2.7),
  reducing their iteration count.

## 7.7 Layers produced in the project

| Designation | Content |
|-------------|---------|
| `Condotte #N` / `Nodi #N` | Collapsed network, actually simulated (Mode A) |
| `R-N-<name> #N` | Nodal results (§9) |
| `R-P-<name> #N` | Pipeline results (§10) |
| `R-P-orig-<name> #N` | Results carried back onto the original geometry, if requested (§6.2) |

The progressive index `#N` increases at every run: **layers from previous
simulations are not removed**. The choice enables direct comparison between
scenarios (§8.4) but leads to a progressive accumulation of legend entries.

## 7.8 Traceability of results

The plugin version and the calculation engine version are **independent**: the
plugin uses a fork of GasNetSim containing modifications absent from any
released upstream version, so the engine version string alone is not sufficient
to identify the code executed.

Every run therefore records both identities in two places:

1. the **first line of the log**, in the form
   `GasNetSim_4Qgis 0.9.0 · motore GasNetSim 0.2.2 (improvement/modular-simulation-architecture @ 6079ec1)`;
2. the **`run_info.json`** file, written in the results folder alongside the
   CSVs, containing:

| Block | Content |
|-------|---------|
| `plugin` | plugin name and version |
| `engine` | declared engine version, branch and commit of the clone it is imported from, installation path |
| `run` | date and time, simulated hour, convergence outcome, iteration count, computation time |
| `parameters` | reference pressure, temperature, roughness, fallback flows, maximum iteration count, tolerance, URF, auto-calibration, refinement, gas composition |

The file is written as separate JSON, rather than as a CSV header, so that the
result files remain readable by any parser without additional options.

The content of `run_info.json` is the minimum information to be reported when
documenting a published result: it identifies the code and the parameters with
which it was produced, and allows the computation to be repeated even after the
files have been moved or reprocessed. Note that the engine commit is read from
the clone the package is imported from: an installation performed by cloning a
*branch* rather than a tag or a specific commit does not guarantee that others
will obtain the same engine.
