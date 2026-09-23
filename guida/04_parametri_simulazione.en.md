# 6. Tab 1 — Physical and numerical parameters

All parameters in this section reside in the collapsible blocks of Tab 1. For
each, the symbol, unit, default value and admissible range are given.

## 6.1 ⚙ Compressors

Block to be enabled for networks equipped with compressor stations.

| Field | Description |
|-------|-------------|
| **Field and Value** | Node-layer field and value identifying compressor nodes. |
| **Pressure OUT** [bar] | Accepts either the name of a node-layer field holding the discharge pressure, or a constant numeric value (for example `70.0`). |

### 6.1.1 Formulation

The node marked as a compressor is split into a suction node and a discharge
node, connected by the station. The discharge pressure is imposed as an
additional constraint equation of system (2.3); the flow handled is determined
by the solution.

Since a pressure constraint may require the upstream network to deliver flows
far in excess of those of natural operation, the procedure comprises:

1. a **baseline** simulation without the compressor, with relaxed tolerance and
   a limited iteration count, used to establish flow directions and as the
   starting point (*warm start*) of the subsequent simulation;
2. in case of non-convergence, a **continuation on the control parameter**: the
   discharge target is raised in successive increments from the equilibrium
   value without compressor to the nominal set point, each step initialised
   from the previous one.

Both stages are automatic and traced in the log with the `[compressori]`
prefix.

### 6.1.2 Warning

In the absence of *Pressure OUT* the engine adopts a fallback compression ratio
of **1.1** (§13.3), insufficient under realistic load and typically a cause of
divergence with collapsing pressures. The plugin issues a non-blocking warning
before starting.

### 6.1.3 Quantities returned

At convergence the isentropic power absorbed by each station is computed:

    P = cp · T₁ · [ r^((n−1)/n) − 1 ] · ṁ / (η · 10⁶)        [MW]         (6.1)

with r = p_out/p_in the effective ratio, n = cp/cv, ṁ the mass flow rate and η
the efficiency. Values are written to `results_compressors.csv` (§10.4).

## 6.2 ⚙ Advanced options

| Parameter | Symbol | Unit | Default | Range | Description |
|-----------|--------|------|---------|-------|-------------|
| **Preserve intermediate nodes** | — | — | off | — | Disables the topological collapse: all intermediate nodes are retained and elevations are sampled from the DEM. Produces larger models but with the elevation profile resolved along the pipelines. Requires a DEM (§5.2). |
| **Hourly node flow** | — | — | not assigned | — | Demand profile field in Mode A (§5.6). |
| **Snap radius** | r_s | m | 50.0 | 0.1–10 000 | Maximum distance within which a node of the node layer is associated with a pipeline endpoint during the collapse. Insufficient values prevent recognition of reference nodes and attribution of demands; excessive values attribute demand to the wrong node. |
| **Flow separator** | — | — | `;` | `;` `,` `\|` `:` space tab | Separator of the hourly profile values. |
| **Reference pressure** | p_ref | bar (gauge) | 75.0 | 1–300 | Pressure imposed at reference nodes. For conversion to absolute pressure see (2.2). |
| **Temperature** | T | K | 288.15 | 250–400 | Gas temperature, uniform across the network (isothermal assumption, §1.3). |
| **Placeholder flow** | D_min | sm³/s | 1×10⁻⁴ | 0–10 | Demand attributed to transit nodes, i.e. those without their own demand. It has a regularising function: an identically zero balance row can render the Jacobian matrix singular. |
| **Pipe roughness** | ε | m | 1.2×10⁻⁵ | 1×10⁻⁷–0.1 | Absolute roughness of the internal wall, parameter of (2.9). Values by material in §13.2. |
| **Minimum export flow** | — | sm³/s | 1×10⁻⁶ | 1×10⁻¹⁰–1 | Value written to the input file for nodes without a known demand. It acts at writing time; *Placeholder flow* acts later, at validation, and prevails. |
| **Result layer decimals** | — | — | 4 | 0–10 | Decimal digits of the numeric fields of the layers produced. |
| **Show collapsed layer in the legend** | — | — | on | — | The `Condotte #N` / `Nodi #N` layers are made visible in the legend. If disabled they are still created, being required for Mode B. |
| **Create coloured original pipelines layer** | — | — | off | — | Produces an additional `R-P-orig-…` layer carrying the results on the original, non-collapsed geometry. |

