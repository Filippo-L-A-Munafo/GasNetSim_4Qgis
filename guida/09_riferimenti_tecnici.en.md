# Technical references & standards

This section collects the reference values, formulas and regulatory
classifications used as the basis for the plugin's default parameters. It's
meant as a quick reference, not something you need to read in one sitting.

## Pipe classification by "species" (Italian D.M. 17/04/2008)

Classification valid for natural gas **transmission** networks in Italy,
based on Maximum Operating Pressure (MOP):

| Species | MOP (Max Operating Pressure) | Network type |
|---------|-------------------------------|---------------|
| **1st** | > 24 bar (2.4 MPa) | National Transmission Network (RNT) |
| **2nd** | 12 bar < MOP ≤ 24 bar (1.2–2.4 MPa) | Regional Transmission Network (RRT) |
| **3rd** | 5 bar < MOP ≤ 12 bar (0.5–1.2 MPa) | High-pressure user derivations |
| **4th** | 1.5 bar < MOP ≤ 5 bar (0.15–0.5 MPa) | Local distribution networks |

> Simulations typically run with this plugin concern **1st and 2nd species**
> networks (RNT/RRT), with pressures in the 24–70 bar range.

## Maximum pipe velocity — erosion formula (API RP 14E)

The erosional velocity estimates the threshold beyond which high-velocity
gas flow starts to damage (through erosion) the pipe's internal walls,
particularly in the presence of solid or liquid particles carried by the
flow:

**Ve = C / √ρgas**

where:

- **Ve** — erosional velocity [m/s]
- **ρgas** — gas density at operating conditions [kg/m³]
- **C = 100** — empirical constant for continuous service, dry gas (SI
  units)

Note the behaviour: the denser the gas (high pressures), the **lower** the
allowable erosional velocity — the opposite of what intuition might suggest.
This is because, at the same velocity, a denser gas carries more momentum
and therefore more impact energy against the walls.

### Indicative estimates for methane (CH₄) at 15 °C

| Species | Typical MOP | Estimated ρ CH₄ | Ve (erosion) | Practical limit |
|---------|-------------|-------------------|--------------|------------------|
| 1st | 60–70 bar | ~44–55 kg/m³ | ~10–13 m/s | ~10–15 m/s |
| 1st | 24–40 bar | ~17–30 kg/m³ | ~13–18 m/s | ~15 m/s |
| 2nd | 12–24 bar | ~8–17 kg/m³ | ~18–24 m/s | ~15–20 m/s |
| 3rd | 5–12 bar | ~3.5–8 kg/m³ | ~24–35 m/s | noise ~15 m/s |
| 4th | 1.5–5 bar | ~1–3.5 kg/m³ | > 35 m/s | noise ~10 m/s |

> For Sicilian RNT transmission networks (60–70 bar), the practical velocity
> limit is typically **10–14 m/s**. Exact values derived from SNAM/Terna
> standards should be verified case by case.

## Supported gas compositions

Components recognised by the calculation engine (keys of the Python
dictionary used in the "Composition" field):

| Key | Component |
|-----|-----------|
| `methane` | Methane (CH₄) |
| `ethane` | Ethane (C₂H₆) |
| `propane` | Propane (C₃H₈) |
| `butane` | Butane (C₄H₁₀) |
| `nitrogen` | Nitrogen (N₂) |
| `carbon_dioxide` | Carbon dioxide (CO₂) |
| `hydrogen` | Hydrogen (H₂) |

### Presets available in the plugin

```
# Pure natural gas
{'methane': 1.0}

# Typical natural gas (Italian network)
{'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}

# 10% hydrogen blend
{'methane': 0.90, 'hydrogen': 0.10}

# 20% hydrogen blend
{'methane': 0.80, 'hydrogen': 0.20}

# 50% hydrogen blend
{'methane': 0.50, 'hydrogen': 0.50}

# Pure hydrogen
{'hydrogen': 1.0}
```

## Solver parameters — reference values

| Parameter | Plugin default | Notes |
|-----------|------------------|-------|
| Max iterations | 50 | Increase to 100–200 for complex networks |
| Tolerance | 1.0 | In the solver's internal units |
| URF | 2.0 | Under-relaxation factor |
| Reference pressure | 70 bar | Typical for Sicilian RNT |
| Reference temperature | 300 K (27 °C) | |
| Pipe roughness | 5×10⁻⁵ m | Steel. PE/HDPE: 7×10⁻⁶ m; cast iron: 2.6×10⁻⁴ m |

## Supported diameter units

| Code | Conversion factor to metres |
|------|-------------------------------|
| `m` | × 1 |
| `in` | × 0.0254 |
| `cm` | × 0.01 |

## Reference networks already tested with the plugin

| Network | Nodes | Pipes | Pressure | Outcome |
|---------|-------|-------|----------|---------|
| RRT Trapani | 7 | 6 | 70 bar | Converged in 4 iterations, ~7.7 s |
| RNT Sicilia | — | — | 24–25 bar | Converged OK (pressures 24.08–25.33 bar) |
