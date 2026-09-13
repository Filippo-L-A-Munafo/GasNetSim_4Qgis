# Introduzione

## Cos'è GasNetSim 4Qgis

GasNetSim 4Qgis è un plugin per QGIS che calcola **come si comporta una rete di
trasporto o distribuzione del gas**: quanta pressione c'è in ogni punto della
rete, quanto gas passa in ogni condotta e a che velocità, partendo semplicemente
dai dati geografici che già hai in QGIS (le condotte disegnate come linee, i
nodi come punti).

In pratica il plugin fa da ponte fra due mondi:

- **QGIS**, dove la rete è fatta di geometrie (linee e punti) con attributi;
- **GasNetSim**, il motore di calcolo che risolve le equazioni della fisica dei
  gas e restituisce pressioni e portate.

Il plugin si occupa di tutta la parte "noiosa" — tradurre i layer GIS nel
formato che il motore di calcolo si aspetta, lanciare il calcolo, e
ridisegnare i risultati come nuovi layer colorati — così l'utente può
concentrarsi sui dati della propria rete e sull'interpretazione dei risultati.

## A cosa serve, in pratica

Simulare una rete gas prima di intervenire sul campo permette di rispondere a
domande come:

- Se aumento il prelievo in una zona, la pressione resta sopra il minimo
  garantito, o rischio di scendere sotto soglia?
- Una condotta esistente riesce a portare più gas, o va sostituita/raddoppiata?
- Cosa succede se nella rete inietto una miscela di idrogeno e metano invece
  di gas naturale puro (blending H₂/CH₄)?
- Dove si trovano i punti più critici della rete (velocità troppo alte,
  perdite di pressione eccessive)?

Senza un simulatore, rispondere a queste domande richiederebbe misure sul
campo o calcoli manuali molto laboriosi; il plugin li automatizza a partire
dai dati che probabilmente hai già in un progetto QGIS.

## Il flusso di lavoro in due fasi

Il plugin è organizzato in due fasi, corrispondenti alle due schede (tab)
della finestra principale:

1. **Prepara Rete** (Tab 1) — qui dici al plugin *quali* layer di QGIS
   rappresentano la tua rete e *come* leggerne i campi (quale campo è il
   diametro, quale identifica i nodi a pressione nota, ecc.). Il risultato di
   questa fase sono due file CSV — uno per i nodi, uno per le condotte — nel
   formato che il motore di calcolo capisce.
2. **Simula** (Tab 2) — qui imposti i parametri fisici (pressione di
   riferimento, temperatura, composizione del gas) e i parametri del metodo
   di calcolo (tolleranza, numero di iterazioni), poi avvii la simulazione
   vera e propria. Al termine, il plugin crea automaticamente in QGIS due
   nuovi layer con i risultati colorati (pressioni sui nodi, portate e
   velocità sulle condotte).

Le sezioni successive di questa Guida seguono proprio questa struttura:
prima qualche concetto di fisica utile a capire *perché* certi campi esistono
(sezione "Concetti fisici di base"), poi la spiegazione di ogni singolo
elemento dell'interfaccia, tab per tab.

## A chi è rivolta questa guida

Questa guida è pensata per chi **non è né un esperto di reti gas, né un
esperto di QGIS**: ogni funzione viene spiegata sia dal punto di vista pratico
("cosa devo scrivere in questo campo") sia dal punto di vista fisico ("perché
questo dato serve al calcolo, e cosa rappresenta fisicamente"). Se sei già
esperto di uno dei due ambiti, puoi saltare direttamente alla sezione che ti
interessa usando l'elenco a sinistra.

## Come usare questa Guida

Usa l'elenco a sinistra per saltare direttamente alla sezione che ti serve.
La Guida è separata dal pulsante **ℹ Info**, che mostra invece la versione del
plugin, l'autore e i riferimenti di licenza.
