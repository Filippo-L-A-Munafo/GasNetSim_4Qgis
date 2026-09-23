# 2. Formulazione del modello

Questa sezione riporta le equazioni effettivamente implementate nel solutore,
nella forma in cui sono codificate, e definisce il significato fisico dei
parametri che l'interfaccia espone. La simbologia completa è nel §14.

## 2.1 Schematizzazione della rete

La rete è rappresentata come un grafo orientato G = (N, P), dove N è l'insieme
dei nodi e P quello delle condotte. Ogni condotta p ∈ P collega un nodo di
ingresso i e un nodo di uscita j, con orientamento convenzionale assegnato in
fase di costruzione del modello e privo di significato fisico: il verso
effettivo del flusso è un risultato del calcolo (§10.2).

I nodi si distinguono in:

- **nodi di riferimento** (node_type = `reference`): nodi a pressione imposta,
  che costituiscono le condizioni al contorno del problema e in cui viene
  assegnata la composizione del gas immesso;
- **nodi di domanda o junction**: nodi in cui è assegnata una portata volumetrica
  in condizioni standard, positiva se prelevata, negativa se immessa.

## 2.2 Condizioni standard e convenzioni di pressione

Le portate volumetriche sono riferite alle condizioni standard

    T_b = 288,15 K        p_b = 1 atm = 101 325 Pa                        (2.1)

coerenti con UNI EN ISO 13443. L'unità corrispondente è lo standard metro cubo
(Smc, equivalentemente sm³).

**Convenzione di pressione.** Il valore assegnato ai nodi di riferimento
attraverso il parametro *Pressione reference* è interpretato come pressione
**relativa** (manometrica); la conversione in pressione assoluta avviene
all'atto della costruzione del modello:

    p_abs = p_gauge + p_atm,     p_atm = 101 325 Pa                       (2.2)

Tutte le pressioni restituite dal calcolo (§9) sono **assolute**. Un valore
assegnato di 75 bar corrisponde pertanto a 76,013 bar nei risultati.

## 2.3 Equazione di continuità ai nodi

Per ogni nodo i non di riferimento, la conservazione della massa impone

    Σ_(p ∈ P_i) s_(i,p) · Q_p − D_i = 0                                   (2.3)

dove Q_p è la portata volumetrica in condizioni standard della condotta p,
s_(i,p) = +1 se la condotta entra nel nodo e −1 se ne esce, D_i è la domanda
nodale (positiva in prelievo). Il sistema (2.3), scritto per tutti i nodi non
di riferimento, costituisce il sistema di equazioni non lineari risolto dal
solutore; le incognite sono le pressioni nodali.

## 2.4 Equazione di portata in condotta

La portata è calcolata con l'equazione generale del moto del gas in condotta:

    Q = sgn(Δ) · C_p · √( |p₁² − p₂² − H| / (Z · SG) )                    (2.4)

con Δ = p₁² − p₂² − H. Il termine C_p raccoglie le caratteristiche fisiche
della condotta:

    C_p = K · (T_b / p_b) · D^2,5 · √( 1 / (L · T_avg · f) ) · η          (2.5)

    K = π · √( R / (16 · M_aria) ),    M_aria = 28,97 g/mol               (2.6)

dove D è il diametro interno, L la lunghezza, T_avg la temperatura media, f il
fattore d'attrito, η il fattore di efficienza della condotta, R la costante
universale dei gas.

La pressione media nella condotta, usata per la valutazione delle proprietà del
gas, è calcolata nella forma consueta per il moto dei gas:

    p_avg = (2/3) · [ (p₁ + p₂) − (p₁ · p₂)/(p₁ + p₂) ]                   (2.7)

che, per la comprimibilità, differisce dalla media aritmetica.

### 2.4.1 Correzione di dislivello

Il termine H rende conto della differenza di quota fra i due estremi:

    H = 0,06835 · SG · (h₂ − h₁) · p_avg² / (Z · T_avg)                   (2.8)

con h₁, h₂ quote dei nodi di ingresso e uscita. Il termine è nullo per condotte
orizzontali. Per un gas a 70 bar la densità è dell'ordine di 70 kg/m³: su
dislivelli di alcune centinaia di metri il contributo di (2.8) è confrontabile
con quello dell'attrito, e in reti di montagna può prevalere. Ne consegue che
l'accuratezza delle quote nodali è determinante quanto quella dei diametri
(§5.4, §6.2).

### 2.4.2 Fattore d'attrito

Il fattore d'attrito è calcolato con la correlazione esplicita di **Chen
(1979)**, valida su tutto il campo turbolento e nella transizione:

    1/√f = −2 · log₁₀[ ε/(3,7065·D)
             − (5,0452/Re) · log₁₀( (ε/D)^1,1098 / 2,8257
             + (7,149/Re)^0,8981 ) ]                                      (2.9)

