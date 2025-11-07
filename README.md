Flujo clave

1) Administrador crea usuarios y define Rutas Fijas (ida/vuelta con orden y destino final).
2) Apoderado marca asistencia del día (si no, queda presente por defecto según configuración).
3) Conductor genera la Ruta del Día desde una Ruta Fija → se crean paradas (solo asistentes activos) y se copia el destino final.
4) Durante el recorrido, el conductor marca RECoger / ENTregar:
   - La API devuelve la Ruta Activa actualizada.
   - Se notifica al apoderado del estudiante correspondiente.
5) Consultas en vivo:
   - Conductor: GET /ruta/activa (todas las paradas).
   - Apoderado: GET /ruta/activa (solo paradas de sus hijos, con es_hijo y tipo ida/vuelta).
6) Finalización: PUT /ruta/finalizar (o automática cuando todos están entregados).
7) Opcional: el conductor actualiza su ubicación periódicamente con PUT /conductor/ubicacion.
# Endpoints esenciales
# Requieren Bearer JWT, salvo /auth/login y /auth/refresh

# Auth
POST   /auth/login                # devuelve access_token y refresh_token
POST   /auth/refresh              # renueva access_token

# Usuarios / Roles (solo administrador)
GET    /usuarios                  # lista usuarios (filtros/paginación opcional)
POST   /usuarios                  # crea usuario (administrador | conductor | apoderado)
GET    /conductores               # lista conductores
GET    /apoderados                # lista apoderados
GET    /estudiantes               # lista estudiantes
POST   /estudiantes               # crea estudiante (direcciones/coordenadas)

# Rutas fijas (solo administrador)
POST   /ruta-fija                 # crea ida (puede incluir parada final colegio) o vuelta (invierte ida y último = destino final)
PUT    /ruta-fija/{id}            # edita ruta fija; en “vuelta” detecta parada final automáticamente
GET    /ruta-fija                 # lista/filtra rutas fijas (p.ej. por conductor_id, tipo)
GET    /ruta-fija/{id}            # detalle con paradas y destino final

# Asistencia (apoderado)
POST   /asistencia                # marca (in)asistencia del día (por defecto: presente, configurable)

# Ruta del Día (conductor)
GET    /mis-estudiantes-hoy       # alumnos del conductor con estado (asiste/recogido/entregado/orden)
POST   /generar-ruta-dia/{id_ruta_fija}  # genera Ruta del Día (solo asistentes activos + copia parada final)
GET    /ruta/activa               # ruta en curso; para apoderado incluye es_hijo y tipo (ida/vuelta)
PUT    /ruta/finalizar            # cierra ruta (manual o automático si todos entregados)

# Paradas (conductor)
PUT    /parada/{id_parada}/recoger  # marca recogido y retorna ruta actualizada (dispara notificación)
PUT    /parada/{id_parada}/entregar # marca entregado y retorna ruta actualizada (dispara notificación)

# Ubicación y notificaciones
PUT    /conductor/ubicacion       # actualiza geolocalización del conductor
POST   /firebase/token            # registra/actualiza token FCM del usuario autenticado

