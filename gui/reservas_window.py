# gui/reservas_window.py
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from typing import Optional, List, Tuple


class ReservasWindow:
    def __init__(self, parent, privilegio="Empleado"):
        self.parent = parent
        self.privilegio = privilegio
        self.db = DatabaseManager()

        # Variables
        self.reserva_seleccionada = None
        self.filtro_estado = "Todas"

        # Colores consistentes con el diseño
        self.COLORES = {
            'activa': "#27AE60",
            'finalizada': "#3498DB",
            'cancelada': "#E74C3C",
            'card_bg': ("#FFFFFF", "#3a3a3a"),
            'primary': "#3498DB",
            'success': "#27AE60",
            'warning': "#F39C12",
            'danger': "#E74C3C",
        }

        self._crear_interfaz()
        self.cargar_reservas()

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Container principal
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(main_container)

        # Panel de filtros y acciones
        self._crear_panel_controles(main_container)

        # Grid de reservas
        self._crear_grid_reservas(main_container)

    def _crear_header(self, parent):
        """Crea el header con título y botón principal"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_frame,
            text="📅 Gestión de Reservas",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Administra las reservas y estadías del hotel",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Botón nueva reserva (destacado)
        btn_nueva = ctk.CTkButton(
            header,
            text="➕ Nueva Reserva",
            command=self.abrir_formulario_nueva_reserva,
            font=("Segoe UI", 14, "bold"),
            height=50,
            width=200,
            corner_radius=12,
            fg_color=self.COLORES['success'],
            hover_color="#229954"
        )
        btn_nueva.pack(side="right")

    def _crear_panel_controles(self, parent):
        """Crea el panel de filtros y acciones"""
        controles_container = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        controles_container.pack(fill="x", pady=(0, 20))

        # Container interno
        content = ctk.CTkFrame(controles_container, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        # Lado izquierdo - Búsqueda y filtros
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)

        # Búsqueda
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 10))

        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por huésped o habitación...",
            height=40,
            width=250,
            font=("Segoe UI", 12),
            corner_radius=10
        )
        self.entry_buscar.pack(side="left")
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.aplicar_filtros())

        # Filtro por estado
        ctk.CTkLabel(
            left_frame,
            text="Estado:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(10, 5))

        self.combo_filtro_estado = ctk.CTkComboBox(
            left_frame,
            values=["Todas", "activa", "finalizada", "cancelada"],
            height=40,
            width=150,
            font=("Segoe UI", 11),
            corner_radius=10,
            command=lambda e: self.aplicar_filtros()
        )
        self.combo_filtro_estado.pack(side="left")
        self.combo_filtro_estado.set("Todas")

        # Lado derecho - Botones de acción
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        # Botón Refrescar
        btn_refrescar = ctk.CTkButton(
            right_frame,
            text="🔄",
            command=self.cargar_reservas,
            width=40,
            height=40,
            font=("Segoe UI", 18),
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A")
        )
        btn_refrescar.pack(side="left", padx=5)

    def _crear_grid_reservas(self, parent):
        """Crea el grid scrollable de reservas"""
        # Frame contenedor con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

    def cargar_reservas(self):
        """Carga y muestra las reservas"""
        # Limpiar grid
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener reservas
        reservas = self.db.obtener_reservas()

        if not reservas:
            self._mostrar_mensaje_vacio()
            return

        # Aplicar filtros
        reservas_filtradas = self._filtrar_reservas(reservas)

        if not reservas_filtradas:
            self._mostrar_mensaje_sin_resultados()
            return

        # Mostrar reservas
        self._mostrar_reservas_lista(reservas_filtradas)

    def _filtrar_reservas(self, reservas: List[Tuple]) -> List[Tuple]:
        """Filtra las reservas según criterios"""
        busqueda = self.entry_buscar.get().strip().lower()
        estado_filtro = self.combo_filtro_estado.get()

        reservas_filtradas = []

        for reserva in reservas:
            # Estructura: (id, huesped_id, huesped_nombre, habitacion_id, numero, tipo, fecha_entrada, fecha_salida, estado, total)
            huesped = reserva[2].lower()
            habitacion = str(reserva[4]).lower()
            estado = reserva[8]

            # Aplicar filtros
            coincide_busqueda = busqueda in huesped or busqueda in habitacion if busqueda else True
            coincide_estado = estado == estado_filtro if estado_filtro != "Todas" else True

            if coincide_busqueda and coincide_estado:
                reservas_filtradas.append(reserva)

        return reservas_filtradas

    def _mostrar_reservas_lista(self, reservas: List[Tuple]):
        """Muestra las reservas en formato de lista de tarjetas"""
        for reserva in reservas:
            card = self._crear_tarjeta_reserva(reserva)
            card.pack(fill="x", pady=8)

    def _crear_tarjeta_reserva(self, datos: Tuple):
        """Crea una tarjeta visual para una reserva"""
        # Estructura: (id, huesped_id, huesped_nombre, habitacion_id, numero, tipo, fecha_entrada, fecha_salida, estado, total)
        (reserva_id, huesped_id, huesped_nombre, habitacion_id,
         habitacion_numero, tipo, fecha_entrada, fecha_salida, estado, total) = datos

        # Frame principal de la tarjeta
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15,
            border_width=2,
            border_color=("#E0E0E0", "#4A4A4A")
        )

        # Hover effect
        card.bind("<Enter>", lambda e: card.configure(border_color=self.COLORES['primary']))
        card.bind("<Leave>", lambda e: card.configure(border_color=("#E0E0E0", "#4A4A4A")))

        # Container interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", padx=20, pady=15)

        # Grid layout
        content.columnconfigure(0, weight=1)  # Info principal
        content.columnconfigure(1, weight=0)  # Fechas
        content.columnconfigure(2, weight=0)  # Total y acciones

        # === COLUMNA 1: Información Principal ===
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # ID y Estado en una línea
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            header_frame,
            text=f"#{reserva_id}",
            font=("Segoe UI", 14, "bold"),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack(side="left", padx=(0, 15))

        # Badge de estado
        badge = ctk.CTkLabel(
            header_frame,
            text=self._get_texto_estado(estado),
            font=("Segoe UI", 9, "bold"),
            fg_color=self.COLORES.get(estado, "#95A5A6"),
            corner_radius=6,
            padx=12,
            pady=4
        )
        badge.pack(side="left")

        # Nombre del huésped
        ctk.CTkLabel(
            info_frame,
            text=f"👤 {huesped_nombre}",
            font=("Segoe UI", 16, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        # Habitación
        ctk.CTkLabel(
            info_frame,
            text=f"🛏️ Habitación #{habitacion_numero} - {tipo}",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w")

        # === COLUMNA 2: Fechas ===
        fechas_frame = ctk.CTkFrame(content, fg_color="transparent")
        fechas_frame.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # Check-in
        checkin_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        checkin_frame.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            checkin_frame,
            text="Check-in",
            font=("Segoe UI", 9),
            text_color=("#95A5A6", "#7F8C8D")
        ).pack(anchor="w")

        ctk.CTkLabel(
            checkin_frame,
            text=str(fecha_entrada),
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # Check-out
        checkout_frame = ctk.CTkFrame(fechas_frame, fg_color="transparent")
        checkout_frame.pack(anchor="w")

        ctk.CTkLabel(
            checkout_frame,
            text="Check-out",
            font=("Segoe UI", 9),
            text_color=("#95A5A6", "#7F8C8D")
        ).pack(anchor="w")

        ctk.CTkLabel(
            checkout_frame,
            text=str(fecha_salida),
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # === COLUMNA 3: Total y Acciones ===
        acciones_frame = ctk.CTkFrame(content, fg_color="transparent")
        acciones_frame.grid(row=0, column=2, sticky="e")

        # Total
        total_frame = ctk.CTkFrame(acciones_frame, fg_color="transparent")
        total_frame.pack(pady=(0, 10))

        ctk.CTkLabel(
            total_frame,
            text="Total",
            font=("Segoe UI", 9),
            text_color=("#95A5A6", "#7F8C8D")
        ).pack()

        ctk.CTkLabel(
            total_frame,
            text=f"${total:,.2f}" if total else "$0.00",
            font=("Segoe UI", 18, "bold"),
            text_color=self.COLORES['success']
        ).pack()

        # Botones de acción (solo para reservas activas)
        if estado == "activa":
            botones_frame = ctk.CTkFrame(acciones_frame, fg_color="transparent")
            botones_frame.pack()

            # Botón Check-out
            btn_checkout = ctk.CTkButton(
                botones_frame,
                text="✅ Check-out",
                command=lambda: self.hacer_checkout(datos),
                height=35,
                width=120,
                font=("Segoe UI", 11, "bold"),
                corner_radius=8,
                fg_color=self.COLORES['primary'],
                hover_color="#2980B9"
            )
            btn_checkout.pack(pady=2)

            # Botón Cancelar (solo admin)
            if self.privilegio == "Administrador":
                btn_cancelar = ctk.CTkButton(
                    botones_frame,
                    text="❌ Cancelar",
                    command=lambda: self.cancelar_reserva(datos),
                    height=35,
                    width=120,
                    font=("Segoe UI", 11, "bold"),
                    corner_radius=8,
                    fg_color=self.COLORES['danger'],
                    hover_color="#C0392B"
                )
                btn_cancelar.pack(pady=2)

        return card

    def _get_texto_estado(self, estado: str) -> str:
        """Retorna el texto formateado del estado"""
        estados = {
            'activa': '✓ Activa',
            'finalizada': '✓ Finalizada',
            'cancelada': '✗ Cancelada'
        }
        return estados.get(estado, estado.capitalize())

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay reservas"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.pack(expand=True, pady=100)

        ctk.CTkLabel(
            mensaje,
            text="📅",
            font=("Segoe UI", 72)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="No hay reservas registradas",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            mensaje,
            text="Crea la primera reserva para comenzar",
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
        self.cargar_reservas()

    def abrir_formulario_nueva_reserva(self):
        """Abre el formulario para crear nueva reserva"""
        FormularioReserva(self.parent, self.db, self.cargar_reservas)

    def hacer_checkout(self, datos):
        """Finaliza una reserva (checkout)"""
        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona una reserva para hacer check-out"
            )
            return

        reserva_id = datos[0]
        estado = datos[8]
        huesped = datos[2]

        if estado != "activa":
            messagebox.showwarning(
                "Advertencia",
                "Solo se puede hacer check-out de reservas activas"
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar Check-out",
            f"¿Realizar check-out para {huesped}?\n\n"
            "La habitación quedará en estado de limpieza."
        )

        if respuesta:
            exito = self.db.finalizar_reserva(reserva_id)
            if exito:
                messagebox.showinfo(
                    "Éxito",
                    "Check-out realizado correctamente.\nHabitación en limpieza."
                )
                self.cargar_reservas()
            else:
                messagebox.showerror("Error", "No se pudo realizar el check-out")

    def cancelar_reserva(self, datos):
        """Cancela una reserva"""
        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona una reserva para cancelar"
            )
            return

        reserva_id = datos[0]
        estado = datos[8]
        huesped = datos[2]

        if estado != "activa":
            messagebox.showwarning(
                "Advertencia",
                "Solo se pueden cancelar reservas activas"
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar Cancelación",
            f"¿Cancelar la reserva de {huesped}?\n\n"
            "La habitación quedará disponible.\n"
            "Esta acción no se puede deshacer."
        )

        if respuesta:
            exito = self.db.cancelar_reserva(reserva_id)
            if exito:
                messagebox.showinfo("Éxito", "Reserva cancelada correctamente")
                self.cargar_reservas()
            else:
                messagebox.showerror("Error", "No se pudo cancelar la reserva")


class FormularioReserva:
    def __init__(self, parent, db, callback_refrescar):
        self.db = db
        self.callback_refrescar = callback_refrescar

        # Variables
        self.huesped_seleccionado = None
        self.habitaciones_disponibles = []
        self.total_calculado = 0

        # Colores
        self.COLORES = {
            'primary': "#3498DB",
            'success': "#27AE60",
            'warning': "#F39C12",
            'danger': "#E74C3C",
        }

        # Crear ventana modal
        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title("Nueva Reserva")
        self.ventana.geometry("650x750")
        self.ventana.resizable(False, False)

        # Hacer modal
        self.ventana.transient(parent)
        self.ventana.after(100, self.ventana.grab_set)

        # Centrar
        self._centrar_ventana()

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

        # Scrollable frame para el contenido
        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Sección 1: Seleccionar Huésped
        self._crear_seccion_huesped(scroll_frame)

        # Separador
        self._crear_separador(scroll_frame)

        # Sección 2: Datos de la Reserva
        self._crear_seccion_reserva(scroll_frame)

        # Botones
        self._crear_botones(container)

    def _crear_header(self, parent):
        """Crea el header del formulario"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="📅",
            font=("Segoe UI", 48)
        ).pack()

        ctk.CTkLabel(
            header,
            text="Nueva Reserva",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="Completa la información para crear la reserva",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _crear_seccion_huesped(self, parent):
        """Crea la sección de selección de huésped"""
        # Título de sección
        ctk.CTkLabel(
            parent,
            text="1. SELECCIONAR HUÉSPED",
            font=("Segoe UI", 14, "bold"),
            text_color=self.COLORES['primary'],
            anchor="w"
        ).pack(anchor="w", pady=(20, 15))

        # Campo de búsqueda
        ctk.CTkLabel(
            parent,
            text="Teléfono del Huésped *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))

        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Ingrese teléfono del huésped",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_buscar = ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self.buscar_huesped,
            width=120,
            height=50,
            font=("Segoe UI", 13, "bold"),
            corner_radius=12,
            fg_color=self.COLORES['primary'],
            hover_color="#2980B9"
        )
        btn_buscar.pack(side="left")

        # Card para mostrar huésped seleccionado
        self.card_huesped = ctk.CTkFrame(
            parent,
            fg_color=("#E8F8F5", "#1B4332"),
            corner_radius=12
        )
        self.card_huesped.pack_forget()  # Ocultar inicialmente

    def _crear_separador(self, parent):
        """Crea un separador visual"""
        ctk.CTkFrame(
            parent,
            height=2,
            fg_color=("#BDC3C7", "#4A4A4A")
        ).pack(fill="x", pady=25)

    def _crear_seccion_reserva(self, parent):
        """Crea la sección de datos de la reserva"""
        # Título de sección
        ctk.CTkLabel(
            parent,
            text="2. DATOS DE LA RESERVA",
            font=("Segoe UI", 14, "bold"),
            text_color=self.COLORES['danger'],
            anchor="w"
        ).pack(anchor="w", pady=(0, 15))

        # Habitación
        self._crear_campo_habitacion(parent)

        # Fechas
        self._crear_campos_fechas(parent)

        # Total
        self._crear_seccion_total(parent)

    def _crear_campo_habitacion(self, parent):
        """Crea el campo de selección de habitación"""
        ctk.CTkLabel(
            parent,
            text="Habitación *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        # Cargar habitaciones disponibles
        self.habitaciones_disponibles = self.db.obtener_habitaciones_disponibles()
        opciones_hab = [
            f"#{hab[1]} - {hab[2]} - ${hab[3]:,.2f}/noche"
            for hab in self.habitaciones_disponibles
        ]

        if not opciones_hab:
            opciones_hab = ["⚠️ No hay habitaciones disponibles"]

        self.combo_habitacion = ctk.CTkComboBox(
            parent,
            values=opciones_hab,
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12,
            button_color=self.COLORES['primary'],
            button_hover_color="#2980B9",
            dropdown_font=("Segoe UI", 12)
        )
        self.combo_habitacion.pack(fill="x", pady=(0, 20))

        if opciones_hab and opciones_hab[0] != "⚠️ No hay habitaciones disponibles":
            self.combo_habitacion.set(opciones_hab[0])
            self.ventana.after(500, self.calcular_total_automatico)

        self.combo_habitacion.configure(command=lambda e: self.calcular_total_automatico())

    def _crear_campos_fechas(self, parent):
        """Crea los campos de fechas con calendarios"""
        fechas_container = ctk.CTkFrame(parent, fg_color="transparent")
        fechas_container.pack(fill="x", pady=(0, 20))

        fechas_container.columnconfigure(0, weight=1)
        fechas_container.columnconfigure(1, weight=1)

        # Check-in
        checkin_frame = ctk.CTkFrame(fechas_container, fg_color="transparent")
        checkin_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            checkin_frame,
            text="📆 Check-in *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        self.date_entrada = DateEntry(
            checkin_frame,
            width=25,
            background='#3498DB',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now(),
            font=("Segoe UI", 12),
            state='readonly',
            locale='es_ES'
        )
        self.date_entrada.pack(fill="x")
        self.date_entrada.bind("<<DateEntrySelected>>", lambda e: self.calcular_total_automatico())

        # Check-out
        checkout_frame = ctk.CTkFrame(fechas_container, fg_color="transparent")
        checkout_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        ctk.CTkLabel(
            checkout_frame,
            text="📆 Check-out *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        self.date_salida = DateEntry(
            checkout_frame,
            width=25,
            background='#3498DB',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now() + timedelta(days=1),
            font=("Segoe UI", 12),
            state='readonly',
            locale='es_ES'
        )
        self.date_salida.pack(fill="x")
        self.date_salida.bind("<<DateEntrySelected>>", lambda e: self.calcular_total_automatico())

    def _crear_seccion_total(self, parent):
        """Crea la sección de visualización del total"""
        self.card_total = ctk.CTkFrame(
            parent,
            fg_color=("#E8F8F5", "#1B4332"),
            corner_radius=12
        )
        self.card_total.pack(fill="x", pady=(0, 10))

        total_content = ctk.CTkFrame(self.card_total, fg_color="transparent")
        total_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            total_content,
            text="Total a Pagar",
            font=("Segoe UI", 11),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

        self.label_total = ctk.CTkLabel(
            total_content,
            text="$0.00",
            font=("Segoe UI", 32, "bold"),
            text_color=self.COLORES['success']
        )
        self.label_total.pack(pady=(5, 0))

        self.label_noches = ctk.CTkLabel(
            total_content,
            text="Selecciona las fechas",
            font=("Segoe UI", 10),
            text_color=("#95A5A6", "#7F8C8D")
        )
        self.label_noches.pack()

    def _crear_botones(self, parent):
        """Crea los botones del formulario"""
        frame_botones = ctk.CTkFrame(parent, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(20, 0))

        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="💾 Guardar Reserva",
            command=self.guardar,
            height=55,
            font=("Segoe UI", 14, "bold"),
            corner_radius=12,
            fg_color=self.COLORES['success'],
            hover_color="#229954"
        )
        btn_guardar.pack(fill="x", pady=(0, 10))

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

    def buscar_huesped(self):
        """Busca un huésped por teléfono"""
        telefono = self.entry_buscar.get().strip()

        if not telefono:
            messagebox.showwarning("Advertencia", "Ingrese un teléfono para buscar")
            return

        huesped = self.db.buscar_huesped_por_telefono(telefono)

        if huesped:
            self.huesped_seleccionado = huesped
            nombre_completo = f"{huesped[1]} {huesped[2]}"
            self._mostrar_huesped_seleccionado(huesped)
            messagebox.showinfo("Encontrado", f"Huésped: {nombre_completo}")
        else:
            self.card_huesped.pack_forget()
            self.huesped_seleccionado = None

            respuesta = messagebox.askyesno(
                "No encontrado",
                "Huésped no encontrado.\n\n"
                "¿Desea registrar un nuevo huésped?\n"
                "(Vaya al módulo de Huéspedes)"
            )

            if respuesta:
                messagebox.showinfo(
                    "Info",
                    "Por favor, registre primero al huésped en el módulo\n"
                    "de Huéspedes y luego cree la reserva."
                )

    def _mostrar_huesped_seleccionado(self, huesped):
        """Muestra la información del huésped seleccionado"""
        for widget in self.card_huesped.winfo_children():
            widget.destroy()

        self.card_huesped.pack(fill="x", pady=(0, 10))

        content = ctk.CTkFrame(self.card_huesped, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="✓",
            font=("Segoe UI", 24),
            text_color=self.COLORES['success']
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text="Huésped Encontrado",
            font=("Segoe UI", 13, "bold"),
            text_color=self.COLORES['success']
        ).pack(side="left")

        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(fill="x")

        nombre_completo = f"{huesped[1]} {huesped[2]}"

        ctk.CTkLabel(
            info_frame,
            text=f"👤 {nombre_completo}",
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        if huesped[4]:  # Email
            ctk.CTkLabel(
                info_frame,
                text=f"📧 {huesped[4]}",
                font=("Segoe UI", 11),
                text_color=("#7F8C8D", "#95A5A6"),
                anchor="w"
            ).pack(anchor="w", pady=(0, 3))

        if huesped[3]:  # Teléfono
            ctk.CTkLabel(
                info_frame,
                text=f"📱 {huesped[3]}",
                font=("Segoe UI", 11),
                text_color=("#7F8C8D", "#95A5A6"),
                anchor="w"
            ).pack(anchor="w")

    def _obtener_indice_habitacion(self):
        """Obtiene el índice de la habitación seleccionada"""
        seleccion = self.combo_habitacion.get()

        for i, hab in enumerate(self.habitaciones_disponibles):
            opcion = f"#{hab[1]} - {hab[2]} - ${hab[3]:,.2f}/noche"
            if opcion == seleccion:
                return i

        return -1

    def calcular_total_automatico(self):
        """Calcula el total automáticamente al cambiar las fechas"""
        try:
            if (not self.combo_habitacion.get() or
                    self.combo_habitacion.get() == "⚠️ No hay habitaciones disponibles"):
                self.label_total.configure(text="$0.00")
                self.label_noches.configure(text="Selecciona una habitación")
                self.total_calculado = 0
                return

            indice = self._obtener_indice_habitacion()
            if indice < 0:
                return

            habitacion = self.habitaciones_disponibles[indice]
            precio_noche = habitacion[3]

            fecha_entrada = self.date_entrada.get_date()
            fecha_salida = self.date_salida.get_date()

            hoy = datetime.now().date()

            if fecha_entrada < hoy:
                self.label_total.configure(text="$0.00")
                self.label_noches.configure(text="Fecha inválida")
                self.total_calculado = 0
                return

            if fecha_salida <= fecha_entrada:
                self.label_total.configure(text="$0.00")
                self.label_noches.configure(text="Check-out debe ser posterior")
                self.total_calculado = 0
                return

            noches = (fecha_salida - fecha_entrada).days
            self.total_calculado = precio_noche * noches

            self.label_total.configure(text=f"${self.total_calculado:,.2f}")
            texto_noches = f"{noches} noche" + ("s" if noches > 1 else "")
            self.label_noches.configure(text=texto_noches)

        except Exception as e:
            self.label_total.configure(text="$0.00")
            self.label_noches.configure(text="Error al calcular")
            self.total_calculado = 0
            print(f"Error en cálculo: {e}")

    def guardar(self):
        """Guarda la reserva"""
        if not self.huesped_seleccionado:
            messagebox.showerror(
                "Campo Requerido",
                "Debe buscar y seleccionar un huésped primero"
            )
            self.entry_buscar.focus()
            return

        if (not self.combo_habitacion.get() or
                self.combo_habitacion.get() == "⚠️ No hay habitaciones disponibles"):
            messagebox.showerror(
                "Campo Requerido",
                "Debe seleccionar una habitación"
            )
            self.combo_habitacion.focus()
            return

        if self.total_calculado == 0:
            messagebox.showerror(
                "Total inválido",
                "El total calculado no puede ser $0.\n\n"
                "Verifica las fechas seleccionadas."
            )
            return

        fecha_entrada = self.date_entrada.get_date().strftime("%Y-%m-%d")
        fecha_salida = self.date_salida.get_date().strftime("%Y-%m-%d")

        indice = self._obtener_indice_habitacion()
        if indice < 0:
            messagebox.showerror("Error", "No se pudo identificar la habitación")
            return

        habitacion_id = self.habitaciones_disponibles[indice][0]
        habitacion_numero = self.habitaciones_disponibles[indice][1]
        huesped_id = self.huesped_seleccionado[0]
        huesped_nombre = f"{self.huesped_seleccionado[1]} {self.huesped_seleccionado[2]}"

        exito = self.db.agregar_reserva(
            huesped_id,
            habitacion_id,
            fecha_entrada,
            fecha_salida,
            self.total_calculado
        )

        if exito:
            messagebox.showinfo(
                "✓ Reserva Creada",
                f"La reserva se ha creado correctamente\n\n"
                f"Huésped: {huesped_nombre}\n"
                f"Habitación: #{habitacion_numero}\n"
                f"Check-in: {fecha_entrada}\n"
                f"Check-out: {fecha_salida}\n"
                f"Total: ${self.total_calculado:,.2f}"
            )
            self.callback_refrescar()
            self.ventana.destroy()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo crear la reserva.\n\n"
                "Verifica que la habitación esté disponible."
            )