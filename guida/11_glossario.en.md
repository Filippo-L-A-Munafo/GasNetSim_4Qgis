# 14. Nomenclature and glossary

## 14.1 Symbols

| Symbol | Quantity | Unit |
|--------|----------|------|
| p | Absolute pressure | Pa, bar |
| p_ref | Pressure assigned to reference nodes (gauge) | bar |
| p_b, T_b | Standard reference pressure and temperature | 101 325 Pa; 288.15 K |
| p_avg | Average pipeline pressure, eq. (2.7) | Pa |
| T | Gas temperature | K |
| Q | Volumetric flow rate at standard conditions | sm³/s, Sm³/h |
| D_i | Nodal demand (positive for withdrawal) | sm³/s |
| ṁ | Mass flow rate | kg/s |
| v | Average gas velocity | m/s |
| D | Internal pipeline diameter | m |
| L | Pipeline length | m |
| ε | Absolute wall roughness | m |
| f | Friction factor, eq. (2.9) | — |
| Re | Reynolds number | — |
| η | Pipeline efficiency factor | — |
| h | Nodal geodetic elevation | m |
| H | Elevation correction term, eq. (2.8) | Pa² |
| Z | Compressibility factor | — |
| SG | Specific gravity relative to air, eq. (2.10) | — |
| ρ | Density at operating conditions | kg/m³ |
| ρ_b | Density at standard conditions | kg/sm³ |
| M | Molar mass of the mixture | g/mol |
| HHV | Higher heating value | MJ/sm³ |
| W | Wobbe index, eq. (2.11) | MJ/sm³ |
| x_H₂ | Molar fraction of hydrogen | — |
| r | Compression ratio, p_out/p_in | — |
| P | Power absorbed by the station, eq. (6.1) | MW |
| F(x) | Vector of nodal balance residuals | sm³/s |
| J | Jacobian matrix ∂F/∂x | — |
| tol | Tolerance of criterion (2.14) | Sm³/s |
| URF | Under-relaxation factor, eq. (2.13) | — |
| r_s | Snap radius | m |
| R | Universal gas constant | J/(mol·K) |

## 14.2 Glossary

**Best iterate** — The result returned when the simulation does not converge:
the last computed state, which does not satisfy the nodal balances.

**Blending** — Injection of hydrogen, or another gas, into a network designed
for natural gas.

**Chen correlation** — Explicit expression (2.9) for the friction factor,
applied to every pipeline.

**Compressor (compressor station)** — Component that raises pressure; in the
plugin it is configured by imposing the discharge pressure, and the results
include the power and energy absorbed.

**Disconnected component (island)** — Subgraph not connected to the main graph.
Without a reference node it renders the system indeterminate.

**Erosional velocity** — Velocity threshold beyond which high-velocity flow
causes erosion of the internal wall, eq. (13.1).

**GERG-2008** — Reference equation of state for natural gas, standardised in
ISO 20765-2.

**General flow equation** — Relation (2.4) between flow rate and the difference
of the squares of the pressures, inclusive of the elevation term and of
real-gas properties.

**Junction (transit) node** — Node without a demand of its own, where pipelines
connect. It receives the fallback demand (§6.2).

**Line search** — Progressive shortening of the Newton step until a reduction
of the residual is obtained.

**MOP** — Maximum operating pressure; basis of the classification by class
(§13.4.1).

**Nodal balance** — Mass conservation equation written at a node, eq. (2.3). It
constitutes the governing equation of the model.

**Non-converged case (NONCONV)** — Outcome in which criterion (2.14) is not
satisfied within the maximum iteration count. The result returned is the last
iterate and does not represent a physically admissible state.

**Placeholder flow** — Demand of negligible magnitude assigned to transit nodes
to avoid identically zero rows in the Jacobian matrix.

**Reference node** — Fixed-pressure node; boundary condition of the problem. It
is also the node at which the composition of the injected gas is assigned.

**Residual** — Value taken by F(x) for a given state: it measures the imbalance
of the nodal balances. The stopping criterion is formulated on its maximum.

**Snap** — Geometric unification of mutually close endpoints (§4.3).

**Snap radius** — Maximum distance within which a node of the node layer is
associated with a pipeline endpoint during the collapse (§6.2).

**Specific gravity** — Ratio between the molar mass of the mixture and that of
air, eq. (2.10). A quantity subject to regulatory constraint in Italian
networks (§13.4.2).

**Standard conditions** — Reference state for volume measurement: 288.15 K and
101 325 Pa, eq. (2.1).

**Steady state** — Operating condition at constant demand, to which the entire
formulation refers. Transients are not modelled.

**Direct / staggered scheme** — Coupling modes between the hydraulic problem
and composition tracking (§2.6). The staggered scheme is enabled where multiple
nodal compositions are present.

**Throughput (nodal)** — Total flow entering a node from the connected
pipelines; distinct from the nodal demand.

**Topological collapse** — Construction of the computational graph from the
vector geometry: explosion of polylines, identification of coincident
endpoints, generation of nodes and edges, computation of lengths (§5.3.1).

**Under-relaxation (URF)** — Divisor of the Newton increment, eq. (2.13).
Larger values damp the iteration.

**Warm start (seed)** — Initialisation of the computation with the pressures of
a previously converged solution, in order to reduce the iteration count (§7.6).

**Wobbe index** — Ratio of the higher heating value to the square root of
specific gravity, eq. (2.11). Index of interchangeability between fuel gases.

**Z factor** — See *Compressibility factor*: departure of real gas behaviour
from ideal, computed with GERG-2008.
