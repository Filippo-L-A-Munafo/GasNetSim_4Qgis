# Risultati — Condotte

Al termine della simulazione, il plugin crea un layer lineare chiamato
`[Risultati] Condotte — <nome_layer>`. Questa sezione spiega il significato
fisico di ogni campo.

| Campo | Unità | Significato |
|-------|-------|-------------|
| `flow_sm3s` | Smc/h | Portata volumetrica **con segno**. Positiva = il gas scorre da Nodo A verso Nodo B (la direzione "convenzionale" scelta in fase di mappatura); negativa = il gas scorre in verso opposto, da B verso A. Le frecce direzionali sulla mappa riflettono automaticamente questo segno. |
| `flow_abs_sm3s` | Smc/h | Portata volumetrica in **valore assoluto** (senza segno). Usata anche per determinare lo spessore della linea sulla mappa: condotte con portata maggiore vengono disegnate più spesse, per far risaltare visivamente i "collettori principali" della rete. |
| `velocity_m_s` | m/s | Velocità media del gas nella condotta, calcolata tenendo conto della comprimibilità reale del gas (non è semplicemente portata/sezione — vedi "Concetti fisici di base" → "Velocità"). Il valore è sempre positivo (è un modulo, indipendente dal verso del flusso). |
| `avg_pressure_bar` | bar | Pressione media lungo la condotta, calcolata come media tra le pressioni ai due nodi estremi. Utile come stima rapida delle condizioni operative "tipiche" in quella condotta (per esempio per stimare la densità media del gas che ci scorre). |
| `sp_gravity` | — | Specific gravity della miscela di gas nella condotta (media tra i due estremi). Vedi la sezione "Risultati — Nodi" per il significato fisico. |
| `z_factor` | — | Fattore di comprimibilità Z medio nella condotta. Vedi "Risultati — Nodi". |
| `density_kg_m3` | kg/m³ | Densità media del gas nelle condizioni operative della condotta (pressione e temperatura medie). |

## Perché la portata può essere negativa

Nella mappatura dei campi (Tab 1), "Nodo A" e "Nodo B" sono solo
un'etichetta arbitraria assegnata durante il collasso o l'importazione dei
dati — non indicano necessariamente il verso reale del flusso. Il motore di
calcolo determina il verso effettivo in base alle pressioni calcolate: il
gas scorre sempre dal punto a pressione più alta verso quello a pressione
più bassa. Se questo verso coincide con "da A verso B", la portata è
positiva; se è l'opposto, la portata è negativa. Questo è del tutto normale,
specialmente in reti magliate (con più percorsi possibili tra due punti) o
quando cambiano le condizioni di domanda.

## Le frecce di direzione del flusso

Se l'opzione è attiva (Tab 2 → Visualizzazione Risultati), ogni condotta ha
un piccolo marcatore triangolare disegnato al centro della sua geometria e
orientato nel verso reale in cui scorre il gas — non nel verso "geometrico"
originale del layer, ma in quello determinato dal segno di `flow_sm3s`. È il
modo più rapido per farsi un'idea visiva di come il gas si distribuisce in
una rete complessa, per esempio per individuare punti di alimentazione
multipla o inversioni di flusso rispetto a condizioni di esercizio abituali.

## Velocità e limiti di erosione

La `velocity_m_s` va confrontata con i limiti pratici di velocità per
evitare rumore eccessivo ed erosione delle pareti interne della condotta.
La sezione "Riferimenti tecnici e normativa" di questa Guida riporta la
formula di erosione (API RP 14E) e alcuni valori indicativi per le diverse
categorie di condotte in pressione.
