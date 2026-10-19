# TransControl API

API REST para **TransControl**, un sistema de gestión de viajes y transportistas. Permite administrar usuarios, registrar y asignar viajes, revisar la documentación de transportistas y consultar información de monitoreo y ubicación GPS.

La API está construida con **FastAPI**, **SQLAlchemy** y **PostgreSQL**. Expone documentación interactiva con OpenAPI y admite ejecución local, en Docker y despliegue serverless en Vercel.

## Tabla de contenidos

- [Funcionalidades](#funcionalidades)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Ejecución local en Windows](#ejecución-local-en-windows)
- [Variables de entorno](#variables-de-entorno)
- [Documentación y comprobación](#documentación-y-comprobación)
- [Autenticación y usuarios iniciales](#autenticación-y-usuarios-iniciales)
- [Resumen de endpoints](#resumen-de-endpoints)
- [Base de datos y archivos](#base-de-datos-y-archivos)
- [Docker](#docker)
- [Despliegue en Vercel](#despliegue-en-vercel)
- [Notas para producción](#notas-para-producción)

## Funcionalidades

- Inicio de sesión con correo o cédula y autenticación mediante tokens JWT.
- Registro y gestión del perfil de usuario.
- Gestión de transportistas, vehículos y estados de activación.
- Carga, consulta, revisión y descarga de documentos PDF de transportistas.
- Creación, consulta, planificación, asignación, reprogramación y cancelación de viajes.
- Monitoreo de viajes, consulta de coordenadas GPS y registro de cambios de ruta.
- Registro de acciones relevantes en una pista de auditoría.
- Perfiles de acceso por rol: `GERENTE`, `SECRETARIA`, `COORDINADOR`, `TRANSPORTISTA` y `PRESIDENTE`.

## Tecnologías

| Área | Tecnología |
| --- | --- |
| API web | FastAPI 0.115 |
| Servidor ASGI | Uvicorn |
| Persistencia | PostgreSQL, SQLAlchemy 2 y Psycopg 3 |
| Validación y configuración | Pydantic 2 y pydantic-settings |
| Autenticación | JWT (python-jose) y contraseñas con bcrypt |
| Entorno | Python 3.10 o superior |
| Despliegue | Docker y configuración para Vercel |

Las dependencias y sus versiones están en [`requirements.txt`](./requirements.txt). El `Dockerfile` utiliza Python 3.10.

## Arquitectura

La aplicación está organizada por responsabilidades:

1. **Entrada y composición — `main.py`:** configura FastAPI, CORS, routers, la ruta raíz, el chequeo de salud y el evento de inicio.
2. **Rutas HTTP — `routers/`:** recibe las solicitudes, aplica dependencias de autenticación y roles, ejecuta la lógica de cada área y devuelve respuestas.
3. **Validación — `schemas/`:** define los modelos Pydantic para los datos de entrada y salida de la API.
4. **Persistencia — `database.py` y `models/`:** configura SQLAlchemy, las sesiones de base de datos y los modelos relacionales almacenados en PostgreSQL.
5. **Servicios transversales — `core/` y `utils/`:** centraliza configuración, seguridad, dependencias de autorización y registro de auditoría.
6. **Patrones de diseño — `patterns/`:** contiene componentes para adaptar ciudades a coordenadas, seleccionar estrategias GPS, notificar eventos de viajes y agregar información visual a respuestas de monitoreo.

### Flujo de una solicitud

```text
Cliente
  │ HTTP / JSON / multipart
  ▼
FastAPI (main.py)
  │
  ├── Router (routers/)
  ├── Autenticación y roles (core/security.py)
  ├── Validación (schemas/)
  ├── Lógica y patrones (patterns/)
  ├── Sesión SQLAlchemy (database.py)
  ▼
PostgreSQL (models/)
```

### Patrones incluidos

- **Adapter — `patterns/adapter/city_gps_adapter.py`:** traduce ciudades de Ecuador a coordenadas GPS para registrar y planificar viajes. El catálogo tiene una lista finita de ciudades y actualmente usa Quito como coordenada alternativa si no reconoce el nombre.
- **Strategy — `patterns/strategy/gps_tracking_strategy.py`:** permite obtener la ubicación desde coordenadas guardadas (`real`) o calcular una ubicación simulada entre origen y destino (`simulado`).
- **Observer — `patterns/observer/trip_observer.py`:** distribuye eventos de cambios de ruta a observadores de auditoría y notificaciones. Las notificaciones push/SMS son una simulación registrada en memoria.
- **Decorator — `patterns/decorator/viaje_visual_decorator.py`:** añade a los datos de monitoreo etiquetas y mensajes de riesgo basados en el retraso.

## Estructura del proyecto

```text
.
├── core/
│   ├── config.py                 # Configuración mediante variables de entorno
│   └── security.py               # Hash de contraseñas, JWT y autorización por rol
├── models/
│   └── models.py                 # Modelos y enums de SQLAlchemy
├── patterns/
│   ├── adapter/                  # Conversión de ciudad a coordenadas
│   ├── decorator/                # Enriquecimiento visual de viajes
│   ├── observer/                 # Auditoría y notificaciones de eventos
│   └── strategy/                 # Ubicación GPS real o simulada
├── routers/
│   ├── auth.py                   # Autenticación y perfil
│   ├── monitoreo.py              # Seguimiento y ubicación
│   ├── transportistas.py        # Transportistas y documentos
│   └── viajes.py                 # Ciclo de vida de viajes
├── schemas/                      # Esquemas Pydantic
├── uploads/                      # Directorio disponible para archivos estáticos
├── utils/
│   └── auditoria.py              # Registro de acciones en la base de datos
├── database.py                   # Motor, sesiones y creación de tablas
├── main.py                       # Aplicación FastAPI
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Imagen Docker
└── vercel.json                   # Configuración de rutas para Vercel
```

## Requisitos

- Python **3.10 o superior**.
- PostgreSQL en ejecución y una base de datos creada para la aplicación.
- Git, si se va a clonar el repositorio.

Para usar el ejemplo de comandos de abajo en Windows también se necesita PowerShell. No se incluye un archivo `docker-compose.yml`: PostgreSQL debe instalarse o iniciarse por separado.

## Ejecución local en Windows

### 1. Crear una base de datos PostgreSQL

Instala e inicia PostgreSQL. Luego, crea una base vacía desde `psql` (ajusta el usuario si no usas `postgres`):

```powershell
psql -U postgres -c "CREATE DATABASE transcontrol;"
```

Si la base de datos ya existe, no vuelvas a crearla. Asegúrate de tener a mano el usuario, la contraseña, el host y el puerto de PostgreSQL.

### 2. Crear y activar un entorno virtual

Desde la carpeta raíz del proyecto:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno, puedes invocar directamente los ejecutables de `.venv\Scripts` o ajustar la política de ejecución para tu usuario de acuerdo con las reglas de tu equipo.

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configurar el entorno

Crea un archivo `.env` en la raíz del proyecto. Sustituye el usuario, la contraseña y la clave secreta por valores propios:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/transcontrol
SECRET_KEY=REEMPLAZA_POR_UNA_CLAVE_ALEATORIA_LARGA
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=TransControl
DEBUG=true
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=2
SMTP_USER=
SMTP_PASS=
```

Puedes generar una clave aleatoria con Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

La configuración se carga desde `.env` mediante `core/config.py`. Para recuperación de contraseña por correo se necesitan configurar `SMTP_USER` y `SMTP_PASS` con las credenciales SMTP de la cuenta de envío.

### 5. Iniciar la API

```powershell
python -m uvicorn main:app --reload
```

Por defecto, Uvicorn escucha en `http://127.0.0.1:8000`. La opción `--reload` es para desarrollo local; no debe usarse como servidor de producción.

## Variables de entorno

| Variable | Propósito | Valor de desarrollo sugerido |
| --- | --- | --- |
| `DATABASE_URL` | Cadena de conexión de PostgreSQL. | `postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/transcontrol` |
| `SECRET_KEY` | Clave usada para firmar tokens JWT. | Clave aleatoria, larga y privada |
| `ALGORITHM` | Algoritmo de firma JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Vigencia del token de acceso en minutos. | `60` |
| `APP_NAME` | Nombre mostrado por la API. | `TransControl` |
| `DEBUG` | Indicador de depuración de la aplicación. | `true` en local |
| `UPLOAD_DIR` | Directorio usado para montar `/uploads`. | `uploads` |
| `MAX_FILE_SIZE_MB` | Límite de tamaño para documentos PDF. | `2` |
| `SMTP_USER` | Usuario de la cuenta SMTP. | Vacío si no se usa correo |
| `SMTP_PASS` | Contraseña de aplicación o credencial SMTP. | Vacío si no se usa correo |

No subas `.env` ni credenciales reales al repositorio.

## Documentación y comprobación

Con el servidor iniciado:

- Swagger UI: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- ReDoc: [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)
- Estado de la aplicación: [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/)
- Health check: [`http://127.0.0.1:8000/health`](http://127.0.0.1:8000/health)

Para endpoints protegidos, usa el botón **Authorize** de Swagger e introduce el token como `Bearer <token>`. El `tokenUrl` del esquema OAuth2 está configurado como `/api/auth/login`.

## Autenticación y usuarios iniciales

Al iniciar, la aplicación crea las tablas declaradas en los modelos si todavía no existen y prepara cuentas de prueba cuando no encuentra usuarios para esos roles. Las cuentas de demostración configuradas en `main.py` son:

| Rol | Usuario | Contraseña inicial |
| --- | --- | --- |
| Gerente | `admin@transcontrol.ec` | `Admin1234!` |
| Secretaria | `secretaria@transcontrol.ec` | `Admin1234!` |
| Coordinador | `coordinador@transcontrol.ec` | `Admin1234!` |
| Transportista | `transportista@transcontrol.ec` | `Admin1234!` |

Inicia sesión en `POST /api/auth/login` enviando `username` (correo o cédula) y `password`. La respuesta incluye `access_token`; úsalo en las solicitudes protegidas como `Authorization: Bearer <access_token>`.

**Estas cuentas y contraseñas son solo para desarrollo y demostración. Cámbialas o elimina la creación de usuarios de prueba antes de exponer la aplicación.**

## Resumen de endpoints

Todos los endpoints de negocio están bajo `/api`. Los endpoints protegidos requieren un JWT válido y algunos además restringen el acceso según el rol.

### Autenticación — `/api/auth`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/login` | Iniciar sesión con correo o cédula. |
| `POST` | `/registro` | Registrar una cuenta. |
| `POST` | `/recuperar-password` | Solicitar recuperación de contraseña; requiere SMTP para entregar el correo. |
| `GET` | `/me` | Consultar el perfil del usuario autenticado. |
| `PUT` | `/me` | Actualizar el perfil del usuario autenticado. |

### Transportistas — `/api/transportistas`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/` | Crear un transportista. |
| `GET` | `/` | Listar transportistas; acepta `solo_activos`. |
| `GET` | `/{transportista_id}` | Consultar un transportista. |
| `PUT` | `/{transportista_id}` | Editar datos del transportista. |
| `DELETE` | `/{transportista_id}` | Desactivar un transportista. |
| `PATCH` | `/{transportista_id}/activar` | Activar un transportista. |
| `DELETE` | `/{transportista_id}/permanente` | Eliminar permanentemente un transportista. |
| `POST` | `/{transportista_id}/documentos` | Subir un documento PDF. |
| `GET` | `/{transportista_id}/documentos` | Consultar documentos del transportista. |
| `PUT` | `/{transportista_id}/documentos/{doc_id}/revisar` | Aprobar o rechazar un documento. |
| `GET` | `/{transportista_id}/documentos/{doc_id}/descargar` | Descargar o visualizar el PDF (`?inline=true`). |

### Viajes — `/api/viajes`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/` | Crear un viaje. |
| `GET` | `/` | Consultar viajes; admite filtros de estado, transportista y fechas. |
| `GET` | `/{viaje_id}` | Consultar un viaje por identificador. |
| `PATCH` | `/{viaje_id}/asignar` | Asignar un transportista a un viaje. |
| `PATCH` | `/{viaje_id}/reprogramar` | Registrar retraso y reprogramar. |
| `PATCH` | `/{viaje_id}/cancelar` | Cancelar un viaje con una causa. |
| `PATCH` | `/{viaje_id}/planificar-ruta` | Actualizar origen, destino y ruta planificada. |
| `PATCH` | `/{viaje_id}` | Actualizar campos generales del viaje. |

### Monitoreo — `/api/monitoreo`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/viajes-en-ejecucion` | Listar viajes asignados o en ejecución. |
| `POST` | `/viajes/{viaje_id}/iniciar` | Iniciar un viaje asignado. |
| `POST` | `/viajes/{viaje_id}/completar` | Marcar un viaje en ejecución como completado. |
| `PATCH` | `/viajes/{viaje_id}/ruta` | Modificar la ruta de un viaje en ejecución. |
| `GET` | `/ubicacion/{viaje_id}` | Consultar ubicación GPS. Acepta `strategy_type=real` o `strategy_type=simulado`. |
| `GET` | `/notificaciones-log` | Consultar el log en memoria de notificaciones simuladas. |
| `GET` | `/auditoria` | Consultar registros de auditoría. |

La documentación OpenAPI de `/docs` es la referencia para ver los esquemas de petición, respuestas y códigos de estado de cada operación.

## Base de datos y archivos

Los modelos principales son:

- `usuarios`: identidad, rol, credenciales cifradas con hash y estado de la cuenta.
- `transportistas`: perfil de vehículo vinculado a un usuario.
- `documentos`: tipo, revisión y vencimiento de documentos del transportista.
- `viajes`: datos de carga, recorrido, estado, horarios y coordenadas GPS.
- `auditoria`: registro de acciones y eventos relevantes.

`database.py` crea el motor y las sesiones de SQLAlchemy. En el arranque, `main.py` llama a `Base.metadata.create_all`, que crea las tablas faltantes; no reemplaza una estrategia de migraciones para cambios de esquema en producción.

Los PDF cargados por la API se guardan como bytes en PostgreSQL, en la columna `documentos.contenido_pdf` (`BYTEA`), y no en el directorio `uploads`. El endpoint `/uploads` sirve archivos estáticos del directorio configurado; es independiente de la persistencia de documentos. En Vercel el sistema de archivos puede ser de solo lectura y ese montaje puede no estar disponible.

## Docker

La imagen instala las dependencias y arranca Uvicorn en el puerto `8000`. Construye la imagen desde la raíz del proyecto:

```powershell
docker build -t transcontrol-api .
```

Para ejecutar el contenedor, asegúrate de que `DATABASE_URL` apunte a una base PostgreSQL accesible desde el contenedor. Si PostgreSQL corre directamente en el equipo Windows, suele ser necesario usar `host.docker.internal` como host, en vez de `localhost`. Con el `.env` ya configurado:

```powershell
docker run --rm -p 8000:8000 --env-file .env transcontrol-api
```

La API quedará disponible en `http://localhost:8000`. El repositorio no define un contenedor PostgreSQL ni una red de Docker Compose.

## Despliegue en Vercel

`vercel.json` define `main.py` como función Python y envía las rutas a la aplicación. Antes de desplegar:

1. Configura en el proyecto de Vercel las variables de entorno requeridas, especialmente `DATABASE_URL` y `SECRET_KEY`.
2. Usa una base PostgreSQL externa accesible desde Vercel.
3. Configura SMTP si se necesita recuperación de contraseña.
4. Considera que los archivos del entorno serverless pueden ser de solo lectura y efímeros.

## Notas para producción

- Sustituye la clave JWT de desarrollo y protege todas las credenciales con variables de entorno.
- Cambia o desactiva las cuentas y contraseñas de prueba creadas al iniciar la aplicación.
- Restringe `allow_origins` de CORS a los dominios autorizados; actualmente la configuración permite cualquier origen.
- Usa un servidor ASGI de producción sin `--reload`.
- Gestiona los cambios de esquema con migraciones coordinadas; aunque Alembic está entre las dependencias, este repositorio no incluye una configuración ni revisiones de migración.
- Revisa el almacenamiento y los límites de PDF para el volumen de datos esperado, especialmente porque los documentos binarios se almacenan en PostgreSQL.
#   T r a n s C o n t r o l - A p i  
 #   T r a n s C o n t r o l - A p i  
 #   T r a n s C o n t r o l - A p i  
 "# TransControl-Api" 
"# TransControl-Api" 
