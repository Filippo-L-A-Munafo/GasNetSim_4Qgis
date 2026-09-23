# 11. Reproducible verification case

The case described in this section serves two purposes: to **validate the
installation**, by comparing the values obtained against those reported, and to
illustrate the complete workflow on a model of minimal size.

The expected values of §11.5 were obtained by running the calculation engine on
the input files produced by the procedure described here; the conditions of the
verification are declared in §11.7.

## 11.1 Description of the case

A transmission branch consisting of 4 nodes and 3 pipelines. Node 1 is the
injection point at known pressure; node 2 is a transit node from which two
deliveries depart, located at different elevations.

| Node | Elevation [m] | Type | Demand [Sm³/h] |
|------|----------------|------|-----------------|
| 1 | 10 | Reference (fixed pressure) | — |
| 2 | 50 | Transit | — |
| 3 | 120 | Delivery | 12 000 |
| 4 | 80 | Delivery | 5 000 |

| Pipeline | A → B | D [m] | L [km] |
|----------|-------|-------|--------|
| 1 | 1 → 2 | 0.508 (20″) | 12 |
| 2 | 2 → 3 | 0.3048 (12″) | 8 |
| 3 | 2 → 4 | 0.2032 (8″) | 5 |

Boundary conditions: p_ref = 75 bar gauge, T = 288.15 K, SNAM Mazara del Vallo
gas (§13.3).

The case is set up in **Mode B** (§5.3.2), which preserves node identifiers and
assigned elevations: in Mode A the identifiers would be regenerated and the
elevations, without a DEM and with two-dimensional geometry, would be zero
(§5.4), producing results different from those reported here.

## 11.2 Preparation of the data

Create two text files with the following content.

`verification_pipes.csv`

```
pipe_id,node_a,node_b,length_m,diameter_m,wkt
1,1,2,12000,0.508,"LINESTRING(400000 4200000, 412000 4200000)"
2,2,3,8000,0.3048,"LINESTRING(412000 4200000, 412000 4208000)"
3,2,4,5000,0.2032,"LINESTRING(412000 4200000, 417000 4200000)"
```

`verification_nodes.csv`

```
node_id,elevation_m,is_ref,demand,wkt
1,10,1,,"POINT(400000 4200000)"
2,50,0,,"POINT(412000 4200000)"
3,120,0,12000,"POINT(412000 4208000)"
4,80,0,5000,"POINT(417000 4200000)"
```

The `demand` field contains a single value, valid for every hour (§5.6); node
2, having no value, will be treated as a transit node.

## 11.3 Loading into QGIS

For each file: **Layer → Add Layer → Add Delimited Text Layer**; CSV format,
comma separator; *Geometry definition* = **Well known text (WKT)**, geometry
field `wkt`; coordinate reference system **EPSG:25833 — ETRS89 / UTM zone
33N**, consistent with the plugin's internal system (§3.5).

The result is a line layer of 3 features and a point layer of 4 features,
superimposed.

## 11.4 Configuration and execution

**Tab 0.** Select the pipeline layer and run *Analyze network*: the expected
outcome is `[OK] Nessun problema topologico rilevato`, with three edges in a
single connected component.

**Tab 1 — Input Data.**

| Field | Value |
|-------|-------|
| Pipeline layer | `verification_pipes` |
| Node layer | `verification_nodes` |
| DEM | `-- none --` |
| Output folder | an empty folder of choice |
| Hour of day | `0h` |
| Simulate 24 hours in parallel | not selected |

**Tab 1 — Mode.** Tick **Network already collapsed**, then indicate the same
two layers in the *Already Collapsed Layers* box and set the mappings:

| Pipeline Field Mapping | Value |
|-------------------------|-------|
| Pipe ID | `pipe_id` |
| Node A / B | `node_a` / `node_b` |
| Length | `length_m` |
| Diameter and unit | `diameter_m`, **metres (m)** |

| Node Field Mapping | Value |
|---------------------|-------|
| Node ID | `node_id` |
| Elevation | `elevation_m` |
| Reference flag | `is_ref` = `1` |
| Hourly node flow | `demand` |

