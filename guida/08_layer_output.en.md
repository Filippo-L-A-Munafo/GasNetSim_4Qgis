# Output layers and CSV files

## The layers created in QGIS

After every simulation, the plugin creates (or recreates, if they already
exist) two **in-memory** layers in the QGIS project:

- **`[Results] Nodes — <name>`** — point layer with a 5-class graduated
  colour scale (quantile method: each class holds roughly the same number of
  nodes) on the field chosen in "Colour by". Colour scale from blue (minimum
  value) to red (maximum value).
- **`[Results] Pipes — <name>`** — line layer with a similar graduated colour
  scale, and line thickness proportional to the absolute flow rate
  (`flow_abs_sm3s`). If direction arrows are enabled, every pipe also shows
  a triangular marker oriented in the actual flow direction.

### Why "in-memory"?

Result layers are **temporary layers** (QGIS memory layers): they exist as
long as the project stays open, but are not automatically saved to disk.
This is intentional, because it lets you re-run the simulation multiple
times (e.g. changing the hour of day or the gas parameters) without piling
up dozens of files on disk: at every new simulation, the previous result
layers are **automatically removed** and replaced with the new ones.

If you want to keep a set of results permanently, export it before running a
new simulation:

1. Right-click the layer in QGIS's "Layers" panel;
2. **Export → Save Features As...**;
3. Choose the desired format (GeoPackage `.gpkg` is generally the best
   choice to preserve both geometry and attributes; Shapefile `.shp` is a
   more universal alternative but with some limitations on field names).

## The automatically saved CSV files

Besides the QGIS layers, every simulation automatically saves two CSV files
in an `output/` subfolder inside the input folder chosen in Tab 2:

- `output/results_nodes.csv` — the same values as the node result layer, in
  plain tabular form.
- `output/results_pipes.csv` — the same values as the pipe result layer.

These files are useful for further analysis outside QGIS (spreadsheets,
Python scripts, comparison across multiple scenarios) without having to
manually re-export the layers every time.
