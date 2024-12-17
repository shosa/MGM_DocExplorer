import os
import re
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QStyleFactory, QMainWindow, QVBoxLayout, QInputDialog, QLineEdit, QPushButton, QFileDialog,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QHBoxLayout, QMessageBox,
    QComboBox, QGroupBox, QFormLayout, QDateEdit, QCheckBox, QMenu , QProgressDialog , QVBoxLayout, QCompleter
)
from datetime import datetime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QDesktopServices, QFont, QIcon
from PyQt5.QtCore import QUrl, QDate, Qt, QSize, QStringListModel
from file_explorer import FileExplorerWindow
from scanner import Scanner
class DocumentSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RACCOLTA DOCUMENTI")
        self.setGeometry(100, 100, 1000, 900)

        # Layout principale
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Stile moderno
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

        # Layout per i pulsanti sulla stessa riga
        buttons_layout = QHBoxLayout()

        # Pulsante "AGGIORNA DB"
        self.update_db_button = QPushButton("AGGIORNA")
        self.update_db_button.setFixedSize(130, 50)  # Pulsante quadrato
        self.update_db_button.setIcon(QIcon("icon/update.png"))  # Percorso all'icona
        self.update_db_button.setIconSize(QSize(24, 24))  # Dimensioni dell'icona
        self.update_db_button.clicked.connect(self.generate_xml)
        buttons_layout.addWidget(self.update_db_button)

        # Pulsante "Esplora File"
        self.open_explorer_button = QPushButton("ESPLORA")
        self.open_explorer_button.setFixedSize(130, 50)  # Pulsante quadrato
        self.open_explorer_button.setIcon(QIcon("icon/explore.png"))  # Percorso all'icona
        self.open_explorer_button.setIconSize(QSize(24, 24))  # Dimensioni dell'icona
        self.open_explorer_button.clicked.connect(self.open_file_explorer)
        buttons_layout.addWidget(self.open_explorer_button)
        
          # Pulsante "SCANSIONI"
          
        self.open_scan_button = QPushButton("SCANNER")
        self.open_scan_button.setFixedSize(130, 50)  # Pulsante quadrato
        self.open_scan_button.setIcon(QIcon("icon/scanner.png"))  # Percorso all'icona
        self.open_scan_button.setIconSize(QSize(24, 24))  # Dimensioni dell'icona
        self.open_scan_button.clicked.connect(self.open_scanner)
        buttons_layout.addWidget(self.open_scan_button)


        # Allinea i pulsanti a destra
        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)

        # Raggruppamento dei documenti
        group_box = QGroupBox("RAGGRUPPA PER")
        group_layout = QFormLayout()
        self.group_combo = QComboBox()
        self.group_combo.addItems(["Nessuno", "Fornitore", "Mese"])
        self.group_combo.currentTextChanged.connect(self.group_documents)
        group_layout.addRow("Seleziona raggruppamento:", self.group_combo)
        group_box.setLayout(group_layout)
        self.layout.addWidget(group_box)

        # Campi di ricerca
        search_box = QGroupBox("RICERCA")
        search_layout = QHBoxLayout()

       # Campi di ricerca con suggerimenti
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Inserisci fornitore...")

        # Imposta i suggerimenti per i fornitori
        self.supplier_completer = QCompleter()
        self.supplier_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.supplier_input.setCompleter(self.supplier_completer)
        search_layout.addWidget(self.supplier_input)

        self.document_number_input = QLineEdit()
        self.document_number_input.setPlaceholderText("Inserisci numero documento...")
        search_layout.addWidget(self.document_number_input)

        self.date_checkbox = QCheckBox("Usa data")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd-MM-yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setEnabled(False)
        self.date_checkbox.stateChanged.connect(lambda: self.date_input.setEnabled(self.date_checkbox.isChecked()))
        search_layout.addWidget(self.date_checkbox)
        search_layout.addWidget(self.date_input)

        self.search_button = QPushButton("")
        self.search_button.setIcon(QIcon("icon/search.png"))  # Percorso all'icona
        self.search_button.setIconSize(QSize(20, 20))  # Dimensioni dell'icona
        self.search_button.clicked.connect(self.search_documents)
        search_layout.addWidget(self.search_button)

        search_box.setLayout(search_layout)
        self.layout.addWidget(search_box)

       # Tabella risultati
        self.result_table = QTableWidget()
        self.result_table.setSortingEnabled(True)
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["Giorno", "Fornitore", "Numero Documento"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.cellDoubleClicked.connect(self.open_document)
        self.result_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_table.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.result_table)

        # Visualizzatore PDF o immagini
        self.viewer = QWebEngineView()
        self.layout.addWidget(self.viewer)

        # Dati XML caricati
        self.documents = []
        self.row_to_doc_map = {}

        # Carica il file XML all'avvio
        self.load_xml()

    def load_xml(self):
        file_path = r"C:\\docs\\db.xml"
        if not os.path.exists(file_path):
            self.generate_xml()
        else:
            self.parse_xml(file_path)

    def open_file_explorer(self):
        server_path = r"\\192.168.3.220\DOCUMENTI\DDT"
        self.explorer_window = FileExplorerWindow(server_path)
        self.explorer_window.show()
        
    def open_scanner(self):
        # Estrai i fornitori unici dall'elenco dei documenti
        suppliers = list({doc["fornitore"] for doc in self.documents if doc["fornitore"]})
        server_path = r"\\192.168.3.220\DOCUMENTI\Scansioni RICOH"
        self.scanner_window = Scanner(server_path, suppliers)
        self.scanner_window.show()

    def parse_xml(self, file_path):
        self.documents = []
        self.row_to_doc_map = {}
        tree = ET.parse(file_path)
        root = tree.getroot()
        supplier_set = set()  # Per raccogliere i fornitori unici
        for month in root.findall("Mese"):
            month_name = month.get("nome", "")
            for day in month.findall("Giorno"):
                day_date = day.get("data", "")
                for doc in day.findall("Documento"):
                    supplier = doc.get("fornitore", "")
                    doc_number = doc.get("numero", "")
                    file_path = doc.get("percorso", "")
                    self.documents.append({
                        "mese": month_name,
                        "giorno": day_date,
                        "fornitore": supplier,
                        "numero": doc_number,
                        "file": file_path,
                    })
                    if supplier:
                        supplier_set.add(supplier)
        self.supplier_completer.setModel(QStringListModel(list(supplier_set)))
        self.documents.sort(key=lambda x: datetime.strptime(x["giorno"], "%d-%m-%Y"))
        self.update_table()

    def update_table(self):
        self.result_table.setRowCount(0)
        for row, doc in enumerate(self.documents):
            self.add_table_row(row, doc)

    def add_table_row(self, row, doc):
        self.result_table.insertRow(row)
        self.result_table.setItem(row, 0, QTableWidgetItem(doc["giorno"]))
        self.result_table.setItem(row, 1, QTableWidgetItem(doc["fornitore"]))
        self.result_table.setItem(row, 2, QTableWidgetItem(doc["numero"]))
        self.row_to_doc_map[row] = doc

    def search_documents(self):
        supplier_query = self.supplier_input.text().strip().lower()
        doc_number_query = self.document_number_input.text().strip().lower()
        date_query = self.date_input.date().toString("dd-MM-yyyy") if self.date_checkbox.isChecked() else None

        filtered_docs = [
            doc for doc in self.documents
            if (not supplier_query or supplier_query in doc["fornitore"].lower()) and
               (not doc_number_query or doc_number_query in doc["numero"].lower()) and
               (not date_query or date_query == doc["giorno"])
        ]

        self.result_table.setRowCount(0)
        self.row_to_doc_map = {}
        for row, doc in enumerate(filtered_docs):
            self.add_table_row(row, doc)

        if not filtered_docs:
            QMessageBox.information(self, "Nessun risultato", "Nessun documento trovato per i criteri di ricerca.")

    def group_documents(self):
        group_by = self.group_combo.currentText()
        if group_by == "Fornitore":
            grouped = self.group_by_supplier()
        elif group_by == "Mese":
            grouped = self.group_by_month()
        else:
            grouped = self.documents

        self.update_table_with_grouped_documents(grouped)

    def group_by_supplier(self):
        grouped = {}
        for doc in self.documents:
            grouped.setdefault(doc["fornitore"], []).append(doc)

        for supplier, docs in grouped.items():
            docs.sort(key=lambda x: datetime.strptime(x["giorno"], "%d-%m-%Y"))
        return grouped

    def group_by_month(self):
        grouped = {}
        for doc in self.documents:
            grouped.setdefault(doc["mese"], []).append(doc)

        for month, docs in grouped.items():
            docs.sort(key=lambda x: datetime.strptime(x["giorno"], "%d-%m-%Y"))
        return grouped

    def update_table_with_grouped_documents(self, grouped_docs):
        self.result_table.setRowCount(0)
        self.row_to_doc_map = {}

        if isinstance(grouped_docs, list):
            for row, doc in enumerate(grouped_docs):
                self.add_table_row(row, doc)
        else:
            for key, docs in grouped_docs.items():
                self.result_table.insertRow(self.result_table.rowCount())
                group_label = QTableWidgetItem(f"{key} (Gruppo)")
                group_label.setFont(QFont("Arial", 12, QFont.Bold))
                self.result_table.setItem(self.result_table.rowCount() - 1, 0, group_label)
                for doc in docs:
                    self.add_table_row(self.result_table.rowCount(), doc)

    def open_document(self, row, column):
        doc = self.get_doc_from_table(row)
        if not doc:
            QMessageBox.warning(self, "Errore", "Documento non trovato.")
            return

        file_path = doc["file"]
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)  # Apre il file con l'applicazione predefinita di Windows
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile aprire il file: {str(e)}")
        else:
            QMessageBox.warning(self, "Errore", "File non trovato.")

    def rename_file(self, doc):
        file_path = doc["file"]
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Errore", "Percorso non valido.")
            return

        new_name, ok = QInputDialog.getText(self, "Rinomina File", "Inserisci nuovo nome:", text=os.path.basename(file_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                doc["file"] = new_path
                QMessageBox.information(self, "Successo", "File rinominato con successo.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante la rinomina: {str(e)}")
    def open_in_explorer(self, doc):
            file_path = doc["file"]
            if os.path.exists(file_path):
                folder = os.path.dirname(file_path)
                os.startfile(folder)  # Apri la directory contenente il file
            else:
                QMessageBox.warning(self, "Errore", "File non trovato.")

    def delete_document(self, doc, row):
        reply = QMessageBox.question(
            self, "Conferma eliminazione",
            f"Sei sicuro di voler eliminare il documento selezionato? Questa azione non può essere annullata.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            file_path = doc["file"]

            # Verifica che il file esista prima di tentare di eliminarlo
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # Elimina fisicamente il file
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione del file: {str(e)}")
                    return

            # Rimuovi il documento dalla lista dei documenti
            self.documents.remove(doc)
    
            # Aggiorna il file XML
            try:
                self.update_xml()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento del file XML: {str(e)}")
                return

            # Aggiorna la tabella
            self.update_table()

            QMessageBox.information(self, "Successo", "Documento eliminato con successo.")
    def update_xml(self):
        """Aggiorna il file XML per riflettere le modifiche apportate alla lista dei documenti."""
        root = ET.Element("Documenti")

        # Raggruppa i documenti per mese e giorno
        grouped_by_month = {}
        for doc in self.documents:
            month = doc["mese"]
            day = doc["giorno"]
            if month not in grouped_by_month:
                grouped_by_month[month] = {}
            if day not in grouped_by_month[month]:
                grouped_by_month[month][day] = []
            grouped_by_month[month][day].append(doc)

        for month, days in grouped_by_month.items():
            month_elem = ET.SubElement(root, "Mese", nome=month)
            for day, docs in days.items():
                day_elem = ET.SubElement(month_elem, "Giorno", data=day)
                for doc in docs:
                    ET.SubElement(
                        day_elem,
                        "Documento",
                        fornitore=doc["fornitore"],
                        numero=doc["numero"],
                        percorso=doc["file"]
                    ).text = os.path.basename(doc["file"])

        # Salva le modifiche nel file XML
        save_path = r"C:\\docs\\db.xml"
        tree = ET.ElementTree(root)
        tree.write(save_path, encoding="utf-8", xml_declaration=True)
    def get_doc_from_table(self, row):
        giorno = self.result_table.item(row, 0).text()
        fornitore = self.result_table.item(row, 1).text()
        numero = self.result_table.item(row, 2).text()

        # Cerca il documento corrispondente nei dati originali
        for doc in self.documents:
            if doc["giorno"] == giorno and doc["fornitore"] == fornitore and doc["numero"] == numero:
                return doc
        return None
    
    def show_context_menu(self, position):
        indexes = self.result_table.selectedIndexes()
        if not indexes:
            return

        selected_row = indexes[0].row()
        doc = self.get_doc_from_table(selected_row)
        if not doc:
            return

        menu = QMenu()
        open_action = menu.addAction("Apri")
        rename_action = menu.addAction("Rinomina")
        goto_action = menu.addAction("Vai al file")
        delete_action = menu.addAction("Elimina")

        action = menu.exec_(self.result_table.viewport().mapToGlobal(position))

        if action == open_action:
            self.open_document(selected_row, 0)
        elif action == rename_action:
            self.rename_file(doc)
        elif action == goto_action:
            self.open_in_explorer(doc)
        elif action == delete_action:
            self.delete_document(doc, selected_row)

    def generate_xml(self):
        # Ottieni il percorso base
        base_path = r"\\192.168.3.220\DOCUMENTI\DDT"
        if not os.path.exists(base_path):
            QMessageBox.warning(self, "Errore", f"Il percorso base {base_path} non esiste.")
            return

        # Genera pulsanti per ogni anno presente nel percorso base
        year_dirs = [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]
        if not year_dirs:
            QMessageBox.warning(self, "Errore", "Nessun anno trovato nel percorso base.")
            return

        # Mostra una finestra di dialogo per selezionare l'anno
        year, ok = QInputDialog.getItem(self, "Seleziona Anno", "Scegli l'anno:", year_dirs, 0, False)
        if not ok:
            return

        year_path = os.path.join(base_path, year)
        if not os.path.exists(year_path):
            QMessageBox.warning(self, "Errore", f"La cartella per l'anno {year} non esiste.")
            return

        # Finestra di caricamento
        progress_dialog = QProgressDialog("Generazione XML in corso...", None, 0, 0, self)
        progress_dialog.setWindowTitle("Attendere")
        progress_dialog.setCancelButton(None)
        progress_dialog.setModal(True)
        progress_dialog.show()

        try:
            # Creazione del file XML
            root = ET.Element("Documenti")
            root.set("anno", year)

            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if os.path.isdir(month_path):
                    month_elem = ET.SubElement(root, "Mese", nome=month)

                    for day in os.listdir(month_path):
                        day_path = os.path.join(month_path, day)
                        if os.path.isdir(day_path):
                            day_elem = ET.SubElement(month_elem, "Giorno", data=day)

                            for file in os.listdir(day_path):
                                file_path = os.path.join(day_path, file)
                                if os.path.isfile(file_path) and file.lower().endswith(".pdf"):
                                    file_name, _ = os.path.splitext(file)
                                    match = re.match(r"^(.*?)(\s\d+(?:\s\(\d+\))?)$", file_name)
                                    if match:
                                        supplier = match.group(1).strip()
                                        doc_number = match.group(2).strip()
                                    else:
                                        supplier = file_name
                                        doc_number = "N/A"
                                    ET.SubElement(
                                        day_elem,
                                        "Documento",
                                        fornitore=supplier,
                                        numero=doc_number,
                                        percorso=file_path
                                    ).text = file

            # Salvataggio del file XML
            save_path = r"C:\\docs\\db.xml"
            if not os.path.exists(r"C:\\docs"):
                os.makedirs(r"C:\\docs")

            tree = ET.ElementTree(root)
            tree.write(save_path, encoding="utf-8", xml_declaration=True)
            QMessageBox.information(self, "Successo", f"Database documenti aggiornato.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la generazione XML: {str(e)}")
        finally:
            progress_dialog.close()

        # Ricarica il file XML appena generato
        self.load_xml()
        
        
if __name__ == "__main__":
    app = QApplication([])
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = DocumentSearchApp()
    window.show()
    app.exec_()