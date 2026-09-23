# 6. Tab 1 — Parametri fisici e numerici

Tutti i parametri di questa sezione risiedono nei blocchi richiudibili del
Tab 1. Per ciascuno si riportano simbolo, unità, valore di default e intervallo
ammesso.

## 6.1 ⚙ Compressori

Blocco attivabile per le reti dotate di stazioni di compressione.

| Campo | Descrizione |
|-------|-------------|
| **Campo e Valore** | Campo del layer nodi e valore che identificano i nodi compressore. |
| **Pressione OUT** [bar] | Accetta indifferentemente il nome di un campo del layer nodi contenente la pressione di mandata, oppure un valore numerico costante (per esempio `70.0`). |

### 6.1.1 Formulazione

Il nodo marcato come compressore viene sdoppiato in un nodo di aspirazione e un
nodo di mandata, connessi dalla stazione. La pressione di mandata è imposta
come equazione di vincolo aggiuntiva del sistema (2.3); la portata elaborata è
determinata dalla soluzione.

Poiché il vincolo di pressione può richiedere alla rete di monte portate molto
superiori a quelle di regime naturale, la procedura prevede:

1. una simulazione **baseline** senza compressore, con tolleranza rilassata e
   numero di iterazioni limitato, impiegata per determinare i versi di flusso
   e come punto di partenza (*warm start*) della simulazione successiva;
2. in caso di mancata convergenza, una **continuazione sul parametro di
   controllo**: il target di mandata è portato per incrementi successivi dal
   valore di equilibrio senza compressore al valore di targa, ciascun passo
   inizializzato dal precedente.

Le due fasi sono automatiche e tracciate nel log con il prefisso
`[compressori]`.

### 6.1.2 Avvertenza

In assenza di *Pressione OUT* il motore adotta un rapporto di compressione di
ripiego pari a **1,1** (§13.3), insufficiente in condizioni di carico reale e
tipicamente causa di divergenza con pressioni che collassano. Il plugin emette
un avviso non bloccante prima dell'avvio.

### 6.1.3 Grandezze restituite

A convergenza è calcolata la potenza isentropica assorbita da ciascuna
stazione:

    P = cp · T₁ · [ r^((n−1)/n) − 1 ] · ṁ / (η · 10⁶)        [MW]         (6.1)

con r = p_out/p_in rapporto effettivo, n = cp/cv, ṁ portata massica, η
rendimento. I valori sono scritti in `results_compressors.csv` (§10.4).

## 6.2 ⚙ Opzioni avanzate

| Parametro | Simbolo | Unità | Default | Intervallo | Descrizione |
|-----------|---------|-------|---------|------------|-------------|
| **Preserva nodi intermedi** | — | — | disattivo | — | Disabilita il collasso topologico: tutti i nodi intermedi sono conservati e le quote campionate dal DEM. Produce modelli di dimensione maggiore ma con profilo altimetrico risolto lungo le condotte. Richiede un DEM (§5.2). |
| **Flusso orario nodi** | — | — | non assegnato | — | Campo dei consumi orari in Modalità A (§5.6). |
| **Raggio aggancio** | r_s | m | 50,0 | 0,1–10 000 | Distanza massima entro cui un nodo del layer nodi è associato a un estremo di condotta durante il collasso. Valori insufficienti impediscono il riconoscimento dei nodi di riferimento e l'attribuzione delle domande; valori eccessivi attribuiscono la domanda al nodo errato. |
| **Separatore flussi** | — | — | `;` | `;` `,` `\|` `:` spazio tab | Separatore dei valori del profilo orario. |
| **Pressione reference** | p_ref | bar (relativi) | 75,0 | 1–300 | Pressione imposta ai nodi di riferimento. Per la conversione in pressione assoluta si veda la (2.2). |
| **Temperatura** | T | K | 288,15 | 250–400 | Temperatura del gas, uniforme sull'intera rete (ipotesi isoterma, §1.3). |
| **Flusso placeholder** | D_min | sm³/s | 1×10⁻⁴ | 0–10 | Domanda attribuita ai nodi di transito, cioè privi di domanda propria. Ha funzione di regolarizzazione: una riga di bilancio identicamente nulla può rendere singolare la matrice jacobiana. |
| **Rugosità condotte** | ε | m | 1,2×10⁻⁵ | 1×10⁻⁷–0,1 | Rugosità assoluta della parete interna, parametro della (2.9). Valori per materiale al §13.2. |
| **Flusso minimo export** | — | sm³/s | 1×10⁻⁶ | 1×10⁻¹⁰–1 | Valore scritto nel file di ingresso per i nodi privi di domanda nota. Agisce in fase di scrittura; il *Flusso placeholder* agisce successivamente, in fase di validazione, e prevale. |
| **Decimali layer risultato** | — | — | 4 | 0–10 | Cifre decimali dei campi numerici dei layer prodotti. |
| **Mostra layer collassato nella legenda** | — | — | attivo | — | I layer `Condotte #N` / `Nodi #N` sono resi visibili nella legenda. Se disattivato essi vengono comunque creati, essendo necessari per la Modalità B. |
| **Crea layer condotte originali colorato** | — | — | disattivo | — | Produce un ulteriore layer `R-P-orig-…` con i risultati riportati sulla geometria originale, non collassata. |