dove ε è la rugosità assoluta della parete (parametro *Rugosità condotte*,
§6.2) e Re il numero di Reynolds, valutato con la viscosità dinamica della
miscela calcolata con i metodi di Lucas e Herning-Zipperer.

La scelta della correlazione è fissata dal plugin (`friction_method = chen` nei
file di ingresso) e non è modificabile dall'interfaccia.

## 2.5 Equazione di stato e proprietà del gas

Il fattore di comprimibilità Z, la densità, la densità in condizioni standard,
la massa molare e le capacità termiche della miscela sono calcolati con
l'equazione di stato **GERG-2008** (ISO 20765-2), in funzione di pressione,
temperatura e composizione molare, e aggiornati nodo per nodo ad ogni
iterazione.

Per un gas ideale si avrebbe Z = 1; nelle condizioni tipiche delle reti di
trasporto (70–76 bar, 288 K) risulta Z ≈ 0,80÷0,88 (§9.3). Trascurare tale
scostamento comporterebbe errori dell'ordine del 15–20 % sulla densità e, di
conseguenza, sulle velocità calcolate.

La densità relativa (specific gravity) è definita come

    SG = M_gas / M_aria                                                   (2.10)

e l'indice di Wobbe come

    W = HHV / √SG                                                         (2.11)

con HHV potere calorifico superiore riferito alle condizioni standard.

## 2.6 Tracciamento della composizione

In presenza di immissioni di gas a composizione diversa, la composizione in
ciascun nodo è determinata per **miscelazione semplice** delle portate entranti
pesate sulle rispettive composizioni. Poiché la composizione modifica le
proprietà che compaiono nella (2.4), il problema idraulico e quello di
composizione sono accoppiati e vengono risolti con uno schema **staggered**:
ad ogni iterazione esterna si risolve il campo di pressione a composizione
congelata, si aggiorna la composizione, e si itera fino a che entrambe le
variazioni scendono sotto le rispettive soglie.

Lo schema staggered è attivato automaticamente quando almeno un nodo non di
riferimento possiede una composizione propria (§5.6); in caso contrario il
solutore adotta uno schema diretto. La differenza fra i due schemi non è solo
formale: incide sulla robustezza della convergenza (§12.3).

## 2.7 Soluzione numerica

Il sistema (2.3), non lineare per la dipendenza di Q dalle pressioni espressa
dalla (2.4), è risolto con il metodo di **Newton-Raphson**. Detto F(x) il
vettore dei residui di bilancio nodale e J(x) = ∂F/∂x la matrice jacobiana,
ad ogni iterazione si risolve

    J(x⁽ᵏ⁾) · Δx = F(x⁽ᵏ⁾)                                               (2.12)

e si aggiorna lo stato secondo

    x⁽ᵏ⁺¹⁾ = x⁽ᵏ⁾ + Δx / URF                                             (2.13)

**Il fattore URF compare a denominatore.** Un valore elevato riduce l'ampiezza
del passo e quindi *smorza* l'iterazione, aumentando la stabilità a scapito
della velocità; un valore inferiore all'unità amplifica il passo di Newton. Il
valore impostato dall'utente costituisce il limite inferiore (passo più
aggressivo ammesso): il solutore lo aumenta automaticamente, fino a un massimo
di max(4·URF, 8), quando il residuo non decresce in modo soddisfacente, e lo
riporta verso il valore assegnato quando la convergenza procede regolarmente.

Ad ogni iterazione l'ampiezza del passo è ulteriormente limitata da una
procedura di *line search* (dimezzamenti successivi fino a ottenere una
riduzione del residuo) e da un vincolo di regione di fiducia sulle componenti
di Δx.

### 2.7.1 Criterio di convergenza

La convergenza è dichiarata quando

    max |F(x)| ≤ tol                                                      (2.14)

cioè quando il massimo squilibrio di portata fra tutti i nodi è inferiore alla
tolleranza assegnata. **La tolleranza è pertanto una portata**, espressa in
Sm³/s: il valore di default 0,001 Sm³/s corrisponde a 3,6 Sm³/h di squilibrio
massimo ammesso per nodo. Nel caso di verifica del §11 lo squilibrio residuo è
esattamente di questo ordine di grandezza (§11.6), e questo spiega perché le
portate restituite non chiudono il bilancio con precisione arbitraria.

Se la (2.14) non è soddisfatta entro il numero massimo di iterazioni
assegnato, il solutore restituisce l'ultimo iterato calcolato, segnalandolo
come **soluzione non convergente**: si tratta di uno stato intermedio che non
soddisfa i bilanci nodali e che non ha significato fisico (§7.5, §12).
