# 11. Caso di verifica riproducibile

Il caso descritto in questa sezione ha due finalità: **validare
l'installazione**, confrontando i valori ottenuti con quelli riportati, e
illustrare il flusso di lavoro completo su un modello di dimensioni minime.

I valori attesi del §11.5 sono stati ottenuti eseguendo il motore di calcolo
sui file di ingresso prodotti dalla procedura qui descritta; le condizioni
della verifica sono dichiarate al §11.7.

## 11.1 Descrizione del caso

Diramazione di trasporto costituita da 4 nodi e 3 condotte. Il nodo 1 è il
punto di immissione a pressione nota; il nodo 2 è un nodo di transito dal quale
si dipartono due consegne, poste a quote diverse.

| Nodo | Quota [m] | Tipo | Domanda [Smc/h] |
|------|-----------|------|------------------|
| 1 | 10 | Riferimento (pressione imposta) | — |
| 2 | 50 | Transito | — |
| 3 | 120 | Consegna | 12 000 |
| 4 | 80 | Consegna | 5 000 |

| Condotta | A → B | D [m] | L [km] |
|----------|-------|-------|--------|
| 1 | 1 → 2 | 0,508 (20″) | 12 |
| 2 | 2 → 3 | 0,3048 (12″) | 8 |
| 3 | 2 → 4 | 0,2032 (8″) | 5 |

Condizioni al contorno: p_ref = 75 bar relativi, T = 288,15 K, gas SNAM Mazara
del Vallo (§13.3).

Il caso è impostato in **Modalità B** (§5.3.2), che conserva gli
identificativi dei nodi e le quote assegnate: in Modalità A gli identificativi
sarebbero rigenerati e le quote, in assenza di DEM e di geometria
tridimensionale, risulterebbero nulle (§5.4), con risultati diversi da quelli
qui riportati.

## 11.2 Preparazione dei dati

Si creino due file di testo con il contenuto seguente.

`verifica_condotte.csv`

```
pipe_id,node_a,node_b,length_m,diametro_m,wkt
1,1,2,12000,0.508,"LINESTRING(400000 4200000, 412000 4200000)"
2,2,3,8000,0.3048,"LINESTRING(412000 4200000, 412000 4208000)"
3,2,4,5000,0.2032,"LINESTRING(412000 4200000, 417000 4200000)"
```

`verifica_nodi.csv`

```
node_id,quota_m,is_ref,consumo,wkt
1,10,1,,"POINT(400000 4200000)"
2,50,0,,"POINT(412000 4200000)"
3,120,0,12000,"POINT(412000 4208000)"
4,80,0,5000,"POINT(417000 4200000)"
```

Il campo `consumo` contiene un valore singolo, valido per ogni ora (§5.6); il
nodo 2, privo di valore, sarà trattato come nodo di transito.

## 11.3 Caricamento in QGIS

Per ciascun file: **Layer → Aggiungi layer → Aggiungi layer da testo
delimitato**; formato CSV, separatore virgola; *Definizione geometria* =
**Geometria well-known text (WKT)**, campo geometria `wkt`; sistema di
riferimento **EPSG:25833 — ETRS89 / UTM zona 33N**, coerente con il sistema
interno del plugin (§3.5).

Il risultato è un layer lineare di 3 elementi e un layer puntuale di 4
elementi, sovrapposti.

## 11.4 Configurazione ed esecuzione

**Tab 0.** Selezionare il layer condotte ed eseguire *Analizza rete*: l'esito
atteso è `[OK] Nessun problema topologico rilevato`, con tre archi in
un'unica componente connessa.

**Tab 1 — Dati di Input.**

| Campo | Valore |
|-------|--------|
| Layer condotte | `verifica_condotte` |
| Layer nodi | `verifica_nodi` |
| DEM | `-- nessuno --` |
| Cartella output | cartella vuota a scelta |
| Ora del giorno | `0h` |
| Simula 24 ore in parallelo | non selezionato |

**Tab 1 — Modalità.** Selezionare **Rete già collassata**, quindi indicare i
medesimi due layer nel riquadro *Layer Già Collassati* e impostare le
mappature:

| Mappatura Campi Condotte | Valore |
|---------------------------|--------|
| ID pipe | `pipe_id` |
| Nodo A / B | `node_a` / `node_b` |
| Lunghezza | `length_m` |
| Diametro e unità | `diametro_m`, **metri (m)** |

| Mappatura Campi Nodi | Valore |
|-----------------------|--------|
| ID nodo | `node_id` |
| Altitudine | `quota_m` |
| Flag reference | `is_ref` = `1` |
| Flusso orario nodi | `consumo` |

**Tab 1 — ⚙ Parametri solutore.** Portare **Max iterazioni** da 50 a **200**.
Con il valore di default il caso non converge (§6.3.1) e il plugin restituisce
un risultato marcato `NONCONV`.

