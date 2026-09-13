# Tab 1 — Prepare Network

This tab starts from the layers you **already** have in your QGIS project
(pipes and nodes, with their attributes) and uses them to **create from
scratch** two new CSV files — one for nodes, one for pipes — with the exact
column names the GasNetSim calculation engine requires. The two CSVs don't
exist beforehand: they are generated every time you press "Generate CSV",
by reading data out of your layers.

For this to work, though, **your layers must already contain, in some
field, all the necessary information**: an identifier for every pipe, which
nodes it connects, its diameter, an identifier for every node, which nodes
have a known pressure, and so on — even if those fields are named
differently in your layer than GasNetSim's own names. This tab's job is
exactly to tell the plugin **where to find** each piece of information in
your layers (the so-called "field mapping"): it does not invent or infer
data that isn't there. This is the most delicate phase of the workflow, for
two distinct reasons: if you map the wrong field, the simulation can fail or
produce wrong results without warning; and if a required piece of
information is missing entirely from the layer (not present in any field),
no mapping can "invent" it — you first need to add it as a new field in the
layer's attribute table.

## 1. Choosing the mode

At the top of the tab there is a "Network already collapsed" checkbox, which
picks between two working modes.

| Option | What happens |
|--------|--------------|
| **Unchecked (default) — Mode A** | You start from a "raw" pipe layer, with geometry exactly as imported from GIS (e.g. from OpenStreetMap, a survey, or a cadastre). The plugin performs a **topological collapse**: it figures out where pipes touch or come close to nodes, assigns a unique ID to every pipe and node, and generates the CSVs. |
| **Checked — Mode B** | You use ready-made layers, where nodes and pipes already carry correctly-linked identifiers (`pipe_id`, `node_a`, `node_b`, `node_id`). The collapse step is skipped: you only map field names and export. |

### What "topological collapse" is and why it's needed

