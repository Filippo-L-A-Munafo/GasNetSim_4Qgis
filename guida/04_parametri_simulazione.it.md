# Tab 2 — Parametri Simulazione

Questa scheda imposta i parametri fisici e numerici usati dal motore di
calcolo, e definisce come verranno visualizzati i risultati in QGIS al
termine.

## 1. Cartella Input CSV

Seleziona la cartella che contiene `sf_nodes.csv` e `sf_pipelines.csv`. Se
sei arrivato qui dopo aver premuto "Genera CSV" nel Tab 1, questo campo si
popola automaticamente con la cartella scelta lì.

## 2. Parametri Fisici

Questi valori vengono applicati sia in fase di export dei CSV sia durante la
simulazione vera e propria.

| Campo | Unità | Default | Descrizione |
|-------|-------|---------|-------------|
| **Pressione reference** | bar | 70 | Pressione assoluta assegnata ai nodi reference. È il valore che "ancora" tutta la rete (vedi "Concetti fisici di base" → "Nodi di riferimento"). Valori tipici: 70 bar per una rete nazionale di trasporto (RNT), 25 bar per una rete regionale (RRT). |
| **Temperatura** | K | 300 | Temperatura operativa del gas, in gradi Kelvin (27 °C ≈ 300 K). Influenza sia la comprimibilità del gas (fattore Z) sia la sua densità nelle condizioni operative. |
| **Flusso nodi senza domanda** | sm³/s | 0,0001 | Flusso minimo assegnato ai nodi "junction" (di transito, senza consumo proprio) che nei CSV risultano a domanda esattamente zero. Serve a evitare righe completamente vuote nella matrice del solutore, che altrimenti può risultare singolare (senza soluzione). Se la rete non converge a causa di nodi isolati, prova ad aumentarlo a 0,001. |

> **Perché serve una temperatura operativa?** Il volume e la densità di un
> gas dipendono sia dalla pressione sia dalla temperatura (legge dei gas,
> vedi "Concetti fisici di base"). Il plugin assume per semplicità una
> temperatura uniforme su tutta la rete — una semplificazione ragionevole
> per reti interrate o poco esposte a forti variazioni termiche locali.

## 3. Parametri Solutore

Il sistema di equazioni della rete è **non lineare** (la perdita di carico
in una condotta dipende dalla portata che ci scorre, che a sua volta dipende
dalle pressioni ai suoi estremi — vedi "Concetti fisici di base"). Un sistema
non lineare, a differenza di uno lineare, non si risolve con un unico
calcolo diretto: va risolto per **approssimazioni successive**, con un
metodo iterativo chiamato **Newton-Raphson**.

