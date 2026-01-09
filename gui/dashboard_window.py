# gui/dashboard_window.py
import customtkinter as ctk
from tkinter import messagebox
from gui.habitaciones_window import HabitacionesWindow
from gui.empleados_window import EmpleadosWindow
from gui.reportes_window import ReportesWindow
from gui.reservas_window import ReservasWindow
from gui.huespedes_window import HuespedesWindow
from database.db_manager import DatabaseManager


class DashboardWindow:
    def __init__(self, root, nombre_empleado, apellido_empleado, puesto, privilegio, login_window=None):
        self.root = root
        self.nombre_empleado = nombre_empleado
        self.apellido_empleado = apellido_empleado
        self.puesto = puesto
        self.privilegio = privilegio
        self.login_window = login_window

        # Base de datos
        self.db = DatabaseManager()

        # Configuración de ventana
        self.root.title("Sistema Hotel Amigues - Dashboard")
        self.root.geometry("1400x800")

        # Variables
        self.boton_activo = None

        # Colores del tema
        self.COLORES = {
            'sidebar': ("#2C3E50", "#1a252f"),
            'sidebar_hover': ("#34495E", "#243342"),
            'sidebar_active': ("#3498DB", "#2980B9"),
            'content_bg': ("#ECF0F1", "#2b2b2b"),
            'card_bg': ("#FFFFFF", "#3a3a3a"),
            'primary': "#3498DB",
            'success': "#27AE60",
            'warning': "#F39C12",
            'danger': "#E74C3C",
            'info': "#3498DB",
        }

        self._crear_interfaz()
        self.mostrar_inicio()

        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _crear_interfaz(self):
        """Crea la interfaz principal del dashboard"""
        # Container principal
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # Sidebar
        self._crear_sidebar(main_container)

        # Área de contenido
        self._crear_area_contenido(main_container)

    def _crear_sidebar(self, parent):
        """Crea la barra lateral de navegación"""
        self.sidebar = ctk.CTkFrame(
            parent,
            width=280,
            corner_radius=0,
            fg_color=self.COLORES['sidebar']
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Header del sidebar
        self._crear_sidebar_header()

        # Perfil del usuario
        self._crear_perfil_usuario()

        # Separador
        ctk.CTkFrame(
            self.sidebar,
            height=2,
            fg_color=self.COLORES['sidebar_active']
        ).pack(fill="x", padx=20, pady=20)

        # Menú de navegación
        self._crear_menu_navegacion()

        # Espaciador
        ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        ).pack(fill="both", expand=True)

    def _crear_sidebar_header(self):
        """Crea el header del sidebar con logo y título"""
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(30, 20))

        # Logo
        #ctk.CTkLabel(
        #    header,
        #    text="🏨",
        #    font=("Segoe UI", 40)
        #).pack()

        # Título
        ctk.CTkLabel(
            header,
            text="HOTEL AMIGUES",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(10, 0))

        # Subtítulo
        ctk.CTkLabel(
            header,
            text="Sistema de Gestión",
            font=("Segoe UI", 11),
            text_color=("#BDC3C7", "#95A5A6")
        ).pack()

    def _crear_perfil_usuario(self):
        """Crea la sección de perfil del usuario"""
        perfil = ctk.CTkFrame(
            self.sidebar,
            fg_color=("#34495E", "#243342"),
            corner_radius=12
        )
        perfil.pack(fill="x", padx=20, pady=(0, 10))

        # Contenido del perfil
        content = ctk.CTkFrame(perfil, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=15)

        # Avatar personalizado según puesto
        self._crear_avatar_puesto(content)

        # Nombre
        ctk.CTkLabel(
            content,
            text=f"{self.nombre_empleado} {self.apellido_empleado}",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(8, 5))

        # Puesto
        ctk.CTkLabel(
            content,
            text=self.puesto,
            font=("Segoe UI", 10),
            text_color=("#95A5A6", "#7F8C8D")
        ).pack(pady=(0, 8))

        # Badge de privilegio
        badge_color = self.COLORES['danger'] if self.privilegio == "Administrador" else self.COLORES['info']
        ctk.CTkLabel(
            content,
            text=self.privilegio,
            font=("Segoe UI", 9, "bold"),
            fg_color=badge_color,
            corner_radius=6,
            padx=12,
            pady=4
        ).pack(pady=(0, 8))

        # Botón de cerrar sesión
        ctk.CTkButton(
            self.sidebar,
            text="  🚪   Cerrar Sesión",
            font=("Segoe UI", 13),
            height=45,
            corner_radius=10,
            fg_color=self.COLORES['danger'],
            hover_color=("#C0392B", "#A93226"),
            anchor="w",
            command=self.salir
        ).pack(padx=20, pady=(0, 10))

    def _crear_avatar_puesto(self, parent):
        """Crea el avatar personalizado según el puesto del empleado"""
        try:
            from PIL import Image, ImageDraw
            import os

            # Mapeo de puestos a nombres de archivo
            avatares_por_puesto = {
                'Gerente': 'cinnamon_gerente.png',
                'Recepcionista': 'cinnamon_recepcion.png',
                'Limpieza': 'cinnamon_limpieza.png',
            }

            # Obtener ruta del proyecto
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)

            # Determinar qué imagen usar según el puesto
            nombre_archivo = avatares_por_puesto.get(self.puesto, 'default_avatar.png')
            imagen_path = os.path.join(project_root, "assets", "images", nombre_archivo)

            # Si no existe la imagen específica, intentar con default
            if not os.path.exists(imagen_path):
                imagen_path = os.path.join(project_root, "assets", "images", "default_avatar.png")

            # Cargar y procesar imagen
            if os.path.exists(imagen_path):
                imagen_pil = Image.open(imagen_path)

                # Redimensionar
                tamaño = 80
                imagen_pil.thumbnail((tamaño, tamaño), Image.Resampling.LANCZOS)

                # Hacer circular
                imagen_pil = self._hacer_avatar_circular(imagen_pil, tamaño)

                # Convertir a CTkImage
                imagen_ctk = ctk.CTkImage(
                    light_image=imagen_pil,
                    dark_image=imagen_pil,
                    size=(tamaño, tamaño)
                )

                # Mostrar imagen
                label_avatar = ctk.CTkLabel(
                    parent,
                    image=imagen_ctk,
                    text=""
                )
                label_avatar.pack()
            else:
                # Fallback: emoji según puesto
                self._crear_avatar_emoji(parent)

        except Exception as e:
            print(f"Error al cargar avatar: {e}")
            # Fallback: emoji según puesto
            self._crear_avatar_emoji(parent)

    def _crear_avatar_emoji(self, parent):
        """Crea un avatar con emoji según el puesto (fallback)"""
        emojis_por_puesto = {
            'Administrador': '👨‍💼',
            'Gerente': '👔',
            'Recepcionista': '🧑‍💻',
            'Ama de Llaves': '🧹',
            'Contador': '📊',
            'Seguridad': '🛡️',
        }

        emoji = emojis_por_puesto.get(self.puesto, '👤')

        ctk.CTkLabel(
            parent,
            text=emoji,
            font=("Segoe UI", 32)
        ).pack()

    def _hacer_avatar_circular(self, imagen, tamaño):
        """Convierte el avatar en circular"""
        from PIL import Image, ImageDraw

        # Convertir a RGBA
        if imagen.mode != 'RGBA':
            imagen = imagen.convert('RGBA')

        # Hacer cuadrada
        ancho, alto = imagen.size
        if ancho != alto:
            lado = min(ancho, alto)
            left = (ancho - lado) // 2
            top = (alto - lado) // 2
            imagen = imagen.crop((left, top, left + lado, top + lado))

        # Redimensionar al tamaño exacto
        imagen = imagen.resize((tamaño, tamaño), Image.Resampling.LANCZOS)

        # Crear máscara circular
        mascara = Image.new('L', (tamaño, tamaño), 0)
        draw = ImageDraw.Draw(mascara)
        draw.ellipse((0, 0, tamaño, tamaño), fill=255)

        # Aplicar máscara
        output = Image.new('RGBA', (tamaño, tamaño), (0, 0, 0, 0))
        output.paste(imagen, (0, 0))
        output.putalpha(mascara)

        return output

    def _crear_menu_navegacion(self):
        """Crea el menú de navegación"""
        # Definir elementos del menú
        menu_items = [
            {
                "texto": "Inicio",
                "icono": "🏠",
                "comando": self.mostrar_inicio,
                "permiso": True
            },
            {
                "texto": "Habitaciones",
                "icono": "🛏️",
                "comando": self.abrir_habitaciones,
                "permiso": True
            },
            {
                "texto": "Reservas",
                "icono": "📅",
                "comando": self.abrir_reservas,
                "permiso": True
            },
            {
                "texto": "Huéspedes",
                "icono": "👥",
                "comando": self.abrir_huesped,
                "permiso": True
            },
            {
                "texto": "Empleados",
                "icono": "💼",
                "comando": self.abrir_empleados,
                "permiso": self.privilegio == "Administrador"
            },
            {
                "texto": "Reportes",
                "icono": "📊",
                "comando": self.abrir_reportes,
                "permiso": self.privilegio == "Administrador"
            },
            {
                "texto": "Configuración",
                "icono": "⚙️",
                "comando": self.abrir_configuracion,
                "permiso": self.privilegio == "Administrador"
            }
        ]

        # Crear botones del menú
        self.botones_menu = {}
        for item in menu_items:
            if item["permiso"]:
                btn = self._crear_boton_menu(
                    item["texto"],
                    item["icono"],
                    item["comando"]
                )
                self.botones_menu[item["texto"]] = btn

    def _crear_boton_menu(self, texto, icono, comando):
        """Crea un botón de menú estilizado"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {icono}   {texto}",
            font=("Segoe UI", 13),
            height=45,
            corner_radius=10,
            fg_color="transparent",
            text_color=("#ECF0F1", "#ECF0F1"),
            hover_color=self.COLORES['sidebar_hover'],
            anchor="w",
            command=lambda: self._activar_boton(texto, comando)
        )
        btn.pack(fill="x", padx=15, pady=3)
        return btn

    def _activar_boton(self, nombre_boton, comando):
        """Activa visualmente el botón seleccionado"""
        # Desactivar botón anterior
        if self.boton_activo and self.boton_activo in self.botones_menu:
            self.botones_menu[self.boton_activo].configure(
                fg_color="transparent"
            )

        # Activar nuevo botón
        if nombre_boton in self.botones_menu:
            self.botones_menu[nombre_boton].configure(
                fg_color=self.COLORES['sidebar_active']
            )
            self.boton_activo = nombre_boton

        # Ejecutar comando
        comando()

    def _crear_area_contenido(self, parent):
        """Crea el área principal de contenido"""
        self.content_frame = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['content_bg'],
            corner_radius=0
        )
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Frame normal (no scrollable) para el contenido
        self.area_contenido = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.area_contenido.pack(fill="both", expand=True, padx=0, pady=0)

    def limpiar_area_contenido(self):
        """Limpia el área de contenido"""
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        """Muestra la pantalla de inicio con estadísticas"""
        self.limpiar_area_contenido()

        # Container principal con padding
        container = ctk.CTkFrame(self.area_contenido, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        self._crear_header_inicio(container)

        # Estadísticas
        self._crear_cards_estadisticas(container)

        # Información adicional
        self._crear_info_adicional(container)

    def _crear_header_inicio(self, parent):
        """Crea el header de la pantalla de inicio"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))

        # Título
        ctk.CTkLabel(
            header,
            text="📊 Panel de Control",
            font=("Segoe UI", 32, "bold"),
            anchor="w"
        ).pack(anchor="w")

        # Subtítulo
        ctk.CTkLabel(
            header,
            text=f"Bienvenido de vuelta, {self.nombre_empleado}",
            font=("Segoe UI", 14),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

    def _crear_cards_estadisticas(self, parent):
        """Crea las tarjetas de estadísticas"""
        # Obtener estadísticas
        stats = self.db.obtener_estadisticas()

        # Grid de estadísticas
        stats_grid = ctk.CTkFrame(parent, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 30))

        # Configurar columnas
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)

        # Definir tarjetas
        cards_data = [
            {
                "titulo": "Disponibles",
                "valor": stats['disponibles'],
                "icono": "✅",
                "color": self.COLORES['success'],
                "subtitulo": "Habitaciones listas"
            },
            {
                "titulo": "Ocupadas",
                "valor": stats['ocupadas'],
                "icono": "🏨",
                "color": self.COLORES['danger'],
                "subtitulo": "En uso actualmente"
            },
            {
                "titulo": "En Limpieza",
                "valor": stats['limpieza'],
                "icono": "🧹",
                "color": self.COLORES['warning'],
                "subtitulo": "En mantenimiento"
            },
            {
                "titulo": "Empleados",
                "valor": stats['empleados'],
                "icono": "👥",
                "color": self.COLORES['info'],
                "subtitulo": "Personal activo"
            }
        ]

        # Crear tarjetas
        for i, card_data in enumerate(cards_data):
            self._crear_tarjeta_stat(stats_grid, card_data, i)

    def _crear_tarjeta_stat(self, parent, data, column):
        """Crea una tarjeta de estadística moderna"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        icon_frame = ctk.CTkFrame(
            header,
            width=50,
            height=50,
            fg_color=data['color'],
            corner_radius=25
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)

        ctk.CTkLabel(
            icon_frame,
            text=data['icono'],
            font=("Segoe UI", 24)
        ).place(relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True, padx=(15, 0))

        ctk.CTkLabel(
            title_frame,
            text=data['titulo'],
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=str(data['valor']),
            font=("Segoe UI", 42, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            content,
            text=data['subtitulo'],
            font=("Segoe UI", 11),
            text_color=("#95A5A6", "#7F8C8D"),
            anchor="w"
        ).pack(anchor="w")

    def _crear_info_adicional(self, parent):
        """Crea sección de información adicional"""
        info_container = ctk.CTkFrame(parent, fg_color="transparent")
        info_container.pack(fill="both", expand=True)

        info_container.columnconfigure(0, weight=2)
        info_container.columnconfigure(1, weight=1)

        self._crear_actividad_reciente(info_container)
        self._crear_accesos_rapidos(info_container)

    def _crear_actividad_reciente(self, parent):
        """Crea la sección de actividad reciente"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 15))

        ctk.CTkLabel(
            header,
            text="📋 Actividad Reciente",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        ).pack(anchor="w")

        activities = [
            "Nueva reserva registrada - Hab. 101",
            "Check-out completado - Hab. 205",
            "Habitación 302 lista para ocupar",
            "Nueva reserva para fin de semana"
        ]

        for activity in activities:
            item = ctk.CTkFrame(card, fg_color="transparent")
            item.pack(fill="x", padx=25, pady=8)

            ctk.CTkLabel(
                item,
                text="•",
                font=("Segoe UI", 16),
                text_color=self.COLORES['primary']
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                item,
                text=activity,
                font=("Segoe UI", 11),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(card, fg_color="transparent", height=15).pack()

    def _crear_accesos_rapidos(self, parent):
        """Crea la sección de accesos rápidos"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLORES['card_bg'],
            corner_radius=15
        )
        card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 15))

        ctk.CTkLabel(
            header,
            text="⚡ Accesos Rápidos",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        ).pack(anchor="w")

        accesos = [
            ("Nueva Reserva", "📅", self.abrir_reservas),
            ("Ver Habitaciones", "🛏️", self.abrir_habitaciones),
            ("Registrar Huésped", "👤", self.abrir_huesped),
        ]

        for texto, icono, comando in accesos:
            btn = ctk.CTkButton(
                card,
                text=f"{icono}  {texto}",
                font=("Segoe UI", 12),
                height=45,
                corner_radius=10,
                fg_color="transparent",
                border_width=2,
                border_color=("#BDC3C7", "#4A4A4A"),
                hover_color=self.COLORES['sidebar_hover'],
                command=comando
            )
            btn.pack(fill="x", padx=25, pady=8)

        ctk.CTkFrame(card, fg_color="transparent", height=15).pack()

    def abrir_habitaciones(self):
        self.limpiar_area_contenido()
        HabitacionesWindow(self.area_contenido, self.privilegio)

    def abrir_empleados(self):
        if self.privilegio != "Administrador":
            self.mostrar_acceso_denegado()
            return
        self.limpiar_area_contenido()
        EmpleadosWindow(self.area_contenido)

    def abrir_reservas(self):
        self.limpiar_area_contenido()
        ReservasWindow(self.area_contenido, self.privilegio)

    def abrir_huesped(self):
        self.limpiar_area_contenido()
        HuespedesWindow(self.area_contenido)

    def abrir_reportes(self):
        if self.privilegio != "Administrador":
            self.mostrar_acceso_denegado()
            return
        self.limpiar_area_contenido()
        ReportesWindow(self.area_contenido)

    def abrir_configuracion(self):
        if self.privilegio != "Administrador":
            self.mostrar_acceso_denegado()
            return
        self.limpiar_area_contenido()
        self.mostrar_en_desarrollo("Configuración", "⚙️")

    def mostrar_en_desarrollo(self, modulo, icono):
        """Muestra pantalla de módulo en desarrollo"""
        container = ctk.CTkFrame(self.area_contenido, fg_color="transparent")
        container.pack(fill="both", expand=True)

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            content,
            text=icono,
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            content,
            text=f"Módulo de {modulo}",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            content,
            text="Esta funcionalidad estará disponible próximamente",
            font=("Segoe UI", 14),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack()

    def mostrar_acceso_denegado(self):
        """Muestra pantalla de acceso denegado"""
        self.limpiar_area_contenido()

        container = ctk.CTkFrame(self.area_contenido, fg_color="transparent")
        container.pack(fill="both", expand=True)

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            content,
            text="🚫",
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            content,
            text="ACCESO DENEGADO",
            font=("Segoe UI", 28, "bold"),
            text_color=self.COLORES['danger']
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            content,
            text="No tienes permisos para acceder a esta sección",
            font=("Segoe UI", 14),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            content,
            text="Contacta al administrador del sistema",
            font=("Segoe UI", 12, "italic"),
            text_color=("#95A5A6", "#7F8C8D")
        ).pack()

    def salir(self):
        """Cierra la sesión y vuelve al login"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Desea cerrar sesión?"
        )

        if respuesta:
            # Cerrar la base de datos
            if self.db:
                self.db.cerrar()
                self.db = None

            # Cerrar la ventana del dashboard
            self._on_closing()

    def _on_closing(self):
        """Maneja el cierre de la ventana del dashboard"""
        if self.db:
            try:
                self.db.cerrar()
            except:
                pass

        # Si hay referencia al login, mostrarlo de nuevo
        if self.login_window:
            self.login_window._on_dashboard_close(self.root)
        else:
            self.root.destroy()

    def __del__(self):
        """Destructor para cerrar conexión a BD"""
        if hasattr(self, 'db') and self.db:
            try:
                self.db.cerrar()
            except Exception:
                pass