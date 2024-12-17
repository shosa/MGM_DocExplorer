import os
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit, QHBoxLayout, QFileDialog, QWidget,
    QMessageBox, QApplication, QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt

class FileExplorerWindow(QMainWindow):
    def __init__(self, server_path):
        super().__init__()
        self.setStyleSheet("""
          QLabel, QLineEdit, QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 8px;
            }
            QPushButton {
                background-color: #F47721;
                color: white;
            }
            QPushButton:hover {
                background-color: #F15A24;
            }
            QTableWidget::item:selected {
                background-color: #3a93e8;
                color: white;
            }
            QComboBox {
                font-size: 15px;
            }
            QDateEdit {
                font-size: 15px;
            }
            QHeaderView::section {
                background-color:#F47721;
                color: white;
                border: 1px solid  #F15A24;
                font-weight: bold;
            }
        """)
        self.setWindowTitle("Esplora File sul Server")
        self.setGeometry(200, 200, 800, 600)

        self.server_path = server_path

        # Layout principale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Tree view per i file
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nome File", "Percorso"])
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.itemExpanded.connect(self.load_directory_contents)  # Carica i contenuti solo quando si espande un nodo
        self.layout.addWidget(self.tree)

        # Layout per i pulsanti
        button_layout = QHBoxLayout()

        # Pulsante "Rinomina File"
        self.rename_button = QPushButton("RINOMINA")
        self.rename_button.clicked.connect(self.rename_file)
        button_layout.addWidget(self.rename_button)

        # Pulsante "Aggiorna"
        self.refresh_button = QPushButton("AGGIORNA")
        self.refresh_button.clicked.connect(self.load_root_directories)
        button_layout.addWidget(self.refresh_button)

        self.layout.addLayout(button_layout)

        # Carica i file all'avvio
        self.load_root_directories()

    def load_root_directories(self):
        """Carica solo le directory di primo livello nella tree view."""
        self.tree.clear()

        if not os.path.exists(self.server_path):
            QMessageBox.critical(self, "Errore", f"Percorso server non trovato: {self.server_path}")
            return

        for item in os.listdir(self.server_path):
            item_path = os.path.join(self.server_path, item)
            if os.path.isdir(item_path):
                directory_item = QTreeWidgetItem([item, item_path])
                directory_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                self.tree.addTopLevelItem(directory_item)

    def load_directory_contents(self, item):
        """Carica il contenuto di una directory solo quando espansa."""
        if item.childCount() > 0:  # Evita di ricaricare se i figli sono già stati caricati
            return

        directory_path = item.text(1)

        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            QMessageBox.warning(self, "Errore", f"Percorso non valido: {directory_path}")
            return

        for sub_item in os.listdir(directory_path):
            sub_item_path = os.path.join(directory_path, sub_item)
            child_item = QTreeWidgetItem([sub_item, sub_item_path])

            if os.path.isdir(sub_item_path):
                child_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

            item.addChild(child_item)

    def rename_file(self):
        """Rinomina il file selezionato."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Attenzione", "Seleziona un file o una directory da rinominare.")
            return

        selected_item = selected_items[0]
        file_path = selected_item.text(1)

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Errore", "Percorso non valido.")
            return

        new_name, ok = QInputDialog.getText(self, "Rinomina File o Directory", "Inserisci nuovo nome:", text=os.path.basename(file_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                selected_item.setText(0, new_name)
                selected_item.setText(1, new_path)
                QMessageBox.information(self, "Successo", "File o directory rinominato con successo.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante la rinomina: {str(e)}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    server_path = r"\\192.168.3.220\DOCUMENTI\DDT"
    window = FileExplorerWindow(server_path)
    window.show()
    sys.exit(app.exec_())