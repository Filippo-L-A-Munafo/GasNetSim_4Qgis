# 3. Architettura dell'interfaccia

## 3.1 Avvio

Il plugin si avvia dall'icona nella barra degli strumenti di QGIS o dal menu
**Plugin → GasNetSim_4Qgis**. Si apre una finestra unica, ridimensionabile,
indipendente dalla finestra principale di QGIS: la mappa resta accessibile
durante la configurazione e durante il calcolo.

## 3.2 Organizzazione della finestra

La finestra è composta da una barra laterale richiudibile e da un contenitore a
tre schede.

### 3.2.1 Barra laterale

Si apre e si chiude con il pulsante **☰** in alto a sinistra.

| Comando | Funzione |
|---------|----------|
| ⚙ Impostazioni | Selezione della lingua dell'interfaccia (italiano/inglese). La modifica ha effetto alla successiva apertura del plugin. |
| Guida | Apre il presente documento. |
| ℹ Info | Versione, autore, repository, licenza. |

### 3.2.2 Schede

| Scheda | Denominazione | Riferimento |
|--------|---------------|-------------|
| Tab 0 | Verifica Condotte | §4 |
| Tab 1 | Prepara e Simula | §5, §6, §7 |
| Tab 2 | Visualizzazione Risultati | §8 |

## 3.3 Struttura del Tab 1

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

## 3.4 Gestione dei dati dell'utente

Il plugin non modifica i layer di origine: i layer topologici, i layer dei
risultati, i file CSV e i GeoPackage prodotti sono elementi nuovi (§7.6).

L'unica eccezione è esplicita e soggetta a conferma: nel Tab 0, l'operazione di
snap degli estremi può essere applicata al layer originale anziché a una copia
(§4.3); se il layer è su file, la modifica è irreversibile.

## 3.5 Sistema di riferimento

Le elaborazioni geometriche interne (costruzione del grafo, aggancio dei nodi,
calcolo delle lunghezze) sono eseguite in **EPSG:25833** (ETRS89 / UTM zona
33N). I layer in sistemi di riferimento diversi vengono riproiettati.

Ne consegue che le grandezze metriche esposte dall'interfaccia — *Raggio
aggancio* (§6.2) e *Tolleranza* di snap (§4.3) — sono espresse in metri. L'uso
di layer in coordinate geografiche (EPSG:4326) è sconsigliato: le tolleranze
andrebbero espresse in gradi e le lunghezze calcolate risulterebbero prive di
significato.

## 3.6 Elementi non presenti

Per evitare ricerche inutili si segnala che l'interfaccia **non** prevede:

- una scheda dedicata ai parametri di simulazione: essi risiedono nei blocchi
  4–6 del Tab 1;
- un campo per la cartella dei file CSV di ingresso: la cartella è unica ed è
  specificata nel blocco 1 del Tab 1 (§5.2);
- una selezione della correlazione d'attrito o dell'equazione di stato: sono
  fissate rispettivamente a Chen (1979) e GERG-2008 (§2.4.2, §2.5).
