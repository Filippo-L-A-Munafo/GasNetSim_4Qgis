# 2. Model formulation

This section reports the equations actually implemented in the solver, in the
form in which they are coded, and defines the physical meaning of the
parameters exposed by the interface. The complete notation is given in §14.

## 2.1 Network representation

The network is represented as a directed graph G = (N, P), where N is the set
of nodes and P the set of pipelines. Each pipeline p ∈ P connects an inlet node
i and an outlet node j; the orientation is a convention assigned when the model
is built and carries no physical meaning: the actual flow direction is a result
of the computation (§10.2).

Nodes are of two kinds:

- **reference nodes** (node_type = `reference`): fixed-pressure nodes, which
  constitute the boundary conditions of the problem and at which the
  composition of the injected gas is assigned;
- **demand or junction nodes**: nodes at which a volumetric flow rate at
  standard conditions is prescribed, positive if withdrawn, negative if
  injected.

## 2.2 Standard conditions and pressure conventions

Volumetric flow rates are referred to standard conditions

    T_b = 288.15 K        p_b = 1 atm = 101 325 Pa                        (2.1)

consistent with UNI EN ISO 13443. The corresponding unit is the standard cubic
metre (Sm³, equivalently sm³).

**Pressure convention.** The value assigned to reference nodes through the
*Reference pressure* parameter is interpreted as **gauge** pressure; conversion
to absolute pressure takes place when the model is built:

    p_abs = p_gauge + p_atm,     p_atm = 101 325 Pa                       (2.2)

All pressures returned by the computation (§9) are **absolute**. An assigned
value of 75 bar therefore corresponds to 76.013 bar in the results.

## 2.3 Nodal continuity equation

For every non-reference node i, conservation of mass requires

    Σ_(p ∈ P_i) s_(i,p) · Q_p − D_i = 0                                   (2.3)

where Q_p is the volumetric flow rate of pipeline p at standard conditions,
s_(i,p) = +1 if the pipeline enters the node and −1 if it leaves it, and D_i is
the nodal demand (positive for withdrawal). System (2.3), written for all
non-reference nodes, constitutes the non-linear system solved; the unknowns are
the nodal pressures.

## 2.4 Pipeline flow equation

Flow is computed with the general gas flow equation:

    Q = sgn(Δ) · C_p · √( |p₁² − p₂² − H| / (Z · SG) )                    (2.4)

with Δ = p₁² − p₂² − H. The term C_p collects the physical characteristics of
the pipeline:

    C_p = K · (T_b / p_b) · D^2.5 · √( 1 / (L · T_avg · f) ) · η          (2.5)

    K = π · √( R / (16 · M_air) ),    M_air = 28.97 g/mol                 (2.6)

where D is the internal diameter, L the length, T_avg the average temperature,
f the friction factor, η the pipeline efficiency factor and R the universal gas
constant.

The average pressure in the pipeline, used to evaluate gas properties, is
computed in the form customary for gas flow:

    p_avg = (2/3) · [ (p₁ + p₂) − (p₁ · p₂)/(p₁ + p₂) ]                   (2.7)

which, because of compressibility, differs from the arithmetic mean.

### 2.4.1 Elevation correction

The term H accounts for the difference in elevation between the two ends:

    H = 0.06835 · SG · (h₂ − h₁) · p_avg² / (Z · T_avg)                   (2.8)

with h₁, h₂ the elevations of the inlet and outlet nodes. The term vanishes for
horizontal pipelines. For gas at 70 bar the density is of the order of
70 kg/m³: over elevation differences of a few hundred metres the contribution
of (2.8) is comparable with that of friction, and in mountainous networks it
may dominate. It follows that the accuracy of nodal elevations matters as much
as that of diameters (§5.4, §6.2).

### 2.4.2 Friction factor

