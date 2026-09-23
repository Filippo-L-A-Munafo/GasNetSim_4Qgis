# 4. Tab 0 — Verifica topologica della rete

## 4.1 Finalità

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

## 4.2 Analisi della rete

### 4.2.1 Selezione dei layer

| Campo | Descrizione |
|-------|-------------|
| **Condotte** | Layer lineare da analizzare. Obbligatorio. |
| **Nodi (opz.)** | Layer puntuale facoltativo. Se assegnato, l'operazione di snap (§4.3) aggancia gli estremi delle condotte ai nodi esistenti entro tolleranza, con precedenza sul baricentro del gruppo. Da utilizzare quando la posizione dei nodi è rilevata e ritenuta attendibile. |

### 4.2.2 Procedura

Il comando **Analizza rete** esegue, in sola lettura:

1. riparazione delle geometrie non valide;
2. **esplosione delle polilinee** nei segmenti elementari, che costituiscono
   gli archi del grafo. Il numero di archi risultante è in generale maggiore
   del numero di feature del layer;
3. costruzione del grafo e conteggio degli archi scartati perché nulli o
   degeneri;
4. individuazione delle patologie e, in loro assenza, messaggio
   `[OK] Nessun problema topologico rilevato.`

### 4.2.3 Patologie rilevate

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

## 4.3 Snap degli estremi

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

### 4.3.1 Criterio di scelta della tolleranza

La tolleranza deve essere superiore all'errore di posizionamento dei dati e
inferiore alla minima distanza fra elementi realmente distinti. Un valore
eccessivo unifica condotte parallele appartenenti al medesimo corridoio,
generando una rete inesistente e, tipicamente, capacità di trasporto
sovrastimate.

Si raccomanda una procedura incrementale: si parte da 1–2 m, si analizza, si
verifica la riduzione del numero di componenti e si incrementa la tolleranza
solo se necessario, controllando visivamente il risultato ad ogni passo.

## 4.4 Isole e ri-analisi

Il blocco si abilita in presenza di componenti sconnesse.

| Comando | Funzione |
|---------|----------|
| **⚠ Seleziona isole** | Seleziona nel layer di origine gli archi appartenenti a componenti staccate dal grafo principale. |
| **Crea layer colorato** | Layer temporaneo con campitura per componente. |
| **Ri-analizza rete corrente** | Ripete l'analisi sul layer prodotto dall'ultimo snap, se presente, altrimenti sul layer selezionato. |

## 4.5 Procedura raccomandata

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
