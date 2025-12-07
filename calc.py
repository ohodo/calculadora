import sqlite3
import customtkinter as ctk
import math
from tkinter import messagebox

# Configurar apariencia de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Conectar a la base de datos
conn = sqlite3.connect("maq.db")
cursor = conn.cursor()

# Obtener lista de generadores
cursor.execute("SELECT nombre FROM energia")
generadores = [fila[0] for fila in cursor.fetchall()]

# Obtener lista de máquinas
cursor.execute("SELECT nombre FROM maquinas")
maquinas = [fila[0] for fila in cursor.fetchall()]

if not maquinas:
    messagebox.showerror("Error", "No hay máquinas registradas en la base de datos.")

# Almacén de selección de máquinas
seleccionadas = {}

# Diccionario para almacenar widgets de la tabla
widgets_tabla = {}

# Variable para el número de filas en la tabla
fila_actual = 1  # Empieza en 1 porque la fila 0 son los encabezados

# Función para añadir máquina seleccionada
def agregar_maquina():
    global fila_actual
    nombre_maquina = combo_maquinas.get()
    
    if nombre_maquina and nombre_maquina not in seleccionadas:
        # Crear frame en la lista de selección
        frame_lista = ctk.CTkFrame(lista_seleccionadas)
        frame_lista.pack(pady=5, padx=5, fill="x")
        
        # Almacenar datos básicos
        seleccionadas[nombre_maquina] = {
            "cantidad": ctk.StringVar(value="1"),
            "overclock": ctk.StringVar(value="100"),
            "frame_lista": frame_lista,
            "fila_tabla": fila_actual  # Guardar número de fila en la tabla
        }
        
        # Widgets en la lista
        ctk.CTkLabel(frame_lista, text=nombre_maquina).pack(side="left", padx=5)
        
        entrada_cantidad = ctk.CTkEntry(frame_lista, width=50, 
                                       textvariable=seleccionadas[nombre_maquina]["cantidad"])
        entrada_cantidad.pack(side="left")
        
        ctk.CTkLabel(frame_lista, text="Overclock (%)").pack(side="left", padx=5)
        
        valores_overclock = [str(i) for i in range(100, 251, 10)]
        combo_overclock = ctk.CTkComboBox(frame_lista, values=valores_overclock,
                                         variable=seleccionadas[nombre_maquina]["overclock"])
        combo_overclock.pack(side="left")
        combo_overclock.set("100")
        
        # Botón eliminar solo de la lista (NO de la tabla)
        btn_eliminar_lista = ctk.CTkButton(frame_lista, text="Quitar de lista", 
                                          command=lambda n=nombre_maquina: eliminar_solo_de_lista(n))
        btn_eliminar_lista.pack(side="left", padx=5)
        
        # Incrementar contador de filas
        fila_actual += 1
        
        # Actualizar tabla
        mostrar_tabla()

# Función para eliminar solo de la lista (NO de la tabla)
def eliminar_solo_de_lista(nombre_maquina):
    if nombre_maquina in seleccionadas:
        # Solo destruir el frame de la lista
        if 'frame_lista' in seleccionadas[nombre_maquina]:
            seleccionadas[nombre_maquina]["frame_lista"].destroy()
        # No eliminar de seleccionadas para mantener en tabla
        # Solo marcar como removida de lista
        seleccionadas[nombre_maquina]["en_lista"] = False

# Función para calcular consumo total
def calcular_consumo():
    consumo_total = 0
    for nombre_maquina, datos in seleccionadas.items():
        cantidad = datos["cantidad"].get()
        overclock = datos["overclock"].get()

        if cantidad.isdigit() and overclock.isdigit():
            cantidad = int(cantidad)
            overclock = max(100, min(int(overclock), 250))

            cursor.execute("SELECT energia FROM maquinas WHERE nombre=?", (nombre_maquina,))
            resultado = cursor.fetchone()

            if resultado:
                consumo_base = resultado[0]
                consumo_ajustado = consumo_base * (overclock / 100) ** 1.321928
                consumo_total += consumo_ajustado * cantidad

                # Guardar consumo calculado
                datos["consumo_calculado"] = round(consumo_ajustado * cantidad, 1)

    lbl_resultado.configure(text=f"Consumo total: {round(consumo_total, 1)} MW")
    calcular_generadores(consumo_total)
    mostrar_tabla()

