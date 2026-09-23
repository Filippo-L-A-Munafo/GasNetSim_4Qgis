# 12. Convergence diagnostics

Non-convergence occurs when criterion (2.14) is not satisfied within the
prescribed number of iterations. The solver nonetheless returns the last
iterate, marked by the `_NONCONV` suffix of the results folder (§7.5): an
intermediate state, devoid of physical meaning, which does not satisfy the
nodal balances.

It is emphasised that convergence is a property of the problem — topology,
demands, diameters, initial state — in combination with the algorithm employed,
and not of the program. Only the default values of the numerical parameters and
the coupling scheme adopted (§12.3) depend on the latter; all the remaining
causes listed below reside in the data or in the network.

This section lists the causes in order of observed frequency, with the
corresponding checks.

## 12.1 Insufficient iteration count

**Frequency: the highest.** The number of iterations required depends on the
distance between the initial state and the solution, not on the size of the
network. In the tests carried out (§11.7) the default value of 50 iterations
proved insufficient on all three networks examined:

| Network | Nodes | Outcome with 50 iterations | Outcome with 200 |
|---------|-------|-----------------------------|-------------------|
| Verification case (§11) | 4 | does not converge | converges in 92 iterations |
| `toy_network_h2` | 10 | does not converge | not determined |
| `Sicily_transmission_network` | 340 | does not converge (residual 1×10⁻¹ Sm³/s) | not determined |

**Action.** Set *Max iterations* to 200, and to 500 if necessary. The increase
carries no penalty: execution terminates as soon as (2.14) is satisfied.

## 12.2 Insufficiently damped Newton step

If the residual oscillates without decreasing — a frequent condition where
pipelines of very different diameter are directly connected — the step length
is excessive.

**Action.** **Increase** the URF, for example from 2.0 to 4.0. Recall that the
URF appears in the denominator of (2.13): larger values shorten the step and
stabilise the iteration; values below 1 amplify the Newton step and should be
reserved for networks that converge readily and for which the iteration count
is to be reduced.

The tolerance may subsequently be relaxed, from 0.001 to 0.01 Sm³/s (36 Sm³/h
of admitted imbalance per node, negligible on networks carrying hundreds of
thousands of Sm³/h).

The *Auto-calibrate tol and URF* option automates this search, walking the
ladder of §13.1.1 towards progressively more relaxed combinations. Check in the
log which values actually achieved convergence, since the tolerances employed
are appreciably wider than the default.

## 12.3 Coupling scheme adopted

Convergence is not a property of the software: it depends on the problem —
topology, demands, diameters, initial state — in combination with the algorithm
used to solve it. The plugin does, however, determine three elements of the
algorithm, and these are the only ones on which it acts:

1. the maximum iteration count (§12.1), whose default value is 50;
2. the coupling scheme between the hydraulic problem and composition tracking;
3. the tolerances of the outer loop of the staggered scheme, set to
   `coupling_tol = tol × 10⁻²` and `coupling_max_iter = max_iter` in place of
   the engine defaults (10⁻⁴ and 20).

### 12.3.1 Selection criterion

The staggered scheme is enabled when at least one non-reference node carries its
own composition in the `sf_nodes.csv` file (§5.7); otherwise the direct scheme
is adopted. The criterion is syntactic in nature — the presence of a value in a
field — and not numerical: it in no way depends on the difficulty of the
problem.

### 12.3.2 Why the scheme matters

In the direct scheme the mixture assigned to each pipeline is redefined from the
sign of the flow rate at every residual evaluation. If nodal compositions differ
from one another, a pipeline that reverses its flow during the iteration changes
its mixture and with it the gas properties: the residual function becomes
discontinuous in x and the line search stalls without achieving a reduction of
the residual (cf. the messages of §12.10). The staggered scheme removes the
discontinuity by freezing the composition during the Newton step and updating it
in a separate step, at fixed pressures, with relaxation.

It follows that on a network with a single composition the two schemes are
substantially equivalent, since redefining the mixture always returns the same
mixture. In that case non-convergence is to be attributed to §12.1 and §12.2,
not to the scheme.

### 12.3.3 Quality of the solution

The inner step of the staggered scheme is the same Newton solver as the direct
scheme, invoked with the same tolerance and the same maximum iteration count;
the inner iteration is considered complete only when criterion (2.14) is
satisfied. Convergence of the staggered scheme is therefore not obtained with a
weaker criterion: two conditions on the outer loop are added to criterion
(2.14) — maximum pressure variation between two outer iterations not exceeding
max(10; tol × 10⁵) Pa, and composition variation not exceeding `coupling_tol`.

### 12.3.4 Action

