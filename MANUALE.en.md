# Manual — GasNetSim 4Qgis

QGIS plugin for hydraulic simulation of gas networks (transmission and distribution) based on the **GasNetSim** library.

---

## 1. Overview

GasNetSim 4Qgis reads QGIS vector layers (pipelines and nodes), exports them to a CSV format compatible with GasNetSim, runs the hydraulic simulation in a separate thread, and creates two colour-coded result layers in the project (pressures, flow rates, velocities).

The workflow is split into two main phases:

1. **Prepare Network** — layer selection, field mapping, topological collapse (optional), CSV export.
2. **Simulate** — physical and solver parameter setup, simulation run, result visualization.

---

## 2. Interface

The main window is split into three horizontal panels:

| Panel | Content |
|----------|-----------|
| **Left** | Preparation panel (Tab 1 and Tab 2) |
| **Centre** | Dashboard — real-time simulation log |
| **Right** | Properties Inspector — attributes of a feature selected on the map |

---

## 3. Tab 1 — Prepare Network

### 3.1 Mode selection

| Option | Description |
|---------|-------------|
| **Network already collapsed** (checkbox unchecked = default) | **Mode A**: starts from a "raw" pipelines layer (original GIS geometry). The plugin performs topological collapse: connects pipelines to the nearest nodes within the snapping radius, assigns unique IDs, and generates the CSVs. |
| **Network already collapsed** (checkbox checked) | **Mode B**: uses already-processed layers (pipelines and nodes already carrying `pipe_id`, `node_a`, `node_b`, `node_id`). Collapse is skipped; only the fields are mapped and the CSVs are exported. |

---

### 3.2 Mode A — Layers to Collapse

Visible when the "Network already collapsed" checkbox is **unchecked**.

| Field | Description |
|-------|-------------|
| **Pipelines layer** | Line vector layer (LineString / MultiLineString) with the raw GIS pipelines. The plugin automatically generates `pipe_id`, `node_a`, `node_b`, `length_m`. |
| **Diameter field** | Field of the pipelines layer holding the internal diameter. Auto-selected by searching among: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. |
| **Diameter unit** | Unit of the diameter field: `inches (in)`, `metres (m)`, `centimetres (cm)`. The value is internally converted to metres. |
| **DEM (opt.)** | DEM raster layer (optional). If provided, it is used to extract the altitude of each node (`altitude_m`). If absent, altitude = 0. |
| **Nodes layer** | Point vector layer with the network nodes (optional in Mode A). If provided, reference nodes (fixed pressure) are recognized via the field/value specified below. |
| **Reference field** | Node layer field + value that identifies **reference nodes** (e.g. field `type` = `reference`, or field `matched` = `1`). Reference nodes are those at a known fixed pressure (solver boundary condition). At least one reference node is mandatory. |
| **Hourly node flow** | Node layer field containing the hourly consumption profile (24 Sm³/h values separated by the chosen character). If not selected, all nodes use the "Placeholder flow". |
| **Snapping radius** | Maximum distance (in metres, layer projection units) within which a node is associated with a pipeline endpoint during topological collapse. Default: 50 m. |
| **Add collapsed layers to project** | If checked, the node and pipeline layers resulting from the collapse are added to the QGIS project (useful for inspection). |

---

### 3.3 Mode B — Already Collapsed Layers

Visible when the "Network already collapsed" checkbox is **checked**.

| Field | Description |
|-------|-------------|
| **Pipelines layer** | Already-collapsed pipelines layer. Must contain at least the fields for pipe ID, node A, node B, length, diameter. |
| **Nodes layer** | Already-collapsed nodes layer. Must contain at least the fields for node ID, reference flag, flow. |

After choosing the layers, two field-mapping sections (Pipelines and Nodes) appear, described below.

---

### 3.4 Pipeline Field Mapping (Mode B)

