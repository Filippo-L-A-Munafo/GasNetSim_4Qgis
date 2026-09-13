# Basic physics concepts

This section explains, in plain language, the physics concepts behind almost
every field in the interface. You don't need to read it all before using the
plugin, but the other sections will often refer back to it.

## The network as a "graph": nodes and pipes

For the calculation, a gas network is simplified into just two kinds of
elements:

- **Nodes**: points where gas enters the network, leaves the network
  (consumption), or where several pipes meet. Each node has a position, an
  elevation, and, if it is a delivery point, a consumption flow rate.
- **Pipes**: connect two nodes (node A and node B) and carry the gas. Each
  pipe has a length, a diameter and an internal roughness.

This representation is called a **graph**: nodes are the "vertices", pipes
are the "edges". It is the same kind of scheme used for electrical circuits
(nodes = circuit points, pipes = resistors) or for hydraulic networks in
general. The plugin's first job (the "topological collapse" described in the
Tab 1 section) is exactly to turn raw GIS geometries into this clean graph of
nodes and pipes.

## Pressure: absolute, relative, and why it matters so much

**Pressure** is the single most important quantity in the whole simulation:
it is what "pushes" gas along the pipes, from the point at higher pressure
towards the point at lower pressure (exactly like water flowing downhill from
a higher to a lower point).

One detail not to overlook: there are two ways of measuring pressure:

- **Absolute pressure**: measured starting from a perfect vacuum (0 bar = no
  pressure at all). This is what the plugin uses.
- **Relative (or gauge) pressure**: measured starting from atmospheric
  pressure (0 bar = atmospheric pressure, ~1.013 bar absolute). This is what
  field gauges usually read.

The plugin always works in **absolute pressure**. If you take a value from a
field gauge (relative/gauge pressure), remember to add about 1 bar
(atmospheric pressure) before using it as a reference pressure.

## Flow rate: why it's measured in "Sm³" and not just any cubic metre

Unlike water, gas is **compressible**: the same "packet" of gas molecules
takes up a different volume depending on the pressure and temperature it is
at (more pressure = more gas in the same space).

This creates a practical problem: saying "100 cubic metres of gas pass
through this pipe every hour" is meaningless until you specify *at what
pressure and temperature* you are measuring that volume, because the same
gas at 70 bar takes up much less space than the same gas at atmospheric
pressure.

The solution adopted by the gas industry (and by the plugin) is to measure
flow rates at **standard conditions**: imagine bringing all the gas back to a
fixed reference pressure and temperature (typically 1.01325 bar and 15 °C)
and measure the volume it would occupy *at those conditions*. The resulting
unit is called **Sm³** (Standard cubic metre), to distinguish it from the
"real" cubic metre at actual operating conditions.

This is why every consumption profile and every flow-rate result in the
plugin is expressed in Sm³/h or sm³/s: it lets you compare and add up flow
rates without worrying about the actual pressure the gas is travelling at, at
that point of the network.

## Velocity: why it isn't simply "flow rate / area"

The gas **velocity** in a pipe is not obtained by dividing the Sm³/h flow
rate by the pipe's cross-sectional area, because that flow rate is expressed
at standard conditions, while the gas inside the pipe travels at actual
operating conditions (high pressure). The flow rate first has to be converted
from standard to operating conditions (using the gas density at that
pressure and temperature, and the compressibility factor — see below), and
only then divided by the pipe's cross section.

Velocity is an important indicator because excessively high velocities cause
noise, vibration and erosion of the pipe walls (see the "Technical
references" section for practical limits).

## Pressure drop: the friction that slows the gas down

As gas flows along a pipe, it loses pressure because of friction with the
pipe's internal walls — just like water flowing through a hose loses
pressure to friction. This phenomenon is called **pressure drop** (or head
loss).

Pressure drop depends on:

- the **flow rate**: more gas flowing means more friction (a non-linear
  dependency: doubling the flow rate more than doubles the pressure drop);
- the pipe's **diameter**: narrower pipes generate more friction for the same
  flow rate;
- the pipe's **length**: the longer it is, the more pressure drop accumulates;
- the **internal roughness** of the wall (how "rough" the inside of the pipe
  is — depends on the material, see the Tab 2 section);
- the gas's **density and viscosity** at operating conditions.

The plugin uses a specific formula (the **Chen formula**, a variant of the
better-known Darcy-Weisbach equation) to compute this effect for every pipe
at every iteration of the calculation. The practical details (where to set
the roughness) are in the Tab 2 section.

## Mass balance at nodes: the network's fundamental law

At every node of the network a very simple rule must hold: **all the gas
that enters a node must leave it** (or be consumed right there). Gas cannot
"disappear" or "appear" out of nowhere. This rule is called **mass balance**
(or the continuity principle), and it is the gas-network equivalent of
Kirchhoff's current law in electrical circuits (the sum of currents entering
a node equals the sum of currents leaving it).

The calculation engine writes this equation for every node in the network
and solves it simultaneously together with the pressure-drop equations for
every pipe: the final result (pressures and flow rates) is the one and only
combination of values that satisfies all these equations at the same time.

## Reference nodes: why they are needed and what they physically represent

The system of equations described above has infinitely many solutions unless
it is "anchored" to a known absolute value: knowing that "node X is 2 bar
higher than node Y" is not enough to determine the absolute pressure of
either one. At least one point in the network needs a known, real absolute
pressure — typically an interconnection point with another network, a
compressor station, or a storage facility.

This point is called a **reference node**: it is a **boundary condition** of
the problem, exactly like the "ground node" in an electrical circuit (the
point arbitrarily assigned 0 Volts, from which every other voltage is
measured). This is why the plugin **requires at least one reference node**:
without one, the mathematical problem has no unique solution and the
simulation cannot start.

## Real-gas compressibility: why the ideal gas law isn't enough

The ideal gas law (pressure × volume = constant × temperature) is an
approximation that works well at low pressures, but it is **not accurate**
at the pressures typical of transmission networks (tens of bar). Real gases
behave slightly differently, and this deviation is measured by the
**compressibility factor Z** (Z = 1 for an ideal gas; Z < 1 for methane at
typical transmission-network conditions).

The calculation engine accounts for this effect at every node and every
pipe, recalculating Z as a function of local pressure, temperature and gas
composition. The `z_factor` field in the results (see the "Results — Nodes"
section) shows exactly this value.

## Steady state: what the plugin does NOT calculate

The plugin computes a **steady-state solution**: it assumes consumption
stays constant over time (the values chosen for the selected hour of the
day) and calculates what the network's state is once it has "settled" under
that demand. It does not simulate what happens during a transient event
(for example a valve suddenly opening, or how pressure changes minute by
minute during a demand change). To compare different conditions (e.g. peak
hour vs. minimum-demand hour), you run separate simulations, one per hour of
interest.

## In summary: the electrical-circuit analogy

If you're familiar with electrical engineering, this table may help:

| Electrical circuit | Gas network |
|---------------------|-------------|
| Voltage (Volt) | Pressure (bar) |
| Current (Ampere) | Flow rate (Sm³/h) |
| Resistance (Ohm, linear) | Pipe pressure drop (non-linear: depends on the flow rate itself) |
| Kirchhoff's current law (nodes) | Mass balance at nodes |
| Ground node (0 V) | Reference node (known pressure) |

The main difference is that in a gas network the "resistance" of each pipe
is not constant like an electrical resistor, but depends itself on the flow
rate passing through it — which is why the system of equations is
**non-linear** and requires an iterative method to be solved (see the Tab 2
→ Solver Parameters section).
