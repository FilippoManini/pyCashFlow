import sys
import os
import datetime
import subprocess
import platform
from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtWidgets import (QWidget, 
                             QApplication, 
                             QPushButton, 
                             QMessageBox, 
                             QTableWidgetItem,
                             QFileDialog)
from PyQt6.QtGui import QIcon, QPixmap

from main_ui import Ui_Form
from database.sqlite_sqlalchemy import (DBManager, 
                                        Transaction)
from storage_handler.file_manager import FileManager
from storage_handler.config_environment import CustomConfig

DEFAULT_DATE = QtCore.QDate(9999, 1, 1)
DEFAULT_CATEGORY = "Select Item"
DEFAULT_AMOUNT = 0.0

# Create a main window class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the UI from a separate UI file
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Create a database connection object
        self.db_manager = DBManager()
        self.file_manager = FileManager()

        self.t_selected: Transaction | None = None

        # Connect UI elements to class variables
        self.name = self.ui.le_name
        self.amount = self.ui.dsb_amount
        self.category = self.ui.cb_category
        self._load_category()
        self.date = self.ui.dateEdit
        self.date.setDate(datetime.date.today())
        self.btn_open_file = self.ui.btn_open_file
        self.file_name = self.ui.le_file
        self.file_paths_full: list[str] = []
        self.btn_select_file = self.ui.btn_select_file

        self.btn_add = self.ui.btn_add
        self.btn_clear = self.ui.btn_clear
        self.btn_delete = self.ui.btn_delete
        self.btn_search = self.ui.btn_search
        self.btn_select = self.ui.btn_select
        self.btn_update = self.ui.btn_update
        self.result_table = self.ui.tableWidget

        self.buttons_list = self.ui.Home.findChildren(QPushButton)

        # set icon for the application
        self.setWindowIcon(QIcon(self._set_resource_path("icons/monitoring.ico")))
        # Force black text for all buttons
        [b.setStyleSheet("color: #000000;") for b in self.buttons_list]
        # Set icons for buttons
        self._set_icons(self.btn_add, "icons/add.svg")
        self._set_icons(self.btn_delete, "icons/delete.svg")
        self._set_icons(self.btn_search, "icons/search.svg")
        self._set_icons(self.btn_clear, "icons/clear.svg")
        self._set_icons(self.btn_select, "icons/select.svg")
        self._set_icons(self.btn_update, "icons/update.svg")

        # Change sorting via UI
        self.result_table.setSortingEnabled(True)
        # sort by date of day
        self.result_table.sortByColumn(3, QtCore.Qt.SortOrder.DescendingOrder)
        self.populate_table()

        # Initialize signal-slot connections
        self.btn_select_file.clicked.connect(self.select_file_path)
        self.btn_open_file.clicked.connect(self.get_file_paths)
        self.btn_add.clicked.connect(self.add_info)
        self.btn_select.clicked.connect(self.select_info)
        self.btn_delete.clicked.connect(self.delete_info)
        self.btn_search.clicked.connect(self.search_info)
        self.btn_update.clicked.connect(self.update_info)
        self.btn_clear.clicked.connect(self.clear_form_info)

    def _set_resource_path(self, relative_path) -> str:
        """
        Get the absolute path to a resource, works for development and for PyInstaller.
        """
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent.parent
        else:
            base_path = Path(".")
        
        return os.path.join(base_path, relative_path)

    def _set_icons(self, button: QPushButton, path_icon: str):
        """
        Set the icon for a given button.
        """
        icon = QIcon()
        path_icon = self._set_resource_path(path_icon)
        icon.addPixmap(QPixmap(path_icon), QIcon.Mode.Normal, QIcon.State.Off)
        button.setIcon(icon)

    def _load_category(self):
        config = CustomConfig.load()
        if config.category:
            self.category.clear()
            self.category.addItem(DEFAULT_CATEGORY)
            self.category.addItems(config.category)
        
        self.category.setCurrentText(DEFAULT_CATEGORY)

    def disable_buttons(self):
        # Disable all buttons
        for button in self.buttons_list:
            button.setDisabled(True)

    def enable_buttons(self):
        # Enable all buttons
        for button in self.buttons_list:
            button.setDisabled(False)
    
    def populate_table(self, transactions : list[Transaction]|None = None):
        # Retrieves all transactions from the database
        if transactions is None:
            transactions = self.db_manager.select()

        self.result_table.setSortingEnabled(False)
        self.result_table.setRowCount(len(transactions))

        # Populate table
        for row, t in enumerate(transactions):
            # name_item = QTableWidgetItem(t.name)
            # Store the transaction's unique ID within the item itself.
            # This makes the data retrieval independent of the visual row order.
            # name_item.setData(QtCore.Qt.ItemDataRole.UserRole, t.id)

            self.result_table.setItem(row, 0, QTableWidgetItem(t.name))
            self.result_table.setItem(row, 1, QTableWidgetItem(str(t.amount)))
            self.result_table.setItem(row, 2, QTableWidgetItem(t.category))
            self.result_table.setItem(row, 3, QTableWidgetItem(str(t.date)))
            self.result_table.setItem(row, 4, QTableWidgetItem(t.get_type()))
            self.result_table.setItem(row, 5, QTableWidgetItem(t.get_file_paths()))
        
        self.result_table.setSortingEnabled(True)

    def get_info_frame(self) -> Transaction:
        """Returns a Transaction object with the information from the form."""
        return Transaction(name=self.name.text(),
                        amount=self.amount.value(),
                        category=self.category.currentText(),
                        date=self.date.date().toPyDate(),
                        file_paths=self.file_name.text().split(" ") if self.file_name.text() else [])
    
    def select_file_path(self):
        """Opens a dialog box to select one or more files and adds them to the list."""
        # Use getOpenFileNames to allow multiple selections
        file_path, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*);;PDF Files (*.pdf);;Image Files (*.png *.jpg)"
        )
        # Store the full paths for later use
        self.file_paths_full = file_path 

        if file_path:
            # Get the string of existing file names from the text box.
            temp_file_paths = self.file_name.text()
            # Extract just the file names from the newly selected full paths.
            file_name = [os.path.basename(path) for path in file_path]
            # Append the old file names string to the list of new file names.
            # This works even if the text box was initially empty.
            if temp_file_paths != "" :
                file_name.append(temp_file_paths)
            # Join all names into a single space-separated string and update the text box.
            self.file_name.setText(" ".join(file_name))

    def get_file_paths(self):
        """
        is necessary to select a row in the table.
        """
        system = platform.system().lower()

        if isinstance(self.t_selected, Transaction) and self.t_selected.file_paths:
            for file_path in self.t_selected.file_paths:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue

                folder_path = os.path.dirname(file_path)

                if system == "windows":
                    subprocess.Popen(["explorer", "/select,", file_path])
                elif system == "linux":
                    for cmd in ["exo-open", "gnome-open", "kde-open", "xdg-open"]:
                        try:
                            subprocess.Popen([cmd, folder_path])
                            subprocess.Popen([cmd, file_path])
                            break
                        except FileNotFoundError:
                            continue
        
        # ? version of QT where files are opened and the destination folder
        # for fp in self.file_paths_full:
        #     QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(os.path.dirname(fp)))
        #     if os.path.exists(fp):
        #         QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(fp))
             
    def add_info(self):
        """Function to add information from the form to the database."""

        t = self.get_info_frame()
        if t.name == "":
            QMessageBox.information(self,
                                    "Warning",
                                    f"Name not insered")
            return
        if t.amount == "":
            QMessageBox.information(self,
                        "Warning",
                        f"Amount not insered")
            return
        
        if t.category == DEFAULT_CATEGORY:
            QMessageBox.information(self,
                        "Warning",
                        f"Category not selected")
            return
        
        if t.file_paths:
            file_path_new = []
            for file_path in self.file_paths_full:
                file_path_new.append(self.file_manager.save_custom_file(
                                                        file_path, 
                                                        str(t.date), 
                                                        t.category))
            t.file_paths = file_path_new

        select = self.db_manager.select(t.name, t.amount, t.category, t.date)
        if len(select) > 0:
            QMessageBox.information(self,
                        "Warning",
                        f"Transaction already exists, please update name or amount or date or category")
            return

        result = self.db_manager.insert(t)
        if result == False: 
            QMessageBox.information(self,
                        "Error",
                        f"Insertion failed")
            return
        
        self.populate_table()


    def select_info(self):
        """Function to select and populate information in the form"""

        self.t_selected = self.get_row_transaction()
        if isinstance(self.t_selected, Transaction):
            self.name.setText(self.t_selected.name)
            self.amount.setValue(self.t_selected.amount)
            self.category.setCurrentText(self.t_selected.category)
            self.date.setDate(QtCore.QDate(self.t_selected.date.year,
                                           self.t_selected.date.month,
                                           self.t_selected.date.day))
        
            t_temp = self.db_manager.select(self.t_selected.name, 
                                            self.t_selected.amount, 
                                            self.t_selected.category, 
                                            self.t_selected.date)
            if len(t_temp) != 1:
                QMessageBox.information(self, "Warning", "Please select one row information",
                                QMessageBox.StandardButton.Ok)
                return
            
            self.t_selected = t_temp[0]
            
            if t_temp[0].file_paths:
                self.file_paths_full = self.file_manager.check_file_paths(t_temp[0].file_paths)
                # Converting lists to sets removes duplicates and ignores order.
                # The comparison then checks for equality of the unique elements
                if set(self.file_paths_full) != set(t_temp[0].file_paths):
                    updated = self.db_manager.update(id=t_temp[0].id, 
                                                    name=t_temp[0].name,
                                                    amount=t_temp[0].amount,
                                                    category=t_temp[0].category,
                                                    date=t_temp[0].date,
                                                    file_paths=self.file_paths_full)
                    if updated:
                        QMessageBox.information(self, "Success", "Transaction updated successfully",
                                                QMessageBox.StandardButton.Ok)
                        self.t_selected.file_paths = self.file_paths_full
                        self.populate_table()
                    else:
                        QMessageBox.information(self, "Error", "Update failed",
                                                QMessageBox.StandardButton.Ok)
                        return

            # to perform the check in update
            self.file_paths_full = []
            self.file_name.setText(self.t_selected.get_file_paths())

    def get_row_transaction(self) -> Transaction | None:
        """Retrieves the Transaction object corresponding to the selected row in the table."""
        selected_row = self.result_table.currentRow()
        if selected_row != -1:
            name_item = self.result_table.item(selected_row, 0)
            name = name_item.text() if name_item else ""

            amount_item = self.result_table.item(selected_row, 1)
            amount = amount_item.text() if amount_item else "0.0"

            category_item = self.result_table.item(selected_row, 2)
            category = category_item.text() if category_item else ""

            date_item = self.result_table.item(selected_row, 3)
            date = date_item.text() if date_item else ""

            file_paths_item = self.result_table.item(selected_row, 5)
            file_paths = file_paths_item.text() if file_paths_item else ""

            return Transaction(name=name,
                               amount=float(amount),
                               category=category,
                               date=datetime.date.fromisoformat(date),
                               file_paths=file_paths.split(" ") if file_paths else [])
        else:
            QMessageBox.information(self, "Warning", "Please select one row information",
                                    QMessageBox.StandardButton.Ok)
            return None                                                                                             

    def delete_info(self):
        t_row = self.get_row_transaction()

        if isinstance(t_row, Transaction):
            t = self.db_manager.select(t_row.name, 
                                        t_row.amount, 
                                        t_row.category, 
                                        t_row.date)
            if len(t) == 0:
                QMessageBox.information(self, "Warning", "No transaction found to delete",
                                        QMessageBox.StandardButton.Ok)
                return
            elif len(t) == 1:
                self.db_manager.delete(t[0].id)
                if t[0].file_paths:
                    self.file_paths_full.clear()
                    for file_path in t[0].file_paths:
                        self.file_manager.delete_file(file_path)

                QMessageBox.information(self, "Success", "Transaction deleted successfully",
                                        QMessageBox.StandardButton.Ok)
                self.populate_table()
                return
            elif len(t) > 1:
                QMessageBox.information(self, "Warning", "Multiple transactions found, please refine your search",
                                        QMessageBox.StandardButton.Ok)
                return
        
        else:
            return

    def update_info(self):
        """
        Updates the selected transaction with the information from the form.

        is necessary to select a row in the table before clicking the update button.
        """
        if self.t_selected is None:
            QMessageBox.information(self, "Warning", "Please select a transaction to update",
                                    QMessageBox.StandardButton.Ok)
            return

        t_new = self.get_info_frame()
        # initialized with the path name instead of just the name
        t_new.file_paths = self.t_selected.file_paths

        if self.t_selected == t_new and self.file_paths_full == []:
            QMessageBox.information(self, "Warning", "No changes to update",
                                    QMessageBox.StandardButton.Ok)
            return

        if isinstance(t_new, Transaction):
            # if different, it means that it has been filled and modified with select_file_path()
            if self.file_paths_full:
                t_new.file_paths = self.t_selected.file_paths = self.file_manager.update_file(
                    new_file_paths=self.file_paths_full,
                    old_file_paths=self.t_selected.file_paths if self.t_selected.file_paths else [],
                    date=str(self.t_selected.date),
                    dir_label=self.t_selected.category)
            
            # change if the date has changed and the file is present for modification
            if t_new.date != self.t_selected.date and self.t_selected.file_paths: 
                    t_new.file_paths = self.file_manager.update_file_date(
                                                            file_paths=self.t_selected.file_paths, 
                                                            date=str(t_new.date))
            
            # I change the category last because that way I move the file last.
            if t_new.category != self.t_selected.category and self.t_selected.file_paths:
                t_new.file_paths = self.file_manager.update_file_category(
                                                        file_paths=self.t_selected.file_paths, 
                                                        dir_label=t_new.category)
                
                if t_new.file_paths == []:
                    QMessageBox.information(self, "Error", f"File: {self.t_selected.file_paths} already exists",
                                    QMessageBox.StandardButton.Ok)
                    return

            updated = self.db_manager.update(id=self.t_selected.id,
                                             name=t_new.name,
                                             amount=t_new.amount,
                                             category=t_new.category,
                                             date=t_new.date,
                                             file_paths=t_new.file_paths)
            if updated:
                QMessageBox.information(self, "Success", "Transaction updated successfully",
                                        QMessageBox.StandardButton.Ok)
                self.t_selected = None
                self.populate_table()
                return
            else:
                    QMessageBox.information(self, "Error", "Update failed",
                                            QMessageBox.StandardButton.Ok)
                    return
        else:
            return

    def search_info(self):
        t = self.get_info_frame()
        results = self.db_manager.select(t.name, 
                                         t.amount if t.amount != DEFAULT_AMOUNT else None, 
                                         t.category if t.category != DEFAULT_CATEGORY else None, 
                                         t.date if t.date != DEFAULT_DATE.toPyDate() else None, 
                                         ) # t.file_paths if t.file_paths else []
        self.populate_table(results)
        print(f"Search results {results}")

    def clear_form_info(self):
        self.name.clear()
        self.amount.setValue(DEFAULT_AMOUNT)
        self.category.setCurrentText(DEFAULT_CATEGORY)
        self.date.setDate(DEFAULT_DATE)
        self.file_name.clear()

        self.file_paths_full.clear()

        self.populate_table()


# Application entry
def run():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()