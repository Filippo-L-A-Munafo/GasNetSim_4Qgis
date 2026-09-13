# The plugin interface

When you open GasNetSim 4Qgis (toolbar icon, or the **GasNetSim_4Qgis**
menu), a single window opens, divided into three horizontal areas plus a
hidden side menu.

## The three main panels

| Panel | Location | Content |
|-------|----------|---------|
| **Preparation** | Left (most of the window) | The two tabs "Prepare Network" and "Simulation Parameters", described in the following sections of this Guide. This is where you spend most of your time. |
| **Dashboard** | Centre | The real-time simulation log: shows every stage of the calculation as it happens (CSV validation, network loading, solver iterations, final pressure summary, result-layer creation). Especially useful to understand *where* a simulation that fails to converge gets stuck. |
| **Properties Inspector** | Right | Shows the attributes of the feature (node or pipe) currently selected on the QGIS map. Lets you quickly check the values of a specific element without opening the layer's attribute table. |

You can resize the window freely (it is designed to be used full-screen or
close to it, since the preparation panel contains many fields).

## The side menu (☰)

At the top left there is a **☰** button that opens/closes a side bar with
three buttons:

| Button | Function |
|--------|----------|
| **⚙ Settings** | Lets you change the interface language (Italian/English). The change takes effect the next time you open the plugin. |
| **📖 Guide** | Opens this guide — the full user manual you are reading now, organised into navigable sections. |
| **ℹ About** | Shows the plugin version, author, repository link and licensing information. |

## The "Close" button

At the bottom right, it closes the plugin window. It does not interrupt any
simulation that has already completed (result layers stay in the QGIS
project like any other layer), but if a simulation is still running it is
best to wait for it to finish before closing.

## A practical note

The plugin **never modifies your original layers**: it reads the geometries
and attributes of the layers you select, but everything it produces
(collapsed layers, result layers, CSV files) is created as a new element,
leaving the source data untouched. This lets you try different
configurations (e.g. different snapping radii, or different hours of the
day) without risking damage to your original data.