## 6.3 ⚙ Solver parameters

Theoretical reference: §2.7.

| Parameter | Unit | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| **Max iterations** | — | 50 | 10–2000 | Maximum number of Newton-Raphson iterations. See the warning in 6.3.1. |
| **Tolerance** | Sm³/s | 0.001 | 1×10⁻⁴–10 | Threshold of criterion (2.14): maximum balance imbalance admitted per node. The adjacent box reports the equivalent in Sm³/h (multiplication by 3600): the default corresponds to 3.6 Sm³/h. |
| **URF** | — | 2.0 | 0.1–20 | Under-relaxation factor of (2.13). **It appears in the denominator**: larger values shorten the step and stabilise the iteration; values below 1 amplify the Newton step. The assigned value acts as the lower bound used by the adaptive scheme (§2.7). |
| **Auto-calibrate tol and URF** | — | off | — | Assigns tolerance and URF as a function of the number of nodes according to table §13.1.1 and, if convergence fails, walks the same ladder towards more relaxed combinations. Enabling it disables the two corresponding fields. |
| **Refine precision** | — | off | — | After the first convergence, repeats the solution with decreasing tolerances — first by factors of 10, then by bisection on a logarithmic scale — down to the limit of 1×10⁻⁴, retaining the result corresponding to the smallest tolerance actually achieved. Independent of *Auto-calibrate*: the latter defines the starting point, *Refine precision* the destination. The value to be quoted when documenting results is the **final** tolerance, reported in the log. |
| **Force Multiprocess** | — | on | — | Execution in independent Python processes, required for parallel simulations (§7.3, §7.4) to make effective use of multiple cores. |

### 6.3.1 Warning on the maximum iteration count

The number of iterations required depends on the distance between the initial
state and the solution, not on the size of the network. In the verification
runs performed on this plugin (§11.7) the default value of 50 iterations proved
**insufficient** on all three networks tested, including two networks of 4 and
10 nodes; the network of §11 converges in 92 iterations.

Setting **Max iterations = 200** as a starting point is therefore recommended.
The increase carries no penalty: the computation terminates as soon as
criterion (2.14) is met.

## 6.4 Gas Composition

| Field | Description |
|-------|-------------|
| **Base gas** | Composition preset: *SNAM — Mazara del Vallo (Algerian gas)* (default), *SNAM — Gela (Libyan gas)*, *Pure methane (100% CH₄)*, *Typical natural gas (94% CH₄)*, *Pure hydrogen (H₂)*, *Custom…*. Molar fractions are given in §13.3. |
| **H₂ addition** | **Molar** fraction of hydrogen added to the base gas, 0–99 %. The base composition is rescaled proportionally: denoting by x the hydrogen fraction and by y_k the base fractions, the resulting mixture has fractions y_k·(1−x) and hydrogen fraction x. |
| **Export composition** | Composition actually written to the input file. It is updated automatically from the two preceding fields and may be edited manually for compositions not covered by the presets; the preset then becomes *Custom*. |

### 6.4.1 Admissible components

`methane`, `ethane`, `propane`, `isobutane`, `butane`, `isopentane`,
`pentane`, `hexane`, `nitrogen`, `carbon dioxide`, `helium`, `hydrogen`.

The key for carbon dioxide is **`carbon dioxide`**, with a space. Molar
fractions must sum to unity.

### 6.4.2 Effect of composition on the hydraulic solution

Composition enters (2.4) through SG and Z and (2.9) through the Reynolds
number. At equal standard volumetric flow rate, a mixture of lower specific
gravity — for example one enriched with hydrogen — exhibits lower pressure loss
and higher velocity, but lower energy content per unit volume. Assessment of a
blending scenario therefore requires joint examination of pressure, velocity,
heating value and Wobbe index (§9.4).
