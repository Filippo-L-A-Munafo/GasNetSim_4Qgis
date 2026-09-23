# 13. Technical and regulatory references

## 13.1 Default values

| Parameter | Symbol | Value | Unit | § |
|-----------|--------|-------|------|---|
| Reference pressure | p_ref | 75.0 | bar gauge | 6.2 |
| Temperature | T | 288.15 | K | 6.2 |
| Absolute roughness | ε | 1.2×10⁻⁵ | m | 6.2 |
| Placeholder flow | D_min | 1×10⁻⁴ | sm³/s | 6.2 |
| Minimum export flow | — | 1×10⁻⁶ | sm³/s | 6.2 |
| Snap radius | r_s | 50.0 | m | 6.2 |
| Result layer decimals | — | 4 | — | 6.2 |
| Maximum iteration count | — | 50 | — | 6.3 |
| Tolerance | tol | 1×10⁻³ | Sm³/s | 6.3 |
| Under-relaxation factor | URF | 2.0 | — | 6.3 |
| Composition | — | SNAM Mazara del Vallo | — | 6.4 |
| Friction correlation | — | Chen (1979) | — | 2.4.2 |
| Equation of state | — | GERG-2008 | — | 2.5 |
| Standard conditions | T_b, p_b | 288.15 K; 101 325 Pa | — | 2.2 |

### 13.1.1 Auto-calibration ladder

| Number of nodes | tol [Sm³/s] | URF [–] |
|-----------------|-------------|---------|
| < 100 | 0.1 | 1.5 |
| < 500 | 1.0 | 2.0 |
| < 2000 | 5.0 | 2.5 |
| ≥ 2000 | 10.0 | 3.0 |

Should convergence fail, the ladder is walked towards the more relaxed values.

## 13.2 Absolute roughness by material

| Material | ε [m] |
|----------|-------|
| Internally coated steel (transmission) | 1.2×10⁻⁵ |
| Bare steel | 5×10⁻⁵ |
| Polyethylene (PE/HDPE) | 7×10⁻⁶ |
| Cast iron | 2.6×10⁻⁴ |

### 13.2.1 Diameter unit conversion

| Code | Factor to metres |
|------|-------------------|
| `m` | 1 |
| `in` | 0.0254 |
| `cm` | 0.01 |

## 13.3 Reference compositions

Molar fractions. The two SNAM compositions correspond to the principal entry
points of the Sicilian system.

| Component | Mazara del Vallo (Algerian) | Gela (Libyan) |
|-----------|------------------------------|----------------|
| methane | 0.86909 | 0.86645 |
| ethane | 0.08661 | 0.05246 |
| propane | 0.01163 | 0.02022 |
| isobutane | 0.00072 | 0.00317 |
| butane | 0.00112 | 0.00478 |
| isopentane | 0.00019 | 0.00071 |
| pentane | 0.00019 | 0.00026 |
| hexane | 0.00014 | 0.00060 |
| nitrogen | 0.01334 | 0.04455 |
| carbon dioxide | 0.01672 | 0.00602 |
| helium | 0.00025 | 0.00078 |

Further presets: `{'methane': 1.0}`; `{'methane': 0.94, 'ethane': 0.04,
'propane': 0.01, 'nitrogen': 0.01}`; `{'hydrogen': 1.0}`.

Default compressor station parameters: compression ratio 1.1; efficiency 0.85;
isentropic process.

## 13.4 Pipeline classification and gas quality

### 13.4.1 Classes (Italian D.M. 17/04/2008)

| Class | MOP | Network type |
|-------|-----|--------------|
| 1st | > 24 bar | National transmission network |
| 2nd | 12 < MOP ≤ 24 bar | Regional transmission network |
| 3rd | 5 < MOP ≤ 12 bar | High-pressure user branches |
| 4th | 1.5 < MOP ≤ 5 bar | Local distribution |

### 13.4.2 Specific gravity constraint

Italian regulation on the quality of gas injected into transmission networks
sets a lower limit on specific gravity, d ≥ 0.555. Since hydrogen appreciably
reduces SG (§9.3), that constraint — rather than the heating value — normally
governs the maximum blendable fraction. For Algerian gas from Mazara del Vallo
the limit is reached at a hydrogen molar fraction of about **13.9 %**, the
value adopted in the example data distributed with the plugin.

> The regulatory references given are indicative and must be verified against
> the sources in force before any formal use.

## 13.5 Erosional velocity limit

API RP 14E criterion:

    v_e = C / √ρ                                                         (13.1)

with v_e the erosional velocity [m/s], ρ the gas density at operating
conditions [kg/m³], and C = 100 in SI units for continuous service with dry
gas.

Equation (13.1) implies that the allowable velocity **decreases** as density,
and hence operating pressure, increases.

| Class | MOP | Estimated ρ [kg/m³] | v_e [m/s] | Practical limit [m/s] |
|-------|-----|----------------------|-----------|------------------------|
| 1st | 60–70 bar | 44–55 | 10–13 | 10–15 |
| 1st | 24–40 bar | 17–30 | 13–18 | ≈ 15 |
| 2nd | 12–24 bar | 8–17 | 18–24 | 15–20 |
| 3rd | 5–12 bar | 3.5–8 | 24–35 | ≈ 15 (noise) |
| 4th | 1.5–5 bar | 1–3.5 | > 35 | ≈ 10 (noise) |

## 13.6 File formats

Field separator `;` for all files produced and read by the solver.

**`sf_nodes.csv`** — `node_index`, `pressure_pa`, `flow_MW`, `flow_sm3_per_s`,
`altitude_m`, `temperature_k`, `gas_composition`, `node_type`, `latitude`,
`longitude`, `flow_type`.

**`sf_pipelines.csv`** — `pipeline_index`, `inlet_index`, `outlet_index`,
`diameter_m`, `length_m`, `friction_method`, `roughness_m`.

**`sf_compressors.csv`** — `compressor_index`, `inlet`, `outlet`,
`compression_ratio`, `efficiency`, `thermodynamic_process`, `control_mode`,
`p_out_target`.

**`results_nodes.csv`**, **`results_pipes.csv`**, **`results_compressors.csv`**
— fields described in §9 and §10.

## 13.7 Bibliographic and regulatory references

1. Chen N.H. (1979). *An Explicit Equation for Friction Factor in Pipe*.
   Industrial & Engineering Chemistry Fundamentals, 18(3), 296–297.
2. ISO 20765-2:2015. *Natural gas — Calculation of thermodynamic properties —
   Part 2: Single-phase properties (gas, liquid, and dense fluid) for extended
   ranges of application* (GERG-2008 equation of state).
3. UNI EN ISO 13443. *Natural gas — Standard reference conditions*.
4. API RP 14E. *Recommended Practice for Design and Installation of Offshore
   Production Platform Piping Systems*.
5. EN 16726. *Gas infrastructure — Quality of gas — Group H*.
6. Italian D.M. 17 April 2008. *Technical rule for the design, construction,
   testing, operation and surveillance of natural gas transmission works and
   installations with relative density not exceeding 0.8*.
7. Lu Y. et al. *GasNetSim* — Forschungszentrum Jülich, ICE-1: Energy Systems
   Engineering. MPL-2.0 licence.
   https://jugit.fz-juelich.de/iek-10/public/simulation/gasnetsim
