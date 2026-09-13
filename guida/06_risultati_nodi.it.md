# Risultati — Nodi

Al termine della simulazione, il plugin crea un layer puntuale chiamato
`[Risultati] Nodi — <nome_layer>`, con un campo per ogni grandezza calcolata.
Questa sezione spiega cosa significa fisicamente ciascun campo.

| Campo | Unità | Significato |
|-------|-------|-------------|
| `pressure_bar` | bar | Pressione assoluta calcolata dalla simulazione in quel nodo. È il risultato principale: rappresenta la forza che spinge il gas verso i nodi a pressione più bassa. |
| `temperature_k` | K | Temperatura operativa al nodo. Nel modello attuale si propaga dal valore impostato nei Parametri Fisici (temperatura uniforme in tutta la rete). |
| `sp_gravity` | — (adimensionale) | **Specific gravity** ("densità relativa"): rapporto tra la densità del gas in quel punto e la densità dell'aria, entrambe nelle stesse condizioni standard. Un valore < 1 significa gas più leggero dell'aria (per esempio l'idrogeno, sp. gravity ≈ 0,07); un valore vicino a 0,6 è tipico del metano puro. È una grandezza importante per valutare la dispersione del gas in caso di fuoriuscita (un gas più leggero dell'aria tende a salire e disperdersi verso l'alto). |
| `z_factor` | — (adimensionale) | **Fattore di comprimibilità Z**: misura quanto il gas reale si discosta dal comportamento ideale (Z = 1 per un gas ideale). Dipende da pressione, temperatura e composizione. Serve al solutore per calcolare correttamente la densità del gas nelle condizioni operative (vedi "Concetti fisici di base"). |
| `hhv_mj_sm3` | MJ/sm³ | **Higher Heating Value** (potere calorifico superiore): l'energia rilasciata dalla combustione completa di un metro cubo standard di quel gas, includendo il calore recuperabile dalla condensazione del vapor d'acqua prodotto. È la grandezza chiave per capire quanta energia sta realmente trasportando la rete in quel punto, non solo quanto "volume" di gas. |
| `wobbe_mj_sm3` | MJ/sm³ | **Indice di Wobbe** = HHV / √(specific gravity). Misura l'intercambiabilità tra gas diversi: due gas con lo stesso indice di Wobbe rilasciano la stessa potenza termica attraverso lo stesso bruciatore, anche se hanno composizioni diverse. È l'indicatore più usato per valutare se una miscela (per esempio con idrogeno) è compatibile con apparecchi progettati per gas naturale puro. |
| `density_kg_m3` | kg/m³ | Densità del gas nelle condizioni operative reali del nodo (pressione e temperatura locali). Più alta è la pressione, più il gas è denso — un metro cubo a 70 bar contiene molto più gas dello stesso metro cubo a pressione atmosferica. |
| `std_density_kg_sm3` | kg/sm³ | Densità del gas alle **condizioni standard** di riferimento (15 °C, 1,01325 bar). A differenza della densità operativa, dipende solo dalla composizione del gas, non dalla pressione locale: è il valore usato per convertire fra portate in Smc e portate in massa (kg/s). |
| `molar_mass` | g/mol | Massa molare media della miscela di gas in quel nodo, calcolata come media pesata sulle frazioni molari dei singoli componenti. Componenti più pesanti (propano, butano) aumentano la massa molare media; l'idrogeno, molto leggero, la riduce drasticamente anche a basse concentrazioni. |

## Come leggere questi valori in pratica

- Un valore di `pressure_bar` che scende sotto la soglia minima contrattuale
  in un punto di consegna segnala un problema di capacità della rete in
  quella zona.
- Un `sp_gravity` o un `molar_mass` che cambiano bruscamente da un nodo
  all'altro possono indicare un punto di miscelazione tra gas di
  composizione diversa (per esempio un'immissione di idrogeno).
- Il `wobbe_mj_sm3` è il primo valore da controllare quando si valuta la
  compatibilità di un blend idrogeno/metano con la normativa e con gli
  apparecchi degli utenti finali.
