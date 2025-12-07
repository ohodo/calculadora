import customtkinter as ctk
import mysql.connector

# Apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pals"
)
cursor = conn.cursor()
cursor.execute("SELECT pal_id, nombre FROM Pals")
pals = cursor.fetchall()

# Crear diccionario de opciones
opciones_dict = {f"{pal[0]} - {pal[1]}": pal[1] for pal in pals}
opciones_menu = list(opciones_dict.keys())

# Control de fila
fila_actual = [1]

# Función para filtrar dinámicamente
def filtrar(event):
    termino = entrada.get().lower()
    coincidencias = [op for op in opciones_menu if termino in op.lower()]
    menu.configure(values=coincidencias or ["Sin resultados"])
    menu.set(coincidencias[0] if coincidencias else "Sin resultados")

# Agrega solo el nombre a la tabla visual
def agregar_a_tabla():
    seleccionado = menu.get()
    if seleccionado in opciones_dict:
        nombre = opciones_dict[seleccionado]
        ctk.CTkLabel(tabla_frame, text=nombre, width=400).grid(
            row=fila_actual[0], column=0, padx=5, pady=2, sticky="w"
        )
        fila_actual[0] += 1

# Limpia la tabla (excepto encabezado)
def limpiar_tabla():
    for widget in tabla_frame.winfo_children():
        if widget.grid_info()["row"] != 0:
            widget.destroy()
    fila_actual[0] = 1

# Crear ventana
ventana = ctk.CTk()
ventana.title("Buscador de Pals")
ancho, alto = 800, 500
ventana.update_idletasks()
xp = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
yp = (ventana.winfo_screenheight() // 2) - (alto // 2)
ventana.geometry(f"{ancho}x{alto}+{xp}+{yp}")

# Entrada y filtrado
entrada = ctk.CTkEntry(ventana, placeholder_text="Buscar Pal...")
entrada.pack(pady=10)
entrada.bind("<KeyRelease>", filtrar)

# Menú desplegable
menu = ctk.CTkOptionMenu(ventana, values=opciones_menu)
menu.pack(pady=10)

# Botones de acción
ctk.CTkButton(ventana, text="Agregar a tabla", command=agregar_a_tabla).pack(pady=5)
ctk.CTkButton(ventana, text="Limpiar tabla", command=limpiar_tabla).pack(pady=5)

# Tabla visual
tabla_frame = ctk.CTkScrollableFrame(ventana, width=500, height=250)
tabla_frame.pack(pady=10)

# Encabezado
ctk.CTkLabel(tabla_frame, text="Nombre", width=400).grid(row=0, column=0, padx=5, pady=5)

ventana.mainloop()