# Sicilian Regional Transmission Network (Sample Data)

This folder contains the benchmark dataset of the Sicilian natural gas transmission
grid (340 nodes, 350 pipelines, ~2,316 km), ready for use with the **GasNetSim_4Qgis**
plugin.

## Datasets Included

1. **Root (`./`):** Autumn transit snapshot (15 Nov 2025, h12) with 13.92 vol% green hydrogen blend.
2. **`winter_peak_0108_h18/`:** Winter peak demand snapshot (08 Jan 2026, h18).

## Using with GasNetSim_4Qgis

1. Open QGIS and load the vector layers or project for the Sicilian network.
2. Open the GasNetSim_4Qgis plugin dialog.
3. Use the batch or single-run simulation interface to run steady-state hydraulics with hydrogen blending.
4. Visualize resulting pressures, volumetric flows, velocities, and hydrogen concentrations directly in QGIS.
