# Sicilian Regional Natural Gas Demand Disaggregation Benchmark (167 Re.Mi. Offtake Stations)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.placeholder.svg)](https://doi.org/10.5281/zenodo.placeholder)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

An open-access geospatial and multi-sectoral benchmark providing hourly natural gas demand profiles for all **167 delivery stations (Cabine Re.Mi. and major industrial poles)** across the 9 administrative provinces of Sicily, Italy.

---

## 1. Context and Scientific Purpose

Accurate nodal loads are a prerequisite for realistic thermo-fluid-dynamic simulations and hydrogen blending ($H_2NG$) assessments in regional transmission networks. However, Transmission System Operators (TSOs) do not publish high-frequency SCADA telemetry at individual municipal city-gates.

Furthermore, estimating internal Sicilian gas consumption directly from border injection flows (**Mazara del Vallo** and **Gela**) leads to gross physical errors:
1. **Trans-regional transit**: Over **85.7%** of imported gas ($16,758.1\text{ MSm}^3/\text{year}$) is not consumed in Sicily, but transits northward across the Strait of Messina toward the Italian peninsula;
2. **National send-out reference**: To determine the actual consumption, the baseline reference must be the **Total Redelivered Gas in Italy** (`TOT_EROGATO`), published daily in SNAM's official physical import/export operational balance ([SNAM Flussi Fisici](https://www.snam.it/it/i-nostri-business/trasporto/flussi-fisici.html));
3. **Sectoral divergence**: Residential heating is climate-dependent, heavy petrochemical industries operate continuously H24, and gas-fired combined-cycle power plants (CCGT) follow electricity dispatch ramps and solar photovoltaic duck-curves.

This benchmark bridges this gap by coupling:
- **ISTAT municipal boundaries and centroid coordinates**;
- **SNAM official transmission network pipeline topology & contractual capacity allocations**;
- **MASE annual provincial sectoral statistics (post-crisis 2024)**;
- **TERNA measured hourly thermoelectric generation dispatch time series across the insular network**.

---

## 2. Primary Official Data Sources & Public Portals

