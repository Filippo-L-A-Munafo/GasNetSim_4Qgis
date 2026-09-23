# 14. Nomenclatura e glossario

## 14.1 Simboli

| Simbolo | Grandezza | Unità |
|---------|-----------|-------|
| p | Pressione assoluta | Pa, bar |
| p_ref | Pressione assegnata ai nodi di riferimento (relativa) | bar |
| p_b, T_b | Pressione e temperatura di riferimento standard | 101 325 Pa; 288,15 K |
| p_avg | Pressione media in condotta, eq. (2.7) | Pa |
| T | Temperatura del gas | K |
| Q | Portata volumetrica in condizioni standard | sm³/s, Smc/h |
| D_i | Domanda nodale (positiva in prelievo) | sm³/s |
| ṁ | Portata massica | kg/s |
| v | Velocità media del gas | m/s |
| D | Diametro interno della condotta | m |
| L | Lunghezza della condotta | m |
| ε | Rugosità assoluta della parete | m |
| f | Fattore d'attrito, eq. (2.9) | — |
| Re | Numero di Reynolds | — |
| η | Fattore di efficienza della condotta | — |
| h | Quota geodetica del nodo | m |
| H | Termine correttivo di dislivello, eq. (2.8) | Pa² |
| Z | Fattore di comprimibilità | — |
| SG | Densità relativa rispetto all'aria, eq. (2.10) | — |
| ρ | Densità in condizioni operative | kg/m³ |
| ρ_b | Densità in condizioni standard | kg/sm³ |
| M | Massa molare della miscela | g/mol |
| HHV | Potere calorifico superiore | MJ/sm³ |
| W | Indice di Wobbe, eq. (2.11) | MJ/sm³ |
| x_H₂ | Frazione molare di idrogeno | — |
| r | Rapporto di compressione, p_out/p_in | — |
| P | Potenza assorbita dalla stazione, eq. (6.1) | MW |
| F(x) | Vettore dei residui di bilancio nodale | sm³/s |
| J | Matrice jacobiana ∂F/∂x | — |
| tol | Tolleranza del criterio (2.14) | Sm³/s |
| URF | Fattore di sotto-rilassamento, eq. (2.13) | — |
| r_s | Raggio di aggancio | m |
| R | Costante universale dei gas | J/(mol·K) |

## 14.2 Glossario

**Bilancio nodale** — Equazione di conservazione della massa scritta al nodo,
eq. (2.3). Costituisce l'equazione risolutiva del modello.

**Blending** — Immissione di idrogeno, o di altro gas, in una rete progettata
per gas naturale.

**Caso non convergente (NONCONV)** — Esito in cui il criterio (2.14) non è
soddisfatto entro il numero massimo di iterazioni. Il risultato restituito è
l'ultimo iterato calcolato e non rappresenta uno stato fisicamente ammissibile.

**Collasso topologico** — Costruzione del grafo di calcolo a partire dalla
geometria vettoriale: esplosione delle polilinee, identificazione degli estremi
coincidenti, generazione di nodi e archi, calcolo delle lunghezze (§5.3.1).

**Componente sconnessa (isola)** — Sottografo non connesso al grafo principale.
Se priva di nodo di riferimento rende il sistema indeterminato.

**Condizioni standard** — Stato di riferimento per la misura dei volumi:
288,15 K e 101 325 Pa, eq. (2.1).

**Densità relativa (specific gravity)** — Rapporto fra la massa molare della
miscela e quella dell'aria, eq. (2.10). Parametro soggetto a vincolo normativo
nelle reti italiane (§13.4.2).

**Equazione generale di portata** — Relazione (2.4) fra portata e differenza
dei quadrati delle pressioni, comprensiva del termine di dislivello e delle
proprietà del gas reale.

**Fattore di comprimibilità (Z)** — Scostamento del comportamento del gas reale
da quello ideale; calcolato con GERG-2008.

**GERG-2008** — Equazione di stato di riferimento per il gas naturale,
normalizzata in ISO 20765-2.

**Indice di Wobbe** — Rapporto fra potere calorifico superiore e radice della
densità relativa, eq. (2.11). Indice di intercambiabilità fra gas combustibili.

**Line search** — Riduzione progressiva dell'ampiezza del passo di Newton fino
a ottenere una diminuzione del residuo.

**MOP** — Massima pressione di esercizio; base della classificazione per specie
(§13.4.1).

**Nodo di riferimento** — Nodo a pressione imposta; condizione al contorno del
problema. È inoltre il nodo in cui è assegnata la composizione del gas immesso.

**Nodo di transito (junction)** — Nodo privo di domanda propria, sede di
connessione fra condotte. Riceve la domanda di ripiego (§6.2).

**Portata di ripiego (placeholder)** — Domanda di valore trascurabile assegnata
ai nodi di transito per evitare righe identicamente nulle nella matrice
jacobiana.

**Raggio di aggancio** — Distanza massima entro cui un nodo del layer nodi è
associato a un estremo di condotta durante il collasso (§6.2).

**Regime stazionario** — Condizione di funzionamento a domanda costante, alla
quale si riferisce l'intera formulazione. I transitori non sono modellati.

**Residuo** — Valore assunto da F(x) per un dato stato: misura lo squilibrio
dei bilanci nodali. Il criterio di arresto è formulato sul suo massimo.

**Schema diretto / schema staggered** — Modalità di accoppiamento fra problema
idraulico e tracciamento della composizione (§2.6). Lo schema staggered è
attivato in presenza di composizioni nodali multiple.

**Snap** — Unificazione geometrica di estremi mutuamente prossimi (§4.3).

**Sotto-rilassamento (URF)** — Divisore dell'incremento di Newton, eq. (2.13).
Valori maggiori smorzano l'iterazione.

**Throughput nodale** — Portata complessiva entrante in un nodo dalle condotte
afferenti; distinta dalla domanda nodale.

**Warm start (seed)** — Inizializzazione del calcolo con le pressioni di una
soluzione conversa precedente, allo scopo di ridurre il numero di iterazioni
(§7.6).

**Velocità di erosione** — Soglia di velocità oltre la quale il flusso ad alta
velocità determina erosione della parete interna, eq. (13.1).
