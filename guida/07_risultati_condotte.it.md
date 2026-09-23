# 10. Grandezze calcolate sulle condotte e sui compressori

## 10.1 Grandezze sulle condotte

Contenute nel layer `R-P-<nome> #N` e nel file `results_pipes.csv`.

| Campo | Simbolo | Unità | Definizione |
|-------|---------|-------|-------------|
| `flow_sm3h` | Q | Smc/h | Portata volumetrica in condizioni standard, **con segno** (§10.2). Ottenuta dalla (2.4). |
| `flow_abs_sm3h` | \|Q\| | Smc/h | Modulo della portata. Campo di default per la colorazione e per la modulazione dello spessore della linea. |
| `velocity_m_s` | v | m/s | Velocità media del gas nelle condizioni operative, sempre positiva (§10.3). |
| `avg_pressure_bar` | — | bar (assoluti) | Media aritmetica delle pressioni ai due estremi. Si noti che non coincide con la pressione media (2.7) impiegata internamente per la valutazione delle proprietà. |
| `sp_gravity` | SG | — | Densità relativa della miscela nella condotta. |
| `z_factor` | Z | — | Fattore di comprimibilità medio. |
| `density_kg_m3` | ρ | kg/m³ | Densità media nelle condizioni operative del tratto. |

## 10.2 Convenzione di segno e verso del flusso

L'orientamento A → B è assegnato in fase di costruzione del modello (§2.1) e
non presuppone alcuna conoscenza del funzionamento della rete. Il verso
effettivo discende dalla soluzione:

    Q > 0  →  flusso da A verso B
    Q < 0  →  flusso da B verso A

L'inversione di segno di una condotta fra due scenari costituisce un risultato
di interesse: individua i tratti alimentati da direzioni diverse al variare
delle condizioni di esercizio, informazione rilevante nella valutazione di
nuovi punti di immissione.

La rappresentazione con frecce (§8.1) segue il segno di `flow_sm3h`.

## 10.3 Velocità

La velocità non è ottenibile dividendo la portata standard per la sezione: la
portata è riferita alle condizioni (2.1), mentre il gas transita nelle
condizioni operative. La conversione richiede la densità locale, funzione di
p, T e composizione attraverso l'equazione di stato (§2.5).

Alle pressioni di trasporto, valori dell'ordine di 0,3–10 m/s corrispondono a
portate di decine di migliaia di Smc/h. Il confronto con i limiti di erosione
è trattato al §13.5; si richiama che la velocità ammissibile **decresce** al
crescere della pressione, essendo il gas più denso.

Velocità dell'ordine di 10⁻³ m/s diffuse sull'intera rete indicano di norma
domande non acquisite (§12.7).

## 10.4 Grandezze sulle stazioni di compressione

Contenute in `results_compressors.csv`, prodotto quando la rete comprende
stazioni di compressione (§6.1).

| Campo | Unità | Definizione |
|-------|-------|-------------|
| `compressor_index` | — | Identificativo della stazione. |
| `inlet_node` / `outlet_node` | — | Nodi di aspirazione e di mandata; il secondo è generato dallo sdoppiamento del nodo marcato (§6.1.1). |
| `inlet_pressure_bar` / `outlet_pressure_bar` | bar (assoluti) | Pressioni a convergenza. |
| `compression_ratio` | — | Rapporto effettivo r = p_out / p_in. Un valore prossimo all'unità indica che la stazione non sta comprimendo. |
| `flow_sm3h` | Smc/h | Portata elaborata. |
| `mass_flow_kg_s` | kg/s | Portata massica, ṁ = ρ_b · Q. |
| `power_MW` | MW | Potenza isentropica assorbita, eq. (6.1). Nulla per r ≤ 1. |
| `energy_MWh` | MWh | Energia corrispondente all'ora simulata. |

La potenza assorbita è calcolata **esclusivamente a convergenza raggiunta**:
in una cartella `_NONCONV` i valori relativi ai compressori sono privi di
significato.

## 10.5 Verifiche di coerenza

**Bilancio ai nodi.** In un nodo di derivazione la portata della condotta di
monte deve eguagliare la somma delle portate di valle, a meno della domanda
nodale e dello squilibrio residuo ammesso dalla tolleranza (2.14). Lo
scostamento atteso è dell'ordine di tol × 3600 Smc/h: con il valore di default
esso vale 3,6 Smc/h, del tutto trascurabile su portate di decine di migliaia di
Smc/h ma non nullo. Il §11.6 riporta un esempio quantitativo di tale verifica.

**Continuità delle proprietà.** In assenza di immissioni multiple, `sp_gravity`
e le altre grandezze di composizione devono risultare costanti su tutte le
condotte. Variazioni indicano la presenza di composizioni nodali non
intenzionali (§5.7).

**Congruenza con le perdite di carico.** A parità di portata, condotte di
diametro maggiore devono presentare cadute di pressione sensibilmente minori,
essendo C_p ∝ D^2,5 nella (2.5). Andamenti contrari segnalano di norma errori
nell'unità del diametro (§12.8).
