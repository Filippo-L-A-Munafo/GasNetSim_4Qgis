# GasNetSim Toy Model: 10-Node Hydrogen Blending Network

This lightweight demonstrative case study allows reviewers and researchers to test the full GasNetSim thermo-hydraulic solving pipeline in less than **2 seconds** without needing a full GIS environment.

## Network Architecture
* **Topology:** 10 nodes, 9 transmission pipelines forming an interconnected corridor connected to the international import hub;
* **Boundary Condition:** Node 8118 (Mazara del Vallo) acts as the high-pressure entry point (76.01 bar abs / 75.0 barg);
* **Orography:** Node elevations range from 7 m to 142 m a.s.l. (demonstrating the 3D geodesic elevation term $\rho g \Delta z$);
* **Gas Quality:** 13.92 vol% green hydrogen in Algerian natural gas (the regulatory relative density bound $d = 0.555$ pursuant to Italian D.M. 18/05/2018).


## Quick Run
From any terminal with Python and GasNetSim installed:

```bash
cd sample_data/toy_network_h2
python run_toy_model.py
```