Raw GIS data (e.g. downloaded from OpenStreetMap or hand-digitised) often
represents pipes as independent lines, without explicitly knowing which
lines touch each other or where the network's nodes actually are. For the
hydraulic calculation, however, we need to know precisely **which pipe
connects which two nodes** (see "Basic physics concepts" → "The network as a
graph"): without this information the mass-balance equations cannot be
written.

The "collapse" step analyses the geometries, decides which pipe endpoints
correspond to the same physical point (within a distance tolerance), and
builds the clean node/pipe graph the calculation then runs on.

## 2. Mode A — Layers to Collapse

Visible when the "Network already collapsed" checkbox is **unchecked**.

| Field | Description |
|-------|-------------|
| **Pipe layer** | Linear vector layer (LineString / MultiLineString) with the raw pipes. From this the plugin automatically generates `pipe_id`, `node_a`, `node_b` and `length_m` (computed from the geometry itself). |
| **Diameter field** | Field in the pipe layer holding the pipe's internal diameter. The plugin tries to auto-select it by looking for common names: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. |
| **Diameter unit** | Unit the diameter field is expressed in: inches (in), metres (m) or centimetres (cm). The plugin automatically converts everything to metres before use. |
| **DEM (optional)** | Digital Elevation Model raster layer (optional). If provided, the plugin automatically extracts each node's elevation by sampling the raster at that point (`altitude_m`). If not provided, every node's elevation is set to 0. |
| **Node layer** | Point vector layer with the network's nodes (optional in this mode). If provided, it lets the plugin recognise which points are "reference" nodes (see below). |
| **Reference field** | Field + value pair identifying reference nodes in the node layer (e.g. field `type` = `reference`, or field `matched` = `1`). See "Why the reference node is mandatory" below. |
| **Node hourly flow** | Field in the node layer holding the hourly consumption profile (24 values in Sm³/h, separated by a chosen character). If nothing is selected, all nodes use the fixed "Placeholder flow" value (see Tab 2). |
| **Snapping radius** | Maximum distance (in metres, in the layer's projection units) within which a node is linked to a pipe endpoint during collapse. Default: 50 m. |
| **Add collapsed layers to project** | If checked, after collapsing the plugin adds the two resulting layers (nodes and pipes) to the QGIS project, so you can visually inspect them before simulating. |

### Why the "snapping radius" matters

In real GIS data, two pipes that *should* meet at the same node often have
slightly misaligned endpoints (digitising errors, different projections,
rounding). The snapping radius tells the plugin "treat all endpoints within
this distance as connected": too small, and nodes that should be connected
stay separate (the network breaks into isolated pieces); too large, and
nodes that are genuinely distinct in reality get merged by mistake. 50
metres is a good starting point for transmission-scale data; for denser
distribution networks it may be worth reducing it.

## 3. Mode B — Already Collapsed Layers

Visible when the "Network already collapsed" checkbox is **checked**.

| Field | Description |
|-------|-------------|
| **Pipe layer** | Already-collapsed pipe layer: must already have fields for pipe ID, node A, node B, length and diameter (even under different names — you'll map them in the next section). |
| **Node layer** | Already-collapsed node layer: must already have fields for node ID, reference flag and flow. |

After picking both layers, two field-mapping sections appear (pipes and
nodes), described below.

## 4. Pipe Field Mapping (Mode B)

| Interface field | Produced CSV field | Description |
|-------------------|-----------------------|-------------|
| **Pipe ID** | `pipe_id` | Unique pipe identifier. Auto-detected among: `pipe_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Node A** | `node_a` | ID of the inlet node (upstream, i.e. where the gas conventionally starts from). Auto: `node_a`, `from_node`, `inlet`, `a`, `start_node`. |
| **Node B** | `node_b` | ID of the outlet node (downstream). Auto: `node_b`, `to_node`, `outlet`, `b`, `end_node`. |
| **Length** | `length_m` | Pipe length in metres. Auto: `length_m`, `length`, `L`, `len`, `lunghezza`. |
| **Diameter** | `diameter_m` | Internal diameter in metres (auto-converted if the unit differs). Auto: `diameter_m`, `diam_m`, `D`, `Diametro_pollici`, etc. |
| **Diameter unit** | — | Unit of the chosen diameter field: `m`, `in`, `cm`. |

> **Physics note**: the distinction between "Node A" and "Node B" does not
> mean the gas must flow in that direction — it's just a labelling
> convention. The calculation determines the actual flow direction on its
> own; if gas flows from B to A, the result will simply show a negative flow
> rate on that pipe (see the "Results — Pipes" section).

## 5. Node Field Mapping (Mode B)

| Interface field | Produced CSV field | Description |
|-------------------|-----------------------|-------------|
| **Node ID** | `node_id` | Unique node identifier. Auto: `node_id`, `id`, `FID`, `OBJECTID`. |
| **Elevation** | `altitude_m` | Node elevation in metres above sea level. Auto: `altitude_m`, `z_m`, `elev`, `altitude`, `ALTITUDINE`. If the field is missing, 0 is used. |
| **Reference flag** | `node_type` = `reference` | Field + value identifying nodes with a known, fixed pressure (see below). Auto field: `matched`, `type`, `is_ref`, `reference`, `nodo_tipo`. Default value: `1`. |
| **Node hourly flow** | `flow_sm3_per_s` | Field with the hourly consumption profile: 24 Sm³/h values separated by a character (e.g. `;`), like `1.23;0.98;0.87;...`. The value for the hour chosen in "Hour of day" (Export Parameters) is used, converted to sm³/s. If nothing is selected, the "Placeholder flow" is used. |

### Why the reference node is mandatory

As explained in "Basic physics concepts", the network's system of equations
needs at least one point with a **known absolute pressure** to have a unique
solution (exactly like an electrical circuit needs a ground node). This is
why **at least one reference node is mandatory**: if the plugin finds none in
the node layer, it blocks the simulation before it even starts, with an
error message in the Dashboard log. If your network has no explicit field
marking reference nodes, you can quickly create one in the node layer's
attribute table (e.g. an `is_ref` field set to 1 on the interconnection point
with the upstream network).

## 6. Export Parameters

| Field | Description |
|-------|-------------|
| **Hour of day** | Hour of the day (0 to 23) used to extract the consumption value from each node's hourly profile. The panel shows a preview of the value that would be extracted from the first node with an available profile, so you can quickly verify it is being read correctly. |
| **Flow separator** | Character separating the 24 values in the hourly profile field. Default: `;`. Other options: `,`, `\|`, `:`, space, tab. It must exactly match the format used in your data, otherwise the profile is not read correctly. |
| **Output folder** | Folder where `sf_nodes.csv` and `sf_pipelines.csv` will be saved when you press "Generate CSV". |

## 7. Action Buttons

| Button | Action |
|--------|--------|
| **↺ Reload layers** | Refreshes all dropdown menus with the current list of layers loaded in the QGIS project (useful if you just added or removed a layer). |
| **> Generate CSV** | Runs the collapse (in Mode A) and/or field mapping, then writes `sf_nodes.csv` and `sf_pipelines.csv` to the chosen output folder. Does not run the simulation: useful to check the CSVs before running the calculation. |
| **>> Generate CSV and Simulate** | Does everything in one step: generates the CSVs in a temporary folder (without touching the permanent filesystem) and immediately runs the simulation. This is the fastest way to go from QGIS layers to results. |

The "Running the simulation" section further ahead in this Guide summarises
all the (equivalent) ways to launch the calculation.
