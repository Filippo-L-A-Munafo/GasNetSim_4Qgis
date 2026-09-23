# 9. Nodal quantities

## 9.1 List of quantities

Contained in the `R-N-<name> #N` layer and in the `results_nodes.csv` file,
subject to the selections made in §8.2.

| Field | Symbol | Unit | Definition |
|-------|--------|------|------------|
| `pressure_bar` | p | bar (absolute) | Nodal pressure, the primary unknown of system (2.3). For its relation to the assigned value see (2.2). |
| `temperature_k` | T | K | Gas temperature at the node; uniform and equal to the assigned value (isothermal assumption). |
| `sp_gravity` | SG | — | Specific gravity relative to air at standard conditions, eq. (2.10). |
| `z_factor` | Z | — | Compressibility factor from the GERG-2008 equation of state (§2.5). |
| `hhv_mj_sm3` | HHV | MJ/sm³ | Higher heating value referred to standard conditions (2.1). |
| `wobbe_mj_sm3` | W | MJ/sm³ | Wobbe index, eq. (2.11). |
| `density_kg_m3` | ρ | kg/m³ | Density at the local operating conditions (p, T). |
| `std_density_kg_sm3` | ρ_b | kg/sm³ | Density at standard conditions; depends on composition alone. Conversion factor between standard volumetric flow and mass flow. |
| `molar_mass` | M | g/mol | Average molar mass of the mixture. |
| `h2_pct` | x_H₂ | % | Molar fraction of hydrogen at the node. |
| `gas_comp` | — | text | Local molar composition, in the form `methane=0.86909;ethane=0.08661;…`, limited to components with fraction above 1×10⁻⁴. |
| `throughput_sm3h` | — | Sm³/h | Total flow entering the node from the connected pipelines. It does not coincide with the nodal demand: it represents transit. |
| `volumetric_flow_sm3s` | D | sm³/s | Signed nodal demand (§5.6). Present in the QGIS layer only. |
| `energy_flow_mw` | — | MW | Nodal demand expressed as thermal power. Present in the QGIS layer only. |
| `node_type` | — | text | `reference` for fixed-pressure nodes. Present in the QGIS layer only. |

## 9.2 Composition-dependent quantities

With a single composition, `sp_gravity`, `hhv_mj_sm3`, `wobbe_mj_sm3`,
`molar_mass`, `std_density_kg_sm3` and `h2_pct` are uniform across the network,
whereas `z_factor` and `density_kg_m3` vary with the local pressure.

Where injections of differing composition are present (§5.7), all
composition-dependent quantities vary from node to node according to the mixing
field solved with the scheme of §2.6. The distribution of `h2_pct` then
describes the dilution of hydrogen away from the injection points and
constitutes the quantity of interest in partial blending studies.

## 9.3 Expected orders of magnitude

Values computed for the default gas (SNAM Mazara del Vallo) and for the same
mixture with 13.92 % molar hydrogen, at 76 bar and 288.15 K.

| Quantity | Mazara | Mazara + 13.92 % H₂ | Change |
|----------|--------|----------------------|--------|
| SG | 0.6323 | 0.5539 | −12.4 % |
| M | 18.32 g/mol | 16.05 g/mol | −12.4 % |
| Z | 0.818 | 0.879 | +7.5 % |
| ρ (76 bar) | ≈ 71 kg/m³ | ≈ 58 kg/m³ | −18 % |
| ρ_b | 0.8172 kg/sm³ | 0.7160 kg/sm³ | −12.4 % |
| HHV | 42.12 MJ/sm³ | 38.04 MJ/sm³ | −9.7 % |
| W | 52.98 MJ/sm³ | 51.11 MJ/sm³ | −3.5 % |

The values were obtained with the plugin's calculation engine under the stated
conditions (§11.7).

## 9.4 Reading criteria

**Minimum pressure.** Adequacy assessment is carried out on the ascending
ordering of `pressure_bar`, or on the thematic rendering of the same field: the
lowest-pressure nodes identify the critical sections of the network.

**Anomalous uniformity.** A nearly uniform pressure field, together with
`throughput_sm3h` values close to zero, indicates that demands have not been
acquired (§12.7), not that the network is oversized.

**Gas quality.** HHV and Wobbe index must be examined jointly: increasing the
hydrogen fraction reduces both, but to a different extent (§9.3), and the
governing regulatory constraint for Italian networks concerns specific gravity
(§13.4). The reduction of the Wobbe index, modest compared with that of the
heating value, is the quantity governing compatibility with end-user
appliances.

**Consistency with the boundary condition.** The pressure at the reference node
must equal the assigned value increased by 1.013 bar (2.2). A discrepancy
indicates that the reference node is not the expected one, or that more than
one exists.