**Tab 1 — ⚙ Solver parameters.** Change **Max iterations** from 50 to **200**.
With the default value the case does not converge (§6.3.1) and the plugin
returns a result flagged `NONCONV`.

All other parameters remain at their defaults: pressure 75.0 bar, temperature
288.15 K, roughness 1.2×10⁻⁵ m, tolerance 0.001 Sm³/s, URF 2.0, SNAM Mazara
del Vallo gas.

**Execution.** Command **▶ Start Simulation**. The log reports validation of
the input files, the parameters adopted and the outcome
`✓ SIMULAZIONE CONVERSA in 92 iterazioni!`. Results are written to
`<output folder>/run_001/h00_OK/` and the layers `R-N-verification #1` and
`R-P-verification #1` are added to the project.

## 11.5 Expected values

Absolute pressures; the value at the reference node equals 75 + 1.013 bar
according to (2.2).

| Node | h [m] | p [bar] | Z [–] | ρ [kg/m³] |
|------|-------|---------|-------|------------|
| 1 | 10 | 76.013 | 0.8176 | 71.08 |
| 2 | 50 | 75.726 | 0.8182 | 70.76 |
| 3 | 120 | 75.202 | 0.8193 | 70.17 |
| 4 | 80 | 75.482 | 0.8187 | 70.48 |

| Pipeline | Q [Sm³/h] | v [m/s] | mean p [bar] |
|----------|-----------|---------|---------------|
| 1 (1→2) | 17 000.3 | 0.311 | 75.870 |
| 2 (2→3) | 12 000.5 | 0.613 | 75.464 |
| 3 (2→4) | 5 003.2 | 0.574 | 75.604 |

Composition-dependent quantities, constant across the network: SG = 0.6323;
M = 18.32 g/mol; ρ_b = 0.8172 kg/sm³; HHV = 42.12 MJ/sm³; W = 52.98 MJ/sm³.

The iteration count may vary by a few units depending on the version of the
numerical libraries; pressures should agree to the third decimal place.

## 11.6 Checks on the result

**Mass balance.** At node 2, equation (2.3) requires:

    Q₁ − Q₂ − Q₃ = 17 000.3 − 12 000.5 − 5 003.2 = −3.4 Sm³/h

The residual imbalance is not zero and is of the order of the tolerance: with
tol = 0.001 Sm³/s, criterion (2.14) admits up to 3.6 Sm³/h of imbalance per
node. The result is therefore consistent with the stopping criterion adopted.
Reducing the tolerance — or enabling *Refine precision* (§6.3) — reduces the
imbalance proportionally.

**Effect of elevation.** Node 3 shows a lower pressure than node 4 (75.202
against 75.482 bar) although it is fed by a larger-diameter pipeline: the
difference is attributable to the geodetic term (2.8), node 3 being 40 m
higher. Setting all elevations to zero and repeating the run reverses the
pressure ranking: this is the most direct verification of the relevance of
§5.4.

**Boundary condition.** The pressure at node 1 must be 76.013 bar; a value of
75.000 would indicate a misinterpretation of (2.2).

## 11.7 Conditions of the verification

The values of §11.5 were obtained by running the GasNetSim 0.2.2 engine
(branch `improvement/modular-simulation-architecture`, commit `6079ec1`) on the `sf_nodes.csv` and
`sf_pipelines.csv` files generated according to the rules of §5.8 for the case
described, with the parameters of §11.4.

Limitations of the verification, stated for completeness:

1. execution took place outside the QGIS environment; the stages that depend on
   the QGIS libraries — graph construction (Mode A), node snapping, layer
   creation — were not executed. The Mode B adopted in this verification case
   reduces that dependency to the writing of the input files alone;
2. the functions compiled with `numba` were replaced by the equivalent pure
   Python implementations: numerical results are identical, computation times
   are not representative;
3. execution times are therefore not reported among the expected values.

The same tests were carried out on the two example networks distributed with
the plugin (`sample_data/toy_network_h2`, 10 nodes, and
`sample_data/Sicily_transmission_network`, 340 nodes): in both cases the
default value of 50 iterations proved insufficient (§6.3.1, §12.1).