| UI Field | CSV field produced | Description |
|----------|--------------------|-------------|
| **Pipe ID** | `pipe_id` | Unique pipeline identifier. Auto-selected among: `pipe_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Node A** | `node_a` | Inlet (upstream) node ID. Auto: `node_a`, `from_node`, `inlet`, `a`, `start_node`. |
| **Node B** | `node_b` | Outlet (downstream) node ID. Auto: `node_b`, `to_node`, `outlet`, `b`, `end_node`. |
| **Length** | `length_m` | Pipeline length in metres. Auto: `length_m`, `length`, `L`, `len`, `lunghezza`. |
| **Diameter** | `diameter_m` | Internal diameter in metres (automatic conversion if a different unit). Auto: `diameter_m`, `diam_m`, `D`, `Diametro_pollici`, etc. |
| **Diameter unit** | — | Unit of the diameter field: `m`, `in`, `cm`. |

---

### 3.5 Node Field Mapping (Mode B)

| UI Field | CSV field produced | Description |
|----------|--------------------|-------------|
| **Node ID** | `node_id` | Unique node identifier. Auto: `node_id`, `id`, `FID`, `OBJECTID`. |
| **Altitude** | `altitude_m` | Node elevation in metres above sea level. Auto: `altitude_m`, `z_m`, `elev`, `altitude`, `ALTITUDINE`. If absent, = 0. |
| **Reference flag** | `node_type` = `reference` | Field + value that identifies fixed-pressure nodes (boundary condition). Auto field: `matched`, `type`, `is_ref`, `reference`, `nodo_tipo`. Default value: `1`. **Mandatory**: at least one reference node must be present; the simulation is blocked if none is found. |
| **Hourly node flow** | `flow_sm3_per_s` | Field with the hourly consumption profile: 24 Sm³/h values separated by `;` (or the chosen separator), e.g.: `1.23;0.98;0.87;...`. The value for the hour chosen in "Hour of day" is used, converted to sm³/s. If not selected, the "Placeholder flow" is used. |

---

### 3.6 Export Parameters

| Field | Description |
|-------|-------------|
| **Hour of day** | Hour (0–23) used to extract consumption from the hourly profile. The panel shows a preview of the value extracted from the first node with an available profile. |
| **Flow separator** | Separator character for the 24 values in the hourly flow field. Default: `;`. Options: `,`, `\|`, `:`, space, tab. |
| **Output folder** | Folder where `sf_nodes.csv` and `sf_pipelines.csv` are saved. Used by the "Generate CSV" button. |

---

### 3.7 Action Buttons (Tab 1)

| Button | Action |
|----------|--------|
| **↺ Reload layers** | Refreshes the drop-down menus with the layers currently loaded in the QGIS project. |
| **> Generate CSV** | Exports `sf_nodes.csv` and `sf_pipelines.csv` to the selected output folder. Does not start the simulation. |
| **>> Generate CSV and Simulate** | Exports the CSVs to a temporary folder and immediately starts the simulation, without touching the permanent filesystem. Equivalent to doing everything in a single click. |

---

## 4. Tab 2 — Simulation Parameters

### 4.1 CSV Input Folder

Select the folder containing `sf_nodes.csv` and `sf_pipelines.csv`. Automatically populated after "Generate CSV" or "Generate CSV and Simulate".

---

### 4.2 Physical Parameters

These values are applied both to the CSV export and to the simulation.

| Field | Unit | Default | Description |
|-------|-------|---------|-------------|
| **Reference pressure** | bar | 70 | Pressure assigned to reference nodes in the CSV. Typical: 70 bar (Sicily RNT), 25 bar (RRT). |
| **Temperature** | K | 300 | Gas operating temperature (27 °C ≈ 300 K). |
| **Flow for nodes without demand** | sm³/s | 0.0001 | Minimum flow assigned to junction nodes that show zero demand in the CSV (e.g. transit nodes). Avoids empty rows in the solver. Increase to 0.001 if the network fails to converge because of isolated nodes. |

---

### 4.3 Solver Parameters

| Field | Default | Description |
|-------|---------|-------------|
| **Max iterations** | 50 | Maximum number of Newton-Raphson iterations. Increase to 100–200 for very large or ill-conditioned networks. |
| **Tolerance** | 1.0 | Convergence criterion (in solver units). Reduce to 0.1 for more accurate results; increase if the network fails to converge. |
| **URF** | 2.0 | Under-Relaxation Factor. Controls iteration stability. Reduce to 1.0–1.5 if the simulation oscillates; increase up to 3.0 to speed up convergence on well-conditioned networks. |
| **Auto-calibrate tol and URF** | off | If enabled, the plugin automatically tries to find the tol/URF combination that leads to convergence, starting from the set values and progressively reducing them. |

---

### 4.4 Network and Gas Composition

| Field | Default | Description |
|-------|---------|-------------|
| **Pipeline roughness** | 5×10⁻⁵ m | Absolute internal roughness. Steel: ~5×10⁻⁵ m; PE/HDPE: ~7×10⁻⁶ m; cast iron: ~2.6×10⁻⁴ m. Used in Chen's friction formula (Darcy-Weisbach). |
| **Export minimum flow** | 1×10⁻⁶ sm³/s | Placeholder value for nodes with no known demand in the CSV. Avoids a singular matrix. Different from "Flow for nodes without demand": this applies to the CSV, the other to the pre-simulation patch. |
| **Gas preset** | Natural gas (100% CH₄) | Shortcut to fill in the composition. Options: pure natural gas, typical (94% CH₄), H₂/CH₄ mix at 10/20/50%, pure hydrogen. Select "Custom..." to enter the composition manually. |
| **Composition (dict)** | `{'methane': 1.0}` | Gas composition as a Python dictionary of mole fractions. The sum must equal 1.0. Supported keys: `methane`, `ethane`, `propane`, `butane`, `nitrogen`, `carbon_dioxide`, `hydrogen`. |

---

### 4.5 Result Visualization

Controls which colour-coded layers are created in the QGIS project after the simulation.

#### Nodes

| Item | Description |
|----------|-------------|
| **Colour by** | Field used for the node layer's colour scale. Options: Pressure, Temperature, Spec. gravity, Z-factor, HHV, Wobbe, Density, Std density, Molar mass. |
| **Field checkboxes** | Selects which result fields to include in the node layer. Selected fields are queryable attributes with the identify tool. Active by default: Pressure, Temp., Sp.gravity, Z-factor, HHV, Wobbe. |

#### Pipelines

| Item | Description |
|----------|-------------|
| **Colour by** | Field used for the pipeline layer's colour scale. Options: Flow (Sm³/h), Velocity (m/s), Avg. pressure (bar), Spec. gravity, Z-factor, Density. |
| **Field checkboxes** | Result fields to include in the pipeline layer. Active by default: Flow, \|Flow\|, Velocity, Avg.pressure, Sp.gravity. |
| **Show flow direction arrows** | If active (default), adds a triangular marker at the midpoint of each pipeline, oriented in the direction of gas flow. The geometry is automatically reversed for pipelines with negative flow (reverse flow). |

---

## 5. Starting the Simulation

The simulation can be started in three equivalent ways:

1. **Tab 1 → ">> Generate CSV and Simulate"** — recommended: export + simulation in one click.
2. **Tab 1 → "> Generate CSV"** then **Tab 2 → "▶ Start Simulation"** — useful for inspecting the CSVs before simulating.
3. **"▶ Start Simulation" button** in the window footer — regenerates the CSVs from the current layers and starts immediately.

The simulation runs in a separate thread (does not block QGIS). The Dashboard log shows, in real time: CSV validation, network loading, iterations, pressure summary, result layer creation.

---

## 6. Result Fields — Nodes

Available in the `[Risultati] Nodi — <layer_name>` layer.

| Field | Unit | Description |
|-------|-------|-------------|
| `pressure_bar` | bar | Absolute pressure at the node computed by the simulation. |
| `temperature_k` | K | Operating temperature at the node (propagated from the reference). |
| `sp_gravity` | — | Specific gravity of the gas at the node (ratio of gas density to air density at standard conditions). |
| `z_factor` | — | Compressibility factor Z (real gas equation of state). |
| `hhv_mj_sm3` | MJ/sm³ | Higher Heating Value of the gas at the node. |
| `wobbe_mj_sm3` | MJ/sm³ | Wobbe index = HHV / √(sp_gravity). Gas interchangeability index. |
| `density_kg_m3` | kg/m³ | Gas density at operating conditions (node temperature and pressure). |
| `std_density_kg_sm3` | kg/sm³ | Standard gas density at 15 °C and 1.01325 bar. |
| `molar_mass` | g/mol | Average molar mass of the gas mixture at the node. |

---

## 7. Result Fields — Pipelines

Available in the `[Risultati] Condotte — <layer_name>` layer.

| Field | Unit | Description |
|-------|-------|-------------|
| `flow_sm3s` | Sm³/h | Signed volumetric flow rate. Positive = flow from node A to node B; negative = reverse flow (from B to A). Direction arrows reflect this sign. |
| `flow_abs_sm3s` | Sm³/h | Absolute-value volumetric flow rate. Also used to compute the line thickness (pipelines with higher flow appear thicker). |
| `velocity_m_s` | m/s | Average gas velocity in the pipeline, computed accounting for compressibility (real gas). Always a positive value (magnitude). |
| `avg_pressure_bar` | bar | Average pressure along the pipeline = average of the pressures at nodes A and B. |
| `sp_gravity` | — | Specific gravity of the gas mixture in the pipeline (average between the two ends). |
| `z_factor` | — | Average Z factor in the pipeline. |
| `density_kg_m3` | kg/m³ | Average gas density at the pipeline's operating conditions. |

---

## 8. Result Layers in QGIS

After each simulation, two in-memory layers are created (or re-created) in the QGIS project:

- **`[Risultati] Nodi — <name>`** — point layer with graduated colouring (5 quantile classes) on the chosen field. Colour scale: blue (minimum value) → red (maximum value).
- **`[Risultati] Condotte — <name>`** — line layer with graduated colouring and line thickness proportional to the absolute flow rate. If arrows are enabled, each pipeline has a triangular marker at its centre, oriented in the flow direction.

Previous layers are automatically removed before the new ones are added. They can be exported as GeoPackage or Shapefile via the standard right-click → "Export".

Results are also automatically saved as CSV in the `output/` subfolder of the input folder:
- `output/results_nodes.csv`
- `output/results_pipes.csv`

---

## Technical References

---

## Pipeline classification by category (Italian D.M. 17/04/2008)

Applies to **transmission** natural gas networks in Italy.

| Category | MOP (Max Operating Pressure) | Notes |
|--------|-------------------------------|------|
| **1st** | > 24 bar (2.4 MPa)            | National transmission network (RNT) |
| **2nd** | 12 bar < MOP ≤ 24 bar (1.2–2.4 MPa) | Regional transmission network (RRT) |
| **3rd** | 5 bar < MOP ≤ 12 bar (0.5–1.2 MPa)  | High-pressure user branches |
| **4th** | 1.5 bar < MOP ≤ 5 bar (0.15–0.5 MPa) | Local distribution networks |

> Current simulations concern **1st and 2nd category** networks (Sicily RNT/RRT,
> pressures 24–70 bar).

---

## Maximum pipeline velocity — erosion formula (API RP 14E)

$$V_e = \frac{C}{\sqrt{\rho_{gas}}}$$

- $V_e$ — erosional velocity [m/s]
- $\rho_{gas}$ — gas density at operating conditions [kg/m³]
- $C = 100$ — constant for continuous service, dry gas (SI)

### Estimates for methane (CH₄) at 15 °C

| Category | Typical MOP | Estimated ρ CH₄ | $V_e$ (erosion) | Practical limit |
|--------|-----------|----------------|-------------------|----------------|
| 1st     | 60–70 bar | ~44–55 kg/m³  | **~10–13 m/s**    | ~10–15 m/s     |
| 1st     | 24–40 bar | ~17–30 kg/m³  | **~13–18 m/s**    | ~15 m/s        |
| 2nd     | 12–24 bar | ~8–17 kg/m³   | **~18–24 m/s**    | ~15–20 m/s     |
| 3rd     | 5–12 bar  | ~3.5–8 kg/m³  | **~24–35 m/s**    | noise ~15 m/s |
| 4th     | 1.5–5 bar | ~1–3.5 kg/m³  | > 35 m/s          | noise ~10 m/s |

> **Note**: at higher pressures (1st category), the gas is denser and the erosional
> velocity is therefore **lower**, not higher. The practical limit for Sicily's RNT
> transmission pipelines (60–70 bar) is around **10–14 m/s**.

> **To be verified**: the exact reference values from D.M. 17/04/2008 and from
> SNAM/Terna standards should be added here once available.

---

## Gas compositions supported by GasNetSim

Components recognized by the solver (Python dict keys):

| Key              | Component         |
|---------------------|--------------------|
| `methane`           | Methane (CH₄)       |
| `ethane`            | Ethane (C₂H₆)       |
| `propane`           | Propane (C₃H₈)     |
| `butane`            | Butane (C₄H₁₀)     |
| `nitrogen`          | Nitrogen (N₂)         |
| `carbon_dioxide`    | Carbon dioxide (CO₂) |
| `hydrogen`          | Hydrogen (H₂)      |

### Presets available in the plugin

```python
# Pure natural gas
{'methane': 1.0}

