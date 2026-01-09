# gui/empleados_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from typing import Optional, List, Tuple


class EmpleadosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager()

        # Variables
        self.empleado_seleccionado = None

        # Colores consistentes
        self.COLORES = {
            'card_bg': ("#FFFFFF", "#3a3a3a"),
            'primary': "#3498DB",
            'success': "#27AE60",
            'danger': "#E74C3C",
            'warning': "#F39C12",
            'info': "#3498DB",
            'admin': "#E74C3C",
            'empleado': "#3498DB",
        }

        self._crear_interfaz()
        self.cargar_empleados()

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Container principal
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header(main_container)

        # Panel de controles
        self._crear_panel_controles(main_container)

        # Grid de empleados
        self._crear_grid_empleados(main_container)

    def _crear_header(self, parent):
        """Crea el header con título y botón principal"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_frame,
            text="👥 Gestión de Empleados",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Administra el personal del hotel",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Botón agregar
        btn_agregar = ctk.CTkButton(
            header,
            text="➕ Agregar Empleado",
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
            placeholder_text="Buscar por nombre, puesto o usuario...",
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

        # Filtro por privilegio
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        ctk.CTkLabel(
            right_frame,
            text="Privilegio:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(10, 5))

        self.combo_filtro_privilegio = ctk.CTkComboBox(
            right_frame,
            values=["Todos", "Administrador", "Empleado"],
            height=40,
            width=150,
            font=("Segoe UI", 11),
            corner_radius=10,
            command=lambda e: self.aplicar_filtros()
        )
        self.combo_filtro_privilegio.set("Todos")
        self.combo_filtro_privilegio.pack(side="left", padx=(0, 10))

        # Botón refrescar
        btn_refrescar = ctk.CTkButton(
            right_frame,
            text="🔄",
            command=self.cargar_empleados,
            width=40,
            height=40,
            font=("Segoe UI", 18),
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A")
        )
        btn_refrescar.pack(side="left")

    def _crear_grid_empleados(self, parent):
        """Crea el grid scrollable de empleados"""
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

        # Configurar grid para 3 columnas
        for i in range(3):
            self.scroll_frame.columnconfigure(i, weight=1)

    def cargar_empleados(self):
        """Carga y muestra los empleados"""
        # Limpiar grid
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener empleados
        empleados = self.db.obtener_empleados()

        if not empleados:
            self._mostrar_mensaje_vacio()
            return

        # Aplicar filtros
        empleados_filtrados = self._filtrar_empleados(empleados)

        if not empleados_filtrados:
            self._mostrar_mensaje_sin_resultados()
            return

        # Mostrar empleados en grid
        self._mostrar_empleados_grid(empleados_filtrados)

    def _filtrar_empleados(self, empleados: List[Tuple]) -> List[Tuple]:
        """Filtra los empleados según criterios"""
        busqueda = self.entry_buscar.get().strip().lower()
        privilegio_filtro = self.combo_filtro_privilegio.get()

        empleados_filtrados = []

        for empleado in empleados:
            # empleado = (id, nombre, apellido, puesto, telefono, usuario, password, privilegio)
            nombre_completo = f"{empleado[1]} {empleado[2]}".lower()
            puesto = str(empleado[3]).lower()
            usuario = str(empleado[5]).lower() if empleado[5] else ""
            privilegio = empleado[7] if len(empleado) > 7 else "Empleado"

            # Aplicar filtros
            coincide_busqueda = (busqueda in nombre_completo or
                                 busqueda in puesto or
                                 busqueda in usuario) if busqueda else True

            coincide_privilegio = (privilegio == privilegio_filtro if
                                   privilegio_filtro != "Todos" else True)

            if coincide_busqueda and coincide_privilegio:
                empleados_filtrados.append(empleado)

        return empleados_filtrados

    def _mostrar_empleados_grid(self, empleados: List[Tuple]):
        """Muestra los empleados en formato grid"""
        row = 0
        col = 0

        for empleado in empleados:
            card = self._crear_tarjeta_empleado(empleado)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _crear_tarjeta_empleado(self, datos: Tuple):
        """Crea una tarjeta visual para un empleado"""
        empleado_id = datos[0]
        nombre = datos[1]
        apellido = datos[2]
        puesto = datos[3]
        telefono = datos[4] if datos[4] else "Sin teléfono"
        usuario = datos[5] if datos[5] else "Sin usuario"
        privilegio = datos[7] if len(datos) > 7 else "Empleado"

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
        card.bind("<Button-1>", lambda e: self._seleccionar_empleado(datos, card))

        # Container interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Avatar circular con color según privilegio
        avatar_color = self.COLORES['admin'] if privilegio == "Administrador" else self.COLORES['empleado']

        avatar_frame = ctk.CTkFrame(
            content,
            width=80,
            height=80,
            fg_color=avatar_color,
            corner_radius=40
        )
        avatar_frame.pack(pady=(0, 15))
        avatar_frame.pack_propagate(False)

        avatar_icon = "👔" if privilegio == "Administrador" else "👤"
        ctk.CTkLabel(
            avatar_frame,
            text=avatar_icon,
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

        # Badge de privilegio
        badge_color = self.COLORES['admin'] if privilegio == "Administrador" else self.COLORES['empleado']
        badge = ctk.CTkLabel(
            content,
            text=privilegio,
            font=("Segoe UI", 9, "bold"),
            fg_color=badge_color,
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(pady=(0, 15))

        # Separador
        ctk.CTkFrame(
            content,
            height=2,
            fg_color=("#E0E0E0", "#4A4A4A")
        ).pack(fill="x", pady=(0, 15))

        # Información
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))

        # Puesto
        puesto_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        puesto_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            puesto_frame,
            text="💼",
            font=("Segoe UI", 14)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            puesto_frame,
            text=puesto,
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Usuario
        if usuario != "Sin usuario":
            user_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            user_frame.pack(fill="x", pady=(0, 8))

            ctk.CTkLabel(
                user_frame,
                text="🔑",
                font=("Segoe UI", 14)
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                user_frame,
                text=usuario,
                font=("Segoe UI", 10),
                text_color=("#7F8C8D", "#95A5A6"),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

        # Teléfono
        if telefono != "Sin teléfono":
            tel_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            tel_frame.pack(fill="x")

            ctk.CTkLabel(
                tel_frame,
                text="📱",
                font=("Segoe UI", 14)
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                tel_frame,
                text=telefono,
                font=("Segoe UI", 10),
                text_color=("#7F8C8D", "#95A5A6"),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

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

        # Botón eliminar (no para admin)
        if datos[0] != 1:  # No mostrar para el usuario admin
            btn_eliminar = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                width=40,
                height=35,
                font=("Segoe UI", 14),
                corner_radius=8,
                fg_color=self.COLORES['danger'],
                hover_color="#C0392B",
                command=lambda: self.eliminar_empleado(datos)
            )
            btn_eliminar.pack(side="left", expand=True, padx=(5, 0))

    def _seleccionar_empleado(self, datos, card):
        """Selecciona un empleado"""
        self.empleado_seleccionado = datos

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay empleados"""
        mensaje = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        mensaje.grid(row=0, column=0, columnspan=3, pady=100)

        ctk.CTkLabel(
            mensaje,
            text="👥",
            font=("Segoe UI", 72)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="No hay empleados registrados",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            mensaje,
            text="Agrega el primer empleado para comenzar",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def _mostrar_mensaje_sin_resultados(self):
        """Muestra mensaje cuando no hay resultados"""
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
        self.cargar_empleados()

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.entry_buscar.delete(0, 'end')
        self.combo_filtro_privilegio.set("Todos")
        self.cargar_empleados()

    def abrir_formulario_agregar(self):
        """Abre el formulario para agregar empleado"""
        FormularioEmpleado(self.parent, self.db, self.cargar_empleados)

    def abrir_formulario_editar(self, datos=None):
        """Abre el formulario para editar empleado"""
        if datos is None:
            datos = self.empleado_seleccionado

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona un empleado para editar"
            )
            return

        FormularioEmpleado(self.parent, self.db, self.cargar_empleados, datos)

    def eliminar_empleado(self, datos=None):
        """Elimina un empleado"""
        if datos is None:
            datos = self.empleado_seleccionado

        if not datos:
            messagebox.showwarning(
                "Advertencia",
                "Selecciona un empleado para eliminar"
            )
            return

        empleado_id = datos[0]
        nombre_completo = f"{datos[1]} {datos[2]}"

        if empleado_id == 1:
            messagebox.showerror(
                "Error",
                "No se puede eliminar el usuario administrador"
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar a {nombre_completo}?\n\n"
            "Esta acción no se puede deshacer."
        )

        if respuesta:
            self.db.eliminar_empleado(empleado_id)
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
            self.cargar_empleados()

