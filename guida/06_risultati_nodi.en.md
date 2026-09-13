# Results — Nodes

At the end of the simulation, the plugin creates a point layer called
`[Results] Nodes — <layer_name>`, with one field per computed quantity. This
section explains what each field physically means.

| Field | Unit | Meaning |
|-------|------|---------|
| `pressure_bar` | bar | Absolute pressure computed by the simulation at that node. This is the main result: it represents the force pushing gas towards lower-pressure nodes. |
| `temperature_k` | K | Operating temperature at the node. In the current model it is propagated from the value set in the Physical Parameters (uniform temperature across the whole network). |
| `sp_gravity` | — (dimensionless) | **Specific gravity**: the ratio between the gas density at that point and the density of air, both at the same standard conditions. A value < 1 means a gas lighter than air (e.g. hydrogen, sp. gravity ≈ 0.07); a value close to 0.6 is typical of pure methane. This matters when assessing gas dispersion in the event of a leak (a gas lighter than air tends to rise and disperse upward). |
| `z_factor` | — (dimensionless) | **Compressibility factor Z**: measures how much the real gas deviates from ideal behaviour (Z = 1 for an ideal gas). Depends on pressure, temperature and composition. The solver needs it to correctly compute the gas density at operating conditions (see "Basic physics concepts"). |
| `hhv_mj_sm3` | MJ/sm³ | **Higher Heating Value**: the energy released by fully burning one standard cubic metre of that gas, including the heat recoverable from condensing the water vapour produced. This is the key quantity to understand how much energy the network is actually carrying at that point, not just how much gas "volume". |
| `wobbe_mj_sm3` | MJ/sm³ | **Wobbe index** = HHV / √(specific gravity). Measures interchangeability between different gases: two gases with the same Wobbe index release the same thermal power through the same burner, even if their compositions differ. It is the most commonly used indicator to assess whether a blend (e.g. with hydrogen) is compatible with appliances designed for pure natural gas. |
| `density_kg_m3` | kg/m³ | Gas density at the node's actual operating conditions (local pressure and temperature). The higher the pressure, the denser the gas — one cubic metre at 70 bar holds far more gas than the same cubic metre at atmospheric pressure. |
| `std_density_kg_sm3` | kg/sm³ | Gas density at **standard reference conditions** (15 °C, 1.01325 bar). Unlike operating density, it depends only on gas composition, not on local pressure: it is the value used to convert between Sm³ flow rates and mass flow rates (kg/s). |
| `molar_mass` | g/mol | Average molar mass of the gas mixture at that node, computed as a weighted average over the mole fractions of the individual components. Heavier components (propane, butane) increase the average molar mass; hydrogen, being very light, drastically lowers it even at low concentrations. |

## How to read these values in practice

- A `pressure_bar` value dropping below the contractual minimum threshold at
  a delivery point signals a network capacity problem in that area.
- A `sp_gravity` or `molar_mass` value that changes sharply from one node to
  another can indicate a mixing point between gases of different composition
  (e.g. a hydrogen injection).
- `wobbe_mj_sm3` is the first value to check when assessing the compliance
  of a hydrogen/methane blend with regulations and with end-user appliances.
