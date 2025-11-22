# pyCFlow

pyCFlow è un'applicazione desktop progettata per una gestione semplice e trasparente delle entrate e delle uscite personali. Al primo avvio, il programma crea un file `cashflow.db` (il database SQLite) e un `config.json` (il file di configurazione) nella stessa directory dell'eseguibile.

Quando si allegano uno o più file a una transazione, il programma li copia in una directory `data_store`, creando una sottocartella basata sulla categoria della transazione. Il file viene rinominato preservando i metadati, seguendo la nomenclatura `YYYY-MM-DD-nomeFileOriginale`, per consentire una facile identificazione e ricerca.

## Funzionalità

- **Gestione delle Transazioni**: Inserimento e modifica di transazioni (flusso di cassa) con campi per Nome, Importo, Categoria, Data e file allegati.
- **Operazioni CRUD**: Aggiungi, aggiorna, cerca, elimina e seleziona i record tramite un'interfaccia utente intuitiva.
- **Gestione Allegati**: Allega uno o più file a ogni transazione. I file vengono salvati in modo organizzato e possono essere aperti direttamente dall'applicazione.
- **Visualizzazione e Ordinamento**: Visualizza tutte le transazioni in una tabella che supporta l'ordinamento per colonna (l'ordinamento predefinito è per data, dal più recente al meno recente).
- **Persistenza dei Dati**: I dati delle transazioni sono salvati in un database SQLite, mentre gli allegati sono gestiti dal `FileManager`.
- **Configurazione Personalizzabile**: Le categorie delle transazioni possono essere personalizzate modificando il file `config.json`.

## Struttura del Progetto

Il progetto è organizzato nei seguenti moduli principali:

- `cash_flow/app.py`: Il punto di ingresso dell'applicazione. Contiene la logica principale della finestra (classe `MainWindow`) che collega l'interfaccia utente alle funzionalità di backend.
- `cash_flow/main_ui.py`: File generato automaticamente da Qt Designer che definisce la struttura e il layout dell'interfaccia utente.
- `cash_flow/database/sqlite_sqlalchemy.py`: Gestisce tutte le interazioni con il database. Definisce il modello `Transaction` tramite SQLAlchemy ORM e la classe `DBManager` che implementa le operazioni CRUD.
- `cash_flow/storage_handler/config_environment.py`: Gestisce la configurazione dell'applicazione. La classe `CustomConfig` carica le impostazioni dal file `config.json` e ne crea uno di default se non esiste.
- `cash_flow/storage_handler/file_manager.py`: Si occupa della gestione dei file allegati (salvataggio, eliminazione e aggiornamento).

## Modello Dati

La tabella principale del database è `transaction`, che ha la seguente struttura:

- `id`: Identificativo univoco (Integer, Primary Key)
- `name`: Nome della transazione (String)
- `amount`: Importo della transazione (Float)
- `category`: Categoria (String)
- `date`: Data della transazione (Date)
- `file_paths`: Lista di percorsi dei file allegati (TEXT, memorizzata come stringa JSON)

## Scelte Implementative

- **SQLite & SQLAlchemy**: SQLite è stato scelto per la sua semplicità e portabilità, non richiedendo un server dedicato. SQLAlchemy è utilizzato come ORM per mappare gli oggetti Python alla tabella del database, semplificando le query e la gestione dei dati. I percorsi dei file sono memorizzati come una lista di stringhe in formato JSON nel database, grazie a un `TypeDecorator` personalizzato (`JSONEncodedList`).
- **PyQt6**: L'interfaccia grafica è costruita con PyQt6. Il layout è progettato con Qt Designer (`.ui` file) e poi convertito in un file Python (`.py`), separando la logica dalla presentazione.
- **Gestione della Configurazione**: Le categorie sono caricate da un file `config.json`. Se il file non esiste, viene creato con una lista di categorie predefinite (es. `home`, `food_groceries`, `salary`, ecc.), rendendo l'applicazione facilmente personalizzabile dall'utente.
- **Gestione dei File**: La classe `FileManager` gestisce gli allegati. I file vengono copiati nella cartella `data_store/{categoria}` e rinominati con il prefisso della data (`YYYY-MM-DD-`). Viene utilizzata la funzione `shutil.copy2` per preservare i metadati originali del file, come la data di creazione.

## Per Iniziare

### Prerequisiti

Per eseguire l'applicazione dal codice sorgente, è necessario avere Python installato sul proprio sistema. Sarà inoltre necessario installare le dipendenze elencate nel file `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Esecuzione dell'Applicazione

Per avviare l'applicazione, eseguire il file `app.py`:

```bash
python cash_flow/app.py
```

## Come Usare l'Applicazione

- **Pulisci**: Prima di ogni operazione, si consiglia di fare clic sul pulsante "Pulisci" per resettare i campi del modulo.
- **Seleziona una transazione**: Per modificare o eliminare una transazione, prima selezionala dalla tabella e poi clicca "Seleziona". I suoi dati appariranno nel modulo.
- **Apri allegati**: Dopo aver selezionato una transazione, clicca sul pulsante "Open File" per aprire la cartella contenente i file allegati e selezionare il file.

1. **Inserire una nuova transazione**:
    - Compilare i campi del modulo (Nome, Importo, Categoria, Data).
    - Se necessario, cliccare "Select File" per allegare uno o più file.
    - Cliccare "Add" per salvare la transazione.
    - Per inserire un Expense o un Income ti basterà indicare il valore con il segno corretto: negativo per le spese, positivo per le entrate.
2. **Modificare un record**:
    - Selezionare una riga nella tabella e cliccare "Select".
    - Modificare i dati nel modulo.
    - Cliccare "Update" per salvare le modifiche.
3. **Eliminare un record**:
    - Selezionare una riga nella tabella e cliccare "Select".
    - Cliccare "Delete" per rimuovere la transazione e i file allegati associati.
    - Per eliminare un allegato devi agire manualmente: seleziona la transazione, usa la funzione "Open file" e cancella il file. Per aggiornare il database, ti basterà riselezionare la voce: il sistema verificherà in automatico se i file sono ancora presenti.
4. **Cercare**:
    - Usare i campi del modulo come filtri di ricerca.
    - Cliccare "Search" per visualizzare i risultati nella tabella.

## Come Modificare il Codice

### Da `.ui` a `.py`

Per rigenerare il file dell'interfaccia utente dopo aver modificato il file `.ui` con Qt Designer, eseguire il comando:

```bash
pyuic6.exe .\qt-designer\main_cf.ui -o .\cash_flow\main_ui.py
```

### Creare l'eseguibile

Per pacchettizzare l'applicazione in un singolo file eseguibile, usare il seguente comando PyInstaller:

Windows
```bash
pyinstaller .\\cash_flow\\app.py --clean --onefile --noconsole --name CashFlow --icon icons\\monitoring.ico
```

Linux
```bash
pyinstaller cash_flow/app.py --clean --onefile --noconsole --name CashFlow --icon icons/monitoring.ico
```

## Contribuire

I contributi sono i benvenuti! Se avete suggerimenti o volete migliorare il codice, non esitate ad aprire una issue o a inviare una pull request.

Icons by Google Material Symbols (Apache License 2.0).