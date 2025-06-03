import psycopg2

# Datos de conexión
host = "localhost"
port = "5432"
dbname = "transporte_escolar"
user = "postgres"
password = "Simon"

# Instrucciones SQL para crear tablas
crear_tablas_sql = """
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS conductores (
    id_conductor SERIAL PRIMARY KEY,
    id_usuario INT UNIQUE NOT NULL REFERENCES usuarios(id_usuario),
    patente TEXT,
    modelo_vehiculo TEXT,
    codigo_vinculacion TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS apoderados (
    id_apoderado SERIAL PRIMARY KEY,
    id_usuario INT UNIQUE NOT NULL REFERENCES usuarios(id_usuario),
    direccion TEXT
);

CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    edad INT,
    direccion TEXT,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    id_apoderado INT NOT NULL REFERENCES apoderados(id_apoderado)
);

CREATE TABLE IF NOT EXISTS acompanantes (
    id_acompanante SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS rutas (
    id_ruta SERIAL PRIMARY KEY,
    id_conductor INT NOT NULL REFERENCES conductores(id_conductor),
    id_acompanante INT REFERENCES acompanantes(id_acompanante),
    fecha DATE NOT NULL,
    hora_inicio TIME,
    estado TEXT DEFAULT 'activa'
);

CREATE TABLE IF NOT EXISTS paradas (
    id_parada SERIAL PRIMARY KEY,
    id_estudiante INT NOT NULL REFERENCES estudiantes(id_estudiante),
    id_ruta INT NOT NULL REFERENCES rutas(id_ruta),
    orden INT NOT NULL,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    recogido BOOLEAN DEFAULT FALSE,
    entregado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS asistencias (
    id_asistencia SERIAL PRIMARY KEY,
    id_estudiante INT NOT NULL REFERENCES estudiantes(id_estudiante),
    fecha DATE NOT NULL,
    asistencia BOOLEAN DEFAULT TRUE,
    registrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificacion SERIAL PRIMARY KEY,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_envio TEXT,
    id_usuario INT NOT NULL REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS vinculos_apoderado_conductor (
    id_vinculo SERIAL PRIMARY KEY,
    id_apoderado INT NOT NULL REFERENCES apoderados(id_apoderado),
    id_conductor INT NOT NULL REFERENCES conductores(id_conductor),
    fecha_vinculacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Conexión y ejecución
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    cursor.execute(crear_tablas_sql)
    conn.commit()
    print("Tablas creadas exitosamente en PostgreSQL.")
except Exception as e:
    print("Error al crear tablas:", e)
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