| Institutional Source | Official Dataset / Document | Official Public Portal URL | Used Variables in Pipeline |
| :--- | :--- | :--- | :--- |
| **ISTAT** (National Institute of Statistics) | *Confini delle unità amministrative a fini statistici e dati demografici aggiornati* | [ISTAT Geodata Portal](https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/) | Official updated municipal boundaries, ISTAT codes, WGS84 / UTM 33N projected centroids, and demographic records. |
| **SNAM Rete Gas S.p.A.** | *Rete Gas e Infrastrutture di Trasporto Gas (RNT)* | [SNAM RNT Infrastructure Map (Tile 9)](https://www.snam.it/it/i-nostri-business/trasporto/informazioni-commerciali/rete-gas-e-infrastrutture-trasporto-gas.html) | High-pressure pipeline vector geometries, internal diameters ($DN300 \div DN1200$), design pressures ($DP = 75 \div 80\text{ bar}$). |
| **SNAM Rete Gas S.p.A.** | *Capacità di trasporto, Pressioni e Parametri Tariffari dei Punti di Riconsegna (AT 2024/2025, Delibera ARERA 138/2024/R/gas)* | [SNAM Transport Tariffs & Re.Mi. Hub](https://www.snam.it/it/trasporto/informazioni-commerciali/tariffa-di-trasporto/) (Doc. `Punti-di-Riconsegna_2025/Db`) | Sectoral use category ($D, I, E, A$), contractual nominal capacity $[\text{Sm}^3/\text{day}]$ for 167 stations. |
| **SNAM Rete Gas S.p.A.** | *Dati Operativi — Flussi Fisici Giornalieri RNT* | [SNAM Flussi Fisici](https://www.snam.it/it/i-nostri-business/trasporto/flussi-fisici.html) & [Dati Operativi](https://www.snam.it/it/trasporto/dati-operativi/) | **Total Redelivered Gas in Italy** $Q_{\text{IT}}(h)$ (`TOT_EROGATO`), hourly physical imports at Mazara and Gela. |
| **MASE** (Ministry of Environment & Energy Security) | *Statistiche dell'Energia — Gas Naturale Distribuito per Provincia e Settore (2024)* | [MASE Energy Statistics Portal](https://www.mase.gov.it/) | Provincial sectoral shares $f(p, s)$ for the 9 Sicilian provinces (Residential, Industrial, Thermoelectric). |
| **TERNA S.p.A.** | *Download Center — Actual Generation («Thermal») & Sicily Zonal Load* | [TERNA Transparency & Download Center](https://www.terna.it/) | Measured hourly thermal power generation and Sicilian electrical load series across the annual cycle $\rightarrow$ direct proportional CCGT profile disaggregation. |

---

## 3. Geospatial Processing & Multi-Cabin Clustering

### 3.1 Reconciliation with ISTAT Municipal Centroids
In the raw SNAM registry (`Punti-di-Riconsegna_2025_Db`), meters are identified by municipal toponyms and unique alphanumeric point codes without native spatial coordinates. A string-normalization algorithm joined each delivery entry with ISTAT municipal centroids (WGS84 / UTM 33N, EPSG:32633).

### 3.2 Clustering Multi-Cabin Municipalities into Single Hydraulic Macro-Nodes
Large urban and industrial centers feature multiple physical off-take meters (for instance, **Catania** concentrates over 15 separate metering lines; **Gela** and **Priolo** host multiple distinct industrial/chemical delivery lines).
- **Physical Consolidation**: All metering stations within the same municipality were clustered into a single geographic macro-node (167 active delivery locations in Sicily);
- **Preservation of Disaggregated Attributes**: While spatially unified, the distinct contractual capacities of each individual physical cabin were strictly preserved and categorized into sectoral registers:
  $$\text{Cap}_D = \sum \text{Cap}(\text{Tipologia} = 'D') \quad [\text{Urban Distribution}]$$
  $$\text{Cap}_I = \sum \text{Cap}(\text{Tipologia} = 'I') \quad [\text{Industrial Process}]$$
  $$\text{Cap}_E = \sum \text{Cap}(\text{Tipologia} = 'E') \quad [\text{Thermoelectric CCGT}]$$
  $$\text{Cap}_A = \sum \text{Cap}(\text{Tipologia} = 'A') \quad [\text{CNG Vehicle Refueling, aggregated into } D]$$

### 3.3 Topological Attachment to the Pipeline Graph and Quality Control
To integrate the clustered delivery stations into the mathematical graph of the transmission system:
- **Nearest Geometric and Functional Allocation**: Municipal delivery centroids were initially assigned to the mathematically nearest and physically most coherent transmission pipeline branch;
- **Expert Quality Audit on Complex Network Sections**: A systematic, segment-by-segment topological verification was conducted—particularly in areas with complex network layouts, parallel corridors (*loopings*), or multiple pressure tiers—to ensure that each delivery station was strictly connected to the appropriate pipeline branch, eliminating any spurious cross-line assignments or mathematical disconnections.


---

## 4. Mathematical Formulation of the 5-Step Disaggregation Pipeline

### Step 1: National Hourly Redelivery Ingestion
The total hourly volume redelivered across the Italian national transmission grid is extracted from SNAM's physical import/export operational balance (`TOT_EROGATO`):
$$Q_{\text{IT}}(h) = \text{TOT\_EROGATO}(h) \quad [\text{Sm}^3/\text{h}], \quad h = 0, \dots, 23$$

### Step 2: Provincial Sectoral Weighting (MASE Matrix)
From the MASE 2024 national provincial census, the regional consumption fraction for province $p$ in sector $s \in \{D (\text{Civil}), I (\text{Industrial}), E (\text{Thermoelectric})\}$ is computed:
$$f(p, s) = \frac{\text{MASE}(p, s)}{\text{MASE}_{\text{IT}}(s)}$$
To prevent artificial demand overestimations, the total national hourly volume is proportionally allocated to each sector:
$$Q_s(h) = Q_{\text{IT}}(h) \cdot \frac{T_s}{T_{\text{tot}}}$$
where $T_s / T_{\text{tot}}$ is the national annual sectoral quota ($T_{\text{Civil}} = 55.4\%$, $T_{\text{Ind}} = 22.8\%$, $T_{\text{CCGT}} = 21.8\%$).

### Step 3: Nodal Delivery Point Weighting (Contractual SNAM Capacity)
Nodal weighting within each province is strictly governed by contractual meter sizing $[\text{Sm}^3/\text{day}]$ rather than proxy demographic counts:
- **Residential & Urban Distribution ($D$)**, incorporating vehicle CNG ($A$):
  $$w(i, D) = \frac{\text{Cap}_D(i) + \text{Cap}_A(i)}{\sum_{j \in p(i)} [\text{Cap}_D(j) + \text{Cap}_A(j)]}$$
- **Industrial Offtake ($I$)**:
  $$w(i, I) = \frac{\text{Cap}_I(i)}{\sum_{j \in p(i)} \text{Cap}_I(j)}$$
- **Thermoelectric Generation ($E$)**:
  $$w(i, E) = \frac{\text{Cap}_E(i)}{\sum_{j \in p(i)} \text{Cap}_E(j)}$$

### Step 4: Sector-Specific Hourly Temporal Modulation
Daily volume is conserved ($\sum_{h=0}^{23} \text{Load}_s(i, h) = L_s(i)$) across three distinct physical laws:
1. **Civil / Residential ($D$)**: Modulated by the normalized shape of national deliveries (temperature and heating season tracking):
   $$\text{Load}_D(i, h) = L_D(i) \cdot \frac{Q_{\text{IT}}(h)}{\sum_{k=0}^{23} Q_{\text{IT}}(k)}$$
2. **Industrial ($I$)**: Constant flat baseline ($L_I / 24$) reflecting 24/7 continuous industrial shifts.
3. **Thermoelectric ($E$)**: Regulated directly in proportion to measured empirical hourly electricity dispatch generation from Terna ($P_{\text{thermo}}(h)$):
   $$p_{\text{thermo}}(h) = \frac{P_{\text{thermo}}(h)}{\sum_{k=0}^{23} P_{\text{thermo}}(k)}$$
   $$\text{Load}_E(i, h) = L_E(i) \cdot p_{\text{thermo}}(h)$$

Total hourly load for station $i$ at hour $h$:
$$\text{Load}_{\text{tot}}(i, h) = \text{Load}_D(i, h) + \text{Load}_I(i, h) + \text{Load}_E(i, h)$$

### Step 5: Regional Hydraulic Balance & Mainland Export
Boundary transmission conditions are closed through the Strait of Messina submarine export line (Node 281):
$$\text{Export}_{\text{Messina}}(h) = \left[ Q_{\text{Mazara}}(h) + Q_{\text{Gela}}(h) \right] - \sum_{i=1}^{167} \text{Load}_{\text{tot}}(i, h)$$

---

## 5. Dataset Organization

```text
Dataset_Disaggregazione_Consumi_Sicilia/
│
├── README.md                                       <- This comprehensive documentation
├── CITATION.cff                                    <- Formal academic citation descriptor
├── .zenodo.json                                    <- Zenodo Open Access archive metadata
├── LICENSE                                         <- CC-BY-4.0 International License
│
├── raw_data/                                       <- Unaltered primary institutional source files
│   ├── SNAM_Punti-di-Riconsegna_2025_Db.pdf        [SNAM: Official 91-page meter registry]
│   ├── MASE_Gas_Distribuito_province_2024.xlsx     [MASE: 2024 provincial sectoral census]
│   └── TERNA_sicilia_orario_19giorni.csv           [TERNA: Sicilian zonal load & thermal series]
│
└── processed_data/                                 <- Analysis-ready structured tables
    ├── remi_stations_sicily_capacities.csv         [167 Sicilian Re.Mi. with Cap_D, Cap_I, Cap_E]
    ├── remi_stations_with_istat_coordinates.csv    [Re.Mi. joined with ISTAT coordinates & IDs]
    └── hourly_nodal_demands_19_representative_days.csv [Final matrix: 167 stations x 19 days x 24h]
```

---

## 6. How to Cite This Dataset

If you utilize this benchmark dataset, methodology, or processed load profiles in your research, please cite:

```bibtex
@dataset{munafo_sicily_gas_demand_2026,
  author       = {Munaf{\`o}, Filippo Luca Alberto},
  title        = {A High-Resolution Spatial and Sectoral Natural Gas Demand Disaggregation Benchmark for the Sicilian Transmission Grid},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.placeholder},
  url          = {https://github.com/Filippo-L-A-Munafo/sicily-gas-demand-disaggregation-benchmark}
}
```
