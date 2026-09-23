# 13. Riferimenti tecnici e normativi

## 13.1 Valori di default

| Parametro | Simbolo | Valore | Unità | § |
|-----------|---------|--------|-------|---|
| Pressione di riferimento | p_ref | 75,0 | bar relativi | 6.2 |
| Temperatura | T | 288,15 | K | 6.2 |
| Rugosità assoluta | ε | 1,2×10⁻⁵ | m | 6.2 |
| Flusso placeholder | D_min | 1×10⁻⁴ | sm³/s | 6.2 |
| Flusso minimo export | — | 1×10⁻⁶ | sm³/s | 6.2 |
| Raggio di aggancio | r_s | 50,0 | m | 6.2 |
| Decimali layer risultato | — | 4 | — | 6.2 |
| Numero massimo di iterazioni | — | 50 | — | 6.3 |
| Tolleranza | tol | 1×10⁻³ | Sm³/s | 6.3 |
| Fattore di sotto-rilassamento | URF | 2,0 | — | 6.3 |
| Composizione | — | SNAM Mazara del Vallo | — | 6.4 |
| Correlazione d'attrito | — | Chen (1979) | — | 2.4.2 |
| Equazione di stato | — | GERG-2008 | — | 2.5 |
| Condizioni standard | T_b, p_b | 288,15 K; 101 325 Pa | — | 2.2 |

### 13.1.1 Scala di auto-calibrazione

| Numero di nodi | tol [Sm³/s] | URF [–] |
|----------------|-------------|---------|
| < 100 | 0,1 | 1,5 |
| < 500 | 1,0 | 2,0 |
| < 2000 | 5,0 | 2,5 |
| ≥ 2000 | 10,0 | 3,0 |

In caso di mancata convergenza la scala è percorsa verso i valori più
rilassati.

## 13.2 Rugosità assoluta per materiale

| Materiale | ε [m] |
|-----------|-------|
| Acciaio con rivestimento interno (trasporto) | 1,2×10⁻⁵ |
| Acciaio non rivestito | 5×10⁻⁵ |
| Polietilene (PE/HDPE) | 7×10⁻⁶ |
| Ghisa | 2,6×10⁻⁴ |

### 13.2.1 Conversione delle unità di diametro

| Codice | Fattore verso il metro |
|--------|-------------------------|
| `m` | 1 |
| `in` | 0,0254 |
| `cm` | 0,01 |

## 13.3 Composizioni di riferimento

Frazioni molari. Le due composizioni SNAM corrispondono ai principali punti di
ingresso del sistema siciliano.

| Componente | Mazara del Vallo (algerino) | Gela (libico) |
|------------|------------------------------|----------------|
| methane | 0,86909 | 0,86645 |
| ethane | 0,08661 | 0,05246 |
| propane | 0,01163 | 0,02022 |
| isobutane | 0,00072 | 0,00317 |
| butane | 0,00112 | 0,00478 |
| isopentane | 0,00019 | 0,00071 |
| pentane | 0,00019 | 0,00026 |
| hexane | 0,00014 | 0,00060 |
| nitrogen | 0,01334 | 0,04455 |
| carbon dioxide | 0,01672 | 0,00602 |
| helium | 0,00025 | 0,00078 |

Ulteriori preset: `{'methane': 1.0}`; `{'methane': 0.94, 'ethane': 0.04,
'propane': 0.01, 'nitrogen': 0.01}`; `{'hydrogen': 1.0}`.

Parametri di default delle stazioni di compressione: rapporto di compressione
1,1; rendimento 0,85; processo isentropico.

## 13.4 Classificazione delle condotte e qualità del gas

### 13.4.1 Specie (D.M. 17/04/2008)

| Specie | MOP | Tipologia di rete |
|--------|-----|--------------------|
| 1ª | > 24 bar | Rete nazionale di trasporto |
| 2ª | 12 < MOP ≤ 24 bar | Rete regionale di trasporto |
| 3ª | 5 < MOP ≤ 12 bar | Derivazioni di utenza in alta pressione |
| 4ª | 1,5 < MOP ≤ 5 bar | Distribuzione locale |