On networks with differing compositions, should stalling of the line search be
observed, check the log for the line `Composizioni multiple rilevate`: its
absence indicates that the composition field was not read and that the problem
is being solved with the direct scheme. The field is named `gas_comp` in the
node layer (§5.7); assigning a composition to a transit node does not alter the
physics of the problem when that composition is identical to the reference
node's, but it switches the solution scheme.

## 12.4 Absence of reference nodes

The simulation is stopped before starting (§7.2.1). No record of the node layer
satisfies the field = value condition set in *Reference field*.

**Checks.** Existence of the field; presence of the expected value (consider
the forms `1`, `1.0`, `"1"`); in Mode A, whether the node lies within the snap
radius (§6.2): a correct node further from the pipeline than the radius set is
not recognised.

## 12.5 All nodes treated as reference

The symmetric condition to the preceding one, and more insidious because it
**does not prevent convergence**: with the flag value left empty, all snapped
nodes assume imposed pressure. System (2.3) is left without unknowns,
convergence is immediate and the results are void of content.

**Symptoms.** Identical or nearly identical pressures at all nodes; flow rates
inconsistent with demands; a very low iteration count.

## 12.6 Disconnected components

A component without a reference node renders the system indeterminate. On
vector data of non-modelling origin it is the most frequent cause after that of
§12.1.

**Action.** Procedure of §4.5. Note that removal of residual components is
necessary even where they correspond to genuinely isolated portions of the
network.

## 12.7 Demands not acquired

**Symptoms.** Nearly uniform pressures; velocities of the order of 10⁻³ m/s;
`throughput_sm3h` close to zero throughout the network.

**Checks, in order.**

1. Assignment of the *Hourly node flow* field. In Mode A it resides in the
   *⚙ Advanced options* block (§6.2) and not in the main block.
2. The value reported by the preview beneath *Hour of day* (§5.2).
3. Correspondence between the separator set (§6.2) and the one actually present
   in the data: a mismatch causes a single uninterpretable value to be read and
   the fallback value to be applied.
4. Units of the values: (5.1) presumes Sm³/h.

## 12.8 Inconsistent pressures or anomalous velocities

**Predominant cause: diameter unit.** The default of the *Unit* menu is
`inches`. A field expressed in metres and interpreted as inches reduces
diameters by a factor of 39.37; through the D^2.5 dependence in (2.5) the
transport capacity is reduced by more than nine orders of magnitude, causing
pressures to collapse. The converse error produces a network that carries any
flow rate without appreciable losses.

**Secondary cause: elevations.** In Mode A elevations do not come from the node
layer (§5.4). The absence of a DEM with two-dimensional geometries nullifies
term (2.8); erroneous elevations, or elevations in units other than metres,
make it dominant.

## 12.9 Compressor stations

Omitting *Pressure OUT* entails adoption of the fallback ratio of 1.1
(§6.1.2), with near-certain divergence under load.

Where the configuration is correct but the network fails to converge, examine
the `[compressori]` lines of the log: the procedure first runs a simulation
without the compressor. Failure of the latter to converge indicates that the
problem lies with the network and not with the station.

## 12.10 Per-iteration diagnostics

For single simulations the file
`<folder>/run_NNN/output/convergence_log.txt` records the detail of each
iteration. The significant lines are those concerning the **equations with the
largest residual**, which identify the node whose balance fails to close and
the current pressure at that node.

Persistence of the same node among the critical equations indicates a local
cause — demand incompatible with the capacity of the connected pipeline, an
isolated node, an incorrect diameter — whose removal is preferable to any
modification of the numerical parameters.

Messages such as `trust region active`, `line search` and `stalled at
iteration` indicate that the step was repeatedly shortened without obtaining a
reduction of the residual: a condition typical of a discontinuity in the
residual function, attributable to flow reversals or to switching in the
compressor logic.

## 12.11 Long computation times

- Enable *CSV export only* when the layers are not required: building the
  symbology on large networks has an appreciable cost.
- Keep *Force Multiprocess* enabled for parallel runs.
- Avoid output folders subject to cloud synchronisation: writing the
  intermediate files is slowed accordingly.
- In an exploratory phase, reduce the iteration count and relax the tolerance;
  refinement (§6.3) is a concluding operation, not a preliminary one.

## 12.12 Checklist before using the results

1. Suffix of the results folder: `_OK`.
2. Presence in the log of `✓ SIMULAZIONE CONVERSA` and the final tolerance
   value.
3. Nodal balance verified within tolerance (§10.5, §11.6).
4. Pressure at the reference node equal to the assigned value plus 1.013 bar.
5. Velocities and pressures within plausible ranges for the pipeline class
   (§13.5).
