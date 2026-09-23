# 3. Interface architecture

## 3.1 Launching

The plugin is launched from the QGIS toolbar icon or from **Plugins →
GasNetSim_4Qgis**. A single resizable window opens, independent of the main
QGIS window: the map remains accessible during configuration and computation.

## 3.2 Window organisation

The window consists of a collapsible side bar and a three-tab container.

### 3.2.1 Side bar

Opened and closed with the **☰** button at the top left.

| Command | Function |
|---------|----------|
| ⚙ Settings | Selection of the interface language (Italian/English). The change takes effect the next time the plugin is opened. |
| Guide | Opens the present document. |
| ℹ About | Version, author, repository, licence. |

### 3.2.2 Tabs

| Tab | Designation | Reference |
|-----|-------------|-----------|
| Tab 0 | Check Pipelines | §4 |
| Tab 1 | Prepare & Simulate | §5, §6, §7 |
| Tab 2 | View Results | §8 |

## 3.3 Structure of Tab 1

Tab 1 is divided into two columns separated by a movable splitter.

**Left column** — scrollable configuration form, articulated in six blocks:

| Block | Title | Visibility | § |
|-------|-------|------------|---|
| 1 | Input Data | always visible | 5.2 |
| 2 | Collapse Options / Already Collapsed Layers and field mapping | depends on mode | 5.3–5.5 |
| 3 | ⚙ Compressors | on request | 6.1 |
| 4 | ⚙ Advanced options | on request | 6.2 |
| 5 | ⚙ Solver parameters | on request | 6.3 |
| 6 | Gas Composition | always visible | 6.4 |

Blocks marked ⚙ are collapsed on opening and expand when the corresponding
checkbox is ticked. This arrangement keeps visible the minimum set of
parameters required for a simulation, deferring the physical and numerical
parameters to those who need to modify them.

**Right column** — execution commands (§7.1) and the log window. The log
reports in real time the stages of the computation, the parameters actually
adopted and the outcome; it is the primary reference for diagnostics (§12). The
log's context menu allows it to be cleared.

## 3.4 Treatment of user data

The plugin does not modify the source layers: the topological layers, result
layers, CSV files and GeoPackages produced are all new items (§7.6).

The single exception is explicit and subject to confirmation: in Tab 0, the
endpoint snapping operation may be applied to the original layer instead of a
copy (§4.3); if the layer is file-based, the change is irreversible.

## 3.5 Coordinate reference system

Internal geometric processing (graph construction, node snapping, length
computation) is carried out in **EPSG:25833** (ETRS89 / UTM zone 33N). Layers
in other reference systems are reprojected.

Consequently the metric quantities exposed by the interface — *Snap radius*
(§6.2) and the snapping *Tolerance* (§4.3) — are expressed in metres. Using
layers in geographic coordinates (EPSG:4326) is discouraged: tolerances would
have to be expressed in degrees and computed lengths would be meaningless.

## 3.6 Elements not present

To avoid fruitless searching, the interface does **not** provide:

- a dedicated tab for simulation parameters: these reside in blocks 4–6 of
  Tab 1;
- a field for the folder of input CSV files: the folder is unique and is
  specified in block 1 of Tab 1 (§5.2);
- a selection of friction correlation or equation of state: these are fixed to
  Chen (1979) and GERG-2008 respectively (§2.4.2, §2.5).
