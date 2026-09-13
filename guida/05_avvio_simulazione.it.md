# Avvio della simulazione

## I tre modi per avviare il calcolo

La simulazione può essere lanciata in tre modi, tutti equivalenti nel
risultato finale — cambia solo il punto del flusso di lavoro da cui parti:

1. **Tab 1 → ">> Genera CSV e Simula"** — il modo consigliato per il lavoro
   quotidiano: esporta i CSV e avvia subito la simulazione in un solo click,
   senza salvare file intermedi sul disco in modo permanente.
2. **Tab 1 → "> Genera CSV"**, poi **Tab 2 → "▶ Avvia Simulazione"** — utile
   quando vuoi controllare (o modificare a mano) i file CSV prima di
   lanciare il calcolo, per esempio per verificare che i valori esportati
   siano quelli attesi.
3. **Pulsante "▶ Avvia Simulazione" nel footer della finestra** — rigenera i
   CSV dai layer correnti e avvia subito il calcolo, senza dover tornare al
   Tab 1.

## Cosa succede internamente

La simulazione viene eseguita in un **thread separato**: questo significa
che QGIS resta pienamente utilizzabile mentre il calcolo è in corso (puoi
continuare a navigare la mappa, aprire altri layer, ecc.) invece di
bloccarsi in attesa del risultato.

Il pannello **Dashboard**, al centro della finestra, mostra in tempo reale
ogni fase del processo:

1. **Validazione dei CSV** — controllo che i file abbiano tutti i campi
   richiesti e che almeno un nodo reference sia presente. Se manca, la
   simulazione si ferma qui con un messaggio d'errore chiaro.
2. **Caricamento della rete** — costruzione del grafo nodi/condotte in
   memoria, con le proprietà del gas (composizione, temperatura) applicate.
3. **Iterazioni del solutore** — il metodo di Newton-Raphson procede per
   approssimazioni successive (vedi Tab 2 → Parametri Solutore); il log
   mostra il progresso e, se attiva, l'auto-calibrazione di tolleranza e URF.
4. **Riepilogo pressioni** — un sommario delle pressioni calcolate su tutta
   la rete (minimo, massimo, valori ai nodi reference), utile per un primo
   controllo di plausibilità del risultato.
5. **Creazione dei layer risultato** — i due nuovi layer colorati (nodi e
   condotte) vengono generati e aggiunti al progetto QGIS.

Se la simulazione non converge (l'errore non scende sotto la tolleranza
entro il numero massimo di iterazioni), il log lo segnala esplicitamente: in
quel caso vedi la sezione "Risoluzione dei problemi comuni" di questa Guida
per i passi da provare.