# Función para calcular generadores
def calcular_generadores(consumo_total):
    tipo_generador = combo_generadores.get()
    if tipo_generador:
        cursor.execute("SELECT capacidad_energia FROM energia WHERE nombre=?", (tipo_generador,))
        resultado = cursor.fetchone()
        if resultado:
            capacidad_generador = resultado[0]
            cantidad_necesaria = math.ceil(consumo_total / capacidad_generador)
            lbl_generadores.configure(text=f"Necesitas {cantidad_necesaria} {tipo_generador}(s)")
            
            # Guardar cantidad de generadores
            for datos in seleccionadas.values():
                datos["generadores_necesarios"] = cantidad_necesaria

# Función para mostrar/actualizar la tabla
def mostrar_tabla():
    global fila_actual
    
    # Limpiar solo los widgets de datos, NO los encabezados
    for widget in tabla_maquinas.winfo_children():
        info = widget.grid_info()
        if info and info['row'] > 0:  # Solo eliminar filas de datos (fila 0 son encabezados)
            widget.destroy()
    
    # Limpiar diccionario de widgets
    widgets_tabla.clear()
    
    # Crear encabezados solo si no existen
    if not hasattr(mostrar_tabla, 'encabezados_creados'):
        columnas = ["Nombre", "Cantidad", "Overclock", "Consumo (MW)", "Generadores", "Acción"]
        
        for i, columna in enumerate(columnas):
            header = ctk.CTkLabel(tabla_maquinas, text=columna, 
                                 font=("Arial", 12, "bold"))
            header.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
        
        mostrar_tabla.encabezados_creados = True
    
    # Crear filas con datos
    fila = 1  # Empieza después de los encabezados
    for nombre, datos in seleccionadas.items():
        fila_widgets = []
        
        # Columna 0: Nombre
        lbl_nombre = ctk.CTkLabel(tabla_maquinas, text=nombre)
        lbl_nombre.grid(row=fila, column=0, padx=10, pady=5, sticky="w")
        fila_widgets.append(lbl_nombre)
        
        # Columna 1: Cantidad
        lbl_cantidad = ctk.CTkLabel(tabla_maquinas, text=datos["cantidad"].get())
        lbl_cantidad.grid(row=fila, column=1, padx=10, pady=5)
        fila_widgets.append(lbl_cantidad)
        
        # Columna 2: Overclock
        lbl_overclock = ctk.CTkLabel(tabla_maquinas, text=datos["overclock"].get() + "%")
        lbl_overclock.grid(row=fila, column=2, padx=10, pady=5)
        fila_widgets.append(lbl_overclock)
        
        # Columna 3: Consumo
        consumo_texto = datos.get("consumo_calculado", "N/A")
        lbl_consumo = ctk.CTkLabel(tabla_maquinas, text=str(consumo_texto))
        lbl_consumo.grid(row=fila, column=3, padx=10, pady=5)
        fila_widgets.append(lbl_consumo)
        
        # Columna 4: Generadores
        generadores_texto = datos.get("generadores_necesarios", "N/A")
        lbl_generadores = ctk.CTkLabel(tabla_maquinas, text=str(generadores_texto))
        lbl_generadores.grid(row=fila, column=4, padx=10, pady=5)
        fila_widgets.append(lbl_generadores)
        
        # Columna 5: Botón Eliminar (SOLO de la tabla)
        btn_eliminar = ctk.CTkButton(
            tabla_maquinas, 
            text="✖ Eliminar", 
            width=80,
            height=30,
            fg_color="#d9534f",  # Rojo
            hover_color="#c9302c",
            command=lambda n=nombre, f=fila: eliminar_fila_tabla(n, f)  # Pasar nombre Y fila
        )
        btn_eliminar.grid(row=fila, column=5, padx=10, pady=5)
        fila_widgets.append(btn_eliminar)
        
        # Guardar referencia
        widgets_tabla[nombre] = {
            "widgets": fila_widgets,
            "fila": fila
        }
        
        # Guardar número de fila en los datos
        datos["fila_tabla"] = fila
        
        fila += 1
    
    # Actualizar contador global
    fila_actual = fila

