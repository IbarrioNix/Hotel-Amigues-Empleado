# gui/habitaciones_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from core.session import obtener_sesion
from typing import Optional, List, Tuple, Dict
import re


class HabitacionesWindow:
    def __init__(self, parent):
        self.parent = parent

        # 🔹 Obtener sesión global
        self.session = obtener_sesion()

        # ✅ VERIFICAR que hay conexión a BD
        if not self.session.db:
            messagebox.showerror(
                "Error de Conexión",
                "No hay conexión a la base de datos.\n"
                "Por favor, reinicia la aplicación."
            )
            return

        # 🔹 Obtener la base de datos desde la sesión
        self.db = self.session.db

        # Variables
        self.habitacion_seleccionada = None
        self.card_seleccionada = None

        # Filtros
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
            'selected': "#3498DB",
            'categoria_bg': ("#F8F9FA", "#2a2a2a"),
        }

        # Iconos por tipo
        self.ICONOS_TIPO = {
            'Sencilla': '🛏️',
            'Doble': '🛏️🛏️',
            'Familiar': '👨‍👩‍👧‍👦',
            'Deluxe': '⭐'
        }

        try:
            self._crear_interfaz()
            self.cargar_habitaciones()
        except Exception as e:
            print(f"Error al inicializar HabitacionesWindow: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el módulo de habitaciones.\n{str(e)}"
            )

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        self._crear_header(main_container)
        self._crear_panel_filtros(main_container)
        self._crear_grid_habitaciones(main_container)

    def _crear_header(self, parent):
        """Crea el header con título y estadísticas rápidas"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

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
            text="Habitaciones organizadas por tipo",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

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

        content = ctk.CTkFrame(filtros_container, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

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
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

    def cargar_habitaciones(self):
        """Carga y muestra las habitaciones organizadas por categorías"""
        try:
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            self.habitacion_seleccionada = None
            self.card_seleccionada = None

            habitaciones = self.db.obtener_habitaciones()

            if not habitaciones:
                self._mostrar_mensaje_vacio()
                return

            habitaciones_filtradas = self._filtrar_habitaciones(habitaciones)

            if not habitaciones_filtradas:
                self._mostrar_mensaje_sin_resultados()
                return

            # ✨ ORGANIZAR POR CATEGORÍAS
            self._mostrar_habitaciones_por_categoria(habitaciones_filtradas)

        except Exception as e:
            print(f"Error al cargar habitaciones: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar las habitaciones.\n{str(e)}"
            )
            self._mostrar_mensaje_error()

    def _filtrar_habitaciones(self, habitaciones: List[Tuple]) -> List[Tuple]:
        """Filtra las habitaciones según criterios"""
        busqueda = self.entry_buscar.get().strip().lower()
        estado_filtro = self.combo_filtro_estado.get()
        tipo_filtro = self.combo_filtro_tipo.get()

        habitaciones_filtradas = []

        for hab in habitaciones:
            numero = str(hab[1]).lower()
            tipo = hab[2]
            estado = hab[4]

            coincide_busqueda = busqueda in numero if busqueda else True
            coincide_estado = estado == estado_filtro if estado_filtro != "Todos" else True
            coincide_tipo = tipo == tipo_filtro if tipo_filtro != "Todos" else True

            if coincide_busqueda and coincide_estado and coincide_tipo:
                habitaciones_filtradas.append(hab)

        return habitaciones_filtradas

    def _mostrar_habitaciones_por_categoria(self, habitaciones: List[Tuple]):
        """Organiza y muestra habitaciones por tipo con ordenamiento inteligente"""
        # Agrupar por tipo
        habitaciones_por_tipo = self._agrupar_por_tipo(habitaciones)

        # Orden de tipos
        orden_tipos = ["Sencilla", "Doble", "Familiar", "Deluxe"]

        for tipo in orden_tipos:
            if tipo not in habitaciones_por_tipo:
                continue

            habs_tipo = habitaciones_por_tipo[tipo]

            # ✨ ORDENAR: disponibles primero (por número), luego ocupadas/limpieza (por número)
            habs_ordenadas = self._ordenar_habitaciones(habs_tipo)

            # Crear sección de categoría
            self._crear_seccion_categoria(tipo, habs_ordenadas)

    def _agrupar_por_tipo(self, habitaciones: List[Tuple]) -> Dict[str, List[Tuple]]:
        """Agrupa habitaciones por tipo"""
        grupos = {}
        for hab in habitaciones:
            tipo = hab[2]
            if tipo not in grupos:
                grupos[tipo] = []
            grupos[tipo].append(hab)
        return grupos

    def _ordenar_habitaciones(self, habitaciones: List[Tuple]) -> List[Tuple]:
        """Ordena habitaciones: disponibles primero (orden numérico),
        luego ocupadas/limpieza (orden numérico)"""

        disponibles = []
        no_disponibles = []

        for hab in habitaciones:
            estado = hab[4]
            if estado == 'disponible':
                disponibles.append(hab)
            else:
                no_disponibles.append(hab)

        # Ordenar cada grupo por número
        disponibles.sort(key=lambda h: self._extraer_numero(h[1]))
        no_disponibles.sort(key=lambda h: self._extraer_numero(h[1]))

        # Concatenar: disponibles primero
        return disponibles + no_disponibles

    def _extraer_numero(self, numero_hab: str) -> int:
        """Extrae el número de la habitación para ordenamiento"""
        # Intenta extraer números del string (ej: "101" -> 101, "3A" -> 3)
        numeros = re.findall(r'\d+', str(numero_hab))
        return int(numeros[0]) if numeros else 0

    def _crear_seccion_categoria(self, tipo: str, habitaciones: List[Tuple]):
        """Crea una sección visual para cada categoría"""
        # Container de la categoría
        categoria_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLORES['categoria_bg'],
            corner_radius=15
        )
        categoria_container.pack(fill="x", pady=(0, 20))

        # Header de categoría
        header = ctk.CTkFrame(categoria_container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        icono = self.ICONOS_TIPO.get(tipo, '🏨')

        ctk.CTkLabel(
            header,
            text=f"{icono}  {tipo}",
            font=("Segoe UI", 20, "bold"),
            anchor="w"
        ).pack(side="left")

        # Badge con cantidad
        badge = ctk.CTkLabel(
            header,
            text=f"{len(habitaciones)} hab.",
            font=("Segoe UI", 11, "bold"),
            fg_color=self.COLORES['primary'],
            corner_radius=8,
            padx=12,
            pady=4
        )
        badge.pack(side="left", padx=(15, 0))

        # Grid de habitaciones de esta categoría
        grid_container = ctk.CTkFrame(categoria_container, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Configurar grid (5 columnas ahora)
        for i in range(5):
            grid_container.columnconfigure(i, weight=1)

        # Mostrar habitaciones
        row = 0
        col = 0

        for hab in habitaciones:
            card = self._crear_tarjeta_habitacion(hab, grid_container)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            col += 1
            if col >= 5:  # Cambio a 5 columnas
                col = 0
                row += 1

    def _crear_tarjeta_habitacion(self, datos: Tuple, parent):
        """Crea una tarjeta visual para una habitación"""
        habitacion_id, numero, tipo, precio, estado = datos

        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=10,
            border_width=2,
            border_color=("#E0E0E0", "#4A4A4A"),
            width=200,
            height=220
        )
        card.pack_propagate(False)

        def on_enter(e):
            if card != self.card_seleccionada:
                card.configure(border_color=self.COLORES['primary'])

        def on_leave(e):
            if card != self.card_seleccionada:
                card.configure(border_color=("#E0E0E0", "#4A4A4A"))

        def on_click(e):
            self._seleccionar_habitacion(datos, card)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", on_click)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Badge de estado
        badge_frame = ctk.CTkFrame(content, fg_color="transparent")
        badge_frame.pack(fill="x")

        badge = ctk.CTkLabel(
            badge_frame,
            text=self._get_texto_estado(estado),
            font=("Segoe UI", 7, "bold"),
            fg_color=self.COLORES.get(estado, "#95A5A6"),
            corner_radius=4,
            padx=6,
            pady=2
        )
        badge.pack(side="right")

        # Número de habitación
        numero_label = ctk.CTkLabel(
            content,
            text=f"#{numero}",
            font=("Segoe UI", 22, "bold")
        )
        numero_label.pack(pady=(5, 2))

        # Tipo (ya se muestra en la categoría, así que hacemos esto más sutil)
        tipo_label = ctk.CTkLabel(
            content,
            text=tipo,
            font=("Segoe UI", 9),
            text_color=("#95A5A6", "#7F8C8D")
        )
        tipo_label.pack(pady=(0, 5))

        separator = ctk.CTkFrame(content, height=1, fg_color=("#E0E0E0", "#4A4A4A"))
        separator.pack(fill="x", pady=(0, 5))

        # Precio
        precio_frame = ctk.CTkFrame(content, fg_color="transparent")
        precio_frame.pack(pady=(0, 5))

        precio_label = ctk.CTkLabel(
            precio_frame,
            text=f"${precio:,.2f}",
            font=("Segoe UI", 13, "bold"),
            text_color=self.COLORES['success']
        )
        precio_label.pack(side="left")

        noche_label = ctk.CTkLabel(
            precio_frame,
            text="/noche",
            font=("Segoe UI", 8),
            text_color=("#95A5A6", "#7F8C8D")
        )
        noche_label.pack(side="left", padx=(3, 0))

        # Binds en todos los widgets
        for widget in [content, badge, badge_frame, numero_label, tipo_label,
                       precio_frame, precio_label, noche_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # Botones de acción
        self._crear_botones_tarjeta(content, datos)

        return card

    def _crear_botones_tarjeta(self, parent, datos):
        """Crea los botones de acción en la tarjeta"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))

        btn_editar = ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=30,
            height=24,
            font=("Segoe UI", 11),
            corner_radius=5,
            fg_color=self.COLORES['primary'],
            hover_color="#2980B9",
            command=lambda: self.abrir_formulario_editar(datos)
        )
        btn_editar.pack(side="left", expand=True, padx=(0, 3))

        if self.session.tiene_privilegio_admin():
            btn_eliminar = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                width=30,
                height=24,
                font=("Segoe UI", 11),
                corner_radius=5,
                fg_color=self.COLORES['danger'],
                hover_color="#C0392B",
                command=lambda: self.eliminar_habitacion(datos)
            )
            btn_eliminar.pack(side="left", expand=True, padx=(3, 0))

    def _get_texto_estado(self, estado: str) -> str:
        """Retorna el texto formateado del estado"""
        estados = {
            'disponible': '✓ Disponible',
            'ocupada': '✗ Ocupada',
            'limpieza': '🧹 Limpieza',
            'mantenimiento': '🔧 Mantto'
        }
        return estados.get(estado, estado.capitalize())

    def _seleccionar_habitacion(self, datos, card):
        """Selecciona una habitación"""
        if self.card_seleccionada:
            self.card_seleccionada.configure(
                border_color=("#E0E0E0", "#4A4A4A"),
                border_width=2
            )

        self.habitacion_seleccionada = datos
        self.card_seleccionada = card

        card.configure(
            border_color=self.COLORES['selected'],
            border_width=3
        )

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay habitaciones"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.pack(expand=True, pady=100)

        ctk.CTkLabel(mensaje, text="🏨", font=("Segoe UI", 72)).pack()
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

        ctk.CTkLabel(mensaje, text="🔍", font=("Segoe UI", 72)).pack()
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

    def _mostrar_mensaje_error(self):
        """Muestra mensaje cuando hay un error"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.pack(expand=True, pady=100)

        ctk.CTkLabel(mensaje, text="⚠️", font=("Segoe UI", 72)).pack()
        ctk.CTkLabel(
            mensaje,
            text="Error al cargar habitaciones",
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORES['danger']
        ).pack(pady=(20, 10))
        ctk.CTkLabel(
            mensaje,
            text="Verifica tu conexión a la base de datos",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack(pady=(0, 20))

        ctk.CTkButton(
            mensaje,
            text="🔄 Reintentar",
            command=self.cargar_habitaciones,
            height=45,
            width=150,
            font=("Segoe UI", 12, "bold"),
            corner_radius=10,
            fg_color=self.COLORES['primary'],
            hover_color="#2980B9"
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

        try:
            FormularioHabitacion(self.parent, self.db, self.cargar_habitaciones, datos)
        except Exception as e:
            print(f"Error al abrir formulario: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el formulario.\n{str(e)}"
            )

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

        try:
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Estás seguro de eliminar la habitación #{numero}?\n\n"
                "Esta acción no se puede deshacer."
            )

            if respuesta:
                exito = self.db.eliminar_habitacion(habitacion_id)

                if exito:
                    messagebox.showinfo("Éxito", "Habitación eliminada correctamente")
                    self.cargar_habitaciones()
                else:
                    messagebox.showerror(
                        "Error",
                        "No se pudo eliminar la habitación.\n"
                        "Puede estar en uso actualmente."
                    )
        except Exception as e:
            print(f"Error al eliminar habitación: {e}")
            messagebox.showerror(
                "Error",
                f"Ocurrió un error al eliminar la habitación.\n{str(e)}"
            )

class FormularioHabitacion:
    def __init__(self, parent, db, callback_refrescar, datos=None):
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos

        # Crear ventana modal
        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title("Nueva Habitación" if not datos else "Editar Habitación")
        self.ventana.geometry("500x700")  # ✅ Reducir altura de 800 a 700
        self.ventana.resizable(False, False)

        # ✅ MEJORAR: Configuración de la ventana modal
        self.ventana.transient(parent)

        # Centrar ANTES de mostrar
        self._centrar_ventana()

        # ✅ CORREGIR: Mejor manejo del grab_set
        try:
            self.ventana.after(100, lambda: self.ventana.grab_set())
            self.ventana.after(150, lambda: self.ventana.focus_force())
        except Exception as e:
            print(f"Advertencia: No se pudo establecer grab_set: {e}")

        # Crear interfaz
        self._crear_formulario()

        # ✅ AGREGAR: Focus en primer campo
        self.ventana.after(200, lambda: self.entry_numero.focus())

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()

        width = 500  # ✅ Usar valores fijos
        height = 700

        screen_width = self.ventana.winfo_screenwidth()
        screen_height = self.ventana.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

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

        # ✅ AGREGAR: Bind de Enter en campos para guardar
        self.entry_numero.bind('<Return>', lambda e: self.guardar())
        self.entry_precio.bind('<Return>', lambda e: self.guardar())

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

        # ✅ AGREGAR: Bind de Escape para cancelar
        self.ventana.bind('<Escape>', lambda e: self.ventana.destroy())

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

        # ✅ AGREGAR: Validación de formato de precio
        try:
            precio = float(precio_str.replace(',', ''))  # Remover comas si existen
        except ValueError:
            messagebox.showerror(
                "Precio Inválido",
                "El precio debe ser un número válido"
            )
            self.entry_precio.focus()
            return

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
            print(f"Error al guardar habitación: {e}")
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

        # ✅ AGREGAR: Validar longitud de número
        if len(numero) > 10:
            messagebox.showerror(
                "Número Demasiado Largo",
                "El número de habitación no puede exceder 10 caracteres"
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
            precio = float(precio_str.replace(',', ''))
            if precio <= 0:
                raise ValueError("Precio debe ser mayor a 0")
            # ✅ AGREGAR: Validar límite máximo razonable
            if precio > 999999:
                raise ValueError("Precio demasiado alto")
        except ValueError as e:
            messagebox.showerror(
                "Precio Inválido",
                f"El precio debe ser un número válido mayor a 0\n{str(e)}"
            )
            self.entry_precio.focus()
            return False

        return True