# Running the simulation

## The three ways to start the calculation

The simulation can be launched in three ways, all equivalent in their final
result — only the point in the workflow you start from changes:

1. **Tab 1 → ">> Generate CSV and Simulate"** — the recommended way for daily
   work: exports the CSVs and immediately runs the simulation in a single
   click, without permanently saving intermediate files to disk.
2. **Tab 1 → "> Generate CSV"**, then **Tab 2 → "▶ Run Simulation"** — useful
   when you want to check (or manually edit) the CSV files before running
   the calculation, for example to verify the exported values are as
   expected.
3. **"▶ Run Simulation" button in the window's footer** — regenerates the
   CSVs from the current layers and immediately runs the calculation,
   without having to go back to Tab 1.

## What happens internally

The simulation runs in a **separate thread**: this means QGIS stays fully
usable while the calculation is running (you can keep navigating the map,
opening other layers, etc.) instead of freezing while waiting for the
result.

The **Dashboard** panel, at the centre of the window, shows every stage of
the process in real time:

1. **CSV validation** — checks that the files have all the required fields
   and that at least one reference node is present. If not, the simulation
   stops right here with a clear error message.
2. **Network loading** — builds the node/pipe graph in memory, applying the
   gas properties (composition, temperature).
3. **Solver iterations** — the Newton-Raphson method proceeds by successive
   approximations (see Tab 2 → Solver Parameters); the log shows progress
   and, if enabled, the tolerance/URF auto-calibration.
4. **Pressure summary** — a summary of the pressures computed across the
   whole network (minimum, maximum, values at reference nodes), useful for a
   first plausibility check of the result.
5. **Result layer creation** — the two new colour-coded layers (nodes and
   pipes) are generated and added to the QGIS project.

If the simulation fails to converge (the error does not drop below the
tolerance within the maximum number of iterations), the log explicitly
reports it: in that case see the "Troubleshooting" section of this Guide for
steps to try.
