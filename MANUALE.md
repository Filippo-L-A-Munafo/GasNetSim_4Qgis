# Manuale — GasNetSim 4Qgis

Plugin QGIS per la simulazione idraulica in regime stazionario di reti di
trasporto gas, basato sul motore di calcolo GasNetSim.

> Questo file è generato unendo le sezioni della Guida integrata nel plugin
> (cartella `guida/`, visibile dal pulsante **Guida**). Non modificarlo a
> mano: le modifiche vanno fatte nei file della cartella `guida/`, poi si
> rilancia `python guida/_genera_manuale.py`.

## Indice

1. [1. Introduzione e ambito di applicazione](#1-introduzione-e-ambito-di-applicazione)
2. [2. Formulazione del modello](#2-formulazione-del-modello)
3. [3. Architettura dell'interfaccia](#3-architettura-dellinterfaccia)
4. [4. Tab 0 — Verifica topologica della rete](#4-tab-0-verifica-topologica-della-rete)
5. [5. Tab 1 — Dati di ingresso e mappatura dei campi](#5-tab-1-dati-di-ingresso-e-mappatura-dei-campi)
6. [6. Tab 1 — Parametri fisici e numerici](#6-tab-1-parametri-fisici-e-numerici)
7. [7. Esecuzione e file prodotti](#7-esecuzione-e-file-prodotti)
8. [8. Tab 2 — Post-processing e rappresentazione](#8-tab-2-post-processing-e-rappresentazione)
9. [9. Grandezze calcolate ai nodi](#9-grandezze-calcolate-ai-nodi)
10. [10. Grandezze calcolate sulle condotte e sui compressori](#10-grandezze-calcolate-sulle-condotte-e-sui-compressori)
11. [11. Caso di verifica riproducibile](#11-caso-di-verifica-riproducibile)
12. [12. Diagnostica della convergenza](#12-diagnostica-della-convergenza)
13. [13. Riferimenti tecnici e normativi](#13-riferimenti-tecnici-e-normativi)
14. [14. Nomenclatura e glossario](#14-nomenclatura-e-glossario)

---

## 1. Introduzione e ambito di applicazione

### 1.1 Oggetto

GasNetSim 4Qgis è un plugin per QGIS che risolve il problema idraulico di
regime stazionario di una rete di trasporto di gas naturale, eventualmente
addizionata di idrogeno, a partire dalla rappresentazione vettoriale della rete
contenuta in un progetto QGIS.

Il plugin costituisce l'interfaccia geospaziale del solutore **GasNetSim**
(Forschungszentrum Jülich, ICE-1) e ne estende le funzionalità con la gestione
delle stazioni di compressione, l'esecuzione parallela di scenari orari e la
restituzione cartografica dei risultati.

### 1.2 Modello risolto

Il modello è di tipo **nodale**, in regime **stazionario** e **isotermo**, con
equazione di stato del gas reale. Le grandezze incognite sono le pressioni ai
nodi; portate, velocità e proprietà termofisiche sono grandezze derivate.

La formulazione completa, con le equazioni effettivamente implementate, è
riportata nel §2. In sintesi il modello include:

- bilancio di massa a ciascun nodo di domanda;
- equazione generale di portata per condotta, con fattore d'attrito calcolato
  secondo la correlazione esplicita di Chen (1979);
- termine correttivo di dislivello geodetico;
- equazione di stato **GERG-2008** (ISO 20765-2) per fattore di
  comprimibilità, densità e capacità termiche;
- tracciamento della composizione in presenza di immissioni di gas diversi.

### 1.3 Ambito di validità e limitazioni

| Aspetto | Ambito |
|---------|--------|
| Regime | Stazionario. I transitori non sono modellati: ogni simulazione descrive lo stato asintotico della rete a domanda costante. |
| Temperatura | Uniforme e assegnata. Il modello non risolve il bilancio termico lungo le condotte. |
| Fase | Monofase gassosa. Non sono trattati condensati né trasporto bifase. |
| Pressioni | Verificato su reti di 1ª e 2ª specie (24–75 barg). La formulazione non pone limiti espliciti di pressione. |
| Componenti | Condotte, nodi di domanda e immissione, nodi a pressione imposta, stazioni di compressione. Valvole di regolazione, riduttori e stoccaggi non sono esposti dall'interfaccia. |
| Ottimizzazione | Assente. Il plugin risolve la configurazione assegnata, non ne ricerca una ottimale. |

Il plugin non effettua controlli di plausibilità sui dati di ingresso al di là
di quelli topologici del §4: valori mancanti vengono sostituiti da valori di
ripiego documentati nel §6, e il calcolo procede comunque. La responsabilità
della coerenza fisica dei dati resta dell'utente.

### 1.4 Applicazioni tipiche

1. **Verifica di adeguatezza**: determinazione delle pressioni ai punti di
   consegna per un assegnato profilo di domanda oraria, e confronto con i
   valori minimi contrattuali.
2. **Analisi di blending di idrogeno**: valutazione dell'effetto di una
   frazione molare di H₂ su pressioni, velocità, potere calorifico, densità
   relativa e indice di Wobbe, per la verifica dei vincoli normativi di
   qualità del gas (§13.4).
3. **Dimensionamento di interventi**: confronto fra configurazioni alternative
   di rete a parità di domanda.
4. **Campagne pluri-scenario**: esecuzione automatica di 24 scenari orari, o
   di una serie di giorni, con raccolta sistematica dei risultati.

### 1.5 Architettura dell'elaborazione

Il flusso è organizzato in tre fasi, corrispondenti alle tre schede
dell'interfaccia:

| Fase | Scheda | Contenuto |
|------|--------|-----------|
| Verifica topologica | Tab 0 | Analisi di connessione del layer condotte, individuazione di geometrie degeneri, duplicati e componenti sconnesse; correzione per snap degli estremi (§4). |
| Definizione ed esecuzione | Tab 1 | Associazione dei campi dei layer alle grandezze del modello, assegnazione dei parametri fisici e numerici, generazione dei file di ingresso ed esecuzione del solutore (§5, §6, §7). |
| Post-processing | Tab 2 | Rappresentazione tematica dei risultati ed esportazione (§8). |

L'ordine 0 → 1 → 2 non è indicativo ma operativo: la mancata verifica
topologica preliminare è la causa più frequente di non convergenza su dati
vettoriali non predisposti per il calcolo (§12.6).

### 1.6 Struttura del documento

I §2–§3 descrivono il modello e l'organizzazione dell'interfaccia; i §4–§8
documentano, scheda per scheda, ogni controllo esposto; i §9–§10 definiscono le
grandezze restituite; il §11 riporta un **caso di verifica riproducibile**, con
i valori numerici attesi, da eseguire per validare l'installazione; il §12
raccoglie la diagnostica di convergenza; i §13–§14 contengono riferimenti
tecnici, normativi e la nomenclatura.

Le grandezze sono indicate con il simbolo e l'unità di misura adottati nel §14.
Le equazioni sono numerate per sezione e richiamate nel testo.

---

## 2. Formulazione del modello

Questa sezione riporta le equazioni effettivamente implementate nel solutore,
nella forma in cui sono codificate, e definisce il significato fisico dei
parametri che l'interfaccia espone. La simbologia completa è nel §14.

### 2.1 Schematizzazione della rete

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

### 2.2 Condizioni standard e convenzioni di pressione

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

### 2.3 Equazione di continuità ai nodi

Per ogni nodo i non di riferimento, la conservazione della massa impone

    Σ_(p ∈ P_i) s_(i,p) · Q_p − D_i = 0                                   (2.3)

dove Q_p è la portata volumetrica in condizioni standard della condotta p,
s_(i,p) = +1 se la condotta entra nel nodo e −1 se ne esce, D_i è la domanda
nodale (positiva in prelievo). Il sistema (2.3), scritto per tutti i nodi non
di riferimento, costituisce il sistema di equazioni non lineari risolto dal
solutore; le incognite sono le pressioni nodali.

### 2.4 Equazione di portata in condotta

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

#### 2.4.1 Correzione di dislivello

Il termine H rende conto della differenza di quota fra i due estremi:

    H = 0,06835 · SG · (h₂ − h₁) · p_avg² / (Z · T_avg)                   (2.8)

con h₁, h₂ quote dei nodi di ingresso e uscita. Il termine è nullo per condotte
orizzontali. Per un gas a 70 bar la densità è dell'ordine di 70 kg/m³: su
dislivelli di alcune centinaia di metri il contributo di (2.8) è confrontabile
con quello dell'attrito, e in reti di montagna può prevalere. Ne consegue che
l'accuratezza delle quote nodali è determinante quanto quella dei diametri
(§5.4, §6.2).

#### 2.4.2 Fattore d'attrito

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

### 2.5 Equazione di stato e proprietà del gas

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

### 2.6 Tracciamento della composizione

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

### 2.7 Soluzione numerica

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

#### 2.7.1 Criterio di convergenza

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

---

## 3. Architettura dell'interfaccia

### 3.1 Avvio

Il plugin si avvia dall'icona nella barra degli strumenti di QGIS o dal menu
**Plugin → GasNetSim_4Qgis**. Si apre una finestra unica, ridimensionabile,
indipendente dalla finestra principale di QGIS: la mappa resta accessibile
durante la configurazione e durante il calcolo.

### 3.2 Organizzazione della finestra

La finestra è composta da una barra laterale richiudibile e da un contenitore a
tre schede.

#### 3.2.1 Barra laterale

Si apre e si chiude con il pulsante **☰** in alto a sinistra.

| Comando | Funzione |
|---------|----------|
| ⚙ Impostazioni | Selezione della lingua dell'interfaccia (italiano/inglese). La modifica ha effetto alla successiva apertura del plugin. |
| Guida | Apre il presente documento. |
| ℹ Info | Versione, autore, repository, licenza. |

#### 3.2.2 Schede

| Scheda | Denominazione | Riferimento |
|--------|---------------|-------------|
| Tab 0 | Verifica Condotte | §4 |
| Tab 1 | Prepara e Simula | §5, §6, §7 |
| Tab 2 | Visualizzazione Risultati | §8 |

### 3.3 Struttura del Tab 1

Il Tab 1 è suddiviso in due colonne separate da un divisore mobile.

**Colonna sinistra** — modulo di configurazione scorrevole, articolato in sei
blocchi:

| Blocco | Titolo | Visibilità | §  |
|--------|--------|------------|----|
| 1 | Dati di Input | sempre visibile | 5.2 |
| 2 | Opzioni Collasso / Layer Già Collassati e mappatura campi | in funzione della modalità | 5.3–5.5 |
| 3 | ⚙ Compressori | su richiesta | 6.1 |
| 4 | ⚙ Opzioni avanzate | su richiesta | 6.2 |
| 5 | ⚙ Parametri solutore | su richiesta | 6.3 |
| 6 | Composizione Gas | sempre visibile | 6.4 |

I blocchi contrassegnati con ⚙ sono chiusi all'apertura e si espandono
spuntando la casella omonima. Tale organizzazione mantiene visibile il
sottoinsieme minimo di parametri necessario a una simulazione, differendo
l'esposizione dei parametri fisici e numerici a chi debba modificarli.

**Colonna destra** — comandi di esecuzione (§7.1) e finestra di log. Il log
riporta in tempo reale le fasi dell'elaborazione, i parametri effettivamente
adottati e l'esito; è il riferimento primario per la diagnostica (§12). Il menu
contestuale del log consente di svuotarlo.

### 3.4 Gestione dei dati dell'utente

Il plugin non modifica i layer di origine: i layer topologici, i layer dei
risultati, i file CSV e i GeoPackage prodotti sono elementi nuovi (§7.6).

L'unica eccezione è esplicita e soggetta a conferma: nel Tab 0, l'operazione di
snap degli estremi può essere applicata al layer originale anziché a una copia
(§4.3); se il layer è su file, la modifica è irreversibile.

### 3.5 Sistema di riferimento

Le elaborazioni geometriche interne (costruzione del grafo, aggancio dei nodi,
calcolo delle lunghezze) sono eseguite in **EPSG:25833** (ETRS89 / UTM zona
33N). I layer in sistemi di riferimento diversi vengono riproiettati.

Ne consegue che le grandezze metriche esposte dall'interfaccia — *Raggio
aggancio* (§6.2) e *Tolleranza* di snap (§4.3) — sono espresse in metri. L'uso
di layer in coordinate geografiche (EPSG:4326) è sconsigliato: le tolleranze
andrebbero espresse in gradi e le lunghezze calcolate risulterebbero prive di
significato.

### 3.6 Elementi non presenti

Per evitare ricerche inutili si segnala che l'interfaccia **non** prevede:

- una scheda dedicata ai parametri di simulazione: essi risiedono nei blocchi
  4–6 del Tab 1;
- un campo per la cartella dei file CSV di ingresso: la cartella è unica ed è
  specificata nel blocco 1 del Tab 1 (§5.2);
- una selezione della correlazione d'attrito o dell'equazione di stato: sono
  fissate rispettivamente a Chen (1979) e GERG-2008 (§2.4.2, §2.5).

---

## 4. Tab 0 — Verifica topologica della rete

### 4.1 Finalità

La verifica topologica precede la costruzione del modello di calcolo. Il
sistema di equazioni (2.3) ammette soluzione unica solo se ogni componente
connessa della rete contiene almeno un nodo a pressione imposta: una porzione
di rete scollegata e priva di nodo di riferimento rende il sistema
indeterminato e la simulazione non converge (§12.6).

La condizione di connessione è **topologica, non grafica**: due condotte i cui
estremi distano pochi centimetri appaiono contigue alla scala di
rappresentazione ma costituiscono due componenti distinte. La scheda individua
questa e altre patologie tipiche dei dati vettoriali di origine non
modellistica.

### 4.2 Analisi della rete

#### 4.2.1 Selezione dei layer

| Campo | Descrizione |
|-------|-------------|
| **Condotte** | Layer lineare da analizzare. Obbligatorio. |
| **Nodi (opz.)** | Layer puntuale facoltativo. Se assegnato, l'operazione di snap (§4.3) aggancia gli estremi delle condotte ai nodi esistenti entro tolleranza, con precedenza sul baricentro del gruppo. Da utilizzare quando la posizione dei nodi è rilevata e ritenuta attendibile. |

#### 4.2.2 Procedura

Il comando **Analizza rete** esegue, in sola lettura:

1. riparazione delle geometrie non valide;
2. **esplosione delle polilinee** nei segmenti elementari, che costituiscono
   gli archi del grafo. Il numero di archi risultante è in generale maggiore
   del numero di feature del layer;
3. costruzione del grafo e conteggio degli archi scartati perché nulli o
   degeneri;
4. individuazione delle patologie e, in loro assenza, messaggio
   `[OK] Nessun problema topologico rilevato.`

#### 4.2.3 Patologie rilevate

| Patologia | Definizione | Conseguenza sul calcolo |
|-----------|-------------|--------------------------|
| Geometrie nulle o degeneri | Feature prive di geometria o di lunghezza nulla | Condotte di lunghezza L = 0: la (2.5) diverge |
| Duplicati e sovrapposizioni | Archi con medesima coppia di estremi, o sovrapposti | Duplicazione non fisica della capacità di trasporto del tratto |
| Componenti sconnesse (isole) | Sottografi non connessi al grafo principale | Sistema indeterminato in assenza di nodo di riferimento nella componente |

L'opzione **Crea layer colorato automaticamente se isole trovate** (attiva per
default) genera un layer temporaneo con una campitura distinta per componente,
che consente di localizzare immediatamente le discontinuità.

Il comando **⚠ Seleziona problematici** seleziona nel layer di origine gli
archi duplicati o sovrapposti individuati dall'ultima analisi.

### 4.3 Snap degli estremi

Operazione di correzione geometrica che unifica gli estremi mutuamente
prossimi. È l'unica operazione del plugin che può modificare i dati di origine.

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| **Tolleranza** | 1,0 m | Distanza massima entro cui due estremi sono considerati coincidenti. Espressa nelle unità del sistema di riferimento del layer (cfr. §3.5). |
| **Strategia — Punto medio** | selezionata | Tutti gli estremi del gruppo sono trasferiti nel baricentro del gruppo stesso. Scelta neutrale, da adottare quando le fonti hanno accuratezza omogenea. |
| **Strategia — Ancora al primo** | — | Un estremo resta fisso e gli altri vi sono ricondotti. Da adottare quando un tratto ha accuratezza planimetrica superiore. |
| **Output — Crea nuovo layer** | selezionata | Genera una copia corretta, aggiunta al progetto. L'originale resta inalterato. |
| **Output — Modifica layer originale** | — | Scrive nel layer di origine. Per layer su file la modifica è **irreversibile**; è richiesta conferma esplicita. |

Se è stato assegnato un layer nodi (§4.2.1), gli estremi vengono agganciati ai
nodi esistenti entro tolleranza.

#### 4.3.1 Criterio di scelta della tolleranza

La tolleranza deve essere superiore all'errore di posizionamento dei dati e
inferiore alla minima distanza fra elementi realmente distinti. Un valore
eccessivo unifica condotte parallele appartenenti al medesimo corridoio,
generando una rete inesistente e, tipicamente, capacità di trasporto
sovrastimate.

Si raccomanda una procedura incrementale: si parte da 1–2 m, si analizza, si
verifica la riduzione del numero di componenti e si incrementa la tolleranza
solo se necessario, controllando visivamente il risultato ad ogni passo.

### 4.4 Isole e ri-analisi

Il blocco si abilita in presenza di componenti sconnesse.

| Comando | Funzione |
|---------|----------|
| **⚠ Seleziona isole** | Seleziona nel layer di origine gli archi appartenenti a componenti staccate dal grafo principale. |
| **Crea layer colorato** | Layer temporaneo con campitura per componente. |
| **Ri-analizza rete corrente** | Ripete l'analisi sul layer prodotto dall'ultimo snap, se presente, altrimenti sul layer selezionato. |

### 4.5 Procedura raccomandata

1. Analisi del layer di origine.
2. In presenza di isole, ispezione del layer colorato.
3. Snap con tolleranza prudenziale, con output su **nuovo layer**.
4. Ri-analisi del layer prodotto.
5. Iterazione dei punti 3–4 fino a che le componenti residue corrispondono a
   porzioni effettivamente isolate della rete reale (per esempio rami non in
   esercizio).
6. Eliminazione o esclusione delle componenti residue prive di alimentazione,
   in quanto incompatibili con la risolubilità del sistema.
7. Passaggio al Tab 1 utilizzando il layer corretto.

> Anche la costruzione del modello (§5.3) può generare segnalazioni: in tal
> caso esse sono presentate in una finestra dedicata, con i comandi
> **Zoom su condotte** e **Flash** per la localizzazione cartografica
> degli elementi interessati.

---

## 5. Tab 1 — Dati di ingresso e mappatura dei campi

### 5.1 Principio

La scheda costruisce, a partire dai layer vettoriali del progetto QGIS, i due
file che costituiscono l'ingresso del solutore: `sf_nodes.csv` e
`sf_pipelines.csv` (§5.7). I file sono rigenerati integralmente ad ogni
esecuzione; non esistono file di ingresso preesistenti da selezionare.

Le informazioni necessarie devono essere già presenti nei layer, in campi di
nome qualsiasi. La mappatura consiste nel dichiarare la corrispondenza fra
campi del layer e grandezze del modello. Il plugin non deduce grandezze
mancanti: in loro assenza applica i valori di ripiego del §6.2 e prosegue.

### 5.2 Blocco 1 — Dati di Input

| Campo | Descrizione |
|-------|-------------|
| **Layer condotte** | Layer lineare. Se è stata eseguita la verifica del §4, si utilizzi il layer corretto e non l'originale. |
| **Layer nodi** | Layer puntuale. Formalmente facoltativo, sostanzialmente necessario: da esso derivano i nodi di riferimento e le domande nodali. In sua assenza il modello risulta privo di condizioni al contorno. |
| **DEM (raster)** | Modello digitale del terreno, facoltativo. Utilizzato per l'assegnazione delle quote nodali secondo le regole del §5.4. |
| **Cartella output** | Cartella di destinazione di file di ingresso, risultati e layer persistiti (§7.6). Unica per l'intera elaborazione. Obbligatoria per il comando *Genera CSV* e per l'esecuzione in parallelo. |
| **Ora del giorno** | Indice orario 0–23 che seleziona il valore da estrarre dal profilo di domanda (§5.6). L'etichetta sottostante riporta il valore letto dal primo nodo dotato di profilo: costituisce la verifica immediata della corretta interpretazione del campo. |
| **Simula 24 ore in parallelo (0-23)** | Esecuzione simultanea dei 24 scenari orari (§7.3). |

### 5.3 Blocco 2 — Modalità di costruzione del modello

La casella **Rete già collassata** determina se il grafo di calcolo debba
essere costruito dalla geometria (Modalità A) o assunto dai layer (Modalità B).

#### 5.3.1 Modalità A — costruzione del grafo dalla geometria

Attiva quando la casella è deselezionata (condizione di default). Il plugin
esegue il **collasso topologico**: esplode le polilinee, identifica gli estremi
coincidenti, genera i nodi, assegna gli identificativi e calcola le lunghezze
dalla geometria tridimensionale.

Al termine vengono aggiunti al progetto due layer, denominati `Condotte #N` e
`Nodi #N`, che costituiscono la rete effettivamente simulata.

**Comportamento da conoscere prima di adottare questa modalità:**

1. **Gli identificativi dei nodi sono generati dal plugin**, mediante un
   contatore progressivo che parte da **0** nell'ordine in cui gli estremi sono
   incontrati durante la scansione delle condotte. Gli identificativi
   eventualmente presenti nel layer nodi **non sono conservati**: essi
   sopravvivono unicamente nei campi `fid_ut` e `label_ut` del layer `Nodi #N`.
   La corrispondenza fra i propri nodi e quelli dei risultati va ricostruita
   attraverso tali campi o per via geometrica.
2. **Gli identificativi delle condotte** sono rinumerati progressivamente a
   partire da 1.
3. **Le quote non provengono dal layer nodi** (§5.4).

Il riquadro **Opzioni Collasso** espone:

| Campo | Descrizione |
|-------|-------------|
| **Diametro** e **Unità** | Campo del layer condotte contenente il diametro interno e relativa unità: `pollici (in)` — prima voce, quindi default —, `metri (m)`, `centimetri (cm)`. Il riconoscimento automatico del campo procede nell'ordine: `diameter_m`, `diam_m`, `D`, `d`, `diam`, `Diametro_pollici`, `Diametro`, `diameter`. La verifica dell'unità è essenziale: per la (2.5) la portata dipende da D^2,5, per cui un errore di unità di fattore 39,37 produce uno scostamento di circa dieci ordini di grandezza sulla capacità di trasporto. |
| **Campo reference** e valore | Campo del layer nodi e valore che identificano i nodi a pressione imposta (per esempio `type` = `reference`, oppure `is_ref` = `1`). Candidati provati automaticamente: `matched`, `type`, `Type`, `NodeID`, `is_ref`, `reference`, `nodo_tipo`. Il confronto è eseguito sia in forma testuale sia numerica. **Se il valore è lasciato vuoto, tutti i nodi agganciati sono trattati come nodi di riferimento**: la rete risulta a pressione imposta ovunque e i risultati privi di significato (§12.5). |

In Modalità A il campo dei consumi orari e il raggio di aggancio risiedono nel
blocco *⚙ Opzioni avanzate* (§6.2).

#### 5.3.2 Modalità B — grafo assunto dai layer

Attiva quando la casella è selezionata. Presuppone che ciascuna condotta
dichiari esplicitamente i due nodi collegati. È la modalità da utilizzare
quando gli identificativi e le quote devono essere conservati, e quella
adottata nel caso di verifica del §11.

I layer tipicamente impiegati sono `Condotte #N` e `Nodi #N` prodotti da un
collasso precedente, che il plugin preseleziona automaticamente, oppure layer
predisposti dall'utente con i campi richiesti.

### 5.4 Origine delle quote nodali

La quota h che compare nella (2.8) è determinata come segue.

| Modalità | Origine della quota |
|----------|---------------------|
| A, geometria delle condotte tridimensionale (LineString Z) | Coordinata Z dei vertici |
| A, geometria bidimensionale, DEM assegnato | Campionamento del DEM alle coordinate dei nodi |
| A, geometria bidimensionale, DEM assente | **h = 0 per tutti i nodi**: il termine (2.8) si annulla |
| A, opzione *Preserva nodi intermedi* attiva | Campionamento del DEM per ogni nodo, compresi gli intermedi (§6.2) |
| B | Campo mappato in *Altitudine* (§5.5.2) |

Il campo altitudine del layer nodi **non è utilizzato in Modalità A**. È un
punto di attenzione: una rete con dislivelli significativi simulata in Modalità
A senza DEM e con geometria bidimensionale restituisce pressioni prive del
contributo geodetico, che alle pressioni di trasporto è dell'ordine di 0,1 bar
ogni 100 m di dislivello.

### 5.5 Mappatura dei campi (Modalità B)

#### 5.5.1 Condotte

| Campo interfaccia | Colonna prodotta | Riconoscimento automatico |
|-------------------|------------------|----------------------------|
| **ID pipe** | `pipeline_index` | `pipe_id`, `id`, `FID`, `fid`, `OBJECTID` |
| **Nodo A / B** | `inlet_index` / `outlet_index` | A: `node_a`, `from_node`, `inlet`, `a`, `start_node`; B: `node_b`, `to_node`, `outlet`, `b`, `end_node` |
| **Lunghezza** | `length_m` | `length_m`, `length`, `L`, `len`, `lunghezza`, `lung_m` |
| **Diametro** e unità | `diameter_m` | come in §5.3.1 |

L'orientamento A → B è convenzionale (§2.1): il verso effettivo del flusso è
restituito dal segno della portata (§10.2).

#### 5.5.2 Nodi

| Campo interfaccia | Colonna prodotta | Note |
|-------------------|------------------|------|
| **ID nodo** | `node_index` | Intero, coerente con i valori usati in Nodo A / Nodo B. Candidati: `node_id`, `id`, `FID`, `fid`, `OBJECTID`. |
| **Altitudine** | `altitude_m` | Candidati: `altitude_m`, `z_m`, `elev`, `altitude`, `alt`, `ALTITUDINE`, `quota`. In assenza del campo si assume h = 0. |
| **Flag reference** e valore | `node_type` = `reference` | Valore proposto: `1`. |
| **Flusso orario nodi** | `flow_sm3_per_s` | Profilo di domanda (§5.6). Se non assegnato, tutti i nodi ricevono il valore di ripiego e la rete risulta priva di domanda. |

### 5.6 Profilo di domanda oraria

**Formato.** Stringa contenente fino a 24 valori numerici separati dal
carattere impostato in *Separatore flussi* (default `;`):

```
1250.0;1180.5;1100.2; … ;1310.8
```

**Unità.** Smc/h. La conversione alle unità del modello è

    D = valore / 3600     [sm³/s]                                         (5.1)

**Selezione del valore.** Viene estratto l'elemento di indice pari all'*Ora del
giorno*; se la stringa contiene un numero di valori inferiore all'indice
richiesto, viene utilizzato l'ultimo disponibile. **Un valore singolo è
pertanto valido per qualunque ora** e rappresenta una domanda costante.

**Convenzione di segno.**

| Valore | Significato | Effetto |
|--------|-------------|---------|
| > 0 | Prelievo | D_i > 0 nella (2.3) |
| < 0 | Immissione in rete | D_i < 0 nella (2.3) |
| 0, vuoto, `NULL` | Nodo di transito | Assegnazione del valore di ripiego (§6.2) |

La convenzione di segno consente di modellare punti di immissione (biometano,
elettrolizzatori, interconnessioni) senza ricorrere a nodi di riferimento
aggiuntivi, che imporrebbero anche la pressione.

### 5.7 Composizione per nodo

Se il layer nodi contiene un campo denominato esattamente **`gas_comp`**, il
suo contenuto è assunto come composizione molare del nodo, in sostituzione
della composizione generale (§6.4).

La presenza di almeno una composizione nodale attiva lo schema di
accoppiamento staggered descritto al §2.6, segnalato nel log con
`Composizioni multiple rilevate`. I risultati includono in tal caso la
composizione locale (`gas_comp`) e la frazione di idrogeno (`h2_pct`) nodo per
nodo (§9.2).

### 5.8 Struttura dei file di ingresso prodotti

Separatore di campo `;`.

**`sf_nodes.csv`**

```
node_index;pressure_pa;flow_MW;flow_sm3_per_s;altitude_m;temperature_k;gas_composition;node_type;latitude;longitude;flow_type
1;7500000.0;;;10.0;288.15;{'methane': 0.86909, …};reference;;;volumetric
2;;;1e-06;50.0;;;;;;volumetric
3;;;3.33333333;120.0;;;;;;volumetric
```

I nodi di riferimento riportano pressione (relativa, cfr. 2.2), temperatura e
composizione; i nodi di domanda riportano portata e quota.

**`sf_pipelines.csv`**

```
pipeline_index;inlet_index;outlet_index;diameter_m;length_m;friction_method;roughness_m
1;1;2;0.508;12000.0;chen;1.2e-05
```

L'ispezione di questi due file dopo l'esecuzione del comando *Genera CSV*
costituisce la verifica più diretta della correttezza della mappatura: un
errore presente in questa fase si propaga inalterato ai risultati.

---

## 6. Tab 1 — Parametri fisici e numerici

Tutti i parametri di questa sezione risiedono nei blocchi richiudibili del
Tab 1. Per ciascuno si riportano simbolo, unità, valore di default e intervallo
ammesso.

### 6.1 ⚙ Compressori

Blocco attivabile per le reti dotate di stazioni di compressione.

| Campo | Descrizione |
|-------|-------------|
| **Campo e Valore** | Campo del layer nodi e valore che identificano i nodi compressore. |
| **Pressione OUT** [bar] | Accetta indifferentemente il nome di un campo del layer nodi contenente la pressione di mandata, oppure un valore numerico costante (per esempio `70.0`). |

#### 6.1.1 Formulazione

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

#### 6.1.2 Avvertenza

In assenza di *Pressione OUT* il motore adotta un rapporto di compressione di
ripiego pari a **1,1** (§13.3), insufficiente in condizioni di carico reale e
tipicamente causa di divergenza con pressioni che collassano. Il plugin emette
un avviso non bloccante prima dell'avvio.

#### 6.1.3 Grandezze restituite

A convergenza è calcolata la potenza isentropica assorbita da ciascuna
stazione:

    P = cp · T₁ · [ r^((n−1)/n) − 1 ] · ṁ / (η · 10⁶)        [MW]         (6.1)

con r = p_out/p_in rapporto effettivo, n = cp/cv, ṁ portata massica, η
rendimento. I valori sono scritti in `results_compressors.csv` (§10.4).

### 6.2 ⚙ Opzioni avanzate

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

### 6.3 ⚙ Parametri solutore

Riferimento teorico: §2.7.

| Parametro | Unità | Default | Intervallo | Descrizione |
|-----------|-------|---------|------------|-------------|
| **Max iterazioni** | — | 50 | 10–2000 | Numero massimo di iterazioni di Newton-Raphson. Si veda l'avvertenza 6.3.1. |
| **Tolleranza** | Sm³/s | 0,001 | 1×10⁻⁴–10 | Soglia del criterio (2.14): massimo squilibrio di bilancio ammesso per nodo. Il riquadro adiacente riporta l'equivalente in Sm³/h (moltiplicazione per 3600): il default corrisponde a 3,6 Sm³/h. |
| **URF** | — | 2,0 | 0,1–20 | Fattore di sotto-rilassamento della (2.13). **Compare a denominatore**: valori maggiori riducono l'ampiezza del passo e stabilizzano l'iterazione; valori inferiori a 1 amplificano il passo di Newton. Il valore assegnato costituisce il limite inferiore adottato dallo schema adattativo (§2.7). |
| **Auto-calibra tol e URF** | — | disattivo | — | Assegna tolleranza e URF in funzione del numero di nodi secondo la tabella §13.1.1 e, in caso di mancata convergenza, percorre la medesima scala verso combinazioni più rilassate. L'attivazione disabilita i due campi corrispondenti. |
| **Affina precisione** | — | disattivo | — | Successivamente alla prima convergenza, ripete la soluzione con tolleranze decrescenti — prima per fattori di 10, quindi per bisezione in scala logaritmica — fino al limite di 1×10⁻⁴, conservando il risultato corrispondente alla tolleranza minima effettivamente raggiunta. Indipendente da *Auto-calibra*: quest'ultima definisce il punto di partenza, *Affina precisione* il punto di arrivo. Il valore da riportare in sede di documentazione dei risultati è la tolleranza **finale**, indicata nel log. |
| **Forza Multiprocesso** | — | attivo | — | Esecuzione in processi Python indipendenti, necessaria affinché le simulazioni parallele (§7.3, §7.4) utilizzino effettivamente più core. |

#### 6.3.1 Avvertenza sul numero massimo di iterazioni

Il numero di iterazioni necessarie dipende dalla distanza fra lo stato iniziale
e la soluzione, non dalla dimensione della rete. Nelle prove di verifica
condotte su questo plugin (§11.7) il valore di default di 50 iterazioni si è
rivelato **insufficiente** su tutte e tre le reti provate, comprese due reti di
4 e 10 nodi; la rete del §11 converge in 92 iterazioni.

Si raccomanda pertanto di assumere **Max iterazioni = 200** come punto di
partenza. L'incremento non comporta penalizzazioni: il calcolo termina
comunque al raggiungimento del criterio (2.14).

### 6.4 Composizione Gas

| Campo | Descrizione |
|-------|-------------|
| **Gas base** | Preset di composizione: *SNAM — Mazara del Vallo (gas algerino)* (default), *SNAM — Gela (gas libico)*, *Metano puro (100% CH₄)*, *Gas naturale tipico (94% CH₄)*, *Idrogeno puro (H₂)*, *Personalizzato…*. Le frazioni molari sono riportate al §13.3. |
| **Aggiunta H₂** | Frazione **molare** di idrogeno addizionata al gas base, 0–99 %. La composizione di base è riscalata proporzionalmente: indicata con x la frazione di H₂ e con y_k le frazioni del gas base, la miscela risultante ha frazioni y_k·(1−x) e frazione di idrogeno x. |
| **Composizione export** | Composizione effettivamente scritta nel file di ingresso. È aggiornata automaticamente in funzione dei due campi precedenti ed è modificabile manualmente per composizioni non previste dai preset; in tal caso il preset assume il valore *Personalizzato*. |

#### 6.4.1 Componenti ammessi

`methane`, `ethane`, `propane`, `isobutane`, `butane`, `isopentane`,
`pentane`, `hexane`, `nitrogen`, `carbon dioxide`, `helium`, `hydrogen`.

La chiave dell'anidride carbonica è **`carbon dioxide`**, con spazio. Le
frazioni molari devono avere somma unitaria.

#### 6.4.2 Effetto della composizione sulla soluzione idraulica

La composizione interviene nella (2.4) attraverso SG e Z e nella (2.9)
attraverso il numero di Reynolds. A parità di portata volumetrica standard,
una miscela a densità relativa inferiore — per esempio addizionata di idrogeno
— presenta minore perdita di carico e maggiore velocità, ma minore contenuto
energetico per unità di volume. La valutazione di uno scenario di blending
richiede pertanto l'esame congiunto di pressione, velocità, potere calorifico
e indice di Wobbe (§9.4).

---

## 7. Esecuzione e file prodotti

### 7.1 Comandi

I comandi risiedono nella colonna destra del Tab 1.

| Comando | Funzione |
|---------|----------|
| **↺ Ricarica layer** | Aggiorna gli elenchi dei layer del progetto. |
| **> Genera CSV** | Esegue costruzione del modello e mappatura e scrive i file di ingresso, senza avviare il solutore. In Modalità B è denominato *Genera CSV da Layer*. |
| **Solo export CSV** | Opzione: i risultati sono scritti su file ma non sono creati layer in QGIS. Riduce sensibilmente il tempo di esecuzione su reti estese. |
| **▶ Avvia Simulazione** | Genera i file di ingresso ed esegue il solutore. |
| **⏹ Ferma** | Interrompe l'elaborazione in corso. |
| **Campagna** | Esecuzione sequenziale del batch orario su una serie di giorni (§7.4). |

In assenza di cartella di output, una simulazione singola utilizza una cartella
temporanea di sistema; *Genera CSV* e l'esecuzione in parallelo la richiedono
esplicitamente.

### 7.2 Controlli preliminari

#### 7.2.1 Condizioni bloccanti

- Modalità A: layer condotte non selezionato.
- Modalità B: layer condotte o layer nodi collassati non selezionati.
- Entrambe: assenza di nodi di riferimento al termine della costruzione del
  modello.

#### 7.2.2 Condizioni di avvertimento

Le seguenti condizioni producono un avviso con richiesta di conferma; la
prosecuzione è ammessa ma in ciascun caso i risultati risultano compromessi:

| Condizione | Conseguenza |
|------------|-------------|
| Layer nodi non selezionato | Assenza di condizioni al contorno: sistema indeterminato |
| Campo *Flag reference* non assegnato | Tutti i nodi trattati come riferimento |
| Valore del flag reference vuoto | Tutti i nodi agganciati trattati come riferimento |
| Compressori attivi senza *Pressione OUT* | Rapporto di ripiego 1,1 (§6.1.2) |

### 7.3 Esecuzione

Il calcolo è eseguito in un thread separato e, se attiva l'opzione
*Forza Multiprocesso*, in processi indipendenti: l'interfaccia di QGIS resta
utilizzabile.

Il log riporta, nell'ordine:

1. cartella di lavoro e pressione di riferimento applicata;
2. esito della validazione dei file di ingresso, con la composizione adottata.
   In questa fase il plugin: scrive temperatura, pressione e composizione sui
   nodi di riferimento; sostituisce le domande nulle o assenti con il flusso di
   ripiego; azzera le quote mancanti; impone `friction_method = chen`;
3. eventuali messaggi relativi a compressori e composizioni multiple;
4. i parametri numerici effettivamente adottati;
5. l'esito: `✓ SIMULAZIONE CONVERSA in N iterazioni!` oppure segnalazione di
   mancata convergenza seguita da `Estraggo l'ultima soluzione calcolata…`;
6. percorso dei risultati e tempo di elaborazione.

Al termine di una simulazione singola sono creati i layer dei risultati e
l'interfaccia passa automaticamente al Tab 2.

#### 7.3.1 Batch orario

L'opzione **Simula 24 ore in parallelo** esegue i 24 scenari orari
simultaneamente. Il grado di parallelismo è determinato dal numero di core
fisici stimati ed è dichiarato nel log. Il riepilogo finale riporta il numero
di ore converse, l'elenco di quelle non converse e il tempo complessivo.

### 7.4 Campagna multi-giorno

Il comando **Campagna** ripete il batch orario su una serie di giorni. La
rete (layer condotte) è comune; variano i layer dei nodi, che rappresentano i
profili di domanda dei singoli giorni.

La procedura richiede: la sorgente dei giorni (file su disco in formato
`.geojson`, `.shp` o equivalente, oppure layer già caricati nel progetto); la
cartella di output; la conferma, con indicazione del numero totale di
simulazioni (giorni × 24).

Durante la campagna l'opzione *Solo export CSV* è forzata e le finestre di
dialogo sono soppresse: un giorno che non superi i controlli del §7.2 viene
saltato e registrato nel log, senza interrompere l'elaborazione. Il riepilogo
finale riporta giorni completati, giorni con 24 ore converse su 24, totale
delle simulazioni converse e tempo complessivo.

### 7.5 Esito della simulazione

Il solutore restituisce un risultato anche in caso di mancata convergenza
(§2.7.1). Tale risultato è l'ultimo iterato calcolato: **non soddisfa i
bilanci nodali e non rappresenta uno stato fisicamente ammissibile**, pur
avendo l'aspetto di una soluzione ordinaria.

L'esito è dichiarato in tre forme: messaggio nel log, colore della riga
conclusiva e — elemento determinante — **suffisso del nome della cartella dei
risultati**, `_OK` oppure `_NONCONV`. La verifica del suffisso deve precedere
qualsiasi utilizzo dei valori prodotti.

### 7.6 Organizzazione dei file prodotti

Ogni esecuzione genera una sottocartella progressiva; nessun file viene
sovrascritto.

```
<cartella output>/
├─ _warmstart_seed.csv              pressioni dell'ultima soluzione conversa
├─ run_001/
│  ├─ input/
│  │  ├─ sf_nodes.csv               dati di ingresso generati (§5.8)
│  │  ├─ sf_pipelines.csv
│  │  └─ sf_compressors.csv         se presenti stazioni di compressione
│  ├─ output/
│  │  └─ convergence_log.txt        diagnostica per iterazione (§12.10)
│  └─ h00_OK/                       risultati dell'ora 0, convergenza raggiunta
│     ├─ results_nodes.csv
│     ├─ results_pipes.csv
│     ├─ results_compressors.csv
│     ├─ run_info.json           provenienza del calcolo (§7.8)
│     ├─ R-N-<nome>_#1.gpkg
│     └─ R-P-<nome>_#1.gpkg
└─ run_002/ …
```

Note:

- i file dei risultati adottano il separatore `;`;
- rieseguendo la medesima ora con esito diverso, la cartella corrispondente
  all'esito precedente viene rimossa, evitando la coesistenza di risultati
  contraddittori;
- i layer dei risultati sono persistiti come **GeoPackage** nella medesima
  cartella: il layer presente in QGIS fa riferimento a tale file e permane alla
  chiusura del progetto;
- il file `_warmstart_seed.csv`, scritto al termine di ogni simulazione singola
  conversa, è riutilizzato come stato iniziale dalle esecuzioni successive
  (§2.7), riducendone il numero di iterazioni.

### 7.7 Layer prodotti nel progetto

| Denominazione | Contenuto |
|---------------|-----------|
| `Condotte #N` / `Nodi #N` | Rete collassata, effettivamente simulata (Modalità A) |
| `R-N-<nome> #N` | Risultati nodali (§9) |
| `R-P-<nome> #N` | Risultati sulle condotte (§10) |
| `R-P-orig-<nome> #N` | Risultati riportati sulla geometria originale, se richiesto (§6.2) |

L'indice progressivo `#N` è incrementato ad ogni esecuzione: **i layer delle
simulazioni precedenti non vengono rimossi**. La scelta consente il confronto
diretto fra scenari (§8.4) ma comporta l'accumulo progressivo di elementi nella
legenda.

### 7.8 Tracciabilità dei risultati

La versione del plugin e quella del motore di calcolo sono **indipendenti**: il
plugin usa un fork di GasNetSim contenente modifiche non presenti in alcuna
versione rilasciata a monte, per cui la sola stringa di versione del motore non
è sufficiente a identificare il codice eseguito.

Ogni esecuzione registra pertanto entrambe le identità in due punti:

1. la **prima riga del log**, nella forma
   `GasNetSim_4Qgis 0.9.0 · motore GasNetSim 0.2.2 (improvement/modular-simulation-architecture @ 6079ec1)`;
2. il file **`run_info.json`**, scritto nella cartella dei risultati accanto ai
   CSV, che contiene:

| Blocco | Contenuto |
|--------|-----------|
| `plugin` | nome e versione del plugin |
| `engine` | versione dichiarata del motore, branch e commit del clone da cui è importato, percorso di installazione |
| `run` | data e ora, ora simulata, esito di convergenza, numero di iterazioni, tempo di calcolo |
| `parameters` | pressione di riferimento, temperatura, rugosità, portate di ripiego, numero massimo di iterazioni, tolleranza, URF, auto-calibrazione, affinamento, composizione del gas |

Il file è scritto in formato JSON separato, e non come intestazione dei CSV,
affinché i file di risultato restino leggibili da qualunque parser senza
opzioni aggiuntive.

Il contenuto di `run_info.json` è l'informazione minima da riportare nella
documentazione di un risultato pubblicato: identifica il codice e i parametri
con cui esso è stato prodotto, e consente di ripetere il calcolo anche dopo
che i file siano stati spostati o rielaborati. Si noti che il commit del motore
viene letto dal clone da cui il pacchetto è importato: un'installazione
effettuata clonando un *branch* anziché un tag o un commit specifico non
garantisce che altri ottengano lo stesso motore.

---

## 8. Tab 2 — Post-processing e rappresentazione

La scheda non esegue calcoli: governa la rappresentazione tematica dei
risultati e la loro esportazione. L'interfaccia vi accede automaticamente al
termine di una simulazione singola.

### 8.1 Visualizza risultati su layer

Applica una nuova rappresentazione tematica a layer già esistenti, senza
ripetere il calcolo.

| Campo | Descrizione |
|-------|-------------|
| **Layer nodi** | Layer da rappresentare. I layer dei risultati (`R-N-…`) sono elencati per primi; è ammessa la selezione di qualunque layer vettoriale del progetto, compresi quelli di simulazioni precedenti. |
| **Colora nodi per** | Campo che governa la scala cromatica. L'elenco riporta i soli campi presenti nel layer selezionato. |
| **Dimensiona nodi per** | Rende il raggio del simbolo proporzionale al valore assoluto del campo scelto. |
| **Layer condotte** | Analogo per il layer lineare (`R-P-…`). |
| **Colora condotte per** | Campo che governa la scala cromatica delle condotte. |
| **Frecce direzione flusso** | Marcatore orientato secondo il verso effettivo del flusso, cioè secondo il segno di `flow_sm3h` (§10.2) e non secondo l'orientamento della geometria. |
| **▶ Applica colorimetria** | Applica le impostazioni. Il comando adiacente aggiorna l'elenco dei layer. |

#### 8.1.1 Criteri di rappresentazione

La classificazione è **graduata a classi quantili**, con numerosità
approssimativamente uniforme per classe. Per le condotte lo spessore della
linea è reso proporzionale alla portata assoluta, in modo da evidenziare la
gerarchia di trasporto. Il campo `h2_pct` adotta una scala dedicata,
progressiva dal bianco/giallo (frazione nulla) al rosso.

L'uso di classi quantili implica che la scala cromatica sia **relativa al
singolo layer**: due simulazioni rappresentate con la stessa impostazione non
sono confrontabili per colore, ma solo per valore. Per confronti quantitativi
si utilizzino i valori numerici o una classificazione manuale a intervalli
fissati, impostabile con gli strumenti standard di QGIS.

### 8.2 Impostazioni per la prossima simulazione

Definisce i campi che verranno prodotti dalla simulazione successiva e la loro
rappresentazione iniziale. Non ha effetto sui risultati già calcolati.

**Nodi.** Campo di colorazione iniziale (default *Pressione*), campo di
dimensionamento (default assente) e selezione dei campi da produrre. Sono
attivi per default: pressione, consumo volumetrico, consumo energetico,
temperatura, densità relativa, fattore Z, potere calorifico, indice di Wobbe,
frazione di H₂, composizione e throughput; risultano disattivi densità, densità
standard, massa molare e tipo nodo.

**Condotte.** Campo di colorazione iniziale (default *Portata*) e selezione dei
campi: attivi per default portata con segno, portata assoluta, velocità,
pressione media e densità relativa; disattivi fattore Z e densità.

**Mostra frecce direzione flusso**: disattivo per default.

Un campo non selezionato non è scritto nel layer e non è pertanto disponibile
per la rappresentazione del §8.1 fino a nuova simulazione. I campi nodali
`volumetric_flow_sm3s`, `energy_flow_mw` e `node_type` sono presenti nei soli
layer QGIS e non nei file CSV (§9.1).

### 8.3 Esporta dati

| Campo | Descrizione |
|-------|-------------|
| **Layer** | Layer da esportare. |
| **Decimali** | Cifre decimali dei valori numerici. |
| **Esporta CSV** | Selezione del percorso di destinazione. |

La funzione è complementare ai file `results_nodes.csv` e `results_pipes.csv`
prodotti automaticamente (§7.6): consente di esportare un sottoinsieme, una
diversa precisione, o un layer la cui simbologia sia stata modificata
manualmente.

### 8.4 Confronto fra scenari

L'accumulo dei layer dei risultati (§7.7) consente il confronto diretto:

1. esecuzione dello scenario di riferimento;
2. modifica del parametro oggetto di analisi — ad esempio la frazione di
   idrogeno (§6.4) — e nuova esecuzione;
3. selezione alternata dei layer `#1` e `#2` sul medesimo campo, nel blocco
   §8.1.

Per il confronto quantitativo si utilizzino i file `results_nodes.csv` delle
rispettive cartelle `run_NNN/h<ora>_OK/`, tenendo presente quanto osservato al
§8.1.1 sulla non confrontabilità delle scale cromatiche quantili.

---

## 9. Grandezze calcolate ai nodi

### 9.1 Elenco delle grandezze

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

### 9.2 Grandezze di composizione

In presenza di una sola composizione, `sp_gravity`, `hhv_mj_sm3`,
`wobbe_mj_sm3`, `molar_mass`, `std_density_kg_sm3` e `h2_pct` risultano
uniformi sull'intera rete, mentre `z_factor` e `density_kg_m3` variano con la
pressione locale.

In presenza di immissioni a composizione differente (§5.7) tutte le grandezze
di composizione variano da nodo a nodo secondo il campo di miscelazione
risolto con lo schema del §2.6. La distribuzione di `h2_pct` descrive in tal
caso la diluizione dell'idrogeno a partire dai punti di immissione e
costituisce il risultato di interesse negli studi di blending parziale.

### 9.3 Ordini di grandezza attesi

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

### 9.4 Criteri di lettura

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

---

## 10. Grandezze calcolate sulle condotte e sui compressori

### 10.1 Grandezze sulle condotte

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

### 10.2 Convenzione di segno e verso del flusso

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

### 10.3 Velocità

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

### 10.4 Grandezze sulle stazioni di compressione

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

### 10.5 Verifiche di coerenza

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

---

## 11. Caso di verifica riproducibile

Il caso descritto in questa sezione ha due finalità: **validare
l'installazione**, confrontando i valori ottenuti con quelli riportati, e
illustrare il flusso di lavoro completo su un modello di dimensioni minime.

I valori attesi del §11.5 sono stati ottenuti eseguendo il motore di calcolo
sui file di ingresso prodotti dalla procedura qui descritta; le condizioni
della verifica sono dichiarate al §11.7.

### 11.1 Descrizione del caso

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

### 11.2 Preparazione dei dati

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

### 11.3 Caricamento in QGIS

Per ciascun file: **Layer → Aggiungi layer → Aggiungi layer da testo
delimitato**; formato CSV, separatore virgola; *Definizione geometria* =
**Geometria well-known text (WKT)**, campo geometria `wkt`; sistema di
riferimento **EPSG:25833 — ETRS89 / UTM zona 33N**, coerente con il sistema
interno del plugin (§3.5).

Il risultato è un layer lineare di 3 elementi e un layer puntuale di 4
elementi, sovrapposti.

### 11.4 Configurazione ed esecuzione

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

### 11.5 Valori attesi

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

### 11.6 Verifiche sul risultato

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

### 11.7 Condizioni della verifica

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

---

## 12. Diagnostica della convergenza

La mancata convergenza si verifica quando il criterio (2.14) non è soddisfatto
entro il numero di iterazioni assegnato. Il solutore restituisce comunque
l'ultimo iterato, segnalato dal suffisso `_NONCONV` della cartella dei
risultati (§7.5): si tratta di uno stato intermedio, privo di significato
fisico, che non soddisfa i bilanci nodali.

Si sottolinea che la convergenza è proprietà del problema — topologia,
domande, diametri, stato iniziale — in combinazione con l'algoritmo impiegato,
e non del programma. Di quest'ultimo dipendono unicamente i valori di default
dei parametri numerici e lo schema di accoppiamento adottato (§12.3); tutte le
restanti cause elencate di seguito risiedono nei dati o nella rete.

La presente sezione elenca le cause in ordine di frequenza osservata, con le
verifiche corrispondenti.

### 12.1 Numero di iterazioni insufficiente

**Frequenza: la più elevata.** Il numero di iterazioni necessarie dipende dalla
distanza fra lo stato iniziale e la soluzione, non dalla dimensione della rete.
Nelle prove condotte (§11.7) il valore di default di 50 iterazioni non è
risultato sufficiente su nessuna delle tre reti esaminate:

| Rete | Nodi | Esito con 50 iterazioni | Esito con 200 |
|------|------|--------------------------|----------------|
| Caso di verifica (§11) | 4 | non converge | converge in 92 iterazioni |
| `toy_network_h2` | 10 | non converge | non determinato |
| `Sicily_transmission_network` | 340 | non converge (residuo 1×10⁻¹ Sm³/s) | non determinato |

**Azione.** Portare *Max iterazioni* a 200, se necessario a 500. L'incremento
non comporta penalizzazioni: l'esecuzione termina al soddisfacimento della
(2.14).

### 12.2 Passo di Newton non smorzato a sufficienza

Se il residuo oscilla senza decrescere — condizione frequente quando condotte
di diametro molto diverso sono direttamente connesse — l'ampiezza del passo è
eccessiva.

**Azione.** **Aumentare** l'URF, per esempio da 2,0 a 4,0. Si ricorda che
l'URF compare a denominatore nella (2.13): valori maggiori riducono il passo e
stabilizzano l'iterazione; valori minori di 1 amplificano il passo di Newton e
sono da riservare a reti che convergono agevolmente e per le quali si intenda
ridurre il numero di iterazioni.

Successivamente si può rilassare la tolleranza, da 0,001 a 0,01 Sm³/s
(36 Smc/h di squilibrio ammesso per nodo, trascurabile su reti che trasportano
centinaia di migliaia di Smc/h).

L'opzione *Auto-calibra tol e URF* automatizza questa ricerca, percorrendo la
scala del §13.1.1 verso combinazioni progressivamente più rilassate. Si
verifichi nel log con quali valori la convergenza è stata effettivamente
conseguita, poiché le tolleranze impiegate sono sensibilmente più larghe del
default.

### 12.3 Schema di accoppiamento adottato

La convergenza non è una proprietà del software: dipende dal problema —
topologia, domande, diametri, stato iniziale — in combinazione con l'algoritmo
impiegato per risolverlo. Il plugin determina tuttavia tre elementi
dell'algoritmo, e sono i soli su cui esso intervenga:

1. il numero massimo di iterazioni (§12.1), il cui valore di default è 50;
2. lo schema di accoppiamento fra problema idraulico e tracciamento della
   composizione;
3. le tolleranze del ciclo esterno dello schema staggered, imposte a
   `coupling_tol = tol × 10⁻²` e `coupling_max_iter = max_iter` in luogo dei
   valori predefiniti del motore (10⁻⁴ e 20).

#### 12.3.1 Criterio di selezione

Lo schema staggered è attivato quando almeno un nodo non di riferimento
possiede una composizione propria nel file `sf_nodes.csv` (§5.7); in caso
contrario si adotta lo schema diretto. Il criterio è di natura sintattica —
presenza di un valore in un campo — e non numerica: non dipende in alcun modo
dalla difficoltà del problema.

#### 12.3.2 Ragione dell'influenza dello schema

Nello schema diretto la miscela attribuita a ciascuna condotta è ridefinita in
base al segno della portata a ogni valutazione del residuo. Se le composizioni
nodali differiscono fra loro, una condotta che inverte il flusso nel corso
dell'iterazione muta la propria miscela e con essa le proprietà del gas: la
funzione residuo risulta discontinua in x e la ricerca lineare si arresta senza
conseguire una riduzione del residuo (cfr. i messaggi del §12.10). Lo schema
staggered rimuove la discontinuità congelando la composizione durante il passo
di Newton e aggiornandola in un passo distinto, a pressioni fissate, con
rilassamento.

Ne consegue che su una rete a composizione unica i due schemi coincidono nella
sostanza, poiché la ridefinizione della miscela restituisce sempre la medesima
miscela. In tal caso la mancata convergenza è da ricondurre al §12.1 e al
§12.2, non allo schema.

#### 12.3.3 Qualità della soluzione

Il passo interno dello schema staggered è il medesimo solutore di Newton dello
schema diretto, invocato con la stessa tolleranza e lo stesso numero massimo di
iterazioni; l'iterazione interna è considerata conclusa solo al soddisfacimento
della (2.14). La convergenza dello schema staggered non è pertanto ottenuta con
un criterio più debole: al criterio (2.14) si aggiungono due condizioni sul
ciclo esterno — variazione massima di pressione fra due iterazioni esterne non
superiore a max(10; tol × 10⁵) Pa e variazione della composizione non superiore
a `coupling_tol`.

#### 12.3.4 Azione

Su reti a composizioni differenti, qualora si osservino arresti della ricerca
lineare, si verifichi nel log la presenza della riga `Composizioni multiple
rilevate`: la sua assenza indica che il campo composizione non è stato letto e
che il problema viene risolto con lo schema diretto. Il campo è denominato
`gas_comp` nel layer nodi (§5.7); l'attribuzione di una composizione a un nodo
di transito non altera la fisica del problema qualora la composizione sia
identica a quella del nodo di riferimento, ma commuta lo schema di soluzione.

### 12.4 Assenza di nodi di riferimento

La simulazione è interrotta prima dell'avvio (§7.2.1). Nessun record del layer
nodi soddisfa la condizione campo = valore impostata in *Campo reference*.

**Verifiche.** Esistenza del campo; presenza del valore atteso (si considerino
le forme `1`, `1.0`, `"1"`); in Modalità A, appartenenza del nodo al raggio di
aggancio (§6.2): un nodo corretto ma distante dalla condotta più del raggio
impostato non viene riconosciuto.

### 12.5 Totalità dei nodi trattati come riferimento

Condizione simmetrica alla precedente, e più insidiosa perché **non impedisce
la convergenza**: con il valore del flag lasciato vuoto tutti i nodi agganciati
assumono pressione imposta. Il sistema (2.3) risulta privo di incognite, la
convergenza è immediata e i risultati sono privi di contenuto.

**Sintomi.** Pressioni identiche o quasi in tutti i nodi; portate incoerenti
con le domande; numero di iterazioni molto ridotto.

### 12.6 Componenti sconnesse

Una componente priva di nodo di riferimento rende il sistema indeterminato.
Sui dati vettoriali di origine non modellistica è la causa più frequente dopo
quella del §12.1.

**Azione.** Procedura del §4.5. Si osservi che l'eliminazione delle componenti
residue è necessaria anche quando esse corrispondono a porzioni realmente
isolate della rete.

### 12.7 Domande non acquisite

**Sintomi.** Pressioni pressoché uniformi; velocità dell'ordine di 10⁻³ m/s;
`throughput_sm3h` prossimo a zero su tutta la rete.

**Verifiche, nell'ordine.**

1. Assegnazione del campo *Flusso orario nodi*. In Modalità A esso risiede nel
   blocco *⚙ Opzioni avanzate* (§6.2) e non nel blocco principale.
2. Valore riportato dall'anteprima sotto *Ora del giorno* (§5.2).
3. Corrispondenza fra il separatore impostato (§6.2) e quello effettivamente
   presente nei dati: una difformità comporta la lettura di un unico valore non
   interpretabile e la conseguente applicazione del valore di ripiego.
4. Unità dei valori: la (5.1) presuppone Smc/h.

### 12.8 Pressioni incoerenti o velocità anomale

**Causa prevalente: unità del diametro.** Il default del menu *Unità* è
`pollici`. Un campo espresso in metri e interpretato in pollici riduce i
diametri di un fattore 39,37; per la dipendenza D^2,5 della (2.5) la capacità
di trasporto risulta ridotta di oltre nove ordini di grandezza, con collasso
delle pressioni. L'errore inverso produce una rete che trasporta qualunque
portata senza perdite apprezzabili.

**Causa secondaria: quote.** In Modalità A le quote non provengono dal layer
nodi (§5.4). L'assenza di DEM con geometrie bidimensionali annulla il termine
(2.8); quote errate o in unità diverse dal metro lo rendono dominante.

### 12.9 Stazioni di compressione

L'omissione della *Pressione OUT* comporta l'adozione del rapporto di ripiego
1,1 (§6.1.2), con divergenza pressoché certa in condizioni di carico.

Qualora la configurazione sia corretta ma la rete non converga, si esaminino le
righe `[compressori]` del log: la procedura esegue dapprima una simulazione
senza compressore. La mancata convergenza di quest'ultima indica che il
problema risiede nella rete e non nella stazione.

### 12.10 Diagnostica per iterazione

Per le simulazioni singole il file
`<cartella>/run_NNN/output/convergence_log.txt` riporta il dettaglio di
ciascuna iterazione. Le righe significative sono quelle relative alle
**equazioni a residuo massimo**, che identificano il nodo il cui bilancio non
chiude e la pressione corrente in tale nodo.

La persistenza del medesimo nodo fra le equazioni critiche indica una causa
locale — domanda incompatibile con la capacità della condotta afferente, nodo
isolato, diametro errato — la cui rimozione è preferibile a qualsiasi
modifica dei parametri numerici.

Messaggi quali `trust region active`, `line search` e `stalled at iteration`
segnalano che il passo è stato ripetutamente ridotto senza ottenere una
diminuzione del residuo: condizione tipica di una discontinuità della funzione
residuo, riconducibile a inversioni di flusso o a commutazioni nella logica dei
compressori.

### 12.11 Tempi di elaborazione elevati

- Attivare *Solo export CSV* quando i layer non sono necessari: la costruzione
  della simbologia su reti estese incide sensibilmente.
- Mantenere attivo *Forza Multiprocesso* per le esecuzioni parallele.
- Evitare cartelle di output soggette a sincronizzazione su servizi cloud: la
  scrittura dei file intermedi ne risulta rallentata.
- In fase esplorativa, ridurre il numero di iterazioni e rilassare la
  tolleranza; l'affinamento (§6.3) è operazione conclusiva, non preliminare.

### 12.12 Lista di controllo prima dell'utilizzo dei risultati

1. Suffisso della cartella dei risultati: `_OK`.
2. Presenza nel log di `✓ SIMULAZIONE CONVERSA` e valore finale della
   tolleranza.
3. Bilancio ai nodi verificato entro la tolleranza (§10.5, §11.6).
4. Pressione al nodo di riferimento pari al valore assegnato più 1,013 bar.
5. Velocità e pressioni entro intervalli plausibili per la specie di condotta
   (§13.5).

---

## 13. Riferimenti tecnici e normativi

### 13.1 Valori di default

| Parametro | Simbolo | Valore | Unità | § |
|-----------|---------|--------|-------|---|
| Pressione di riferimento | p_ref | 75,0 | bar relativi | 6.2 |
| Temperatura | T | 288,15 | K | 6.2 |
| Rugosità assoluta | ε | 1,2×10⁻⁵ | m | 6.2 |
| Flusso placeholder | D_min | 1×10⁻⁴ | sm³/s | 6.2 |
| Flusso minimo export | — | 1×10⁻⁶ | sm³/s | 6.2 |
| Raggio di aggancio | r_s | 50,0 | m | 6.2 |
| Decimali layer risultato | — | 4 | — | 6.2 |
| Numero massimo di iterazioni | — | 50 | — | 6.3 |
| Tolleranza | tol | 1×10⁻³ | Sm³/s | 6.3 |
| Fattore di sotto-rilassamento | URF | 2,0 | — | 6.3 |
| Composizione | — | SNAM Mazara del Vallo | — | 6.4 |
| Correlazione d'attrito | — | Chen (1979) | — | 2.4.2 |
| Equazione di stato | — | GERG-2008 | — | 2.5 |
| Condizioni standard | T_b, p_b | 288,15 K; 101 325 Pa | — | 2.2 |

#### 13.1.1 Scala di auto-calibrazione

| Numero di nodi | tol [Sm³/s] | URF [–] |
|----------------|-------------|---------|
| < 100 | 0,1 | 1,5 |
| < 500 | 1,0 | 2,0 |
| < 2000 | 5,0 | 2,5 |
| ≥ 2000 | 10,0 | 3,0 |

In caso di mancata convergenza la scala è percorsa verso i valori più
rilassati.

### 13.2 Rugosità assoluta per materiale

| Materiale | ε [m] |
|-----------|-------|
| Acciaio con rivestimento interno (trasporto) | 1,2×10⁻⁵ |
| Acciaio non rivestito | 5×10⁻⁵ |
| Polietilene (PE/HDPE) | 7×10⁻⁶ |
| Ghisa | 2,6×10⁻⁴ |

#### 13.2.1 Conversione delle unità di diametro

| Codice | Fattore verso il metro |
|--------|-------------------------|
| `m` | 1 |
| `in` | 0,0254 |
| `cm` | 0,01 |

### 13.3 Composizioni di riferimento

Frazioni molari. Le due composizioni SNAM corrispondono ai principali punti di
ingresso del sistema siciliano.

| Componente | Mazara del Vallo (algerino) | Gela (libico) |
|------------|------------------------------|----------------|
| methane | 0,86909 | 0,86645 |
| ethane | 0,08661 | 0,05246 |
| propane | 0,01163 | 0,02022 |
| isobutane | 0,00072 | 0,00317 |
| butane | 0,00112 | 0,00478 |
| isopentane | 0,00019 | 0,00071 |
| pentane | 0,00019 | 0,00026 |
| hexane | 0,00014 | 0,00060 |
| nitrogen | 0,01334 | 0,04455 |
| carbon dioxide | 0,01672 | 0,00602 |
| helium | 0,00025 | 0,00078 |

Ulteriori preset: `{'methane': 1.0}`; `{'methane': 0.94, 'ethane': 0.04,
'propane': 0.01, 'nitrogen': 0.01}`; `{'hydrogen': 1.0}`.

Parametri di default delle stazioni di compressione: rapporto di compressione
1,1; rendimento 0,85; processo isentropico.

### 13.4 Classificazione delle condotte e qualità del gas

#### 13.4.1 Specie (D.M. 17/04/2008)

| Specie | MOP | Tipologia di rete |
|--------|-----|--------------------|
| 1ª | > 24 bar | Rete nazionale di trasporto |
| 2ª | 12 < MOP ≤ 24 bar | Rete regionale di trasporto |
| 3ª | 5 < MOP ≤ 12 bar | Derivazioni di utenza in alta pressione |
| 4ª | 1,5 < MOP ≤ 5 bar | Distribuzione locale |

#### 13.4.2 Vincolo di densità relativa

La normativa italiana sulla qualità del gas immesso nelle reti di trasporto
fissa un limite inferiore alla densità relativa, d ≥ 0,555. Poiché l'idrogeno
riduce sensibilmente SG (§9.3), tale vincolo — e non il potere calorifico —
determina di norma la frazione massima miscelabile. Per il gas algerino di
Mazara del Vallo il limite è raggiunto in corrispondenza di una frazione molare
di idrogeno pari a circa **13,9 %**, valore adottato nei dati di esempio
distribuiti con il plugin.

> I riferimenti normativi riportati hanno valore orientativo e vanno verificati
> sulla fonte vigente prima di qualsiasi utilizzo in sede formale.

### 13.5 Velocità limite per erosione

Criterio API RP 14E:

    v_e = C / √ρ                                                         (13.1)

con v_e velocità di erosione [m/s], ρ densità del gas nelle condizioni
operative [kg/m³], C = 100 in unità SI per servizio continuo con gas secco.

La (13.1) implica che la velocità ammissibile **decresca** al crescere della
densità, e quindi della pressione di esercizio.

| Specie | MOP | ρ stimata [kg/m³] | v_e [m/s] | Limite pratico [m/s] |
|--------|-----|--------------------|-----------|-----------------------|
| 1ª | 60–70 bar | 44–55 | 10–13 | 10–15 |
| 1ª | 24–40 bar | 17–30 | 13–18 | ≈ 15 |
| 2ª | 12–24 bar | 8–17 | 18–24 | 15–20 |
| 3ª | 5–12 bar | 3,5–8 | 24–35 | ≈ 15 (rumore) |
| 4ª | 1,5–5 bar | 1–3,5 | > 35 | ≈ 10 (rumore) |

### 13.6 Formato dei file

Separatore di campo `;` per tutti i file prodotti e letti dal solutore.

**`sf_nodes.csv`** — `node_index`, `pressure_pa`, `flow_MW`, `flow_sm3_per_s`,
`altitude_m`, `temperature_k`, `gas_composition`, `node_type`, `latitude`,
`longitude`, `flow_type`.

**`sf_pipelines.csv`** — `pipeline_index`, `inlet_index`, `outlet_index`,
`diameter_m`, `length_m`, `friction_method`, `roughness_m`.

**`sf_compressors.csv`** — `compressor_index`, `inlet`, `outlet`,
`compression_ratio`, `efficiency`, `thermodynamic_process`, `control_mode`,
`p_out_target`.

**`results_nodes.csv`**, **`results_pipes.csv`**, **`results_compressors.csv`**
— campi descritti ai §9 e §10.

### 13.7 Riferimenti bibliografici e normativi

1. Chen N.H. (1979). *An Explicit Equation for Friction Factor in Pipe*.
   Industrial & Engineering Chemistry Fundamentals, 18(3), 296–297.
2. ISO 20765-2:2015. *Natural gas — Calculation of thermodynamic properties —
   Part 2: Single-phase properties (gas, liquid, and dense fluid) for extended
   ranges of application* (equazione di stato GERG-2008).
3. UNI EN ISO 13443. *Gas naturale — Condizioni di riferimento standard*.
4. API RP 14E. *Recommended Practice for Design and Installation of Offshore
   Production Platform Piping Systems*.
5. EN 16726. *Gas infrastructure — Quality of gas — Group H*.
6. D.M. 17 aprile 2008. *Regola tecnica per la progettazione, costruzione,
   collaudo, esercizio e sorveglianza delle opere e degli impianti di trasporto
   di gas naturale con densità non superiore a 0,8*.
7. Lu Y. et al. *GasNetSim* — Forschungszentrum Jülich, ICE-1: Energy Systems
   Engineering. Licenza MPL-2.0.
   https://jugit.fz-juelich.de/iek-10/public/simulation/gasnetsim

---

## 14. Nomenclatura e glossario

### 14.1 Simboli

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

### 14.2 Glossario

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