The friction factor is computed with the explicit correlation of **Chen
(1979)**, valid over the whole turbulent range and in the transition:

    1/√f = −2 · log₁₀[ ε/(3.7065·D)
             − (5.0452/Re) · log₁₀( (ε/D)^1.1098 / 2.8257
             + (7.149/Re)^0.8981 ) ]                                      (2.9)

where ε is the absolute wall roughness (*Pipe roughness* parameter, §6.2) and
Re the Reynolds number, evaluated with the dynamic viscosity of the mixture
computed by the Lucas and Herning-Zipperer methods.

The choice of correlation is fixed by the plugin (`friction_method = chen` in
the input files) and cannot be changed from the interface.

## 2.5 Equation of state and gas properties

The compressibility factor Z, density, standard density, molar mass and heat
capacities of the mixture are computed with the **GERG-2008** equation of state
(ISO 20765-2), as functions of pressure, temperature and molar composition, and
are updated node by node at every iteration.

For an ideal gas Z = 1; under conditions typical of transmission networks
(70–76 bar, 288 K) Z ≈ 0.80–0.88 (§9.3). Neglecting this departure would
introduce errors of the order of 15–20 % in density and, consequently, in the
computed velocities.

Specific gravity is defined as

    SG = M_gas / M_air                                                    (2.10)

and the Wobbe index as

    W = HHV / √SG                                                         (2.11)

with HHV the higher heating value referred to standard conditions.

## 2.6 Composition tracking

Where gases of different composition are injected, the composition at each node
is determined by **simple mixing** of the incoming flows weighted by their
respective compositions. Since composition modifies the properties appearing in
(2.4), the hydraulic and composition problems are coupled and are solved with a
**staggered** scheme: at each outer iteration the pressure field is solved with
frozen composition, the composition is then updated, and the process is
repeated until both variations fall below their respective thresholds.

The staggered scheme is enabled automatically when at least one non-reference
node carries its own composition (§5.7); otherwise the solver adopts a direct
scheme. The difference between the two schemes is not merely formal: it affects
the robustness of convergence (§12.3).

## 2.7 Numerical solution

System (2.3), non-linear because of the dependence of Q on pressures expressed
by (2.4), is solved with the **Newton-Raphson** method. Denoting by F(x) the
vector of nodal balance residuals and by J(x) = ∂F/∂x the Jacobian matrix, at
each iteration the linear system

    J(x⁽ᵏ⁾) · Δx = F(x⁽ᵏ⁾)                                               (2.12)

is solved and the state is updated as

    x⁽ᵏ⁺¹⁾ = x⁽ᵏ⁾ + Δx / URF                                             (2.13)

**The URF appears in the denominator.** A large value reduces the step length
and therefore *damps* the iteration, increasing stability at the expense of
speed; a value below unity amplifies the Newton step. The value set by the user
acts as a lower bound (the most aggressive step allowed): the solver raises it
automatically, up to a maximum of max(4·URF, 8), when the residual fails to
decrease satisfactorily, and returns it towards the assigned value when
convergence proceeds regularly.

At each iteration the step length is further limited by a *line search*
(successive halving until the residual decreases) and by a trust-region
constraint on the components of Δx.

### 2.7.1 Convergence criterion

Convergence is declared when

    max |F(x)| ≤ tol                                                      (2.14)

that is, when the largest flow imbalance among all nodes falls below the
prescribed tolerance. **The tolerance is therefore a flow rate**, expressed in
Sm³/s: the default value of 0.001 Sm³/s corresponds to a maximum admissible
imbalance of 3.6 Sm³/h per node. In the verification case of §11 the residual
imbalance is precisely of this order (§11.6), which explains why the returned
flow rates do not close the balance to arbitrary precision.

If (2.14) is not satisfied within the prescribed maximum number of iterations,
the solver returns the last computed iterate, flagged as a **non-converged
solution**: an intermediate state that does not satisfy the nodal balances and
has no physical meaning (§7.5, §12).
