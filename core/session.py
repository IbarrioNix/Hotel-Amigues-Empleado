# core/session.py
"""
Gestor de Sesión Global - Singleton Pattern
Mantiene la conexión a BD y datos del usuario a través de toda la aplicación
"""

from database.db_manager import DatabaseManager
from typing import Optional, Dict, Any


class SessionManager:
    """
    Singleton que mantiene el estado de la sesión del usuario
    y la conexión a la base de datos compartida
    """
    _instance: Optional['SessionManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Solo inicializar una vez
        if self._initialized:
            return

        self._initialized = True
        self._db: Optional[DatabaseManager] = None
        self._usuario: Dict[str, Any] = {}
        self._activa = False

    # ==================== CONEXIÓN A BD ====================

    def conectar_db(self) -> bool:
        """Establece conexión con la base de datos"""
        if self._db is not None:
            return True  # Ya está conectado

        try:
            self._db = DatabaseManager()
            return True
        except Exception as e:
            print(f"Error al conectar a BD: {e}")
            self._db = None
            return False

    def cerrar_db(self):
        """Cierra la conexión a la base de datos"""
        if self._db:
            try:
                self._db.cerrar()
            except Exception as e:
                print(f"Error al cerrar BD: {e}")
            finally:
                self._db = None

    @property
    def db(self) -> Optional[DatabaseManager]:
        """Obtiene la instancia de base de datos"""
        return self._db

    # ==================== GESTIÓN DE SESIÓN ====================

    def iniciar_sesion(self, empleado_data: tuple, privilegio: str) -> bool:
        """
        Inicia sesión con los datos del empleado

        Args:
            empleado_data: (id, nombre, apellido, puesto)
            privilegio: Nivel de privilegio del empleado
        """
        try:
            self._usuario = {
                'id': empleado_data[0],
                'nombre': empleado_data[1],
                'apellido': empleado_data[2],
                'puesto': empleado_data[3],
                'privilegio': privilegio,
                'nombre_completo': f"{empleado_data[1]} {empleado_data[2]}"
            }
            self._activa = True
            return True
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return False

    def cerrar_sesion(self):
        """Cierra la sesión actual y limpia datos"""
        self._usuario = {}
        self._activa = False
        self.cerrar_db()

    @property
    def sesion_activa(self) -> bool:
        """Verifica si hay una sesión activa"""
        return self._activa and bool(self._usuario)

    # ==================== ACCESO A DATOS DEL USUARIO ====================

    @property
    def empleado_id(self) -> Optional[int]:
        """ID del empleado actual"""
        return self._usuario.get('id')

    @property
    def nombre(self) -> str:
        """Nombre del empleado actual"""
        return self._usuario.get('nombre', '')

    @property
    def apellido(self) -> str:
        """Apellido del empleado actual"""
        return self._usuario.get('apellido', '')

    @property
    def nombre_completo(self) -> str:
        """Nombre completo del empleado actual"""
        return self._usuario.get('nombre_completo', '')

    @property
    def puesto(self) -> str:
        """Puesto del empleado actual"""
        return self._usuario.get('puesto', '')

    @property
    def privilegio(self) -> str:
        """Nivel de privilegio del empleado actual"""
        return self._usuario.get('privilegio', '')

    def tiene_privilegio_admin(self) -> bool:
        """Verifica si el usuario tiene privilegios de administrador"""
        return self.privilegio == "Administrador"

    # ==================== MÉTODOS DE UTILIDAD ====================

    def obtener_info_usuario(self) -> Dict[str, Any]:
        """Obtiene toda la información del usuario actual"""
        return self._usuario.copy()

    def __repr__(self) -> str:
        if self.sesion_activa:
            return f"<SessionManager: {self.nombre_completo} ({self.puesto})>"
        return "<SessionManager: Sin sesión activa>"


# ==================== FUNCIONES DE ACCESO RÁPIDO ====================

def obtener_sesion() -> SessionManager:
    """
    Obtiene la instancia única del gestor de sesión

    Uso:
        from core.session import obtener_sesion
        session = obtener_sesion()
        db = session.db
        nombre = session.nombre
    """
    return SessionManager()


def obtener_db() -> Optional[DatabaseManager]:
    """
    Acceso rápido a la base de datos

    Uso:
        from core.session import obtener_db
        db = obtener_db()
        if db:
            habitaciones = db.obtener_habitaciones()
    """
    return SessionManager().db


def obtener_usuario() -> Dict[str, Any]:
    """
    Acceso rápido a la info del usuario

    Uso:
        from core.session import obtener_usuario
        usuario = obtener_usuario()
        print(f"Hola {usuario['nombre']}")
    """
    return SessionManager().obtener_info_usuario()