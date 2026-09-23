# 1. Introduction and scope

## 1.1 Subject

GasNetSim 4Qgis is a QGIS plugin that solves the steady-state hydraulic
problem of a natural gas transmission network, optionally blended with
hydrogen, starting from the vector representation of the network held in a
QGIS project.

The plugin acts as the geospatial interface to the **GasNetSim** solver
(Forschungszentrum Jülich, ICE-1) and extends it with compressor station
handling, parallel execution of hourly scenarios, and cartographic rendering of
the results.

## 1.2 Model solved

The model is **nodal**, **steady-state** and **isothermal**, with a real-gas
equation of state. The unknowns are the nodal pressures; flow rates, velocities
and thermophysical properties are derived quantities.

The complete formulation, with the equations as implemented, is given in §2. In
summary the model comprises:

- a mass balance at each demand node;
- the general flow equation for each pipeline, with the friction factor from
  the explicit correlation of Chen (1979);
- a geodetic elevation correction term;
- the **GERG-2008** equation of state (ISO 20765-2) for compressibility factor,
  density and heat capacities;
- composition tracking where gases of different composition are injected.

## 1.3 Range of validity and limitations

| Aspect | Scope |
|--------|-------|
| Regime | Steady state. Transients are not modelled: each run describes the asymptotic state of the network at constant demand. |
| Temperature | Uniform and prescribed. The thermal balance along pipelines is not solved. |
| Phase | Single-phase gas. Condensates and two-phase transport are not treated. |
| Pressures | Verified on 1st and 2nd class networks (24–75 barg). The formulation imposes no explicit pressure limits. |
| Components | Pipelines, demand and injection nodes, fixed-pressure nodes, compressor stations. Control valves, regulators and storage are not exposed by the interface. |
| Optimisation | Not provided. The plugin solves the configuration supplied; it does not search for an optimal one. |

Beyond the topological checks of §4, the plugin performs no plausibility
checking of the input data: missing values are replaced by the fallback values
documented in §6.2 and the computation proceeds. Ensuring the physical
consistency of the data remains the user's responsibility.

## 1.4 Typical applications

1. **Adequacy assessment**: determination of pressures at delivery points for a
   given hourly demand profile, and comparison against contractual minima.
2. **Hydrogen blending analysis**: assessment of the effect of a molar fraction
   of H₂ on pressures, velocities, heating value, specific gravity and Wobbe
   index, for verification of gas quality constraints (§13.4).
3. **Reinforcement sizing**: comparison of alternative network configurations
   at equal demand.
4. **Multi-scenario campaigns**: automatic execution of 24 hourly scenarios, or
   of a series of days, with systematic collection of results.

## 1.5 Processing architecture

The workflow is organised in three stages, matching the three tabs of the
interface:

| Stage | Tab | Content |
|-------|-----|---------|
| Topological verification | Tab 0 | Connectivity analysis of the pipeline layer, detection of degenerate geometries, duplicates and disconnected components; correction by endpoint snapping (§4). |
| Case definition and execution | Tab 1 | Association of layer fields with model quantities, assignment of physical and numerical parameters, generation of the input files and execution of the solver (§5, §6, §7). |
| Post-processing | Tab 2 | Thematic rendering of results and export (§8). |

The order 0 → 1 → 2 is operational rather than indicative: omitting the
preliminary topological verification is the most frequent cause of
non-convergence on vector data not prepared for computation (§12.6).

## 1.6 Structure of this document

§2–§3 describe the model and the organisation of the interface; §4–§8 document
every exposed control, tab by tab; §9–§10 define the quantities returned; §11
presents a **reproducible verification case**, with the expected numerical
values, to be run in order to validate the installation; §12 collects
convergence diagnostics; §13–§14 contain technical and regulatory references
and the nomenclature.

Quantities are denoted by the symbols and units adopted in §14. Equations are
numbered by section and referenced in the text.
