# gui/huespedes_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from typing import Optional, List, Tuple


class HuespedesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager()

        # Variables
        self.huesped_seleccionado = None

        # Colores consistentes con el diseño
        self.COLORES = {
            'card_bg': ("#FFFFFF", "#3a3a3a"),
            'primary': "#3498DB",
            'success': "#27AE60",
            'danger': "#E74C3C",
            'warning': "#F39C12",
            'info': "#3498DB",
        }

        self._crear_interfaz()
        self.cargar_huespedes()

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Container principal
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(main_container)

        # Panel de controles
        self._crear_panel_controles(main_container)

        # Grid de huéspedes
        self._crear_grid_huespedes(main_container)

    def _crear_header(self, parent):
        """Crea el header con título y botón principal"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_frame,
            text="👥 Gestión de Huéspedes",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Administra la información de los clientes del hotel",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Botón agregar (destacado)
        btn_agregar = ctk.CTkButton(
            header,
            text="➕ Agregar Huésped",
            command=self.abrir_formulario_agregar,
            font=("Segoe UI", 14, "bold"),
            height=50,
            width=200,
            corner_radius=12,
            fg_color=self.COLORES['success'],
            hover_color="#229954"
        )
        btn_agregar.pack(side="right")

    def _crear_panel_controles(self, parent):
        """Crea el panel de búsqueda y filtros"""
        controles_container = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        controles_container.pack(fill="x", pady=(0, 20))

        # Container interno
        content = ctk.CTkFrame(controles_container, fg_color="transparent")
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
            placeholder_text="Buscar por nombre, email o teléfono...",
            height=40,
            width=400,
            font=("Segoe UI", 12),
            corner_radius=10
        )
        self.entry_buscar.pack(side="left", padx=(0, 10))
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.aplicar_filtros())

        btn_limpiar = ctk.CTkButton(
            search_frame,
            text="✖",
            command=self.limpiar_busqueda,
            width=40,
            height=40,
            font=("Segoe UI", 16),
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A")
        )
        btn_limpiar.pack(side="left")

        # Botones de acción
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        # Botón Refrescar
        btn_refrescar = ctk.CTkButton(
            right_frame,
            text="🔄",
            command=self.cargar_huespedes,
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

    def _crear_grid_huespedes(self, parent):
        """Crea el grid scrollable de huéspedes"""
        # Frame contenedor con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

        # Configurar grid para 3 columnas
        for i in range(3):
            self.scroll_frame.columnconfigure(i, weight=1)

    def cargar_huespedes(self):
        """Carga y muestra los huéspedes"""
        # Limpiar grid
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener huéspedes
        huespedes = self.db.obtener_huespedes()

        if not huespedes:
            self._mostrar_mensaje_vacio()
            return

        # Aplicar filtros
        huespedes_filtrados = self._filtrar_huespedes(huespedes)

        if not huespedes_filtrados:
            self._mostrar_mensaje_sin_resultados()
            return

        # Mostrar huéspedes en grid
        self._mostrar_huespedes_grid(huespedes_filtrados)

    def _filtrar_huespedes(self, huespedes: List[Tuple]) -> List[Tuple]:
        """Filtra los huéspedes según criterios de búsqueda"""
        busqueda = self.entry_buscar.get().strip().lower()

        if not busqueda:
            return huespedes

        huespedes_filtrados = []

        for huesped in huespedes:
            # huesped = (id, nombre, apellido, telefono, password, email)
            nombre_completo = f"{huesped[1]} {huesped[2]}".lower()
            telefono = str(huesped[3]).lower() if huesped[3] else ""
            email = str(huesped[5]).lower() if len(huesped) > 5 and huesped[5] else ""

            if busqueda in nombre_completo or busqueda in telefono or busqueda in email:
                huespedes_filtrados.append(huesped)

        return huespedes_filtrados

    def _mostrar_huespedes_grid(self, huespedes: List[Tuple]):
        """Muestra los huéspedes en formato grid"""
        row = 0
        col = 0

        for huesped in huespedes:
            card = self._crear_tarjeta_huesped(huesped)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _crear_tarjeta_huesped(self, datos: Tuple):
        """Crea una tarjeta visual para un huésped"""
        huesped_id = datos[0]
        nombre = datos[1]
        apellido = datos[2]
        telefono = datos[3]
        email = datos[5] if len(datos) > 5 else None

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

        # Click para seleccionar
        card.bind("<Button-1>", lambda e: self._seleccionar_huesped(datos, card))

        # Container interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Avatar circular
        avatar_frame = ctk.CTkFrame(
            content,
            width=80,
            height=80,
            fg_color=self.COLORES['primary'],
            corner_radius=40
        )
        avatar_frame.pack(pady=(0, 15))
        avatar_frame.pack_propagate(False)

        ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=("Segoe UI", 40)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Nombre completo
        nombre_completo = f"{nombre} {apellido}"
        ctk.CTkLabel(
            content,
            text=nombre_completo,
            font=("Segoe UI", 16, "bold"),
            wraplength=250
        ).pack(pady=(0, 5))

        # ID badge
        id_badge = ctk.CTkLabel(
            content,
            text=f"ID: #{huesped_id}",
            font=("Segoe UI", 9, "bold"),
            fg_color=("#ECF0F1", "#2C3E50"),
            corner_radius=6,
            padx=10,
            pady=4
        )
        id_badge.pack(pady=(0, 15))

        # Separador
        ctk.CTkFrame(
            content,
            height=2,
            fg_color=("#E0E0E0", "#4A4A4A")
        ).pack(fill="x", pady=(0, 15))

        # Información de contacto
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))

        # Teléfono (cambiar icono)
        tel_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        tel_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            tel_frame,
            text="📱",  # Icono de teléfono
            font=("Segoe UI", 14)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            tel_frame,
            text=telefono,
            font=("Segoe UI", 11),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Email
        if email:
            email_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            email_frame.pack(fill="x")

            ctk.CTkLabel(
                email_frame,
                text="📧",
                font=("Segoe UI", 14)
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                email_frame,
                text=email,
                font=("Segoe UI", 10),
                text_color=("#7F8C8D", "#95A5A6"),
                anchor="w",
                wraplength=220
            ).pack(side="left", fill="x", expand=True)
        else:
            ctk.CTkLabel(
                info_frame,
                text="Sin email registrado",
                font=("Segoe UI", 9, "italic"),
                text_color=("#95A5A6", "#7F8C8D")
            ).pack()

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
            height=35,
            font=("Segoe UI", 14),
            corner_radius=8,
            fg_color=self.COLORES['primary'],
            hover_color="#2980B9",
            command=lambda: self.abrir_formulario_editar(datos)
        )
        btn_editar.pack(side="left", expand=True, padx=(0, 5))

        # Botón eliminar
        btn_eliminar = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=40,
            height=35,
            font=("Segoe UI", 14),
            corner_radius=8,
            fg_color=self.COLORES['danger'],
            hover_color="#C0392B",
            command=lambda: self.eliminar_huesped(datos)
        )
        btn_eliminar.pack(side="left", expand=True, padx=(5, 0))

    def _seleccionar_huesped(self, datos, card):
        """Selecciona un huésped"""
        self.huesped_seleccionado = datos

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay huéspedes"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.grid(row=0, column=0, columnspan=3, pady=100)

        ctk.CTkLabel(
            mensaje,
            text="👥",
            font=("Segoe UI", 72)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="No hay huéspedes registrados",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            mensaje,
            text="Agrega el primer huésped para comenzar",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _mostrar_mensaje_sin_resultados(self):
        """Muestra mensaje cuando no hay resultados de búsqueda"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.grid(row=0, column=0, columnspan=3, pady=100)

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
            text="Intenta con otros términos de búsqueda",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def aplicar_filtros(self):
        """Aplica los filtros de búsqueda"""
        self.cargar_huespedes()

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.entry_buscar.delete(0, 'end')
        self.cargar_huespedes()

    def abrir_formulario_agregar(self):
        """Abre el formulario para agregar huésped"""
        FormularioHuesped(self.parent, self.db, self.cargar_huespedes)

    def abrir_formulario_editar(self, datos=None):
        """Abre el formulario para editar huésped"""
        if datos is None:
            datos = self.huesped_seleccionado

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona un huésped para editar"
            )
            return

        FormularioHuesped(self.parent, self.db, self.cargar_huespedes, datos)

    def eliminar_huesped(self, datos=None):
        """Elimina un huésped"""
        if datos is None:
            datos = self.huesped_seleccionado

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona un huésped para eliminar"
            )
            return

        huesped_id = datos[0]
        nombre_completo = f"{datos[1]} {datos[2]}"

        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar a {nombre_completo}?\n\n"
            "Esta acción no se puede deshacer."
        )

        if respuesta:
            self.db.eliminar_huesped(huesped_id)
            messagebox.showinfo("Éxito", "Huésped eliminado correctamente")
            self.cargar_huespedes()


