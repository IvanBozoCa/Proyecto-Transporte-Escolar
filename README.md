Endpoints esenciales (mínimo viable)

Prefijo base (si aplica): /api. Requieren Bearer JWT salvo login.

Auth

POST /auth/login — obtiene access_token y refresh_token.

POST /auth/refresh — renueva access_token.

Usuarios / Roles (admin)

GET /usuarios — listado (filtros/paginación opcional).

POST /usuarios — crear usuario (tipo_usuario: administrador/conductor/apoderado).

GET /conductores · GET /apoderados · GET /estudiantes

POST /estudiantes — registra estudiante (incluye direcciones/coordenadas).

Rutas fijas (admin)

POST /ruta-fija — crea ida (puede incluir parada final colegio) o vuelta (invierte ida y toma último como destino final).

PUT /ruta-fija/{id} — edita; en vuelta detecta parada final automáticamente.

GET /ruta-fija · GET /ruta-fija/{id} — consulta definición con paradas.

Asistencia (apoderado)

POST /asistencia — marca (in)asistencia del día. Si no se marca, se considera presente por defecto (configurable).

Ruta del Día (conductor)

GET /mis-estudiantes-hoy — estudiantes del conductor con estado del día.

POST /generar-ruta-dia/{id_ruta_fija} — crea la ruta del día (solo asistentes + copia parada final).

GET /ruta/activa — devuelve la ruta en curso (para apoderado incluye es_hijo y tipo ida/vuelta).

PUT /ruta/finalizar — cierra ruta (manual o automática si todos entregados).

Paradas (conductor)

PUT /parada/{id_parada}/recoger — marca recogido y retorna ruta actualizada.

PUT /parada/{id_parada}/entregar — marca entregado y retorna ruta actualizada.

En ambas se dispara notificación al apoderado correspondiente.

Ubicación y notificaciones

PUT /conductor/ubicacion — actualiza geoloc del conductor.

POST /firebase/token — registra/actualiza token FCM del usuario autenticado.

Flujos clave

Admin crea usuarios y rutas fijas (ida/vuelta con orden y destino final).

Apoderado marca asistencia (o queda presente por defecto).

Conductor genera la Ruta del Día y ejecuta recogido/entregado (ruta activa y notificaciones se actualizan).

Se finaliza la ruta (manual/auto).
