# Riferimenti tecnici e normativa

Questa sezione raccoglie i valori di riferimento, le formule e le
classificazioni normative usate come base per i parametri di default del
plugin. È pensata come consultazione rapida, non richiede di essere letta
tutta d'un fiato.

## Classificazione delle condotte per "specie" (D.M. 17/04/2008)

Classificazione valida per le reti di **trasporto** (trasmissione) di gas
naturale in Italia, in base alla Massima Pressione Operativa (MOP):

| Specie | MOP (Pressione Max Esercizio) | Tipo di rete |
|--------|-------------------------------|--------------|
| **1a** | > 24 bar (2,4 MPa) | Rete Nazionale di Trasporto (RNT) |
| **2a** | 12 bar < MOP ≤ 24 bar (1,2–2,4 MPa) | Rete Regionale di Trasporto (RRT) |
| **3a** | 5 bar < MOP ≤ 12 bar (0,5–1,2 MPa) | Derivazioni d'utenza in alta pressione |
| **4a** | 1,5 bar < MOP ≤ 5 bar (0,15–0,5 MPa) | Reti di distribuzione locale |

> Le simulazioni tipicamente condotte con questo plugin riguardano reti di
> **1a e 2a specie** (RNT/RRT), con pressioni nell'ordine di 24–70 bar.

## Velocità massima in condotta — formula di erosione (API RP 14E)

La velocità di erosione stima la soglia oltre la quale il flusso di gas ad
alta velocità inizia a danneggiare (per erosione) le pareti interne della
condotta, in particolare in presenza di particelle solide o liquide
trascinate dal flusso:

**Ve = C / √ρgas**

dove:

- **Ve** — velocità di erosione [m/s]
- **ρgas** — densità del gas nelle condizioni operative [kg/m³]
- **C = 100** — costante empirica per servizio continuo, gas secco (unità SI)

Nota il comportamento: più il gas è denso (alte pressioni), **più bassa** è
la velocità di erosione ammissibile — l'opposto di quanto si potrebbe
intuire. Questo perché a parità di velocità, un gas più denso trasporta più
quantità di moto e quindi più energia d'urto contro le pareti.

### Stime indicative per metano (CH₄) a 15 °C

| Specie | MOP tipico | ρ CH₄ stimata | Ve (erosione) | Limite pratico |
|--------|-----------|----------------|-----------------|----------------|
| 1a | 60–70 bar | ~44–55 kg/m³ | ~10–13 m/s | ~10–15 m/s |
| 1a | 24–40 bar | ~17–30 kg/m³ | ~13–18 m/s | ~15 m/s |
| 2a | 12–24 bar | ~8–17 kg/m³ | ~18–24 m/s | ~15–20 m/s |
| 3a | 5–12 bar | ~3,5–8 kg/m³ | ~24–35 m/s | rumore ~15 m/s |
| 4a | 1,5–5 bar | ~1–3,5 kg/m³ | > 35 m/s | rumore ~10 m/s |

> Per reti di trasmissione RNT Sicilia (60–70 bar), il limite pratico di
> velocità è tipicamente **10–14 m/s**. I valori esatti derivati dagli
> standard SNAM/Terna dovrebbero essere verificati caso per caso.

## Composizioni gas supportate

Componenti riconosciuti dal motore di calcolo (chiavi del dizionario Python
usato nel campo "Composizione"):

| Chiave | Componente |
|--------|------------|
| `methane` | Metano (CH₄) |
| `ethane` | Etano (C₂H₆) |
| `propane` | Propano (C₃H₈) |
| `butane` | Butano (C₄H₁₀) |
| `nitrogen` | Azoto (N₂) |
| `carbon_dioxide` | Anidride carbonica (CO₂) |
| `hydrogen` | Idrogeno (H₂) |

### Preset disponibili nel plugin

```
# Gas naturale puro
{'methane': 1.0}

# Gas naturale tipico (rete italiana)
{'methane': 0.94, 'ethane': 0.04, 'propane': 0.01, 'nitrogen': 0.01}

# Mix idrogeno 10%
{'methane': 0.90, 'hydrogen': 0.10}

# Mix idrogeno 20%
{'methane': 0.80, 'hydrogen': 0.20}

# Mix idrogeno 50%
{'methane': 0.50, 'hydrogen': 0.50}

# Idrogeno puro
{'hydrogen': 1.0}
```

## Parametri del solutore — valori di riferimento

| Parametro | Default plugin | Note |
|-----------|----------------|------|
| Max iterazioni | 50 | Aumentare a 100–200 per reti complesse |
| Tolleranza | 1,0 | Nelle unità interne del solutore |
| URF | 2,0 | Under-relaxation factor |
| Pressione reference | 70 bar | Tipica per RNT Sicilia |
| Temperatura reference | 300 K (27 °C) | |
| Rugosità condotte | 5×10⁻⁵ m | Acciaio. PE/HDPE: 7×10⁻⁶ m; ghisa: 2,6×10⁻⁴ m |

## Unità di diametro supportate

| Codice | Fattore di conversione a metri |
|--------|----------------------------------|
| `m` | × 1 |
| `in` | × 0,0254 |
| `cm` | × 0,01 |

## Reti di riferimento già testate con il plugin

| Rete | Nodi | Condotte | Pressione | Esito |
|------|------|----------|-----------|-------|
| RRT Trapani | 7 | 6 | 70 bar | Convergenza in 4 iterazioni, ~7,7 s |
| RNT Sicilia | — | — | 24–25 bar | Convergenza OK (pressioni 24,08–25,33 bar) |