### 13.4.2 Vincolo di densità relativa

La normativa italiana sulla qualità del gas immesso nelle reti di trasporto
fissa un limite inferiore alla densità relativa, d ≥ 0,555. Poiché l'idrogeno
riduce sensibilmente SG (§9.3), tale vincolo — e non il potere calorifico —
determina di norma la frazione massima miscelabile. Per il gas algerino di
Mazara del Vallo il limite è raggiunto in corrispondenza di una frazione molare
di idrogeno pari a circa **13,9 %**, valore adottato nei dati di esempio
distribuiti con il plugin.

> I riferimenti normativi riportati hanno valore orientativo e vanno verificati
> sulla fonte vigente prima di qualsiasi utilizzo in sede formale.

## 13.5 Velocità limite per erosione

Criterio API RP 14E:

    v_e = C / √ρ                                                         (13.1)

con v_e velocità di erosione [m/s], ρ densità del gas nelle condizioni
operative [kg/m³], C = 100 in unità SI per servizio continuo con gas secco.

La (13.1) implica che la velocità ammissibile **decresca** al crescere della
densità, e quindi della pressione di esercizio.

| Specie | MOP | ρ stimata [kg/m³] | v_e [m/s] | Limite pratico [m/s] |
|--------|-----|--------------------|-----------|-----------------------|
| 1ª | 60–70 bar | 44–55 | 10–13 | 10–15 |
| 1ª | 24–40 bar | 17–30 | 13–18 | ≈ 15 |
| 2ª | 12–24 bar | 8–17 | 18–24 | 15–20 |
| 3ª | 5–12 bar | 3,5–8 | 24–35 | ≈ 15 (rumore) |
| 4ª | 1,5–5 bar | 1–3,5 | > 35 | ≈ 10 (rumore) |

## 13.6 Formato dei file

Separatore di campo `;` per tutti i file prodotti e letti dal solutore.

**`sf_nodes.csv`** — `node_index`, `pressure_pa`, `flow_MW`, `flow_sm3_per_s`,
`altitude_m`, `temperature_k`, `gas_composition`, `node_type`, `latitude`,
`longitude`, `flow_type`.

**`sf_pipelines.csv`** — `pipeline_index`, `inlet_index`, `outlet_index`,
`diameter_m`, `length_m`, `friction_method`, `roughness_m`.

**`sf_compressors.csv`** — `compressor_index`, `inlet`, `outlet`,
`compression_ratio`, `efficiency`, `thermodynamic_process`, `control_mode`,
`p_out_target`.

**`results_nodes.csv`**, **`results_pipes.csv`**, **`results_compressors.csv`**
— campi descritti ai §9 e §10.

## 13.7 Riferimenti bibliografici e normativi

1. Chen N.H. (1979). *An Explicit Equation for Friction Factor in Pipe*.
   Industrial & Engineering Chemistry Fundamentals, 18(3), 296–297.
2. ISO 20765-2:2015. *Natural gas — Calculation of thermodynamic properties —
   Part 2: Single-phase properties (gas, liquid, and dense fluid) for extended
   ranges of application* (equazione di stato GERG-2008).
3. UNI EN ISO 13443. *Gas naturale — Condizioni di riferimento standard*.
4. API RP 14E. *Recommended Practice for Design and Installation of Offshore
   Production Platform Piping Systems*.
5. EN 16726. *Gas infrastructure — Quality of gas — Group H*.
6. D.M. 17 aprile 2008. *Regola tecnica per la progettazione, costruzione,
   collaudo, esercizio e sorveglianza delle opere e degli impianti di trasporto
   di gas naturale con densità non superiore a 0,8*.
7. Lu Y. et al. *GasNetSim* — Forschungszentrum Jülich, ICE-1: Energy Systems
   Engineering. Licenza MPL-2.0.
   https://jugit.fz-juelich.de/iek-10/public/simulation/gasnetsim
