# Glossary

A quick list of the technical terms used in the plugin and in this guide,
for anyone unfamiliar with gas hydraulics or GIS terminology.

**Absolute pressure** — Pressure measured starting from a perfect vacuum (0
bar = no pressure). This is the unit used throughout the plugin.

**Relative (gauge) pressure** — Pressure measured starting from atmospheric
pressure (0 bar = atmospheric pressure). This is usually what a field gauge
reads; to use it in the plugin, convert it to absolute by adding about 1 bar.

**Flow rate** — Amount of gas passing through a pipe's cross section per
unit time. In the plugin it's expressed in Sm³/h (standard volumetric flow)
or sm³/s.

**Sm³ (Standard cubic metre)** — Unit of gas volume referred to fixed
standard conditions (15 °C, 1.01325 bar), used to compare flow rates without
having to specify the gas's actual pressure every time.

**Density** — Mass of gas per unit volume (kg/m³). Changes with pressure and
temperature, because gas is compressible.

**Standard density** — Gas density at standard reference conditions;
depends only on gas composition, not on the local pressure.

**Molar mass** — Average mass of one mole of molecules of the gas mixture
(g/mol). Heavier components (propane, butane) increase it; hydrogen lowers
it.

**Specific gravity** — Ratio between gas density and air density, at the
same conditions. Indicates whether the gas is lighter (< 1) or heavier (> 1)
than air.

**Compressibility factor Z** — Measure of how much a real gas deviates from
ideal behaviour (Z = 1 for an ideal gas).

**HHV (Higher Heating Value)** — Energy released by fully burning one
standard cubic metre of gas, including the heat recoverable from condensing
the water vapour produced.

**Wobbe index** — Indicator of interchangeability between different gases
(HHV divided by the square root of specific gravity): two gases with the
same Wobbe index behave the same way in the same burner.

**Reference node** — Network node assigned a known absolute pressure; acts
as the "anchor" for the whole calculation (like the ground node in an
electrical circuit). Mandatory: at least one per network.

**Mass balance** — Principle stating that, at every node, all the gas
entering must leave it (or be consumed there); underlies the equations
solved by the solver.

**Pressure drop** — Drop in pressure along a pipe caused by friction between
the gas and the internal walls.

**Roughness** — Degree of roughness of a pipe's internal surface; affects
friction and therefore pressure drop. Depends on the material.

**Chen formula** — Formula used by the calculation engine to estimate
frictional pressure drop in each pipe, a variant of the Darcy-Weisbach
equation.

**Steady state** — Type of solution computed by the plugin: assumes
consumption stays constant over time and computes the network's state once
it has settled, without simulating its evolution over time (transients).

**Newton-Raphson method** — Iterative numerical method used to solve the
network's non-linear system of equations, by successive approximations.

**Iteration** — A single correction cycle of the Newton-Raphson method.

**Tolerance** — Threshold below which the calculation's residual error is
considered acceptable (convergence reached).

**URF (Under-Relaxation Factor)** — Parameter controlling how "decisive"
each correction of the iterative method is; too high causes oscillations,
too low slows down convergence.

**Convergence** — The point at which the calculation's error drops below the
set tolerance and the simulation is considered successfully complete.

**Topological collapse** — Operation that turns raw GIS geometries
(independent lines and points) into a clean graph of correctly-connected
nodes and pipes.

**Snapping radius** — Maximum distance within which, during collapse, a node
is connected to a nearby pipe's endpoint.

**DEM (Digital Elevation Model)** — Raster layer representing terrain
elevation; used by the plugin to extract node elevations.

**Erosional velocity** — Velocity limit beyond which high-velocity gas flow
starts to damage the pipe's internal walls through erosion.

**Pipe species (Italian D.M. 17/04/2008)** — Italian regulatory
classification of gas transmission pipes based on their maximum operating
pressure (1st, 2nd, 3rd, 4th species).

**Hydrogen/methane blending** — The practice of injecting a hydrogen/methane
mixture into a network originally designed for pure natural gas, in order to
reduce CO₂ emissions.
