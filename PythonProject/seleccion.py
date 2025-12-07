import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
ventana = ctk.CTk()
ventana.title("Supermarket Simulator Mod Manager")
ventana.geometry("800x500")

# ─── Variables ──────────────────────────────────────────
mods_bepinex = []
mods_melon = []
archivo_es3 = None
valor_money = ctk.StringVar()
valor_day = ctk.StringVar()

# ─── Funciones ──────────────────────────────────────────
def cargar_mods():
    carpeta = filedialog.askdirectory(title="Selecciona carpeta de Mods")
    if carpeta:
        mods_bepinex.clear()
        mods_melon.clear()
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".dll"):
                mods_bepinex.append(archivo)
            elif archivo.endswith(".cfg"):
                mods_melon.append(archivo)
        listar_mods()

def listar_mods():
    lista_bepinex.configure(values=mods_bepinex)
    lista_melon.configure(values=mods_melon)

def cargar_save():
    global archivo_es3
    archivo = filedialog.askopenfilename(filetypes=[("Save File", "*.es3")])
    if archivo:
        try:
            archivo_es3 = archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                valor_money.set(str(round(datos["Progression"]["value"]["Money"], 2)))
                valor_day.set(str(datos.get("Progression", {}).get("value", {}).get("CurrentDay", 1)))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

def guardar_save():
    if not archivo_es3:
        return messagebox.showwarning("Sin archivo", "Primero debes seleccionar un archivo .es3")
    try:
        with open(archivo_es3, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        datos["Progression"]["value"]["Money"] = float(valor_money.get())
        datos["Progression"]["value"]["CurrentDay"] = int(valor_day.get())
        with open(archivo_es3, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
        messagebox.showinfo("Éxito", "Archivo guardado correctamente")
    except Exception as e:
        messagebox.showerror("Error al guardar", str(e))

# ─── Layout de Interfaz ─────────────────────────────────

frame_mods = ctk.CTkFrame(ventana)
frame_mods.pack(side="left", fill="y", padx=10, pady=10)

titulo = ctk.CTkLabel(frame_mods, text="Mods Instalados", font=("Arial", 16))
titulo.pack(pady=5)

btn_cargar = ctk.CTkButton(frame_mods, text="Cargar mods", command=cargar_mods)
btn_cargar.pack(pady=5)

ctk.CTkLabel(frame_mods, text="BepInEx DLLs").pack()
lista_bepinex = ctk.CTkComboBox(frame_mods, values=[], state="readonly")
lista_bepinex.pack(pady=2)

ctk.CTkLabel(frame_mods, text="MelonLoader CFGs").pack()
lista_melon = ctk.CTkComboBox(frame_mods, values=[], state="readonly")
lista_melon.pack(pady=2)

frame_editor = ctk.CTkFrame(ventana)
frame_editor.pack(side="left", fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(frame_editor, text="Editor de Partida", font=("Arial", 16)).pack(pady=10)

btn_cargar_save = ctk.CTkButton(frame_editor, text="Seleccionar archivo .es3", command=cargar_save)
btn_cargar_save.pack(pady=5)

ctk.CTkLabel(frame_editor, text="Dinero actual").pack()
entry_money = ctk.CTkEntry(frame_editor, textvariable=valor_money, width=150)
entry_money.pack(pady=5)

ctk.CTkLabel(frame_editor, text="Día actual").pack()
entry_day = ctk.CTkEntry(frame_editor, textvariable=valor_day, width=150)
entry_day.pack(pady=5)

btn_guardar = ctk.CTkButton(frame_editor, text="Guardar cambios", command=guardar_save)
btn_guardar.pack(pady=10)

ventana.mainloop()