Gli altri parametri restano ai valori di default: pressione 75,0 bar,
temperatura 288,15 K, rugosità 1,2×10⁻⁵ m, tolleranza 0,001 Sm³/s, URF 2,0,
gas SNAM Mazara del Vallo.

**Esecuzione.** Comando **▶ Avvia Simulazione**. Il log riporta la validazione
dei file di ingresso, i parametri adottati e l'esito
`✓ SIMULAZIONE CONVERSA in 92 iterazioni!`. I risultati sono scritti in
`<cartella output>/run_001/h00_OK/` e i layer `R-N-verifica #1` e
`R-P-verifica #1` sono aggiunti al progetto.

## 11.5 Valori attesi

Pressioni assolute; il valore al nodo di riferimento è pari a 75 + 1,013 bar
secondo la (2.2).

| Nodo | h [m] | p [bar] | Z [–] | ρ [kg/m³] |
|------|-------|---------|-------|------------|
| 1 | 10 | 76,013 | 0,8176 | 71,08 |
| 2 | 50 | 75,726 | 0,8182 | 70,76 |
| 3 | 120 | 75,202 | 0,8193 | 70,17 |
| 4 | 80 | 75,482 | 0,8187 | 70,48 |

| Condotta | Q [Smc/h] | v [m/s] | p media [bar] |
|----------|-----------|---------|----------------|
| 1 (1→2) | 17 000,3 | 0,311 | 75,870 |
| 2 (2→3) | 12 000,5 | 0,613 | 75,464 |
| 3 (2→4) | 5 003,2 | 0,574 | 75,604 |

Grandezze di composizione, costanti su tutta la rete: SG = 0,6323;
M = 18,32 g/mol; ρ_b = 0,8172 kg/sm³; HHV = 42,12 MJ/sm³; W = 52,98 MJ/sm³.

Il numero di iterazioni può variare di poche unità in funzione della versione
delle librerie numeriche; le pressioni devono coincidere entro la terza cifra
decimale.

## 11.6 Verifiche sul risultato

**Bilancio di massa.** Al nodo 2 deve valere la (2.3):

    Q₁ − Q₂ − Q₃ = 17 000,3 − 12 000,5 − 5 003,2 = −3,4 Smc/h

Lo squilibrio residuo non è nullo ed è dell'ordine della tolleranza: con
tol = 0,001 Sm³/s il criterio (2.14) ammette fino a 3,6 Smc/h di squilibrio per
nodo. Il risultato è quindi consistente con il criterio di arresto adottato.
Riducendo la tolleranza — o attivando *Affina precisione* (§6.3) — lo
squilibrio si riduce proporzionalmente.

**Effetto del dislivello.** Il nodo 3 presenta pressione inferiore al nodo 4
(75,202 contro 75,482 bar) pur essendo alimentato da una condotta di diametro
maggiore: la differenza è attribuibile al termine geodetico (2.8), essendo il
nodo 3 posto 40 m più in alto. Ponendo a zero tutte le quote e ripetendo
l'esecuzione, la gerarchia delle pressioni si inverte: è la verifica più
diretta della rilevanza del §5.4.

**Condizione al contorno.** La pressione al nodo 1 deve risultare pari a
76,013 bar; un valore pari a 75,000 indicherebbe un'interpretazione errata
della (2.2).

## 11.7 Condizioni della verifica

I valori del §11.5 sono stati ottenuti eseguendo il motore GasNetSim 0.2.2
(ramo `improvement/modular-simulation-architecture`, commit `6079ec1`) sui file `sf_nodes.csv` e
`sf_pipelines.csv` generati secondo le regole del §5.8 per il caso descritto,
con i parametri del §11.4.

Limitazioni della verifica, dichiarate per completezza:

1. l'esecuzione è avvenuta al di fuori dell'ambiente QGIS; le fasi che
   dipendono dalle librerie QGIS — costruzione del grafo (Modalità A), aggancio
   dei nodi, creazione dei layer — non sono state eseguite. La Modalità B
   adottata in questo caso di verifica riduce tale dipendenza alla sola
   scrittura dei file di ingresso;
2. le funzioni compilate con `numba` sono state sostituite dalle equivalenti
   implementazioni in Python puro: i risultati numerici sono i medesimi, i
   tempi di calcolo non sono rappresentativi;
3. i tempi di esecuzione non sono pertanto riportati fra i valori attesi.

Le medesime prove sono state condotte sulle due reti di esempio distribuite con
il plugin (`sample_data/toy_network_h2`, 10 nodi, e
`sample_data/Sicily_transmission_network`, 340 nodi): in entrambi i casi il
valore di default di 50 iterazioni non è risultato sufficiente (§6.3.1, §12.1).
