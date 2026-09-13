# Risoluzione dei problemi comuni

## "Simulazione bloccata: nessun nodo reference trovato"

**Causa**: il layer nodi non contiene nessun punto marcato come nodo
reference secondo il campo/valore impostato in "Campo reference" (Tab 1).

**Come risolvere**:

1. Controlla che il campo scelto in "Campo reference" esista davvero nel
   layer nodi e che almeno una riga abbia il valore atteso (per esempio
   `type = reference`, o `matched = 1`).
2. Se la tua rete non ha ancora un campo del genere, aprine la tabella
   attributi in QGIS e crea un nuovo campo (per esempio `is_ref`), assegnando
   il valore `1` al punto che rappresenta un'interconnessione a pressione
   nota (per esempio il punto di ingresso del gas nella rete che stai
   modellando).
3. Ricorda: serve **almeno un** nodo reference, ma puoi averne anche più di
   uno se la rete ha più punti di alimentazione a pressione nota.

Il perché di questo requisito è spiegato nella sezione "Concetti fisici di
base" → "Nodi di riferimento": senza un punto di pressione assoluta nota, il
sistema di equazioni non ha un'unica soluzione.

## "La simulazione non converge" (l'errore non scende sotto la tolleranza)

Prova, in ordine:

1. **Aumenta il numero massimo di iterazioni** (Tab 2 → Parametri Solutore),
   per esempio da 50 a 150–200: a volte la rete converge, solo più
   lentamente del previsto.
2. **Riduci l'URF** (per esempio da 2,0 a 1,0–1,5): un valore troppo alto fa
   oscillare la soluzione senza mai stabilizzarla, specialmente su reti con
   condotte di diametro molto diverso collegate direttamente tra loro.
3. **Aumenta leggermente la tolleranza** (per esempio da 1,0 a 2,0 o 5,0), se
   una precisione minore è accettabile per il tuo scopo (per esempio una
   prima analisi esplorativa).
4. **Attiva "Auto-calibra tol e URF"**: il plugin proverà automaticamente
   diverse combinazioni al posto tuo.
5. **Controlla i nodi isolati**: se alcuni nodi risultano scollegati dal
   resto della rete (per esempio per un raggio di aggancio troppo piccolo in
   fase di collasso — vedi Tab 1), possono generare righe "vuote" nel
   sistema di equazioni. Prova ad aumentare il "Flusso nodi senza domanda"
   (Tab 2 → Parametri Fisici) da 0,0001 a 0,001.

## "Alcuni nodi/condotte sembrano mancanti dopo il collasso"

**Causa più comune**: il **raggio di aggancio** (Tab 1, Modalità A) è troppo
piccolo rispetto alla precisione geometrica dei tuoi dati, quindi alcuni
estremi di condotta che dovrebbero essere collegati allo stesso nodo
risultano scollegati.

**Come risolvere**: aumenta gradualmente il raggio di aggancio (per esempio
da 50 a 100 metri) e rilancia il collasso, controllando ogni volta il
risultato con l'opzione "Aggiungi layer collassati al progetto" attiva, così
puoi ispezionare visivamente dove i nodi vengono effettivamente creati.

Attenzione al rischio opposto: un raggio troppo grande può fondere per
errore nodi che nella realtà sono distinti (per esempio due condotte
parallele ma non collegate).

## "Il profilo di consumo orario non viene letto correttamente"

**Causa più comune**: il **separatore** scelto (Tab 1 → Parametri Export)
non corrisponde al carattere effettivamente usato nel campo del layer nodi.

**Come risolvere**: apri la tabella attributi del layer nodi, guarda il
valore del campo "Flusso orario nodi" per una riga qualsiasi, e verifica
quale carattere separa i 24 valori (`;`, `,`, `|`, `:`, spazio, tabulazione).
Imposta lo stesso carattere nel menu "Separatore flussi". Il campo di
anteprima dell'ora del giorno mostra subito se la lettura ha funzionato
correttamente.

## "L'altitudine dei nodi è sempre 0"

**Causa**: non è stato fornito un layer DEM (Tab 1, Modalità A → campo "DEM
(opz.)"), oppure il layer DEM non copre l'area dei nodi.

**Come risolvere**: fornisci un layer raster DEM che copra tutta l'estensione
della rete. Se non hai un DEM disponibile, puoi lasciare l'altitudine a 0:
per reti di trasporto su territorio pianeggiante l'effetto sulla pressione è
generalmente piccolo, ma su territori con forti dislivelli (come buona parte
del territorio siciliano) può essere significativo e andrebbe verificato.

## Problemi di installazione (motore GasNetSim, numba, percorsi lunghi)

Questi problemi non riguardano l'uso del plugin ma la sua installazione, e
sono documentati in dettaglio nel file `README.md` del repository: in
sintesi, su Windows il motore GasNetSim va installato in un percorso breve
(non dentro la cartella dei plugin di QGIS, che è già molto lunga di suo),
altrimenti `numba` può generare errori di `FileNotFoundError` per superamento
del limite di 260 caratteri nei percorsi di Windows.
