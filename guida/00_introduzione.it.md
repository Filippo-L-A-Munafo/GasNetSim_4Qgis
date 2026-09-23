# 1. Introduzione e ambito di applicazione

## 1.1 Oggetto

GasNetSim 4Qgis è un plugin per QGIS che risolve il problema idraulico di
regime stazionario di una rete di trasporto di gas naturale, eventualmente
addizionata di idrogeno, a partire dalla rappresentazione vettoriale della rete
contenuta in un progetto QGIS.

Il plugin costituisce l'interfaccia geospaziale del solutore **GasNetSim**
(Forschungszentrum Jülich, ICE-1) e ne estende le funzionalità con la gestione
delle stazioni di compressione, l'esecuzione parallela di scenari orari e la
restituzione cartografica dei risultati.

## 1.2 Modello risolto

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

## 1.3 Ambito di validità e limitazioni

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

## 1.4 Applicazioni tipiche

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

## 1.5 Architettura dell'elaborazione

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

## 1.6 Struttura del documento

I §2–§3 descrivono il modello e l'organizzazione dell'interfaccia; i §4–§8
documentano, scheda per scheda, ogni controllo esposto; i §9–§10 definiscono le
grandezze restituite; il §11 riporta un **caso di verifica riproducibile**, con
i valori numerici attesi, da eseguire per validare l'installazione; il §12
raccoglie la diagnostica di convergenza; i §13–§14 contengono riferimenti
tecnici, normativi e la nomenclatura.

Le grandezze sono indicate con il simbolo e l'unità di misura adottati nel §14.
Le equazioni sono numerate per sezione e richiamate nel testo.
