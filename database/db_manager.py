# database/db_manager.py
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2 import errors
import bcrypt

load_dotenv()


class DatabaseManager:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=int(os.getenv("DB_PORT", 5432)),
                sslmode="require"
            )
            self.cursor = self.conn.cursor()
            print("✓ Conexión exitosa a Supabase PostgreSQL")
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            raise

    # ==================== UTILIDADES DE SEGURIDAD ====================

    @staticmethod
    def hashear_password(password):
        """Hashea una contraseña usando bcrypt"""
        if not password:
            return ''
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verificar_password(password, password_hash):
        """Verifica si una contraseña coincide con su hash"""
        if not password or not password_hash:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Error al verificar contraseña: {e}")
            return False

    # ==================== HABITACIONES ====================

    def obtener_habitaciones(self):
        self.cursor.execute("SELECT * FROM habitaciones")
        return self.cursor.fetchall()

    def agregar_habitacion(self, numero, tipo, precio, estado='disponible'):
        try:
            self.cursor.execute("""
                                INSERT INTO habitaciones (numero, tipo, precio, estado)
                                VALUES (%s, %s, %s, %s)
                                """, (numero, tipo, precio, estado))
            self.conn.commit()
            return True
        except errors.UniqueViolation:
            self.conn.rollback()
            return False

    def actualizar_habitacion(self, id, numero, tipo, precio, estado):
        self.cursor.execute("""
                            UPDATE habitaciones
                            SET numero=%s,
                                tipo=%s,
                                precio=%s,
                                estado=%s
                            WHERE id = %s
                            """, (numero, tipo, precio, estado, id))
        self.conn.commit()
        return True

    def eliminar_habitacion(self, id):
        self.cursor.execute("DELETE FROM habitaciones WHERE id=%s", (id,))
        self.conn.commit()

    def cambiar_estado_habitacion(self, id, nuevo_estado):
        self.cursor.execute("""
                            UPDATE habitaciones
                            SET estado=%s
                            WHERE id = %s
                            """, (nuevo_estado, id))
        self.conn.commit()

    # ==================== EMPLEADOS ====================

    def obtener_empleados(self):
        self.cursor.execute("SELECT * FROM empleados")
        return self.cursor.fetchall()

    def validar_login(self, usuario, password):
        """Valida login con contraseña hasheada"""
        self.cursor.execute("""
                            SELECT id, nombre, apellido, puesto, password
                            FROM empleados
                            WHERE usuario = %s
                            """, (usuario,))
        resultado = self.cursor.fetchone()

        if resultado and len(resultado) >= 5:
            password_hash = resultado[4]
            # Verificar contraseña hasheada
            if self.verificar_password(password, password_hash):
                return (resultado[0], resultado[1], resultado[2], resultado[3])

        return None

    def agregar_empleado(self, nombre, apellido, puesto, telefono='', usuario='', password='', privilegio=''):
        """Agrega un empleado con contraseña hasheada"""
        try:
            # Hashear contraseña antes de guardar
            password_hash = self.hashear_password(password) if password else ''

            self.cursor.execute("""
                                INSERT INTO empleados
                                    (nombre, apellido, puesto, telefono, usuario, password, privilegio)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (nombre, apellido, puesto, telefono, usuario, password_hash, privilegio))
            self.conn.commit()
            return True
        except errors.UniqueViolation:
            self.conn.rollback()
            return False

    def actualizar_empleado(self, id, nombre, apellido, puesto, telefono, privilegio):
        self.cursor.execute("""
                            UPDATE empleados
                            SET nombre=%s,
                                apellido=%s,
                                puesto=%s,
                                telefono=%s,
                                privilegio=%s
                            WHERE id = %s
                            """, (nombre, apellido, puesto, telefono, privilegio, id))
        self.conn.commit()
        return True

    def eliminar_empleado(self, id):
        self.cursor.execute("DELETE FROM empleados WHERE id=%s", (id,))
        self.conn.commit()

    # ==================== HUESPEDES ====================

    def obtener_huespedes(self):
        self.cursor.execute("SELECT * FROM huespedes")
        return self.cursor.fetchall()

    def buscar_huesped_por_telefono(self, telefono):
        """Busca un huésped por su número de teléfono"""
        self.cursor.execute("""
                            SELECT id, nombre, apellido, telefono, email, password
                            FROM huespedes
                            WHERE telefono = %s
                            """, (telefono,))
        return self.cursor.fetchone()

    def agregar_huesped(self, nombre, apellido, telefono, password='', email=''):
        """Agrega un huésped con contraseña hasheada"""
        try:
            # Hashear contraseña antes de guardar
            password_hash = self.hashear_password(password) if password else ''

            self.cursor.execute("""
                                INSERT INTO huespedes (nombre, apellido, telefono, password, email)
                                VALUES (%s, %s, %s, %s, %s) RETURNING id
                                """, (nombre, apellido, telefono, password_hash, email))
            self.conn.commit()
            return self.cursor.fetchone()
        except errors.UniqueViolation:
            self.conn.rollback()
            return None

    # ==================== RESERVAS ====================

    def obtener_reservas(self):
        self.cursor.execute("""
                            SELECT r.id,
                                   r.huesped_id,
                                   h.nombre || ' ' || h.apellido AS huesped_nombre,
                                   r.habitacion_id,
                                   hab.numero,
                                   hab.tipo,
                                   r.fecha_entrada,
                                   r.fecha_salida,
                                   r.estado,
                                   r.total
                            FROM reservaciones r
                                     JOIN huespedes h ON r.huesped_id = h.id
                                     JOIN habitaciones hab ON r.habitacion_id = hab.id
                            ORDER BY r.fecha_entrada DESC
                            """)
        return self.cursor.fetchall()

    def obtener_habitaciones_disponibles(self):
        """Obtiene las habitaciones disponibles para reservar"""
        self.cursor.execute("""
                            SELECT id, numero, tipo, precio
                            FROM habitaciones
                            WHERE estado = 'disponible'
                            ORDER BY numero
                            """)
        return self.cursor.fetchall()

    def agregar_reserva(self, huesped_id, habitacion_id, fecha_entrada, fecha_salida, total):
        try:
            self.cursor.execute("""
                                INSERT INTO reservaciones
                                    (huesped_id, habitacion_id, fecha_entrada, fecha_salida, total, estado)
                                VALUES (%s, %s, %s, %s, %s, 'activa')
                                """, (huesped_id, habitacion_id, fecha_entrada, fecha_salida, total))
            self.cambiar_estado_habitacion(habitacion_id, 'ocupada')
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error al agregar reserva: {e}")
            return False

    def finalizar_reserva(self, reserva_id):
        """Finaliza una reserva (check-out) y pone la habitación en limpieza"""
        try:
            # Obtener habitacion_id de la reserva
            self.cursor.execute("""
                                SELECT habitacion_id
                                FROM reservaciones
                                WHERE id = %s
                                """, (reserva_id,))
            resultado = self.cursor.fetchone()

            if resultado:
                habitacion_id = resultado[0]

                # Actualizar estado de la reserva
                self.cursor.execute("""
                                    UPDATE reservaciones
                                    SET estado = 'finalizada'
                                    WHERE id = %s
                                    """, (reserva_id,))

                # Cambiar habitación a limpieza
                self.cambiar_estado_habitacion(habitacion_id, 'limpieza')

                self.conn.commit()
                return True
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"Error al finalizar reserva: {e}")
            return False

    def cancelar_reserva(self, reserva_id):
        """Cancela una reserva y libera la habitación"""
        try:
            # Obtener habitacion_id de la reserva
            self.cursor.execute("""
                                SELECT habitacion_id
                                FROM reservaciones
                                WHERE id = %s
                                """, (reserva_id,))
            resultado = self.cursor.fetchone()

            if resultado:
                habitacion_id = resultado[0]

                # Actualizar estado de la reserva
                self.cursor.execute("""
                                    UPDATE reservaciones
                                    SET estado = 'cancelada'
                                    WHERE id = %s
                                    """, (reserva_id,))

                # Cambiar habitación a disponible
                self.cambiar_estado_habitacion(habitacion_id, 'disponible')

                self.conn.commit()
                return True
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"Error al cancelar reserva: {e}")
            return False

    # ==================== ESTADÍSTICAS ====================

    def obtener_estadisticas(self):
        """Obtiene estadísticas generales del hotel"""
        try:
            # Contar habitaciones por estado
            self.cursor.execute("""
                                SELECT estado, COUNT(*)
                                FROM habitaciones
                                GROUP BY estado
                                """)
            habitaciones_estado = dict(self.cursor.fetchall())

            # Contar empleados
            self.cursor.execute("SELECT COUNT(*) FROM empleados")
            total_empleados = self.cursor.fetchone()[0]

            return {
                'disponibles': habitaciones_estado.get('disponible', 0),
                'ocupadas': habitaciones_estado.get('ocupada', 0),
                'limpieza': habitaciones_estado.get('limpieza', 0),
                'mantenimiento': habitaciones_estado.get('mantenimiento', 0),
                'empleados': total_empleados
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {
                'disponibles': 0,
                'ocupadas': 0,
                'limpieza': 0,
                'mantenimiento': 0,
                'empleados': 0
            }

    def obtener_reporte_reservas(self, fecha_inicio, fecha_fin):
        """Obtiene el historial completo de reservas en un período"""
        try:
            self.cursor.execute("""
                                SELECT r.id,
                                       h.nombre || ' ' || h.apellido AS huesped,
                                       hab.numero,
                                       r.fecha_entrada,
                                       r.fecha_salida,
                                       r.total,
                                       r.estado
                                FROM reservaciones r
                                         JOIN huespedes h ON r.huesped_id = h.id
                                         JOIN habitaciones hab ON r.habitacion_id = hab.id
                                WHERE r.fecha_entrada >= %s
                                  AND r.fecha_entrada <= %s
                                ORDER BY r.fecha_entrada DESC
                                """, (fecha_inicio, fecha_fin))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener reporte de reservas: {e}")
            return []

    def obtener_reporte_habitaciones(self, fecha_inicio, fecha_fin):
        """Obtiene el historial de uso y limpieza de habitaciones"""
        try:
            self.cursor.execute("""
                                -- Eventos de check-in (ocupación)
                                SELECT hab.numero,
                                       hab.tipo,
                                       'Check-in / Ocupación'        as evento,
                                       r.fecha_entrada               as fecha,
                                       h.nombre || ' ' || h.apellido as huesped,
                                       'Entrada del huésped'         as detalles
                                FROM reservaciones r
                                         JOIN habitaciones hab ON r.habitacion_id = hab.id
                                         JOIN huespedes h ON r.huesped_id = h.id
                                WHERE r.fecha_entrada >= %s
                                  AND r.fecha_entrada <= %s

                                UNION ALL

                                -- Eventos de check-out (salida)
                                SELECT hab.numero,
                                       hab.tipo,
                                       'Check-out / Limpieza'                       as evento,
                                       r.fecha_salida                               as fecha,
                                       h.nombre || ' ' || h.apellido                as huesped,
                                       'Salida del huésped - Habitación a limpieza' as detalles
                                FROM reservaciones r
                                         JOIN habitaciones hab ON r.habitacion_id = hab.id
                                         JOIN huespedes h ON r.huesped_id = h.id
                                WHERE r.fecha_salida >= %s
                                  AND r.fecha_salida <= %s
                                  AND r.estado = 'finalizada'

                                ORDER BY fecha DESC, numero
                                """, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener reporte de habitaciones: {e}")
            return []

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Conexión cerrada")