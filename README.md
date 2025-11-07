# Endpoints esenciales (prefijo /api si aplica)
# Requieren Bearer JWT, salvo /auth/login y /auth/refresh

# Auth
POST   /auth/login
POST   /auth/refresh

# Usuarios / Roles (solo administrador)
GET    /usuarios
POST   /usuarios
GET    /conductores
GET    /apoderados
GET    /estudiantes
POST   /estudiantes

# Rutas fijas (solo administrador)
POST   /ruta-fija
PUT    /ruta-fija/{id}
GET    /ruta-fija
GET    /ruta-fija/{id}

# Asistencia (apoderado)
POST   /asistencia

# Ruta del Día (conductor)
GET    /mis-estudiantes-hoy
POST   /generar-ruta-dia/{id_ruta_fija}
GET    /ruta/activa
PUT    /ruta/finalizar

# Paradas (conductor)
PUT    /parada/{id_parada}/recoger
PUT    /parada/{id_parada}/entregar

# Ubicación y notificaciones
PUT    /conductor/ubicacion
POST   /firebase/token

flowchart TD
  A[1) Admin crea usuarios y Rutas Fijas (ida/vuelta)] --> B[2) Apoderado marca asistencia (o presente por defecto)]
  B --> C[3) Conductor genera Ruta del Día desde Ruta Fija]
  C --> D[4) Conductor marca RECoger / ENTregar]
  D --> E[5) API actualiza Ruta Activa y notifica al apoderado]
  E --> F[6) Consultas en vivo: GET /ruta/activa (conductor/apoderado)]
  F --> G[7) Finalizar ruta: PUT /ruta/finalizar]
  G --> H[8) Opcional: PUT /conductor/ubicacion]

