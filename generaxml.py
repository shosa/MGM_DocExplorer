import os
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET


def generate_xml():
    year = year_entry.get()
    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Errore", "Inserisci un anno valido (es. 2024).")
        return

    base_path = r"\\192.168.3.220\DOCUMENTI\DDT"
    year_path = os.path.join(base_path, year)

    if not os.path.exists(year_path):
        messagebox.showerror("Errore", f"La cartella per l'anno {year} non esiste.")
        return

    # Creazione dell'XML
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

                            # Gestione del nome fornitore e numero documento
                            try:
                                *supplier_parts, doc_number = file_name.split(" ")
                                supplier = " ".join(supplier_parts)
                            except ValueError:
                                supplier, doc_number = file_name, "N/A"

                            # Aggiungere il percorso come attributo del documento
                            ET.SubElement(
                                day_elem,
                                "Documento",
                                fornitore=supplier,
                                numero=doc_number,
                                percorso=file_path
                            ).text = file

    # Salvataggio dell'XML
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")],
        title="Salva il file XML",
    )
    if save_path:
        tree = ET.ElementTree(root)
        tree.write(save_path, encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Successo", f"File XML salvato in: {save_path}")


# Creazione della GUI
root = tk.Tk()
root.title("Generatore XML Documenti")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Inserisci l'anno (es. 2024):").grid(row=0, column=0, sticky="w")

year_entry = tk.Entry(frame, width=10)
year_entry.grid(row=0, column=1)

generate_btn = tk.Button(frame, text="Genera XML", command=generate_xml)
generate_btn.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()