class FormularioHuesped:
    def __init__(self, parent, db, callback_refrescar, datos=None):
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos
        self.callback = None

        # Colores
        self.COLORES = {
            'success': "#27AE60",
            'danger': "#E74C3C",
        }

        # Crear ventana modal
        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title("Agregar Huésped" if not datos else "Editar Huésped")
        self.ventana.geometry("550x950")
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
        # Container principal con scroll
        container = ctk.CTkFrame(self.ventana, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(container)

        # Formulario
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, pady=(20, 0))

        # Campos
        self._crear_campo_nombre(form)
        self._crear_campo_apellido(form)
        self._crear_campo_telefono(form)
        self._crear_campo_email(form)
        self._crear_campo_password(form)

        # Rellenar si es edición
        if self.datos:
            self._rellenar_campos()

        # Botones
        self._crear_botones(form)

    def _crear_header(self, parent):
        """Crea el header del formulario"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x")

        icono = "👤" if not self.datos else "✏️"
        titulo = "Agregar Huésped" if not self.datos else "Editar Huésped"

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

        subtitulo = "Completa la información del huésped" if not self.datos else "Modifica los datos necesarios"
        ctk.CTkLabel(
            header,
            text=subtitulo,
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _crear_campo_nombre(self, parent):
        """Crea el campo de nombre"""
        ctk.CTkLabel(
            parent,
            text="Nombre *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_nombre = ctk.CTkEntry(
            parent,
            placeholder_text="Ejemplo: Carlos, María, Juan",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_nombre.pack(fill="x")

    def _crear_campo_apellido(self, parent):
        """Crea el campo de apellido"""
        ctk.CTkLabel(
            parent,
            text="Apellido *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_apellido = ctk.CTkEntry(
            parent,
            placeholder_text="Ejemplo: González, Pérez, García",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_apellido.pack(fill="x")

    def _crear_campo_telefono(self, parent):
        """Crea el campo de teléfono"""
        ctk.CTkLabel(
            parent,
            text="Teléfono *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_telefono = ctk.CTkEntry(
            parent,
            placeholder_text="+52 123 456 7890",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_telefono.pack(fill="x")

    def _crear_campo_email(self, parent):
        """Crea el campo de email"""
        ctk.CTkLabel(
            parent,
            text="Email (opcional)",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_email = ctk.CTkEntry(
            parent,
            placeholder_text="correo@ejemplo.com",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_email.pack(fill="x")

    def _crear_campo_password(self, parent):
        """Crea el campo de contrasena"""
        ctk.CTkLabel(
            parent,
            text="Se creara una contrasena predeterminada *",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(20, 8))

        self.entry_password = ctk.CTkEntry(
            parent,
            placeholder_text="PASSWORD",
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12
        )
        self.entry_password.pack(fill="x")

    def _crear_botones(self, parent):
        """Crea los botones del formulario"""
        frame_botones = ctk.CTkFrame(parent, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(30, 0))

        # Botón Guardar
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="💾 Guardar",
            command=self._guardar,
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
        # datos = (id, nombre, apellido, telefono, password, email)
        self.entry_nombre.insert(0, self.datos[1])
        self.entry_apellido.insert(0, self.datos[2])
        self.entry_telefono.insert(0, self.datos[3])
        if len(self.datos) > 5 and self.datos[5]:
            self.entry_email.insert(0, self.datos[5])

    def _guardar(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()

        if not self._validar(nombre, apellido, telefono):
            return

        if self.datos:
            if not password:
                password = self.datos[4]

            ok = self.db.actualizar_huesped(
                self.datos[0], nombre, apellido, telefono, password, email
            )
        else:
            ok = self.db.agregar_huesped(
                nombre, apellido, telefono, password, email
            )

        if ok:
            if self.callback_refrescar:
                self.callback_refrescar()
            self.ventana.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar el huésped")

    def _validar(self, nombre, apellido, telefono):
        if not nombre or not apellido or not telefono:
            messagebox.showerror("Error", "Nombre, apellido y teléfono son obligatorios")
            return False
        return True