# Función CORREGIDA para eliminar solo una fila de la tabla
def eliminar_fila_tabla(nombre_maquina, numero_fila):
    """Elimina SOLO la fila de la tabla, NO toda la aplicación"""
    
    # Preguntar confirmación
    respuesta = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Estás seguro de eliminar '{nombre_maquina}' de la tabla?\n\n"
        "NOTA: Esto solo la quitará de la tabla de resultados."
    )
    
    if not respuesta:
        return  # Cancelar si el usuario dice no
    
    try:
        # Verificar que el nombre existe en widgets_tabla
        if nombre_maquina not in widgets_tabla:
            messagebox.showerror("Error", f"No se encontró '{nombre_maquina}' en la tabla.")
            return
        
        # 1. Eliminar solo los widgets de ESTA fila específica
        if nombre_maquina in widgets_tabla:
            for widget in widgets_tabla[nombre_maquina]["widgets"]:
                if widget and widget.winfo_exists():
                    widget.destroy()
            
            # Eliminar del diccionario de widgets
            del widgets_tabla[nombre_maquina]
        
        # 2. Eliminar de seleccionadas (opcional, dependiendo de lo que quieras)
        # Si quieres que desaparezca completamente:
        if nombre_maquina in seleccionadas:
            # Eliminar también de la lista si existe
            if 'frame_lista' in seleccionadas[nombre_maquina]:
                frame = seleccionadas[nombre_maquina]["frame_lista"]
                if frame and frame.winfo_exists():
                    frame.destroy()
            
            # Eliminar del diccionario seleccionadas
            del seleccionadas[nombre_maquina]
        
        # 3. Reorganizar las filas restantes
        reorganizar_filas_tabla()
        
        # 4. Recalcular si hay máquinas restantes
        if seleccionadas:
            calcular_consumo()
        else:
            lbl_resultado.configure(text="Consumo total: N/A")
            lbl_generadores.configure(text="Cantidad de generadores necesaria: N/A")
        
        messagebox.showinfo("Eliminado", f"'{nombre_maquina}' ha sido eliminado de la tabla.")
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

# Función para reorganizar filas después de eliminar
def reorganizar_filas_tabla():
    """Reorganiza los números de fila después de eliminar una"""
    global fila_actual
    
    # Recrear widgets_tabla con nuevas posiciones
    nuevos_widgets = {}
    fila = 1
    
    for nombre, datos in seleccionadas.items():
        if nombre in widgets_tabla:
            # Actualizar posición de cada widget
            widgets_fila = widgets_tabla[nombre]["widgets"]
            
            for i, widget in enumerate(widgets_fila):
                if widget and widget.winfo_exists():
                    widget.grid(row=fila, column=i, padx=10, pady=5)
            
            # Actualizar en nuevo diccionario
            nuevos_widgets[nombre] = {
                "widgets": widgets_fila,
                "fila": fila
            }
            
            # Actualizar en seleccionadas
            seleccionadas[nombre]["fila_tabla"] = fila
            
            fila += 1
    
    # Actualizar diccionario global
    widgets_tabla.clear()
    widgets_tabla.update(nuevos_widgets)
    
    # Actualizar contador
    fila_actual = fila

# Función para limpiar TODO (incluye confirmación)
def limpiar_todo():
    """Limpia completamente la aplicación (lista y tabla)"""
    respuesta = messagebox.askyesno(
        "Confirmar limpieza total",
        "¿Estás seguro de que quieres eliminar TODAS las máquinas?\n\n"
        "Esto limpiará tanto la lista como la tabla."
    )
    
    if not respuesta:
        return
    
    # 1. Eliminar frames de la lista
    for nombre, datos in list(seleccionadas.items()):
        if 'frame_lista' in datos and datos['frame_lista']:
            if datos['frame_lista'].winfo_exists():
                datos['frame_lista'].destroy()
    
    # 2. Limpiar diccionarios
    seleccionadas.clear()
    widgets_tabla.clear()
    
    # 3. Limpiar widgets de datos en la tabla (mantener encabezados)
    for widget in tabla_maquinas.winfo_children():
        info = widget.grid_info()
        if info and info['row'] > 0:  # Solo filas de datos
            widget.destroy()
    
    # 4. Resetear contador
    global fila_actual
    fila_actual = 1
    
    # 5. Actualizar etiquetas
    lbl_resultado.configure(text="Consumo total: N/A")
    lbl_generadores.configure(text="Cantidad de generadores necesaria: N/A")
    
    messagebox.showinfo("Limpieza completada", "Todas las máquinas han sido eliminadas.")

