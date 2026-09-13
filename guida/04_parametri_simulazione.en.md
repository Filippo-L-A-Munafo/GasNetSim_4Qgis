# Tab 2 — Simulation Parameters

This tab sets the physical and numerical parameters used by the calculation
engine, and defines how the results will be displayed in QGIS at the end.

## 1. Input CSV Folder

Select the folder containing `sf_nodes.csv` and `sf_pipelines.csv`. If you
arrived here after pressing "Generate CSV" in Tab 1, this field is
automatically filled with the folder chosen there.

## 2. Physical Parameters

These values are applied both when exporting the CSVs and during the actual
simulation.

| Field | Unit | Default | Description |
|-------|------|---------|-------------|
| **Reference pressure** | bar | 70 | Absolute pressure assigned to reference nodes. This is the value that "anchors" the whole network (see "Basic physics concepts" → "Reference nodes"). Typical values: 70 bar for a national transmission network, 25 bar for a regional one. |
| **Temperature** | K | 300 | Gas operating temperature, in Kelvin (27 °C ≈ 300 K). It affects both gas compressibility (Z factor) and its density at operating conditions. |
| **Flow for demand-less nodes** | sm³/s | 0.0001 | Minimum flow assigned to "junction" nodes (transit points with no consumption of their own) that show up as exactly zero demand in the CSVs. This prevents completely empty rows in the solver's matrix, which could otherwise be singular (no solution). If the network fails to converge because of isolated nodes, try increasing this to 0.001. |

> **Why is an operating temperature needed?** A gas's volume and density
> depend on both pressure and temperature (gas law, see "Basic physics
> concepts"). For simplicity the plugin assumes a uniform temperature across
> the whole network — a reasonable approximation for buried pipes or ones not
> exposed to strong local thermal variations.

## 3. Solver Parameters

The network's system of equations is **non-linear** (the pressure drop in a
pipe depends on the flow rate through it, which in turn depends on the
pressures at its ends — see "Basic physics concepts"). Unlike a linear
system, a non-linear one cannot be solved with a single direct calculation:
it must be solved by **successive approximations**, using an iterative
method called **Newton-Raphson**.

The basic idea: start from an initial guess of the pressures, compute how
"wrong" the balance equations are with that guess (the error, or residual),
and correct the guess in a direction that reduces the error. Repeat until
the error drops below an acceptable threshold (convergence), or until a
maximum number of unsuccessful attempts is reached (in which case the
simulation stops without a result).

| Field | Default | Description |
|-------|---------|-------------|
| **Max iterations** | 50 | Maximum number of correction cycles the Newton-Raphson method can run before giving up. Increase to 100–200 for very large, heavily branched, or "ill-conditioned" networks (with very different pipe diameters directly connected to each other). |
| **Tolerance** | 1.0 | Threshold below which the residual error is considered acceptable and the calculation stops, declaring "convergence reached". Reduce to 0.1 for more precise results (but more iterations needed); increase if the network struggles to converge and lower precision is acceptable for your purpose. |
| **URF (Under-Relaxation Factor)** | 2.0 | Controls how "decisive" each correction is at every iteration. A value that is too high can make the solution "oscillate" around the correct point without ever settling (like pushing a swing too hard); a value too low makes convergence slower but more stable. Reduce to 1.0–1.5 if the simulation oscillates without converging; increase up to 3.0 to speed up convergence on well-conditioned networks that already converge easily. |
| **Auto-calibrate tol & URF** | Off | If enabled, the plugin automatically tries different combinations of tolerance and URF (starting from the set values and progressively reducing them) until it finds one that leads to convergence, saving you manual trial and error. |

## 4. Network and Gas Composition

| Field | Default | Description |
|-------|---------|-------------|
| **Pipe roughness** | 5×10⁻⁵ m | Absolute internal roughness of the pipe walls: how "rough" the inside is, on average, relative to the diameter. It feeds into the **Chen formula** (a variant of the Darcy-Weisbach equation, see "Basic physics concepts" → "Pressure drop") used to compute friction in every pipe. It depends on the material: steel ≈ 5×10⁻⁵ m; polyethylene (PE/HDPE) ≈ 7×10⁻⁶ m (much smoother); cast iron ≈ 2.6×10⁻⁴ m (rougher). |
| **Export minimum flow** | 1×10⁻⁶ sm³/s | Placeholder value written into the CSV for nodes with no known demand, to prevent the export file from containing empty rows (which would cause a singular matrix in the solver). It is conceptually similar to the "Flow for demand-less nodes" in the Physical Parameters, but acts at a different point in the pipeline: this one during CSV export, the other as a correction right before the simulation. |
| **Gas preset** | Natural gas (100% CH₄) | Shortcut to quickly fill in the composition. Available options: pure natural gas, "typical" natural gas (94% methane plus minor components), 10%, 20% or 50% hydrogen/methane blends, and pure hydrogen. Choose "Custom..." to enter a composition by hand. |
| **Composition (dict)** | `{'methane': 1.0}` | The gas composition, as a Python dictionary of mole fractions for each component. The fractions must always add up to 1.0. Supported components: `methane`, `ethane`, `propane`, `butane`, `nitrogen`, `carbon_dioxide`, `hydrogen`. |

### Why gas composition matters for the hydraulic calculation

Gas is not a "generic" fluid: its physical properties — density, viscosity,
compressibility (Z factor), heating value — depend directly on which
molecules make it up and in what proportion. Different mixtures (e.g. pure
methane versus a blend with 20% hydrogen) have different densities and
compressibilities, and therefore behave differently in the same pipe at the
same pressure: for the same standard volumetric flow rate, a lighter mixture
(richer in hydrogen) flows faster and generates less pressure drop than pure
methane, but it also carries less energy per unit volume (see the
`hhv_mj_sm3` field in the "Results — Nodes" section). This is why the plugin
lets you explicitly set the composition, and uses it in every single gas
property calculation, node by node and pipe by pipe.

## 5. Result Visualisation

This part does not affect the calculation at all: it only chooses **how**
the results are drawn in the new QGIS layers created at the end of the
simulation.

### Nodes

| Element | Description |
|---------|-------------|
| **Colour by** | The field used for the node layer's colour scale. Options: Pressure, Temperature, Specific gravity, Z-factor, HHV, Wobbe, Density, Standard density, Molar mass (see the "Results — Nodes" section for the physical meaning of each). |
| **Field checkboxes** | Chooses which result fields are included as attributes in the node layer (queryable with QGIS's "Identify" tool). Active by default: Pressure, Temperature, Specific gravity, Z-factor, HHV, Wobbe. |

### Pipes

| Element | Description |
|---------|-------------|
| **Colour by** | The field used for the pipe layer's colour scale. Options: Flow rate (Sm³/h), Velocity (m/s), Average pressure (bar), Specific gravity, Z-factor, Density. |
| **Field checkboxes** | Result fields to include as attributes in the pipe layer. Active by default: Flow rate, Absolute flow rate, Velocity, Average pressure, Specific gravity. |
| **Show flow direction arrows** | If enabled (default), draws a small triangular marker at the centre of every pipe, oriented in the actual direction the gas flows (the geometry is automatically flipped for pipes with negative flow, i.e. flow from B to A — see "Results — Pipes"). Very useful to understand flow direction at a glance in a complex network. |
