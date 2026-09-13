# Glossario

Un elenco rapido dei termini tecnici usati nel plugin e in questa guida, per
chi non ha familiarità con il linguaggio dell'idraulica del gas o del GIS.

**Pressione assoluta** — Pressione misurata a partire dal vuoto assoluto (0
bar = nessuna pressione). È l'unità usata da tutto il plugin.

**Pressione relativa (manometrica)** — Pressione misurata a partire dalla
pressione atmosferica (0 bar = pressione atmosferica). È quella letta di
solito da un manometro; per usarla nel plugin va convertita in assoluta
sommando circa 1 bar.

**Portata** — Quantità di gas che attraversa una sezione di condotta
nell'unità di tempo. Nel plugin è espressa in Smc/h (portata volumetrica
standard) o sm³/s.

**Smc (Standard metro cubo)** — Unità di volume di gas riferita a condizioni
standard fisse (15 °C, 1,01325 bar), usata per confrontare portate senza
dover specificare ogni volta la pressione reale del gas.

**Densità** — Massa di gas per unità di volume (kg/m³). Cambia con pressione
e temperatura, perché il gas è comprimibile.

**Densità standard** — Densità del gas alle condizioni standard di
riferimento; dipende solo dalla composizione del gas, non dalla pressione
del punto in cui ci si trova.

**Massa molare** — Massa media di una mole di molecole della miscela di gas
(g/mol). Componenti più pesanti (propano, butano) la aumentano; l'idrogeno la
riduce.

**Specific gravity** — Rapporto tra la densità del gas e la densità
dell'aria, nelle stesse condizioni. Indica se il gas è più leggero (< 1) o
più pesante (> 1) dell'aria.

**Fattore di comprimibilità Z** — Misura di quanto un gas reale si discosta
dal comportamento ideale (Z = 1 per un gas ideale).

**HHV (Higher Heating Value, potere calorifico superiore)** — Energia
rilasciata dalla combustione completa di un metro cubo standard di gas,
incluso il calore recuperabile dalla condensazione del vapore prodotto.

**Indice di Wobbe** — Indicatore di intercambiabilità tra gas diversi (HHV
diviso la radice quadrata della specific gravity): due gas con lo stesso
indice di Wobbe si comportano allo stesso modo nello stesso bruciatore.

**Nodo di riferimento (reference)** — Nodo della rete a cui è assegnata una
pressione assoluta nota; funge da "ancora" per tutto il calcolo (come il
nodo di massa in un circuito elettrico). Obbligatorio: almeno uno per rete.

**Bilancio di massa** — Principio secondo cui, in ogni nodo, tutto il gas
che entra deve uscirne (o essere consumato lì); alla base delle equazioni
risolte dal solutore.

**Perdita di carico** — Caduta di pressione lungo una condotta causata
dall'attrito tra il gas e le pareti interne.

**Rugosità** — Grado di scabrosità della superficie interna di una condotta;
influenza l'attrito e quindi la perdita di carico. Dipende dal materiale.

**Formula di Chen** — Formula usata dal motore di calcolo per stimare la
perdita di carico per attrito in ogni condotta, variante dell'equazione di
Darcy-Weisbach.

**Regime permanente (steady-state)** — Tipo di soluzione calcolata dal
plugin: assume che i consumi restino costanti nel tempo e calcola lo stato
della rete una volta stabilizzata, senza simulare l'evoluzione nel tempo
(transitori).

**Metodo di Newton-Raphson** — Metodo numerico iterativo usato per risolvere
il sistema di equazioni non lineari della rete, per approssimazioni
successive.

**Iterazione** — Un singolo ciclo di correzione del metodo di Newton-Raphson.

**Tolleranza** — Soglia sotto la quale l'errore residuo del calcolo viene
considerato accettabile (convergenza raggiunta).

**URF (Under-Relaxation Factor)** — Parametro che controlla quanto è
"decisa" ogni correzione del metodo iterativo; troppo alto genera
oscillazioni, troppo basso rallenta la convergenza.

**Convergenza** — Il momento in cui l'errore del calcolo scende sotto la
tolleranza impostata e la simulazione si considera conclusa con successo.

**Collasso topologico** — Operazione che trasforma geometrie GIS grezze
(linee e punti indipendenti) in un grafo pulito di nodi e condotte collegati
correttamente tra loro.

**Raggio di aggancio** — Distanza massima entro cui, durante il collasso, un
nodo viene collegato all'estremità di una condotta vicina.

**DEM (Digital Elevation Model)** — Layer raster che rappresenta la quota
del terreno; usato dal plugin per estrarre l'altitudine dei nodi.

**Velocità di erosione** — Velocità limite oltre la quale il flusso di gas
ad alta velocità inizia a danneggiare per erosione le pareti interne della
condotta.

**Specie di condotta (D.M. 17/04/2008)** — Classificazione normativa
italiana delle condotte di trasporto gas in base alla loro pressione massima
di esercizio (1a, 2a, 3a, 4a specie).

**Blending idrogeno/metano** — Pratica di iniettare una miscela di idrogeno e
metano in una rete progettata originariamente per gas naturale puro, per
ridurre le emissioni di CO₂.
