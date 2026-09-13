# Introduction

## What GasNetSim 4Qgis is

GasNetSim 4Qgis is a QGIS plugin that calculates **how a gas transmission or
distribution network behaves**: how much pressure there is at every point of
the network, how much gas flows through each pipe and at what speed — starting
simply from the geographic data you already have in QGIS (pipelines drawn as
lines, nodes as points).

In practice the plugin bridges two worlds:

- **QGIS**, where the network is made of geometries (lines and points) with
  attributes;
- **GasNetSim**, the calculation engine that solves the physics equations for
  gas flow and returns pressures and flow rates.

The plugin handles all the "boring" part — translating the GIS layers into
the format the calculation engine expects, running the calculation, and
redrawing the results as new coloured layers — so the user can focus on their
network's data and on interpreting the results.

## What it is used for, in practice

Simulating a gas network before acting in the field lets you answer questions
such as:

- If I increase demand in one area, does pressure stay above the guaranteed
  minimum, or is there a risk of dropping below the threshold?
- Can an existing pipe carry more gas, or does it need to be replaced or
  duplicated?
- What happens if I inject a hydrogen/methane blend into the network instead
  of pure natural gas (H₂/CH₄ blending)?
- Where are the most critical points in the network (too-high velocities,
  excessive pressure losses)?

Without a simulator, answering these questions would require field
measurements or very laborious manual calculations; the plugin automates
them starting from data you probably already have in a QGIS project.

## The two-phase workflow

The plugin is organised into two phases, matching the two tabs of the main
window:

1. **Prepare Network** (Tab 1) — here you tell the plugin *which* QGIS layers
   represent your network and *how* to read their fields (which field is the
   diameter, which one identifies nodes with a known pressure, etc.). The
   output of this phase is two CSV files — one for nodes, one for pipes — in
   the format the calculation engine understands.
2. **Simulate** (Tab 2) — here you set the physical parameters (reference
   pressure, temperature, gas composition) and the solver parameters
   (tolerance, number of iterations), then run the actual simulation. At the
   end, the plugin automatically creates two new colour-coded layers in QGIS
   with the results (pressures on nodes, flow rates and velocities on pipes).

The following sections of this Guide follow exactly this structure: first a
few physics concepts useful to understand *why* certain fields exist
("Basic physics concepts" section), then an explanation of every single
interface element, tab by tab.

## Who this guide is for

This guide is written for someone who is **neither a gas-network expert nor a
QGIS expert**: every function is explained both from a practical point of view
("what do I write in this field") and from a physical point of view ("why
this data is needed for the calculation, and what it physically represents").
If you are already an expert in one of the two fields, feel free to jump
straight to the section you need using the list on the left.

## How to use this Guide

Use the list on the left to jump directly to the section you need. This
Guide is separate from the **ℹ About** button, which instead shows the
plugin version, author and licensing information.