class FormularioEmpleado:
    def __init__(self, parent, db, callback_refrescar, datos=None):
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos

        # Crear ventana emergente
        from tkinter import Toplevel
        self.ventana = Toplevel(parent)
        self.ventana.title("Agregar Empleado" if not datos else "Editar Empleado")
        self.ventana.geometry("550x700")
        self.ventana.resizable(False, False)
        #self.ventana.grab_set()

        # Aplicar tema oscuro
        self.ventana.configure(bg="#2b2b2b")

        # Centrar ventana
        self.centrar_ventana()

        # Crear formulario
        self.crear_formulario()

    def centrar_ventana(self):
        self.ventana.update_idletasks()
        width = self.ventana.winfo_width()
        height = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry(f'{width}x{height}+{x}+{y}')

    def crear_formulario(self):
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.ventana, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = "AGREGAR EMPLEADO" if not self.datos else "EDITAR EMPLEADO"
        ctk.CTkLabel(main_frame,
                     text=titulo,
                     font=("Segoe UI", 18, "bold")).pack(pady=(10, 25))

        # DATOS PERSONALES
        ctk.CTkLabel(main_frame,
                     text="DATOS PERSONALES",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#3498db").pack(anchor="w", padx=20, pady=(10, 15))

        # Nombre
        ctk.CTkLabel(main_frame,
                     text="Nombre",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_nombre = ctk.CTkEntry(main_frame,
                                         placeholder_text="Ej: Juan",
                                         height=40,
                                         font=("Segoe UI", 12),
                                         corner_radius=10)
        self.entry_nombre.pack(fill="x", padx=20, pady=(0, 12))

        # Apellido
        ctk.CTkLabel(main_frame,
                     text="Apellido",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_apellido = ctk.CTkEntry(main_frame,
                                           placeholder_text="Ej: Pérez",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           corner_radius=10)
        self.entry_apellido.pack(fill="x", padx=20, pady=(0, 12))

        # Puesto
        ctk.CTkLabel(main_frame,
                     text="Puesto",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.combo_puesto = ctk.CTkComboBox(main_frame,
                                            values=["Gerente", "Recepcionista", "Limpieza",
                                                    "Mantenimiento", "Seguridad", "Cocina"],
                                            height=40,
                                            font=("Segoe UI", 12),
                                            corner_radius=10,
                                            button_color="#3498db",
                                            button_hover_color="#2980b9")
        self.combo_puesto.pack(fill="x", padx=20, pady=(0, 12))
        self.combo_puesto.set("Recepcionista")

        # Teléfono
        ctk.CTkLabel(main_frame,
                     text="Teléfono",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_telefono = ctk.CTkEntry(main_frame,
                                           placeholder_text="Ej: 1234567890",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           corner_radius=10)
        self.entry_telefono.pack(fill="x", padx=20, pady=(0, 20))

        # Separador
        ctk.CTkFrame(main_frame, height=2, fg_color=("gray70", "gray30")).pack(fill="x", padx=20, pady=15)

        # DATOS DE ACCESO
        ctk.CTkLabel(main_frame,
                     text="DATOS DE ACCESO AL SISTEMA",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#e74c3c").pack(anchor="w", padx=20, pady=(10, 15))

        # Usuario
        ctk.CTkLabel(main_frame,
                     text="Usuario",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_usuario = ctk.CTkEntry(main_frame,
                                          placeholder_text="Nombre de usuario único",
                                          height=40,
                                          font=("Segoe UI", 12),
                                          corner_radius=10)
        self.entry_usuario.pack(fill="x", padx=20, pady=(0, 12))

        # Contraseña
        ctk.CTkLabel(main_frame,
                     text="Contraseña",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_password = ctk.CTkEntry(main_frame,
                                           placeholder_text="Mínimo 4 caracteres",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           show="•",
                                           corner_radius=10)
        self.entry_password.pack(fill="x", padx=20, pady=(0, 12))

        # Privilegio
        ctk.CTkLabel(main_frame,
                     text="Nivel de Privilegio",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.combo_privilegio = ctk.CTkComboBox(main_frame,
                                                values=["Administrador", "Empleado"],
                                                height=40,
                                                font=("Segoe UI", 12),
                                                corner_radius=10,
                                                button_color="#3498db",
                                                button_hover_color="#2980b9")
        self.combo_privilegio.pack(fill="x", padx=20, pady=(0, 25))
        self.combo_privilegio.set("Empleado")

        # Si hay datos (modo editar), rellenar campos
        if self.datos:
            # datos = (id, nombre, apellido, puesto, telefono, usuario, password, privilegio)
            self.entry_nombre.insert(0, self.datos[1])
            self.entry_apellido.insert(0, self.datos[2])
            self.combo_puesto.set(self.datos[3])
            self.entry_telefono.insert(0, self.datos[4] if self.datos[4] else "")
            self.entry_usuario.insert(0, self.datos[5] if self.datos[5] else "")
            self.entry_password.insert(0, self.datos[6] if self.datos[6] else "")
            self.combo_privilegio.set(self.datos[7] if self.datos[7] else "Empleado")

            # Si es el admin, deshabilitar privilegio
            if self.datos[0] == 1:
                self.combo_privilegio.configure(state="disabled")

        # Frame para botones
        frame_botones = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_botones.pack(pady=(10, 15))

        # Botón Guardar
        btn_guardar = ctk.CTkButton(frame_botones,
                                    text="💾 Guardar",
                                    command=self.guardar,
                                    width=180,
                                    height=45,
                                    font=("Segoe UI", 13, "bold"),
                                    corner_radius=10,
                                    fg_color="#27ae60",
                                    hover_color="#229954")
        btn_guardar.pack(side="left", padx=5)

        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(frame_botones,
                                     text="❌ Cancelar",
                                     command=self.ventana.destroy,
                                     width=180,
                                     height=45,
                                     font=("Segoe UI", 13, "bold"),
                                     corner_radius=10,
                                     fg_color="#e74c3c",
                                     hover_color="#c0392b")
        btn_cancelar.pack(side="left", padx=5)

    def guardar(self):
        """Guarda o actualiza el empleado"""
        # Obtener valores
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        puesto = self.combo_puesto.get()
        telefono = self.entry_telefono.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        privilegio = self.combo_privilegio.get()

        # Validaciones básicas
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        if not apellido:
            messagebox.showerror("Error", "El apellido es obligatorio")
            return

        # Validar teléfono (solo números)
        if telefono and not telefono.isdigit():
            messagebox.showerror("Error", "El teléfono debe contener solo números")
            return

        # Guardar en base de datos
        if self.datos:  # EDITAR
            empleado_id = self.datos[0]
            exito = self.db.actualizar_empleado(empleado_id, nombre, apellido,
                                                puesto, telefono, privilegio)

            if exito:
                messagebox.showinfo("Éxito", "Empleado actualizado correctamente")
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el empleado")

        else:  # AGREGAR
            if not usuario or not password:
                messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
                return

            exito = self.db.agregar_empleado(nombre, apellido, puesto, telefono,
                                             usuario, password, privilegio)

            if exito:
                messagebox.showinfo("Éxito", "Empleado agregado correctamente")
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "El nombre de usuario ya existe")