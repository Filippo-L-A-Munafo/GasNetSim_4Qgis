# Layer di output e file CSV

## I layer creati in QGIS

Dopo ogni simulazione, il plugin crea (o ricrea, se già esistenti) due layer
**in memoria** nel progetto QGIS:

- **`[Risultati] Nodi — <nome>`** — layer puntuale con colorimetria graduata
  a 5 classi (metodo quantile: ogni classe contiene circa lo stesso numero
  di nodi) sul campo scelto in "Colora per". Scala cromatica dal blu (valore
  minimo) al rosso (valore massimo).
- **`[Risultati] Condotte — <nome>`** — layer lineare con colorimetria
  graduata analoga, e spessore della linea proporzionale alla portata
  assoluta (`flow_abs_sm3s`). Se le frecce di direzione sono attive, ogni
  condotta mostra anche un marcatore triangolare orientato nel verso reale
  del flusso.

### Perché "in memoria"?

I layer risultato sono **layer temporanei** (memory layer di QGIS): esistono
finché il progetto resta aperto, ma non vengono salvati automaticamente su
disco. Questo è intenzionale, perché permette di rilanciare la simulazione
più volte (per esempio cambiando l'ora del giorno o i parametri del gas)
senza accumulare decine di file sul disco: ad ogni nuova simulazione, i
layer risultato precedenti vengono **automaticamente rimossi** e sostituiti
dai nuovi.

Se vuoi conservare un set di risultati in modo permanente, esportalo prima
di lanciare una nuova simulazione:

1. Tasto destro sul layer nel pannello "Layer" di QGIS;
2. **Esporta → Salva Oggetti Come...**;
3. Scegli il formato desiderato (GeoPackage `.gpkg` è generalmente la scelta
   migliore per conservare sia geometria sia attributi; Shapefile `.shp` è
   un'alternativa più universale ma con alcune limitazioni sui nomi dei
   campi).

## I file CSV salvati automaticamente

Oltre ai layer in QGIS, ogni simulazione salva automaticamente due file CSV
in una sottocartella `output/` dentro la cartella di input scelta nel Tab 2:

- `output/results_nodes.csv` — gli stessi valori del layer risultato nodi,
  in formato tabellare puro.
- `output/results_pipes.csv` — gli stessi valori del layer risultato
  condotte.

Questi file sono utili per analisi successive fuori da QGIS (fogli di
calcolo, script Python, confronto tra più scenari) senza dover riesportare
manualmente i layer ogni volta.
