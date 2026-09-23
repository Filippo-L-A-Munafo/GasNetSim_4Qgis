# 4. Tab 0 — Topological verification of the network

## 4.1 Purpose

Topological verification precedes the construction of the computational model.
System (2.3) admits a unique solution only if every connected component of the
network contains at least one fixed-pressure node: a disconnected portion
without a reference node makes the system indeterminate and the simulation
fails to converge (§12.6).

Connectivity is a **topological, not a graphical** property: two pipelines
whose endpoints lie a few centimetres apart appear contiguous at the display
scale but constitute two distinct components. This tab detects this and other
pathologies typical of vector data not originally produced for modelling.

## 4.2 Network analysis

### 4.2.1 Layer selection

| Field | Description |
|-------|-------------|
| **Pipelines** | Line layer to be analysed. Required. |
| **Nodes (opt.)** | Optional point layer. If assigned, the snapping operation (§4.3) attaches pipeline endpoints to existing nodes within tolerance, taking priority over the cluster centroid. To be used when node positions are surveyed and considered reliable. |

### 4.2.2 Procedure

The **Analyze network** command performs, read-only:

1. repair of invalid geometries;
2. **explosion of polylines** into elementary segments, which constitute the
   graph edges. The resulting number of edges is generally larger than the
   number of layer features;
3. construction of the graph and counting of edges discarded as null or
   degenerate;
4. identification of pathologies or, in their absence, the message
   `[OK] Nessun problema topologico rilevato.`

### 4.2.3 Pathologies detected

| Pathology | Definition | Consequence for the computation |
|-----------|------------|----------------------------------|
| Null or degenerate geometries | Features without geometry or of zero length | Pipelines with L = 0: equation (2.5) diverges |
| Duplicates and overlaps | Edges with the same pair of endpoints, or overlapping | Non-physical duplication of the transport capacity of that stretch |
| Disconnected components (islands) | Subgraphs not connected to the main graph | Indeterminate system in the absence of a reference node in the component |

The option **Automatically create a coloured layer if islands are found**
(enabled by default) generates a temporary layer with a distinct colour per
component, allowing discontinuities to be located immediately.

The **⚠ Select problem pipelines** command selects, in the source layer, the
duplicate or overlapping edges identified by the last analysis.

## 4.3 Endpoint snapping

A geometric correction operation that unifies mutually close endpoints. It is
the only operation of the plugin capable of modifying the source data.

| Parameter | Default | Description |
|-----------|---------|-------------|
| **Tolerance** | 1.0 m | Maximum distance within which two endpoints are considered coincident. Expressed in the layer's CRS units (cf. §3.5). |
| **Strategy — Midpoint** | selected | All endpoints of the cluster are moved to the cluster centroid. A neutral choice, appropriate when sources have homogeneous accuracy. |
| **Strategy — Anchor to first** | — | One endpoint remains fixed and the others are moved onto it. Appropriate when one stretch has superior planimetric accuracy. |
| **Output — Create new layer** | selected | Produces a corrected copy, added to the project. The original is left unchanged. |
| **Output — Modify original layer** | — | Writes into the source layer. For file-based layers the change is **irreversible**; explicit confirmation is required. |

If a node layer has been assigned (§4.2.1), endpoints are snapped to existing
nodes within tolerance.

### 4.3.1 Criterion for choosing the tolerance

The tolerance must exceed the positional error of the data and remain below the
minimum distance between genuinely distinct elements. An excessive value merges
parallel pipelines belonging to the same corridor, producing a network that
does not exist and, typically, overestimated transport capacity.

An incremental procedure is recommended: start from 1–2 m, analyse, check the
reduction in the number of components, and increase the tolerance only if
necessary, inspecting the result visually at each step.

## 4.4 Islands and re-analysis

This block becomes active when disconnected components are present.

| Command | Function |
|---------|----------|
| **⚠ Select islands** | Selects, in the source layer, the edges belonging to components detached from the main graph. |
| **Create coloured layer** | Temporary layer with one colour per component. |
| **Re-analyze current network** | Repeats the analysis on the layer produced by the last snapping operation, if any, otherwise on the selected layer. |

## 4.5 Recommended procedure

1. Analysis of the source layer.
2. Where islands are present, inspection of the coloured layer.
3. Snapping with a conservative tolerance, output to a **new layer**.
4. Re-analysis of the layer produced.
5. Iteration of steps 3–4 until the remaining components correspond to portions
   of the real network that are genuinely isolated (for example branches not in
   service).
6. Removal or exclusion of residual components without supply, since they are
   incompatible with solvability of the system.
7. Proceeding to Tab 1 using the corrected layer.

> Model construction (§5.3) may itself generate warnings: these are presented
> in a dedicated window, with the **Zoom to pipelines** and **Flash**
> commands for cartographic location of the elements concerned.