L'idea di base del metodo: si parte da una stima iniziale delle pressioni,
si calcola quanto le equazioni di bilancio sono "sbagliate" con quella
stima (l'errore, o residuo), e si corregge la stima in una direzione che
riduce l'errore. Si ripete finché l'errore non scende sotto una soglia
accettabile (convergenza), oppure finché non si raggiunge un numero massimo
di tentativi senza successo (in tal caso la simulazione si ferma senza
risultato).

| Campo | Default | Descrizione |
|-------|---------|-------------|
| **Max iterazioni** | 50 | Numero massimo di cicli di correzione che il metodo di Newton-Raphson può eseguire prima di arrendersi. Aumenta a 100–200 per reti molto grandi, molto ramificate, o "mal condizionate" (con condotte di diametro molto diverso tra loro collegate direttamente). |
| **Tolleranza** | 1,0 | Soglia sotto la quale l'errore residuo viene considerato accettabile e il calcolo si ferma dichiarando "convergenza raggiunta". Riduci a 0,1 per risultati più precisi (ma più iterazioni necessarie); aumenta se la rete fatica a convergere e una precisione minore è accettabile per il tuo scopo. |
| **URF (Under-Relaxation Factor)** | 2,0 | Controlla quanto "decisa" è ogni correzione ad ogni iterazione. Un valore troppo alto può far "oscillare" la soluzione attorno al punto corretto senza mai stabilizzarsi (come spingere troppo forte un'altalena); un valore troppo basso rende la convergenza più lenta ma più stabile. Riduci a 1,0–1,5 se la simulazione oscilla senza convergere; aumenta fino a 3,0 per accelerare la convergenza su reti ben condizionate che convergono già facilmente. |
| **Auto-calibra tol e URF** | Off | Se attivo, il plugin prova automaticamente diverse combinazioni di tolleranza e URF (partendo dai valori impostati e riducendoli progressivamente) fino a trovarne una che porta a convergenza, risparmiandoti i tentativi manuali. |

## 4. Rete e Composizione Gas

| Campo | Default | Descrizione |
|-------|---------|-------------|
| **Rugosità condotte** | 5×10⁻⁵ m | Rugosità interna assoluta delle pareti della condotta: quanto sono "scabre" internamente, in media, rispetto al diametro. Entra nella **formula di Chen** (una variante dell'equazione di Darcy-Weisbach, vedi "Concetti fisici di base" → "Perdita di carico") usata per calcolare l'attrito in ogni condotta. Dipende dal materiale: acciaio ≈ 5×10⁻⁵ m; polietilene (PE/HDPE) ≈ 7×10⁻⁶ m (molto più liscio); ghisa ≈ 2,6×10⁻⁴ m (più scabra). |
| **Flusso minimo export** | 1×10⁻⁶ sm³/s | Valore segnaposto scritto nel CSV per i nodi senza una domanda nota, per evitare che il file di export contenga righe vuote (che causerebbero una matrice singolare nel solutore). È concettualmente simile al "Flusso nodi senza domanda" dei Parametri Fisici, ma agisce in un momento diverso della pipeline: questo durante l'esportazione dei CSV, l'altro come correzione appena prima della simulazione. |
| **Preset gas** | Gas naturale (100% CH₄) | Scorciatoia per compilare rapidamente la composizione. Opzioni disponibili: gas naturale puro, gas naturale "tipico" (94% metano + altri componenti minori), mix idrogeno/metano al 10%, 20% o 50%, e idrogeno puro. Scegli "Personalizzato..." per inserire una composizione a mano. |
| **Composizione (dict)** | `{'methane': 1.0}` | La composizione del gas, come dizionario Python con le frazioni molari di ciascun componente. La somma delle frazioni deve sempre essere 1,0. Componenti supportati: `methane` (metano), `ethane` (etano), `propane` (propano), `butane` (butano), `nitrogen` (azoto), `carbon_dioxide` (anidride carbonica), `hydrogen` (idrogeno). |

### Perché la composizione del gas conta per il calcolo idraulico

Il gas non è un fluido "generico": le sue proprietà fisiche — densità,
viscosità, comprimibilità (fattore Z), potere calorifico — dipendono
direttamente da quali molecole lo compongono e in che proporzione. Miscele
diverse (per esempio metano puro contro un blend con il 20% di idrogeno)
hanno densità e comprimibilità diverse, e quindi si comportano in modo
diverso nella stessa condotta alla stessa pressione: a parità di portata
volumetrica standard, una miscela più leggera (più ricca di idrogeno) scorre
più velocemente e genera meno perdita di carico rispetto a metano puro, ma
trasporta anche meno energia per unità di volume (vedi il campo `hhv_mj_sm3`
nella sezione "Risultati — Nodi"). Per questo motivo il plugin permette di
impostare esplicitamente la composizione, e la usa in ogni singolo calcolo di
proprietà del gas, nodo per nodo e condotta per condotta.

## 5. Visualizzazione Risultati

Questa parte non influisce sul calcolo: sceglie solo **come vengono
disegnati** i risultati nei nuovi layer QGIS creati al termine della
simulazione.

### Nodi

| Elemento | Descrizione |
|----------|-------------|
| **Colora per** | Il campo usato per la scala cromatica del layer nodi. Opzioni: Pressione, Temperatura, Specific gravity, Z-factor, HHV, Wobbe, Densità, Densità standard, Massa molare (vedi la sezione "Risultati — Nodi" per il significato fisico di ciascuno). |
| **Checkbox campi** | Sceglie quali campi risultato vengono inclusi come attributi nel layer nodi (interrogabili con lo strumento "Identifica" di QGIS). Attivi per default: Pressione, Temperatura, Specific gravity, Z-factor, HHV, Wobbe. |

### Condotte

| Elemento | Descrizione |
|----------|-------------|
| **Colora per** | Il campo usato per la scala cromatica del layer condotte. Opzioni: Portata (Smc/h), Velocità (m/s), Pressione media (bar), Specific gravity, Z-factor, Densità. |
| **Checkbox campi** | Campi risultato da includere come attributi nel layer condotte. Attivi per default: Portata, Portata assoluta, Velocità, Pressione media, Specific gravity. |
| **Mostra frecce direzione flusso** | Se attivo (default), disegna un piccolo marcatore triangolare al centro di ogni condotta, orientato nel verso reale in cui scorre il gas (la geometria viene invertita automaticamente per le condotte con portata negativa, cioè flusso da B verso A — vedi "Risultati — Condotte"). Molto utile per capire a colpo d'occhio la direzione del flusso in una rete complessa. |
