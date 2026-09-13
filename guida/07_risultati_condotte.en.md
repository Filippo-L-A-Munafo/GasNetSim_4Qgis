# Results — Pipes

At the end of the simulation, the plugin creates a line layer called
`[Results] Pipes — <layer_name>`. This section explains the physical meaning
of each field.

| Field | Unit | Meaning |
|-------|------|---------|
| `flow_sm3s` | Sm³/h | **Signed** volumetric flow rate. Positive = gas flows from Node A to Node B (the "conventional" direction chosen during mapping); negative = gas flows the other way, from B to A. The direction arrows on the map automatically reflect this sign. |
| `flow_abs_sm3s` | Sm³/h | Volumetric flow rate in **absolute value** (unsigned). Also used to set the line thickness on the map: pipes with a higher flow rate are drawn thicker, visually highlighting the network's "main trunks". |
| `velocity_m_s` | m/s | Average gas velocity in the pipe, computed accounting for the gas's real compressibility (it is not simply flow rate / area — see "Basic physics concepts" → "Velocity"). The value is always positive (it's a magnitude, independent of flow direction). |
| `avg_pressure_bar` | bar | Average pressure along the pipe, computed as the average of the pressures at its two end nodes. Useful as a quick estimate of the "typical" operating conditions in that pipe (e.g. to estimate the average density of the gas flowing through it). |
| `sp_gravity` | — | Specific gravity of the gas mixture in the pipe (average of the two ends). See "Results — Nodes" for the physical meaning. |
| `z_factor` | — | Average compressibility factor Z in the pipe. See "Results — Nodes". |
| `density_kg_m3` | kg/m³ | Average gas density at the pipe's operating conditions (average pressure and temperature). |

## Why the flow rate can be negative

In field mapping (Tab 1), "Node A" and "Node B" are just an arbitrary label
assigned during collapse or data import — they don't necessarily indicate
the actual flow direction. The calculation engine determines the actual
direction from the computed pressures: gas always flows from the
higher-pressure point towards the lower-pressure one. If this direction
matches "from A to B", the flow rate is positive; if it's the opposite, the
flow rate is negative. This is completely normal, especially in meshed
networks (with several possible paths between two points) or when demand
conditions change.

## Flow direction arrows

If this option is enabled (Tab 2 → Result Visualisation), every pipe gets a
small triangular marker drawn at the centre of its geometry, oriented in the
actual direction the gas flows — not the layer's original "geometric"
direction, but the one determined by the sign of `flow_sm3s`. This is the
quickest way to get a visual sense of how gas distributes across a complex
network, for example to spot multi-feed points or flow reversals relative to
usual operating conditions.

## Velocity and erosion limits

`velocity_m_s` should be compared against practical velocity limits to avoid
excessive noise and erosion of the pipe's internal walls. The "Technical
references & standards" section of this Guide gives the erosion formula
(API RP 14E) and some indicative values for different categories of
pressurised pipes.
