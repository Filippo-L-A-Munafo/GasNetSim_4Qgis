# 9. Grandezze calcolate ai nodi

## 9.1 Elenco delle grandezze

Contenute nel layer `R-N-<nome> #N` e nel file `results_nodes.csv`, in funzione
delle selezioni operate al §8.2.

| Campo | Simbolo | Unità | Definizione |
|-------|---------|-------|-------------|
| `pressure_bar` | p | bar (assoluti) | Pressione nodale, incognita primaria del sistema (2.3). Per la relazione con il valore assegnato si veda la (2.2). |
| `temperature_k` | T | K | Temperatura del gas al nodo; uniforme e pari al valore assegnato (ipotesi isoterma). |
| `sp_gravity` | SG | — | Densità relativa rispetto all'aria in condizioni standard, eq. (2.10). |
| `z_factor` | Z | — | Fattore di comprimibilità da equazione GERG-2008 (§2.5). |
| `hhv_mj_sm3` | HHV | MJ/sm³ | Potere calorifico superiore riferito alle condizioni standard (2.1). |
| `wobbe_mj_sm3` | W | MJ/sm³ | Indice di Wobbe, eq. (2.11). |
| `density_kg_m3` | ρ | kg/m³ | Densità nelle condizioni operative locali (p, T). |
| `std_density_kg_sm3` | ρ_b | kg/sm³ | Densità in condizioni standard; dipende dalla sola composizione. Fattore di conversione fra portata volumetrica standard e portata massica. |
| `molar_mass` | M | g/mol | Massa molare media della miscela. |
| `h2_pct` | x_H₂ | % | Frazione molare di idrogeno nel nodo. |
| `gas_comp` | — | testo | Composizione molare locale, nella forma `methane=0.86909;ethane=0.08661;…`, limitata ai componenti con frazione superiore a 1×10⁻⁴. |
| `throughput_sm3h` | — | Smc/h | Portata complessiva entrante nel nodo dalle condotte afferenti. Non coincide con la domanda nodale: rappresenta il transito. |
| `volumetric_flow_sm3s` | D | sm³/s | Domanda nodale con segno (§5.6). Presente nel solo layer QGIS. |
| `energy_flow_mw` | — | MW | Domanda nodale espressa come potenza termica. Presente nel solo layer QGIS. |
| `node_type` | — | testo | `reference` per i nodi a pressione imposta. Presente nel solo layer QGIS. |

## 9.2 Grandezze di composizione

In presenza di una sola composizione, `sp_gravity`, `hhv_mj_sm3`,
`wobbe_mj_sm3`, `molar_mass`, `std_density_kg_sm3` e `h2_pct` risultano
uniformi sull'intera rete, mentre `z_factor` e `density_kg_m3` variano con la
pressione locale.

In presenza di immissioni a composizione differente (§5.7) tutte le grandezze
di composizione variano da nodo a nodo secondo il campo di miscelazione
risolto con lo schema del §2.6. La distribuzione di `h2_pct` descrive in tal
caso la diluizione dell'idrogeno a partire dai punti di immissione e
costituisce il risultato di interesse negli studi di blending parziale.

## 9.3 Ordini di grandezza attesi

Valori calcolati per il gas di default (SNAM Mazara del Vallo) e per la
medesima miscela addizionata di idrogeno al 13,92 % molare, a 76 bar e
288,15 K.

| Grandezza | Mazara | Mazara + 13,92 % H₂ | Variazione |
|-----------|--------|----------------------|------------|
| SG | 0,6323 | 0,5539 | −12,4 % |
| M | 18,32 g/mol | 16,05 g/mol | −12,4 % |
| Z | 0,818 | 0,879 | +7,5 % |
| ρ (76 bar) | ≈ 71 kg/m³ | ≈ 58 kg/m³ | −18 % |
| ρ_b | 0,8172 kg/sm³ | 0,7160 kg/sm³ | −12,4 % |
| HHV | 42,12 MJ/sm³ | 38,04 MJ/sm³ | −9,7 % |
| W | 52,98 MJ/sm³ | 51,11 MJ/sm³ | −3,5 % |

I valori sono stati ottenuti con il motore di calcolo del plugin nelle
condizioni indicate (§11.7).

## 9.4 Criteri di lettura

**Pressione minima.** La verifica di adeguatezza si conduce sull'ordinamento
crescente di `pressure_bar` o sulla rappresentazione tematica del medesimo
campo: i nodi a pressione minore individuano le sezioni critiche della rete.

**Uniformità anomala.** Un campo di pressione pressoché uniforme, associato a
valori di `throughput_sm3h` prossimi a zero, indica che le domande non sono
state acquisite (§12.7) e non che la rete sia sovradimensionata.

**Qualità del gas.** HHV e indice di Wobbe vanno esaminati congiuntamente:
l'incremento della frazione di idrogeno riduce entrambi, ma in misura diversa
(§9.3), e il vincolo normativo determinante per le reti italiane riguarda la
densità relativa (§13.4). La riduzione dell'indice di Wobbe, contenuta rispetto
a quella del potere calorifico, è la grandezza che governa la compatibilità con
le apparecchiature di utenza.

**Coerenza con la condizione al contorno.** La pressione del nodo di
riferimento deve risultare pari al valore assegnato aumentato di 1,013 bar
(2.2). Uno scostamento indica che il nodo di riferimento non è quello atteso,
o che ne esistono più di uno.
