import psycopg2
from faker import Faker
import random

# Conexión a la base de datos
host = "localhost"
port = "5432"
dbname = "transporte_escolar"
user = "postgres"
password = "Simon"

# Instancia de Faker para generar datos falsos
faker = Faker()

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # Insertar 5 usuarios (administradores, conductores y apoderados)
    for _ in range(5):
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, contrasena, tipo_usuario, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            faker.name(),
            faker.email(),
            '1234',  # contraseña dummy
            random.choice(['administrador', 'conductor', 'apoderado']),
            faker.phone_number()
        ))
    
    conn.commit()
    print("5 usuarios insertados.")

    # Obtener IDs de usuarios tipo conductor
    cursor.execute("SELECT id_usuario FROM usuarios WHERE tipo_usuario = 'conductor'")
    conductores_ids = [row[0] for row in cursor.fetchall()]

    # Insertar 5 conductores
    for id_usuario in conductores_ids:
        cursor.execute("""
            INSERT INTO conductores (id_usuario, patente, modelo_vehiculo, codigo_vinculacion)
            VALUES (%s, %s, %s, %s)
        """, (
            id_usuario,
            faker.license_plate(),
            faker.word() + " Modelo",
            faker.uuid4()[:8]  # Código corto
        ))
    
    conn.commit()
    print("5 conductores insertados.")

    # Obtener IDs de usuarios tipo apoderado
    cursor.execute("SELECT id_usuario FROM usuarios WHERE tipo_usuario = 'apoderado'")
    apoderados_ids = [row[0] for row in cursor.fetchall()]

    # Insertar 5 apoderados
    for id_usuario in apoderados_ids:
        cursor.execute("""
            INSERT INTO apoderados (id_usuario, direccion)
            VALUES (%s, %s)
        """, (
            id_usuario,
            faker.address()
        ))
    
    conn.commit()
    print("5 apoderados insertados.")

    # Obtener IDs de apoderados para insertar estudiantes
    cursor.execute("SELECT id_apoderado FROM apoderados")
    apoderado_ids_final = [row[0] for row in cursor.fetchall()]

    # Insertar 5 estudiantes (1 por apoderado para comenzar)
    for id_apoderado in apoderado_ids_final:
        cursor.execute("""
            INSERT INTO estudiantes (nombre, edad, direccion, latitud, longitud, id_apoderado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            faker.name(),
            random.randint(4, 12),
            faker.address(),
            faker.latitude(),
            faker.longitude(),
            id_apoderado
        ))
    
    conn.commit()
    print("5 estudiantes insertados.")

    # Insertar 5 acompañantes
    for _ in range(5):
        cursor.execute("""
            INSERT INTO acompanantes (nombre, telefono)
            VALUES (%s, %s)
        """, (
            faker.name(),
            faker.phone_number()
        ))
    
    conn.commit()
    print("5 acompanantes insertados.")

except Exception as e:
    print("Error:", e)
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
