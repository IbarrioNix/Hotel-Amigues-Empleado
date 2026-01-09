# gui/login_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from typing import Optional, Tuple

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Hotel - Login")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)

        # Variables
        self.db: Optional[DatabaseManager] = None
        self.intentos_fallidos = 0
        self.max_intentos = 3
        self.password_visible = False

        # Inicializar
        self._inicializar_db()
        self._centrar_ventana()
        self._crear_widgets()

        # Focus inicial
        self.entry_usuario.focus()

        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _inicializar_db(self):
        """Inicializa la conexión a la base de datos con manejo de errores"""
        try:
            self.db = DatabaseManager()
        except Exception as e:
            messagebox.showerror(
                "Error de Conexión",
                f"No se pudo conectar a la base de datos:\n{str(e)}"
            )
            self.root.quit()

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Container principal
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # Panel izquierdo - Imagen/Branding
        panel_izq = ctk.CTkFrame(container, fg_color=("#2C3E50", "#1a252f"), corner_radius=0)
        panel_izq.pack(side="left", fill="both", expand=True)

        self._crear_panel_branding(panel_izq)

        # Panel derecho - Formulario
        panel_der = ctk.CTkFrame(container, fg_color=("#ECF0F1", "#2b2b2b"), corner_radius=0, width=450)
        panel_der.pack(side="right", fill="both", padx=0, pady=0)
        panel_der.pack_propagate(False)

        self._crear_panel_login(panel_der)

    def _crear_panel_branding(self, parent):
        """Crea el panel de branding con diseño atractivo"""
        # Container centrado
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Cargar y mostrar imagen
        try:
            from PIL import Image, ImageDraw
            import os

            # Obtener ruta del proyecto (carpeta raíz)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            imagen_path = os.path.join(project_root, "assets", "images", "cinnamon_login.png")

            imagen_pil = Image.open(imagen_path)

            # Redimensionar imagen manteniendo aspecto
            ancho_max = 350
            alto_max = 600
            imagen_pil.thumbnail((ancho_max, alto_max), Image.Resampling.LANCZOS)

            # Crear imagen redondeada
            imagen_pil = self._hacer_imagen_circular(imagen_pil)

            # Convertir a CTkImage
            imagen_ctk = ctk.CTkImage(
                light_image=imagen_pil,
                dark_image=imagen_pil,
                size=imagen_pil.size
            )

            # Mostrar imagen
            label_imagen = ctk.CTkLabel(
                content,
                image=imagen_ctk,
                text=""
            )
            label_imagen.pack(pady=(0, 30))

        except Exception as e:
            # Si falla cargar la imagen, usar emoji como fallback
            print(f"Error al cargar imagen: {e}")
            print(f"Ruta intentada: {imagen_path if 'imagen_path' in locals() else 'No se pudo determinar'}")
            ctk.CTkLabel(
                content,
                text="🏨",
                font=("Segoe UI", 120)
            ).pack(pady=(0, 30))

        # Título principal
        titulo = ctk.CTkLabel(
            content,
            text="HOTEL AMIGUES",
            font=("Segoe UI", 42, "bold"),
            text_color=("#ECF0F1", "#ECF0F1")
        )
        titulo.pack(pady=(0, 15))

        # Línea decorativa
        linea = ctk.CTkFrame(content, height=3, width=200, fg_color=("#3498DB", "#3498DB"))
        linea.pack(pady=(0, 15))

        # Subtítulo
        subtitulo = ctk.CTkLabel(
            content,
            text="Sistema de Gestión Hotelera",
            font=("Segoe UI", 18),
            text_color=("#BDC3C7", "#BDC3C7")
        )
        subtitulo.pack(pady=(0, 50))

        # Features
        features = [
            "✓ Gestión de Reservas",
            "✓ Control de Habitaciones",
            "✓ Administración de Personal",
            "✓ Reportes en Tiempo Real"
        ]

        for feature in features:
            feature_label = ctk.CTkLabel(
                content,
                text=feature,
                font=("Segoe UI", 14),
                text_color=("#95A5A6", "#95A5A6"),
                anchor="w"
            )
            feature_label.pack(pady=5, anchor="w", padx=20)

    def _hacer_imagen_circular(self, imagen):
        """Convierte una imagen en perfectamente circular"""
        from PIL import Image, ImageDraw

        # Convertir a RGBA si no lo es
        if imagen.mode != 'RGBA':
            imagen = imagen.convert('RGBA')

        # Hacer la imagen cuadrada (recortar al centro)
        ancho, alto = imagen.size
        tamaño = min(ancho, alto)

        # Calcular coordenadas para recortar al centro
        left = (ancho - tamaño) // 2
        top = (alto - tamaño) // 2
        right = left + tamaño
        bottom = top + tamaño

        # Recortar imagen a cuadrado
        imagen_cuadrada = imagen.crop((left, top, right, bottom))

        # Crear máscara circular perfecta
        mascara = Image.new('L', (tamaño, tamaño), 0)
        draw = ImageDraw.Draw(mascara)

        # Dibujar círculo perfecto
        draw.ellipse((0, 0, tamaño, tamaño), fill=255)

        # Aplicar máscara
        output = Image.new('RGBA', (tamaño, tamaño), (0, 0, 0, 0))
        output.paste(imagen_cuadrada, (0, 0))
        output.putalpha(mascara)

        return output

    def _crear_panel_login(self, parent):
        """Crea el panel de login con diseño moderno"""
        # Container del formulario
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header del formulario
        header = ctk.CTkLabel(
            form_container,
            text="Iniciar Sesión",
            font=("Segoe UI", 32, "bold"),
            text_color=("#2C3E50", "#ECF0F1")
        )
        header.pack(pady=(0, 10))

        subheader = ctk.CTkLabel(
            form_container,
            text="Ingresa tus credenciales para continuar",
            font=("Segoe UI", 12),
            text_color=("#7F8C8D", "#95A5A6")
        )
        subheader.pack(pady=(0, 40))

        # Campo Usuario
        self._crear_campo_usuario(form_container)

        # Campo Contraseña
        self._crear_campo_password(form_container)

        # Checkbox recordar
        self.check_recordar = ctk.CTkCheckBox(
            form_container,
            text="Recordar mi usuario",
            font=("Segoe UI", 11),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=5
        )
        self.check_recordar.pack(pady=(10, 25), anchor="w", padx=5)

        # Botón Ingresar
        self.btn_login = ctk.CTkButton(
            form_container,
            text="INGRESAR",
            width=350,
            height=50,
            font=("Segoe UI", 15, "bold"),
            corner_radius=12,
            fg_color=("#27AE60", "#27AE60"),
            hover_color=("#229954", "#229954"),
            command=self.validar_login
        )
        self.btn_login.pack(pady=(0, 15))

        # Botón Limpiar
        btn_limpiar = ctk.CTkButton(
            form_container,
            text="Limpiar campos",
            width=350,
            height=40,
            font=("Segoe UI", 12),
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            text_color=("#7F8C8D", "#95A5A6"),
            hover_color=("#ECF0F1", "#3A3A3A"),
            command=self._limpiar_campos
        )
        btn_limpiar.pack(pady=(0, 30))

        # Footer
        footer_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        footer_frame.pack(pady=(20, 0))

        # Botón cambiar tema
        btn_tema = ctk.CTkButton(
            footer_frame,
            text="🌓",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            corner_radius=20,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A"),
            command=self._toggle_theme
        )
        btn_tema.pack(side="left", padx=5)

        # Info adicional
        info_label = ctk.CTkLabel(
            footer_frame,
            text="¿Problemas para ingresar? Contacta al administrador",
            font=("Segoe UI", 9),
            text_color=("#95A5A6", "#7F8C8D")
        )
        info_label.pack(side="left", padx=10)

    def _crear_campo_usuario(self, parent):
        """Crea el campo de usuario con diseño mejorado"""
        label_usuario = ctk.CTkLabel(
            parent,
            text="Usuario",
            font=("Segoe UI", 13, "bold"),
            text_color=("#2C3E50", "#ECF0F1"),
            anchor="w"
        )
        label_usuario.pack(anchor="w", pady=(0, 8))

        self.entry_usuario = ctk.CTkEntry(
            parent,
            placeholder_text="Ingresa tu nombre de usuario",
            width=350,
            height=50,
            font=("Segoe UI", 13),
            corner_radius=12,
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A")
        )
        self.entry_usuario.pack(pady=(0, 20))

    def _crear_campo_password(self, parent):
        """Crea el campo de contraseña con botón mostrar/ocultar"""
        label_password = ctk.CTkLabel(
            parent,
            text="Contraseña",
            font=("Segoe UI", 13, "bold"),
            text_color=("#2C3E50", "#ECF0F1"),
            anchor="w"
        )
        label_password.pack(anchor="w", pady=(0, 8))

        # Frame contenedor
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(pady=(0, 5))

        self.entry_password = ctk.CTkEntry(
            password_frame,
            placeholder_text="Ingresa tu contraseña",
            width=295,
            height=50,
            font=("Segoe UI", 13),
            show="•",
            corner_radius=12,
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A")
        )
        self.entry_password.pack(side="left", padx=(0, 5))
        self.entry_password.bind('<Return>', lambda e: self.validar_login())

        # Botón mostrar/ocultar
        self.btn_mostrar = ctk.CTkButton(
            password_frame,
            text="👁",
            width=50,
            height=50,
            font=("Segoe UI", 18),
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            border_color=("#BDC3C7", "#4A4A4A"),
            hover_color=("#ECF0F1", "#3A3A3A"),
            command=self._toggle_password_visibility
        )
        self.btn_mostrar.pack(side="left")

    def _toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña"""
        if self.entry_password.cget("show") == "•":
            self.entry_password.configure(show="")
            self.btn_mostrar.configure(text="🙈")
        else:
            self.entry_password.configure(show="•")
            self.btn_mostrar.configure(text="👁")

    def _toggle_theme(self):
        """Cambia entre modo oscuro y claro"""
        nuevo_modo = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(nuevo_modo)

    def _limpiar_campos(self):
        """Limpia los campos de entrada"""
        self.entry_usuario.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.entry_usuario.focus()

    def _validar_campos(self) -> Tuple[bool, str, str]:
        """Valida los campos de entrada"""
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if not usuario:
            messagebox.showwarning("Advertencia", "Por favor ingrese su usuario")
            self.entry_usuario.focus()
            return False, "", ""

        if not password:
            messagebox.showwarning("Advertencia", "Por favor ingrese su contraseña")
            self.entry_password.focus()
            return False, "", ""

        if len(usuario) < 3:
            messagebox.showwarning("Advertencia", "El usuario debe tener al menos 3 caracteres")
            return False, "", ""

        return True, usuario, password

    def _bloquear_login(self):
        """Bloquea temporalmente el login"""
        self.btn_login.configure(
            state="disabled",
            text="BLOQUEADO",
            fg_color=("#E74C3C", "#C0392B")
        )
        messagebox.showerror(
            "Cuenta Bloqueada",
            "Demasiados intentos fallidos.\nPor favor contacte al administrador."
        )

    def validar_login(self):
        """Valida las credenciales del usuario"""
        es_valido, usuario, password = self._validar_campos()
        if not es_valido:
            return

        if self.intentos_fallidos >= self.max_intentos:
            self._bloquear_login()
            return

        try:
            empleado = self.db.validar_login(usuario, password)

            if empleado:
                self._login_exitoso(empleado)
            else:
                self._login_fallido()

        except Exception as e:
            messagebox.showerror("Error", f"Error al validar credenciales:\n{str(e)}")

    def _login_exitoso(self, empleado):
        """Maneja un login exitoso"""
        empleado_id, nombre, apellido, puesto = empleado
        privilegio = self._obtener_privilegio(empleado_id)

        # NO cerrar BD aquí - se cerrará cuando el dashboard cierre
        # Solo ocultar ventana de login
        self.root.withdraw()

        # Abrir dashboard
        self._abrir_dashboard(nombre, apellido, puesto, privilegio)

    def _login_fallido(self):
        """Maneja un login fallido"""
        self.intentos_fallidos += 1
        intentos_restantes = self.max_intentos - self.intentos_fallidos

        if intentos_restantes > 0:
            messagebox.showerror(
                "Error de Autenticación",
                f"Usuario o contraseña incorrectos.\nIntentos restantes: {intentos_restantes}"
            )
            self.entry_password.delete(0, 'end')
            self.entry_password.focus()
        else:
            self._bloquear_login()

    def _obtener_privilegio(self, empleado_id: int) -> str:
        """Obtiene el privilegio del empleado"""
        try:
            empleados = self.db.obtener_empleados()
            for emp in empleados:
                if emp[0] == empleado_id:
                    return emp[7] if emp[7] else "Administrador"
            return "Administrador"
        except Exception:
            return "Administrador"

    def _abrir_dashboard(self, nombre: str, apellido: str, puesto: str, privilegio: str):
        """Abre la ventana del dashboard"""
        from gui.dashboard_window import DashboardWindow

        try:
            # Crear nueva ventana toplevel
            dashboard_window = ctk.CTkToplevel(self.root)
            dashboard_window.withdraw()  # Ocultar mientras se configura

            # Crear dashboard
            dashboard = DashboardWindow(
                dashboard_window,
                nombre,
                apellido,
                puesto,
                privilegio,
                self  # Pasar referencia al login
            )

            # Mostrar dashboard
            dashboard_window.deiconify()

            # Cuando se cierre el dashboard, mostrar login nuevamente
            dashboard_window.protocol("WM_DELETE_WINDOW", lambda: self._on_dashboard_close(dashboard_window))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el dashboard:\n{str(e)}")
            self.root.deiconify()  # Mostrar login de nuevo

    def _on_dashboard_close(self, dashboard_window):
        """Maneja el cierre del dashboard"""
        dashboard_window.destroy()
        self._limpiar_campos()
        self.intentos_fallidos = 0

        # Reinicializar la conexión a la base de datos
        try:
            self.db = DatabaseManager()
        except Exception as e:
            messagebox.showerror(
                "Error de Conexión",
                f"No se pudo reconectar a la base de datos:\n{str(e)}"
            )

        self.root.deiconify()  # Mostrar login de nuevo

    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        if self.db:
            try:
                self.db.cerrar()
            except:
                pass
        self.root.quit()

    def __del__(self):
        """Destructor para cerrar la conexión a la BD"""
        if hasattr(self, 'db') and self.db:
            try:
                self.db.cerrar()
            except Exception:
                pass