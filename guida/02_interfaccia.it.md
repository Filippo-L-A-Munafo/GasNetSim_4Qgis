# L'interfaccia del plugin

Quando apri GasNetSim 4Qgis (icona nella toolbar di QGIS, o menu
**GasNetSim_4Qgis**), si apre un'unica finestra divisa in tre zone
orizzontali, più una barra laterale nascosta.

## I tre pannelli principali

| Pannello | Dove si trova | Cosa contiene |
|----------|----------------|----------------|
| **Preparazione** | Sinistra (la maggior parte della finestra) | Le due schede (tab) "Prepara Rete" e "Parametri Simulazione", descritte nelle prossime sezioni di questa Guida. È qui che si passa la maggior parte del tempo. |
| **Dashboard** | Centro | Il log della simulazione in tempo reale: mostra ogni fase del calcolo mentre avviene (validazione dei CSV, caricamento della rete, iterazioni del solutore, riepilogo finale delle pressioni, creazione dei layer risultato). Utile soprattutto per capire *dove* si blocca una simulazione che non converge. |
| **Properties Inspector** | Destra | Mostra gli attributi della feature (nodo o condotta) attualmente selezionata sulla mappa di QGIS. Permette di controllare rapidamente i valori di un elemento specifico senza aprire la tabella attributi del layer. |

Puoi ridimensionare la finestra liberamente (è pensata per essere usata a
schermo intero o quasi, dato che il pannello di preparazione contiene molti
campi).

## Il menu laterale (☰)

In alto a sinistra c'è un pulsante **☰** che apre/chiude una barra laterale
con tre pulsanti:

| Pulsante | Funzione |
|----------|----------|
| **⚙ Impostazioni** | Permette di cambiare la lingua dell'interfaccia (italiano/inglese). La modifica si applica alla prossima apertura del plugin. |
| **📖 Guida** | Apre questa guida — il manuale d'uso completo che stai leggendo ora, organizzato in sezioni navigabili. |
| **ℹ Info** | Mostra la versione del plugin, l'autore, il link al repository e le informazioni di licenza. |

## Il pulsante "Chiudi"

In basso a destra, chiude la finestra del plugin. Non interrompe eventuali
simulazioni già completate (i layer risultato restano nel progetto QGIS come
qualsiasi altro layer), ma se una simulazione è ancora in corso è preferibile
attendere che finisca prima di chiudere.

## Un'osservazione pratica

Il plugin **non modifica mai i tuoi layer originali**: legge le geometrie e
gli attributi dei layer che selezioni, ma tutto ciò che produce (layer
collassati, layer dei risultati, file CSV) viene creato come elemento nuovo,
lasciando intatti i dati di partenza. Questo permette di provare
configurazioni diverse (per esempio raggi di aggancio diversi, o ore del
giorno diverse) senza rischiare di rovinare i dati originali.