# Typical natural gas (Italian network)
{'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}

# 10% hydrogen mix
{'methane': 0.90, 'hydrogen': 0.10}

# 20% hydrogen mix
{'methane': 0.80, 'hydrogen': 0.20}

# 50% hydrogen mix
{'methane': 0.50, 'hydrogen': 0.50}

# Pure hydrogen
{'hydrogen': 1.0}
```

---

## Solver parameters — reference values

| Parameter         | Plugin default | Notes |
|-------------------|---------------|------|
| Max iterations    | 50            | Increase to 100–200 for complex networks |
| Tolerance        | 1.0           | [bar or solver units] |
| URF               | 2.0           | Under-relaxation factor |
| Ref. pressure    | 70 bar        | Typical for Sicily RNT |
| Ref. temperature  | 300 K (27 °C) | |
| Pipeline roughness | 5×10⁻⁵ m      | Steel. PE/HDPE: 7×10⁻⁶ m; cast iron: 2.6×10⁻⁴ m |

---

## Supported diameter units

| Code | Conversion |
|--------|------------|
| `m`    | × 1         |
| `in`   | × 0.0254    |
| `cm`   | × 0.01      |

---

## Tested reference networks

| Network             | Nodes | Pipelines | Pressure | Result |
|------------------|------|----------|-----------|-----------|
| RRT Trapani      | 7    | 6        | 70 bar    | Converged in 4 iter, 7.7 s |
| RNT Sicilia      | —    | —        | 24–25 bar | Converged OK (pressures 24.08–25.33 bar) |
