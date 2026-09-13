# Troubleshooting

## "Simulation blocked: no reference node found"

**Cause**: the node layer contains no point marked as a reference node
according to the field/value set in "Reference field" (Tab 1).

**How to fix it**:

1. Check that the field chosen in "Reference field" actually exists in the
   node layer and that at least one row has the expected value (e.g.
   `type = reference`, or `matched = 1`).
2. If your network doesn't yet have such a field, open the node layer's
   attribute table in QGIS and create a new field (e.g. `is_ref`), setting
   the value `1` on the point that represents an interconnection with a
   known pressure (e.g. the gas entry point into the network you are
   modelling).
3. Remember: you need **at least one** reference node, but you can have more
   than one if the network has multiple known-pressure feed points.

The reason for this requirement is explained in "Basic physics concepts" →
"Reference nodes": without a point of known absolute pressure, the system of
equations has no unique solution.

## "The simulation doesn't converge" (the error doesn't drop below tolerance)

Try, in order:

1. **Increase the maximum number of iterations** (Tab 2 → Solver
   Parameters), e.g. from 50 to 150–200: sometimes the network does
   converge, just more slowly than expected.
2. **Reduce the URF** (e.g. from 2.0 to 1.0–1.5): a value that is too high
   makes the solution oscillate without ever settling, especially in
   networks with very different pipe diameters directly connected to each
   other.
3. **Slightly increase the tolerance** (e.g. from 1.0 to 2.0 or 5.0), if
   lower precision is acceptable for your purpose (e.g. a first exploratory
   analysis).
4. **Enable "Auto-calibrate tol & URF"**: the plugin will automatically try
   several combinations for you.
5. **Check for isolated nodes**: if some nodes end up disconnected from the
   rest of the network (e.g. because of a too-small snapping radius during
   collapse — see Tab 1), they can generate "empty" rows in the system of
   equations. Try increasing "Flow for demand-less nodes" (Tab 2 → Physical
   Parameters) from 0.0001 to 0.001.

## "Some nodes/pipes seem to be missing after the collapse"

**Most common cause**: the **snapping radius** (Tab 1, Mode A) is too small
relative to your data's geometric precision, so some pipe endpoints that
should be connected to the same node end up disconnected.

**How to fix it**: gradually increase the snapping radius (e.g. from 50 to
100 metres) and re-run the collapse, checking the result each time with
"Add collapsed layers to project" enabled, so you can visually inspect where
nodes are actually being created.

Beware of the opposite risk: too large a radius can mistakenly merge nodes
that are genuinely distinct in reality (e.g. two parallel but unconnected
pipes).

## "The hourly consumption profile isn't being read correctly"

**Most common cause**: the **separator** chosen (Tab 1 → Export Parameters)
doesn't match the character actually used in the node layer's field.

**How to fix it**: open the node layer's attribute table, look at the value
of the "Node hourly flow" field for any row, and check which character
separates the 24 values (`;`, `,`, `|`, `:`, space, tab). Set the same
character in the "Flow separator" menu. The hour-of-day preview field
immediately shows whether the reading worked correctly.

## "Node elevation is always 0"

**Cause**: no DEM layer was provided (Tab 1, Mode A → "DEM (optional)"
field), or the DEM layer doesn't cover the nodes' area.

**How to fix it**: provide a DEM raster layer covering the network's whole
extent. If you don't have a DEM available, you can leave elevation at 0: for
transmission networks on flat terrain the effect on pressure is generally
small, but in areas with significant elevation changes (as in much of
Sicily) it can be significant and should be verified.

## Installation issues (GasNetSim engine, numba, long paths)

These issues are not about using the plugin but about installing it, and
are documented in detail in the repository's `README.md` file: in short, on
Windows the GasNetSim engine must be installed under a short path (not
inside the QGIS plugins folder, which is already quite long on its own),
otherwise `numba` can raise `FileNotFoundError` errors from exceeding
Windows' 260-character path limit.
