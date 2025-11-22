# pyCFlow

pyCFlow is a desktop application designed for simple and transparent management of personal income and expenses. On first launch, the program creates a `cashflow.db` file (the SQLite database) and a `config.json` (the configuration file) in the same directory as the executable.

When you attach one or more files to a transaction, the program copies them to a `data_store` directory, creating a subfolder based on the transaction category. The file is renamed while preserving metadata, following the `YYYY-MM-DD-originalFileName` naming convention, to allow for easy identification and searching.

## Features

- **Transaction Management**: Enter and edit transactions (cash flow) with fields for Name, Amount, Category, Date, and attached files.
- **CRUD Operations**: Add, update, search, delete, and select records through an intuitive user interface.
- **Attachment Management**: Attach one or more files to each transaction. The files are saved in an organized manner and can be opened directly from the application.
- **Viewing and Sorting**: View all transactions in a table that supports column sorting (the default sort is by date, from newest to oldest).
- **Data Persistence**: Transaction data is saved in an SQLite database, while attachments are managed by the `FileManager`.
- **Customizable Configuration**: Transaction categories can be customized by editing the `config.json` file.

## Project Structure

The project is organized into the following main modules:

- `cash_flow/app.py`: The application's entry point. It contains the main window logic (`MainWindow` class) that connects the user interface to the backend functionalities.
- `cash_flow/main_ui.py`: An automatically generated file from Qt Designer that defines the structure and layout of the user interface.
- `cash_flow/database/sqlite_sqlalchemy.py`: Manages all interactions with the database. It defines the `Transaction` model using SQLAlchemy ORM and the `DBManager` class that implements CRUD operations.
- `cash_flow/storage_handler/config_environment.py`: Manages the application's configuration. The `CustomConfig` class loads settings from the `config.json` file and creates a default one if it doesn't exist.
- `cash_flow/storage_handler/file_manager.py`: Handles the management of attached files (saving, deleting, and updating).

## Data Model

The main database table is `transaction`, which has the following structure:

- `id`: Unique identifier (Integer, Primary Key)
- `name`: Transaction name (String)
- `amount`: Transaction amount (Float)
- `category`: Category (String)
- `date`: Transaction date (Date)
- `file_paths`: List of paths of attached files (TEXT, stored as a JSON string)

## Implementation Choices

- **SQLite & SQLAlchemy**: SQLite was chosen for its simplicity and portability, not requiring a dedicated server. SQLAlchemy is used as an ORM to map Python objects to the database table, simplifying queries and data management. File paths are stored as a list of strings in JSON format in the database, thanks to a custom `TypeDecorator` (`JSONEncodedList`).
- **PyQt6**: The graphical interface is built with PyQt6. The layout is designed with Qt Designer (`.ui` file) and then converted to a Python file (`.py`), separating logic from presentation.
- **Configuration Management**: Categories are loaded from a `config.json` file. If the file does not exist, one is created with a list of predefined categories (e.g., `home`, `food_groceries`, `salary`, etc.), making the application easily customizable by the user.
- **File Management**: The `FileManager` class manages attachments. Files are copied to the `data_store/{category}` folder and renamed with the date prefix (`YYYY-MM-DD-`). The `shutil.copy2` function is used to preserve the original file metadata, such as the creation date.

## Getting Started

### Prerequisites

To run the application from the source code, you need to have Python installed on your system. You will also need to install the dependencies listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Running the Application

To start the application, run the `app.py` file:

```bash
python cash_flow/app.py
```

## How to Use the Application

- **Clear**: Before each operation, it is recommended to click the "Clear" button to reset the form fields.
- **Select a transaction**: To edit or delete a transaction, first select it from the table and then click "Select". Its data will appear in the form.
- **Open attachments**: After selecting a transaction, click the "Open File" button to open the folder containing the attached files and select the file.

1.  **Enter a new transaction**:
    -   Fill in the form fields (Name, Amount, Category, Date).
    -   If necessary, click "Select File" to attach one or more files.
    -   Click "Add" to save the transaction.
    -   To enter an Expense or an Income, simply indicate the value with the correct sign: negative for expenses, positive for income.
2.  **Modify a record**:
    -   Select a row in the table and click "Select".
    -   Modify the data in the form.
    -   Click "Update" to save the changes.
3.  **Delete a record**:
    -   Select a row in the table and click "Select".
    -   Click "Delete" to remove the transaction and its associated attached files.
    -   To delete an attachment, you must act manually: select the transaction, use the "Open file" function and delete the file. To update the database, simply re-select the item: the system will automatically check if the files are still present.
4.  **Search**:
    -   Use the form fields as search filters.
    -   Click "Search" to display the results in the table.

## How to Modify the Code

### From `.ui` to `.py`

To regenerate the user interface file after modifying the `.ui` file with Qt Designer, run the command:

```bash
pyuic6.exe .\qt-designer\main_cf.ui -o .\cash_flow\main_ui.py
```

### Create the executable

To package the application into a single executable file, use the following PyInstaller command:

Windows
```bash
pyinstaller .\\cash_flow\\app.py --clean --onefile --noconsole --name CashFlow --icon icons\\monitoring.ico
```

Linux
```bash
pyinstaller cash_flow/app.py --clean --onefile --noconsole --name CashFlow --icon icons/monitoring.ico
```

## Contributing

Contributions are welcome! If you have suggestions or want to improve the code, feel free to open an issue or submit a pull request.

Icons by Google Material Symbols (Apache License 2.0).