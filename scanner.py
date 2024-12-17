from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLineEdit, QFormLayout, QPushButton,
    QWidget, QMessageBox, QApplication, QLabel, QSplitter, QGraphicsView, QGraphicsScene,
    QDateEdit, QHBoxLayout, QMenu, QAction, QCompleter
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap
import os
import shutil
import fitz  # PyMuPDF

class Scanner(QMainWindow):
    def __init__(self, server_path, suppliers):
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
        self.setWindowTitle("Visualizzatore PDF")
        self.showMaximized()
        self.server_path = server_path
        self.suppliers = suppliers

        # Layout principale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Splitter principale per dividere contenuti
        vertical_splitter = QSplitter(Qt.Vertical)

        # Parte superiore: TreeView e Visualizzatore PDF
        main_splitter = QSplitter(Qt.Horizontal)

        # Layout sinistra (TreeView + Controlli Rinomina)
        left_splitter = QSplitter(Qt.Vertical)

        # Tree widget per elencare i file PDF
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nome File"])
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)  # Selezione con Ctrl
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemClicked.connect(self.load_pdf)
        left_splitter.addWidget(self.tree)

        # Form per rinomina (sotto il TreeView)
        rename_layout = QFormLayout()
        self.fornitore_input = QLineEdit()
        self.documento_input = QLineEdit()

        # Aggiungi suggerimenti per il campo Fornitore
        completer = QCompleter(self.suppliers, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.fornitore_input.setCompleter(completer)

        self.rename_button = QPushButton("Rinomina")
        self.rename_button.clicked.connect(self.rename_pdf)

        rename_layout.addRow("Fornitore:", self.fornitore_input)
        rename_layout.addRow("Documento:", self.documento_input)
        rename_layout.addRow(self.rename_button)

        rename_widget = QWidget()
        rename_widget.setLayout(rename_layout)
        left_splitter.addWidget(rename_widget)

        # Aggiungi la parte sinistra al main_splitter
        main_splitter.addWidget(left_splitter)

        # Viewer PDF (a destra)
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        main_splitter.addWidget(self.graphics_view)

        # Imposta proporzioni per la parte sinistra e destra
        main_splitter.setSizes([50, 50])

        # Aggiungi il main_splitter al vertical_splitter
        vertical_splitter.addWidget(main_splitter)

        # Parte inferiore: Controlli Data e Salva
        save_layout = QHBoxLayout()
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())

        self.save_button = QPushButton("Salva")
        self.save_button.clicked.connect(self.save_files)

        save_layout.addWidget(QLabel("Data:"))
        save_layout.addWidget(self.date_picker)
        save_layout.addWidget(self.save_button)

        save_widget = QWidget()
        save_widget.setLayout(save_layout)
        vertical_splitter.addWidget(save_widget)

        # Imposta proporzioni per le due sezioni
        vertical_splitter.setSizes([80, 20])

        # Aggiungi il vertical_splitter al layout principale
        main_layout.addWidget(vertical_splitter)

        # Carica i file PDF all'avvio
        self.load_pdfs()

    def load_pdfs(self):
        self.tree.clear()

        if not os.path.exists(self.server_path):
            QMessageBox.critical(self, "Errore", f"Percorso non trovato: {self.server_path}")
            return

        for file_name in os.listdir(self.server_path):
            file_path = os.path.join(self.server_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
                item = QTreeWidgetItem([file_name])
                item.setData(0, Qt.UserRole, file_path)
                self.tree.addTopLevelItem(item)

    def load_pdf(self, item):
        file_path = item.data(0, Qt.UserRole)

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Errore", f"File non trovato: {file_path}")
            return

        try:
            self.graphics_scene.clear()
            pdf_document = fitz.open(file_path)

            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                pix = page.get_pixmap(dpi=150)
                qt_image = QPixmap()
                qt_image.loadFromData(pix.tobytes("ppm"))
                self.graphics_scene.addPixmap(qt_image).setOffset(0, page_number * pix.height)

            pdf_document.close()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare il PDF: {e}")

    def rename_pdf(self):
        selected_item = self.tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Errore", "Nessun file selezionato.")
            return

        fornitore = self.fornitore_input.text().strip()
        documento = self.documento_input.text().strip()

        if not fornitore or not documento:
            QMessageBox.warning(self, "Errore", "Compilare entrambi i campi Fornitore e Documento.")
            return

        old_path = selected_item.data(0, Qt.UserRole)
        new_name = f"{fornitore} {documento}.pdf"
        new_path = os.path.join(self.server_path, new_name)

        try:
            os.rename(old_path, new_path)
            self.load_pdfs()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile rinominare il file: {e}")

    def save_files(self):
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        year, month, day = selected_date.split("-")
        months = ["GENNAIO", "FEBBRAIO", "MARZO", "APRILE", "MAGGIO", "GIUGNO", "LUGLIO", "AGOSTO", "SETTEMBRE", "OTTOBRE", "NOVEMBRE", "DICEMBRE"]
        month_name = months[int(month) - 1]

        dest_path = os.path.join(
            r"\\192.168.3.220\DOCUMENTI\DDT",
            year,
            month_name,
            f"{day}-{month}-{year}"
        )

        try:
            os.makedirs(dest_path, exist_ok=True)
            for file_name in os.listdir(self.server_path):
                file_path = os.path.join(self.server_path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
                    shutil.move(file_path, os.path.join(dest_path, file_name))

            QMessageBox.information(self, "Successo", f"Tutti i file sono stati spostati in: {dest_path}")
            self.load_pdfs()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile spostare i file: {e}")

    def show_context_menu(self, position):
        menu = QMenu()
        merge_action = QAction("Unisci", self)
        merge_action.triggered.connect(self.merge_selected_pdfs)
        menu.addAction(merge_action)

        delete_action = QAction("Elimina", self)
        delete_action.triggered.connect(self.delete_selected_pdf)
        menu.addAction(delete_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def merge_selected_pdfs(self):
        selected_items = self.tree.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "Errore", "Seleziona almeno due file per unirli.")
            return

        output_file_path = os.path.join(self.server_path, "Unione.pdf")
        merger = fitz.open()

        try:
            for item in selected_items:
                file_path = item.data(0, Qt.UserRole)
                merger.insert_pdf(fitz.open(file_path))
                os.remove(file_path)  # Elimina il file originale

            merger.save(output_file_path)
            merger.close()
            QMessageBox.information(self, "Successo", f"File uniti in: {output_file_path}")
            self.load_pdfs()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile unire i file: {e}")

    def delete_selected_pdf(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Errore", "Nessun file selezionato per l'eliminazione.")
            return

        try:
            for item in selected_items:
                file_path = item.data(0, Qt.UserRole)
                os.remove(file_path)

            QMessageBox.information(self, "Successo", "File eliminati correttamente.")
            self.load_pdfs()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile eliminare i file: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    server_path = r"\\192.168.3.220\DOCUMENTI\Scansioni RICOH"

    # Esempio: fornitori da passare
    suppliers = ["Fornitore1", "Fornitore2", "Fornitore3"]

    viewer = Scanner(server_path, suppliers)
    viewer.show()
    sys.exit(app.exec_())