# Crear ventana principal
root = ctk.CTk()
root.title("Calculadora de Consumo Energético")
root.geometry("1000x800")

# Configurar grid para expansión
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(7, weight=1)

# Título
titulo = ctk.CTkLabel(root, text="🔧 Calculadora de Consumo Energético", 
                     font=("Arial", 18, "bold"))
titulo.grid(row=0, column=0, pady=20)

# Frame para lista de selección
frame_lista = ctk.CTkFrame(root)
frame_lista.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

ctk.CTkLabel(frame_lista, text="Seleccionar Máquina:").pack(side="left", padx=5)
combo_maquinas = ctk.CTkComboBox(frame_lista, values=maquinas, width=250)
combo_maquinas.pack(side="left", padx=5)

btn_agregar = ctk.CTkButton(frame_lista, text="➕ Agregar a lista", 
                           command=agregar_maquina)
btn_agregar.pack(side="left", padx=10)

# Frame scrollable para lista de máquinas seleccionadas
lista_seleccionadas = ctk.CTkScrollableFrame(root, height=150)
lista_seleccionadas.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

# Frame para botón calcular
frame_calcular = ctk.CTkFrame(root)
frame_calcular.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

btn_calcular = ctk.CTkButton(frame_calcular, text="🧮 Calcular Consumo", 
                            command=calcular_consumo, 
                            font=("Arial", 12, "bold"),
                            height=40)
btn_calcular.pack(side="left", padx=10)

lbl_resultado = ctk.CTkLabel(frame_calcular, text="Consumo total: N/A", 
                            font=("Arial", 12, "bold"))
lbl_resultado.pack(side="left", padx=20)

# Frame para selección de generador
frame_gen = ctk.CTkFrame(root)
frame_gen.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

ctk.CTkLabel(frame_gen, text="Generador de energía:").pack(side="left", padx=5)
combo_generadores = ctk.CTkComboBox(frame_gen, values=generadores, width=200)
combo_generadores.pack(side="left", padx=5)

lbl_generadores = ctk.CTkLabel(frame_gen, 
                              text="Cantidad necesaria: N/A")
lbl_generadores.pack(side="left", padx=20)

# Botón para limpiar todo
btn_limpiar_todo = ctk.CTkButton(root, text="🗑️ Limpiar Todo", 
                                command=limpiar_todo,
                                fg_color="#d9534f",
                                hover_color="#c9302c",
                                font=("Arial", 11))
btn_limpiar_todo.grid(row=5, column=0, pady=10)

# Título de la tabla
ctk.CTkLabel(root, text="📊 Tabla de Resultados", 
            font=("Arial", 14, "bold")).grid(row=6, column=0, pady=10)

# Frame para la tabla (con scroll)
frame_tabla = ctk.CTkFrame(root)
frame_tabla.grid(row=7, column=0, padx=20, pady=10, sticky="nsew")
frame_tabla.grid_columnconfigure(0, weight=1)
frame_tabla.grid_rowconfigure(0, weight=1)

# Tabla scrollable
tabla_scrollable = ctk.CTkScrollableFrame(frame_tabla)
tabla_scrollable.grid(row=0, column=0, sticky="nsew")
tabla_scrollable.grid_columnconfigure(0, weight=1)

# Tabla de máquinas (DENTRO del scrollable)
tabla_maquinas = ctk.CTkFrame(tabla_scrollable)
tabla_maquinas.pack(fill="both", expand=True, padx=5, pady=5)

# Configurar columnas de la tabla
for i in range(6):
    tabla_maquinas.grid_columnconfigure(i, weight=1)

root.mainloop()
conn.close()