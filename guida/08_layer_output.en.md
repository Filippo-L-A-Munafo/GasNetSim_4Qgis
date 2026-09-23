# 8. Tab 2 — Post-processing and rendering

This tab performs no computation: it governs the thematic rendering of results
and their export. The interface switches to it automatically at the end of a
single simulation.

## 8.1 View results on layer

Applies a new thematic rendering to existing layers, without repeating the
computation.

| Field | Description |
|-------|-------------|
| **Node layer** | Layer to be rendered. Result layers (`R-N-…`) are listed first; any vector layer of the project may be selected, including those of previous simulations. |
| **Colour nodes by** | Field governing the colour scale. The list contains only the fields present in the selected layer. |
| **Size nodes by** | Makes the symbol radius proportional to the absolute value of the chosen field. |
| **Pipeline layer** | Likewise for the line layer (`R-P-…`). |
| **Colour pipelines by** | Field governing the colour scale of the pipelines. |
| **Flow direction arrows** | Marker oriented according to the actual flow direction, i.e. the sign of `flow_sm3h` (§10.2) and not the orientation of the geometry. |
| **▶ Apply colouring** | Applies the settings. The adjacent command refreshes the layer list. |

### 8.1.1 Rendering criteria

Classification is **graduated with quantile classes**, with approximately
uniform population per class. For pipelines the line width is made proportional
to the absolute flow rate, so as to highlight the transport hierarchy. The
`h2_pct` field uses a dedicated scale, progressing from white/yellow (zero
fraction) to red.

The use of quantile classes implies that the colour scale is **relative to the
individual layer**: two simulations rendered with the same settings are not
comparable by colour, only by value. For quantitative comparison, use the
numerical values or a manual classification with fixed intervals, available
through the standard QGIS tools.

## 8.2 Settings for the next simulation

Defines the fields that the next simulation will produce and their initial
rendering. It has no effect on results already computed.

**Nodes.** Initial colouring field (default *Pressure*), sizing field (default
none) and selection of the fields to be produced. Enabled by default: pressure,
volumetric consumption, energy consumption, temperature, specific gravity, Z
factor, heating value, Wobbe index, H₂ fraction, composition and throughput;
disabled: density, standard density, molar mass and node type.

**Pipelines.** Initial colouring field (default *Flow*) and field selection:
enabled by default signed flow, absolute flow, velocity, average pressure and
specific gravity; disabled Z factor and density.

**Show flow direction arrows**: disabled by default.

A field not selected here is not written to the layer and is therefore
unavailable for the rendering of §8.1 until a new simulation is run. The nodal
fields `volumetric_flow_sm3s`, `energy_flow_mw` and `node_type` are present in
the QGIS layers only and not in the CSV files (§9.1).

## 8.3 Export data

| Field | Description |
|-------|-------------|
| **Layer** | Layer to be exported. |
| **Decimals** | Decimal digits of numeric values. |
| **Export CSV** | Selection of the destination path. |

The function complements the `results_nodes.csv` and `results_pipes.csv` files
produced automatically (§7.6): it allows export of a subset, of a different
precision, or of a layer whose symbology has been modified manually.

## 8.4 Comparison between scenarios

The accumulation of result layers (§7.7) allows direct comparison:

1. run the reference scenario;
2. modify the parameter under analysis — for example the hydrogen fraction
   (§6.4) — and run again;
3. select alternately layers `#1` and `#2` on the same field, in block §8.1.

For quantitative comparison use the `results_nodes.csv` files of the respective
`run_NNN/h<hour>_OK/` folders, bearing in mind the observation of §8.1.1 on the
non-comparability of quantile colour scales.
