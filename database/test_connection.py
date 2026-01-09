# test_connection.py
from database.db_manager import DatabaseManager


def test_connection():
    try:
        print("Intentando conectar a Supabase...")
        db = DatabaseManager()
        print("✓ Conexión exitosa!")

        # Prueba simple
        empleados = db.obtener_empleados()
        print(f"✓ Se encontraron {len(empleados)} empleados")

        db.cerrar()
        print("✓ Test completado")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    test_connection()