## 6.3 ⚙ Parametri solutore

Riferimento teorico: §2.7.

| Parametro | Unità | Default | Intervallo | Descrizione |
|-----------|-------|---------|------------|-------------|
| **Max iterazioni** | — | 50 | 10–2000 | Numero massimo di iterazioni di Newton-Raphson. Si veda l'avvertenza 6.3.1. |
| **Tolleranza** | Sm³/s | 0,001 | 1×10⁻⁴–10 | Soglia del criterio (2.14): massimo squilibrio di bilancio ammesso per nodo. Il riquadro adiacente riporta l'equivalente in Sm³/h (moltiplicazione per 3600): il default corrisponde a 3,6 Sm³/h. |
| **URF** | — | 2,0 | 0,1–20 | Fattore di sotto-rilassamento della (2.13). **Compare a denominatore**: valori maggiori riducono l'ampiezza del passo e stabilizzano l'iterazione; valori inferiori a 1 amplificano il passo di Newton. Il valore assegnato costituisce il limite inferiore adottato dallo schema adattativo (§2.7). |
| **Auto-calibra tol e URF** | — | disattivo | — | Assegna tolleranza e URF in funzione del numero di nodi secondo la tabella §13.1.1 e, in caso di mancata convergenza, percorre la medesima scala verso combinazioni più rilassate. L'attivazione disabilita i due campi corrispondenti. |
| **Affina precisione** | — | disattivo | — | Successivamente alla prima convergenza, ripete la soluzione con tolleranze decrescenti — prima per fattori di 10, quindi per bisezione in scala logaritmica — fino al limite di 1×10⁻⁴, conservando il risultato corrispondente alla tolleranza minima effettivamente raggiunta. Indipendente da *Auto-calibra*: quest'ultima definisce il punto di partenza, *Affina precisione* il punto di arrivo. Il valore da riportare in sede di documentazione dei risultati è la tolleranza **finale**, indicata nel log. |
| **Forza Multiprocesso** | — | attivo | — | Esecuzione in processi Python indipendenti, necessaria affinché le simulazioni parallele (§7.3, §7.4) utilizzino effettivamente più core. |

### 6.3.1 Avvertenza sul numero massimo di iterazioni

Il numero di iterazioni necessarie dipende dalla distanza fra lo stato iniziale
e la soluzione, non dalla dimensione della rete. Nelle prove di verifica
condotte su questo plugin (§11.7) il valore di default di 50 iterazioni si è
rivelato **insufficiente** su tutte e tre le reti provate, comprese due reti di
4 e 10 nodi; la rete del §11 converge in 92 iterazioni.

Si raccomanda pertanto di assumere **Max iterazioni = 200** come punto di
partenza. L'incremento non comporta penalizzazioni: il calcolo termina
comunque al raggiungimento del criterio (2.14).

## 6.4 Composizione Gas

| Campo | Descrizione |
|-------|-------------|
| **Gas base** | Preset di composizione: *SNAM — Mazara del Vallo (gas algerino)* (default), *SNAM — Gela (gas libico)*, *Metano puro (100% CH₄)*, *Gas naturale tipico (94% CH₄)*, *Idrogeno puro (H₂)*, *Personalizzato…*. Le frazioni molari sono riportate al §13.3. |
| **Aggiunta H₂** | Frazione **molare** di idrogeno addizionata al gas base, 0–99 %. La composizione di base è riscalata proporzionalmente: indicata con x la frazione di H₂ e con y_k le frazioni del gas base, la miscela risultante ha frazioni y_k·(1−x) e frazione di idrogeno x. |
| **Composizione export** | Composizione effettivamente scritta nel file di ingresso. È aggiornata automaticamente in funzione dei due campi precedenti ed è modificabile manualmente per composizioni non previste dai preset; in tal caso il preset assume il valore *Personalizzato*. |

### 6.4.1 Componenti ammessi

`methane`, `ethane`, `propane`, `isobutane`, `butane`, `isopentane`,
`pentane`, `hexane`, `nitrogen`, `carbon dioxide`, `helium`, `hydrogen`.

La chiave dell'anidride carbonica è **`carbon dioxide`**, con spazio. Le
frazioni molari devono avere somma unitaria.

### 6.4.2 Effetto della composizione sulla soluzione idraulica

La composizione interviene nella (2.4) attraverso SG e Z e nella (2.9)
attraverso il numero di Reynolds. A parità di portata volumetrica standard,
una miscela a densità relativa inferiore — per esempio addizionata di idrogeno
— presenta minore perdita di carico e maggiore velocità, ma minore contenuto
energetico per unità di volume. La valutazione di uno scenario di blending
richiede pertanto l'esame congiunto di pressione, velocità, potere calorifico
e indice di Wobbe (§9.4).
