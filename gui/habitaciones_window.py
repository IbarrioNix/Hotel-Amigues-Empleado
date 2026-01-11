# gui/habitaciones_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from core.session import obtener_sesion
from typing import Optional, List, Tuple


class HabitacionesWindow:
    def __init__(self, parent):
        self.parent = parent

        # 🔹 Obtener sesión global
        self.session = obtener_sesion()

        # 🔹 Obtener la base de datos desde la sesión
        self.db = self.session.db

        # Variables
        self.habitacion_seleccionada = None
        self.filtro_estado = "Todos"
        self.filtro_tipo = "Todos"

        # Colores
        self.COLORES = {
            'disponible': "#27AE60",
            'ocupada': "#E74C3C",
            'limpieza': "#F39C12",
            'mantenimiento': "#95A5A6",
            'card_bg': ("#FFFFFF", "#3a3a3a"),
            'primary': "#3498DB",
            'success': "#27AE60",
            'danger': "#E74C3C",
        }

        self._crear_interfaz()
        self.cargar_habitaciones()

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Container principal
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(main_container)

        # Filtros y búsqueda
        self._crear_panel_filtros(main_container)

        # Grid de habitaciones
        self._crear_grid_habitaciones(main_container)

    def _crear_header(self, parent):
        """Crea el header con título y estadísticas rápidas"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_frame,
            text="🛏️ Gestión de Habitaciones",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Administra el inventario de habitaciones del hotel",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Botón agregar (destacado)
        btn_agregar = ctk.CTkButton(
            header,
            text="➕ Nueva Habitación",
            command=self.abrir_formulario_agregar,
            font=("Segoe UI", 14, "bold"),
            height=50,
            width=200,
            corner_radius=12,
            fg_color=self.COLORES['success'],
            hover_color="#229954"
        )
        btn_agregar.pack(side="right")

    def _crear_panel_filtros(self, parent):
        """Crea el panel de filtros y búsqueda"""
        filtros_container = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        filtros_container.pack(fill="x", pady=(0, 20))

        # Container interno
        content = ctk.CTkFrame(filtros_container, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        # Búsqueda
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 10))

        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por número de habitación...",
            height=40,
            width=300,
            font=("Segoe UI", 12),
            corner_radius=10
        )
        self.entry_buscar.pack(side="left", padx=(0, 15))
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.aplicar_filtros())

        # Filtro por estado
        ctk.CTkLabel(
            search_frame,
            text="Estado:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(10, 5))

        self.combo_filtro_estado = ctk.CTkComboBox(
            search_frame,
            values=["Todos", "disponible", "ocupada", "limpieza", "mantenimiento"],
            height=40,
            width=150,
            font=("Segoe UI", 11),
            corner_radius=10,
            command=lambda e: self.aplicar_filtros()
        )
        self.combo_filtro_estado.pack(side="left", padx=(0, 15))
        self.combo_filtro_estado.set("Todos")

        # Filtro por tipo
        ctk.CTkLabel(
            search_frame,
            text="Tipo:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(10, 5))

        self.combo_filtro_tipo = ctk.CTkComboBox(
            search_frame,
            values=["Todos", "Sencilla", "Doble", "Familiar", "Deluxe"],
            height=40,
            width=130,
            font=("Segoe UI", 11),
            corner_radius=10,
            command=lambda e: self.aplicar_filtros()
        )
        self.combo_filtro_tipo.pack(side="left")
        self.combo_filtro_tipo.set("Todos")

        # Botón refrescar
        btn_refrescar = ctk.CTkButton(
            content,
            text="🔄",
            command=self.cargar_habitaciones,
            width=40,
            height=40,
            font=("Segoe UI", 18),
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A")
        )
        btn_refrescar.pack(side="right", padx=(10, 0))

    def _crear_grid_habitaciones(self, parent):
        """Crea el grid scrollable de habitaciones"""
        # Frame contenedor con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

        # Configurar grid
        for i in range(4):
            self.scroll_frame.columnconfigure(i, weight=1)

    def cargar_habitaciones(self):
        """Carga y muestra las habitaciones"""
        # Limpiar grid
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener habitaciones
        habitaciones = self.db.obtener_habitaciones()

        if not habitaciones:
            self._mostrar_mensaje_vacio()
            return

        # Aplicar filtros
        habitaciones_filtradas = self._filtrar_habitaciones(habitaciones)

        if not habitaciones_filtradas:
            self._mostrar_mensaje_sin_resultados()
            return

        # Mostrar habitaciones en grid
        self._mostrar_habitaciones_grid(habitaciones_filtradas)

    def _filtrar_habitaciones(self, habitaciones: List[Tuple]) -> List[Tuple]:
        """Filtra las habitaciones según criterios"""
        busqueda = self.entry_buscar.get().strip().lower()
        estado_filtro = self.combo_filtro_estado.get()
        tipo_filtro = self.combo_filtro_tipo.get()

        habitaciones_filtradas = []

        for hab in habitaciones:
            # hab = (id, numero, tipo, precio, estado)
            numero = str(hab[1]).lower()
            tipo = hab[2]
            estado = hab[4]

            # Aplicar filtros
            coincide_busqueda = busqueda in numero if busqueda else True
            coincide_estado = estado == estado_filtro if estado_filtro != "Todos" else True
            coincide_tipo = tipo == tipo_filtro if tipo_filtro != "Todos" else True

            if coincide_busqueda and coincide_estado and coincide_tipo:
                habitaciones_filtradas.append(hab)

        return habitaciones_filtradas

    def _mostrar_habitaciones_grid(self, habitaciones: List[Tuple]):
        """Muestra las habitaciones en formato grid"""
        row = 0
        col = 0

        for hab in habitaciones:
            card = self._crear_tarjeta_habitacion(hab)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            col += 1
            if col >= 4:
                col = 0
                row += 1

    def _crear_tarjeta_habitacion(self, datos: Tuple):
        """Crea una tarjeta visual para una habitación"""
        habitacion_id, numero, tipo, precio, estado = datos

        # Frame principal de la tarjeta
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15,
            border_width=2,
            border_color=("#E0E0E0", "#4A4A4A"),
            width=280,
            height=320
        )
        card.pack_propagate(False)

        # Hover effect
        card.bind("<Enter>", lambda e: card.configure(border_color=self.COLORES['primary']))
        card.bind("<Leave>", lambda e: card.configure(border_color=("#E0E0E0", "#4A4A4A")))

        # Click para seleccionar
        card.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Container interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)

        # Bind click en todos los elementos hijos
        for widget in content.winfo_children():
            widget.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Badge de estado en la esquina superior
        badge_frame = ctk.CTkFrame(content, fg_color="transparent")
        badge_frame.pack(fill="x")

        badge = ctk.CTkLabel(
            badge_frame,
            text=self._get_texto_estado(estado),
            font=("Segoe UI", 9, "bold"),
            fg_color=self.COLORES.get(estado, "#95A5A6"),
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(side="right")
        badge.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Número de habitación (grande)
        numero_label = ctk.CTkLabel(
            content,
            text=f"#{numero}",
            font=("Segoe UI", 32, "bold")
        )
        numero_label.pack(pady=(10, 5))
        numero_label.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Tipo de habitación
        tipo_label = ctk.CTkLabel(
            content,
            text=tipo,
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        )
        tipo_label.pack(pady=(0, 10))
        tipo_label.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Separador
        separator = ctk.CTkFrame(content, height=2, fg_color=("#E0E0E0", "#4A4A4A"))
        separator.pack(fill="x", pady=(0, 10))

        # Precio
        precio_frame = ctk.CTkFrame(content, fg_color="transparent")
        precio_frame.pack(pady=(0, 10))
        precio_frame.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        precio_label = ctk.CTkLabel(
            precio_frame,
            text=f"${precio:,.2f}",
            font=("Segoe UI", 18, "bold"),
            text_color=self.COLORES['success']
        )
        precio_label.pack(side="left")
        precio_label.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        noche_label = ctk.CTkLabel(
            precio_frame,
            text="/noche",
            font=("Segoe UI", 10),
            text_color=("#95A5A6", "#7F8C8D")
        )
        noche_label.pack(side="left", padx=(5, 0))
        noche_label.bind("<Button-1>", lambda e: self._seleccionar_habitacion(datos, card))

        # Botones de acción
        self._crear_botones_tarjeta(content, datos)

        return card

    def _crear_botones_tarjeta(self, parent, datos):
        """Crea los botones de acción en la tarjeta"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        # Botón editar
        btn_editar = ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=40,
            height=32,
            font=("Segoe UI", 14),
            corner_radius=8,
            fg_color=self.COLORES['primary'],
            hover_color="#2980B9",
            command=lambda: self.abrir_formulario_editar(datos)
        )
        btn_editar.pack(side="left", expand=True, padx=(0, 5))

        # Botón eliminar (solo admin)
        if self.session.tiene_privilegio_admin():
            btn_eliminar = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                width=40,
                height=32,
                font=("Segoe UI", 14),
                corner_radius=8,
                fg_color=self.COLORES['danger'],
                hover_color="#C0392B",
                command=lambda: self.eliminar_habitacion(datos)
            )
            btn_eliminar.pack(side="left", expand=True, padx=(5, 0))

    def _get_texto_estado(self, estado: str) -> str:
        """Retorna el texto formateado del estado"""
        estados = {
            'disponible': '✓ Disponible',
            'ocupada': '✗ Ocupada',
            'limpieza': '🧹 Limpieza',
            'mantenimiento': '🔧 Mantenimiento'
        }
        return estados.get(estado, estado.capitalize())

    def _seleccionar_habitacion(self, datos, card):
        """Selecciona una habitación"""
        self.habitacion_seleccionada = datos

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay habitaciones"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.pack(expand=True, pady=100)

        ctk.CTkLabel(
            mensaje,
            text="🏨",
            font=("Segoe UI", 72)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="No hay habitaciones registradas",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            mensaje,
            text="Agrega la primera habitación para comenzar",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _mostrar_mensaje_sin_resultados(self):
        """Muestra mensaje cuando no hay resultados de búsqueda"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.pack(expand=True, pady=100)

        ctk.CTkLabel(
            mensaje,
            text="🔍",
            font=("Segoe UI", 72)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="No se encontraron resultados",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            mensaje,
            text="Intenta con otros filtros de búsqueda",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def aplicar_filtros(self):
        """Aplica los filtros de búsqueda"""
        self.cargar_habitaciones()

    def abrir_formulario_agregar(self):
        """Abre el formulario para agregar habitación"""
        FormularioHabitacion(self.parent, self.db, self.cargar_habitaciones)

    def abrir_formulario_editar(self, datos=None):
        """Abre el formulario para editar habitación"""
        if datos is None:
            datos = self.habitacion_seleccionada

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona una habitación para editar"
            )
            return

        FormularioHabitacion(self.parent, self.db, self.cargar_habitaciones, datos)

    def eliminar_habitacion(self, datos=None):
        """Elimina una habitación"""
        if datos is None:
            datos = self.habitacion_seleccionada

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona una habitación para eliminar"
            )
            return

        habitacion_id, numero = datos[0], datos[1]

        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar la habitación #{numero}?\n\n"
            "Esta acción no se puede deshacer."
        )

        if respuesta:
            self.db.eliminar_habitacion(habitacion_id)
            messagebox.showinfo("Éxito", "Habitación eliminada correctamente")
            self.cargar_habitaciones()


class FormularioHabitacion:
    def __init__(self, parent, db, callback_refrescar, datos=None):
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos

        # Crear ventana modal
        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title("Nueva Habitación" if not datos else "Editar Habitación")
        self.ventana.geometry("500x800")
        self.ventana.resizable(False, False)

        # Hacer modal (después de que la ventana sea visible)
        self.ventana.transient(parent)

        # Centrar
        self._centrar_ventana()

        # Esperar a que la ventana sea visible antes de grab_set
        self.ventana.after(100, self.ventana.grab_set)

        # Crear interfaz
        self._crear_formulario()

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()
        width = self.ventana.winfo_width()
        height = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry(f'{width}x{height}+{x}+{y}')

    def _crear_formulario(self):
        """Crea el formulario del modal"""
        # Container principal
        container = ctk.CTkFrame(self.ventana, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(container)

        # Formulario
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, pady=(20, 0))

        # Campos
        self._crear_campo_numero(form)
        self._crear_campo_tipo(form)
        self._crear_campo_precio(form)
        self._crear_campo_estado(form)

        # Rellenar si es edición
        if self.datos:
            self._rellenar_campos()

        # Botones
        self._crear_botones(container)

    def _crear_header(self, parent):
        """Crea el header del formulario"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x")

        icono = "➕" if not self.datos else "✏️"
        titulo = "Nueva Habitación" if not self.datos else "Editar Habitación"

        ctk.CTkLabel(
            header,
            text=icono,
            font=("Segoe UI", 48)
        ).pack()

        ctk.CTkLabel(
            header,
            text=titulo,
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(10, 5))

        subtitulo = "Completa la información de la habitación" if not self.datos else "Modifica los datos necesarios"
        ctk.CTkLabel(
            header,
            text=subtitulo,
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _crear_campo_numero(self, parent):
        """Crea el campo de número"""
        ctk.CTkLabel(
            parent,
            text="Número de Habitación *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_numero = ctk.CTkEntry(
            parent,
            placeholder_text="Ejemplo: 101, 205, 3A",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_numero.pack(fill="x")

    def _crear_campo_tipo(self, parent):
        """Crea el campo de tipo"""
        ctk.CTkLabel(
            parent,
            text="Tipo de Habitación *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.combo_tipo = ctk.CTkComboBox(
            parent,
            values=["Sencilla", "Doble", "Familiar", "Deluxe"],
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12,
            button_color="#3498DB",
            button_hover_color="#2980B9",
            dropdown_font=("Segoe UI", 12)
        )
        self.combo_tipo.pack(fill="x")
        self.combo_tipo.set("Sencilla")

    def _crear_campo_precio(self, parent):
        """Crea el campo de precio"""
        ctk.CTkLabel(
            parent,
            text="Precio por Noche *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        frame_precio = ctk.CTkFrame(parent, fg_color="transparent")
        frame_precio.pack(fill="x")

        ctk.CTkLabel(
            frame_precio,
            text="$",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=(0, 10))

        self.entry_precio = ctk.CTkEntry(
            frame_precio,
            placeholder_text="0.00",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_precio.pack(side="left", fill="x", expand=True)

    def _crear_campo_estado(self, parent):
        """Crea el campo de estado"""
        ctk.CTkLabel(
            parent,
            text="Estado *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.combo_estado = ctk.CTkComboBox(
            parent,
            values=["disponible", "ocupada", "limpieza", "mantenimiento"],
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12,
            button_color="#3498DB",
            button_hover_color="#2980B9",
            dropdown_font=("Segoe UI", 12)
        )
        self.combo_estado.pack(fill="x")
        self.combo_estado.set("disponible")

    def _crear_botones(self, parent):
        """Crea los botones del formulario"""
        frame_botones = ctk.CTkFrame(parent, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(30, 0))

        # Botón Guardar
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="💾 Guardar",
            command=self.guardar,
            height=55,
            font=("Segoe UI", 14, "bold"),
            corner_radius=12,
            fg_color="#27AE60",
            hover_color="#229954"
        )
        btn_guardar.pack(fill="x", pady=(0, 10))

        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=self.ventana.destroy,
            height=45,
            font=("Segoe UI", 12),
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            text_color=("#7F8C8D", "#95A5A6"),
            hover_color=("#ECF0F1", "#3A3A3A")
        )
        btn_cancelar.pack(fill="x")

    def _rellenar_campos(self):
        """Rellena los campos con los datos existentes"""
        self.entry_numero.insert(0, self.datos[1])
        self.combo_tipo.set(self.datos[2])
        self.entry_precio.insert(0, self.datos[3])
        self.combo_estado.set(self.datos[4])

    def guardar(self):
        """Guarda o actualiza la habitación"""
        # Obtener valores
        numero = self.entry_numero.get().strip()
        tipo = self.combo_tipo.get()
        precio_str = self.entry_precio.get().strip()
        estado = self.combo_estado.get()

        # Validaciones
        if not self._validar_campos(numero, precio_str):
            return

        precio = float(precio_str)

        # Guardar en base de datos
        try:
            if self.datos:  # EDITAR
                habitacion_id = self.datos[0]
                exito = self.db.actualizar_habitacion(habitacion_id, numero, tipo, precio, estado)
                mensaje = "Habitación actualizada correctamente"
            else:  # AGREGAR
                exito = self.db.agregar_habitacion(numero, tipo, precio, estado)
                mensaje = "Habitación agregada correctamente"

            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "El número de habitación ya existe.\nIntenta con otro número."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def _validar_campos(self, numero: str, precio_str: str) -> bool:
        """Valida los campos del formulario"""
        if not numero:
            messagebox.showerror(
                "Campo Requerido",
                "El número de habitación es obligatorio"
            )
            self.entry_numero.focus()
            return False

        if not precio_str:
            messagebox.showerror(
                "Campo Requerido",
                "El precio es obligatorio"
            )
            self.entry_precio.focus()
            return False

        try:
            precio = float(precio_str)
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Precio Inválido",
                "El precio debe ser un número válido mayor a 0"
            )
            self.entry_precio.focus()
            return False

        return True