# TransControl API

API REST para la gestión de viajes y transportistas. El sistema permite administrar usuarios y transportistas, organizar viajes, revisar documentos y consultar el monitoreo GPS.

Desarrollada con **FastAPI**, **SQLAlchemy** y **PostgreSQL**. Incluye documentación OpenAPI interactiva y opciones de ejecución local, con Docker y despliegue en Vercel.

> [!IMPORTANT]
> Las credenciales de demostración incluidas en este README son únicamente para desarrollo. No expongas la aplicación con esas credenciales ni con la clave secreta predeterminada.

<details>
<summary>Contenido</summary>

- [Funciones principales](#funciones-principales)
- [Tecnologías](#tecnologias)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación local en Windows](#instalacion-local-en-windows)
- [Variables de entorno](#variables-de-entorno)
- [Uso de la API](#uso-de-la-api)
- [Endpoints](#endpoints)
- [Datos y archivos](#datos-y-archivos)
- [Docker](#docker)
- [Despliegue en Vercel](#despliegue-en-vercel)
- [Recomendaciones de producción](#recomendaciones-de-produccion)

</details>

## Funciones principales

- Inicio de sesión con correo o cédula y autenticación JWT.
- Gestión de usuarios, transportistas y vehículos.
- Carga, revisión y descarga de documentos PDF.
- Creación, asignación, planificación, reprogramación y cancelación de viajes.
- Monitoreo de viajes y consulta de ubicación GPS real o simulada.
- Registro de acciones en la pista de auditoría.
- Control de acceso por rol: `GERENTE`, `SECRETARIA`, `COORDINADOR`, `TRANSPORTISTA` y `PRESIDENTE`.

<a id="tecnologias"></a>

## Tecnologías

| Componente | Tecnología |
| --- | --- |
| API | FastAPI |
| Servidor | Uvicorn |
| Base de datos | PostgreSQL |
| ORM y driver | SQLAlchemy 2 y Psycopg 3 |
| Validación y configuración | Pydantic 2 y pydantic-settings |
| Autenticación | JWT, python-jose y bcrypt |
| Ejecución | Python 3.10 o superior |
| Despliegue | Docker y Vercel |

Las dependencias y versiones se encuentran en [`requirements.txt`](./requirements.txt). La imagen Docker se basa en Python 3.10.

## Arquitectura

La aplicación se divide en capas con responsabilidades claras:

| Capa | Ubicación | Responsabilidad |
| --- | --- | --- |
| Aplicación | `main.py` | Configura FastAPI, CORS, routers, health check e inicialización. |
| API | `routers/` | Define rutas HTTP, autorización y operaciones de cada módulo. |
| Validación | `schemas/` | Define esquemas Pydantic de entrada y salida. |
| Persistencia | `database.py`, `models/` | Configura sesiones SQLAlchemy y modelos de PostgreSQL. |
| Servicios compartidos | `core/`, `utils/` | Configuración, seguridad, roles y auditoría. |
| Patrones | `patterns/` | Componentes reutilizables para GPS y eventos de viaje. |

### Flujo de una solicitud

```text
Cliente
  │
  ▼
FastAPI (main.py)
  │
  ├── Router y autorización (routers/, core/security.py)
  ├── Validación (schemas/)
  ├── Lógica de dominio y patrones (patterns/)
  └── Sesión de base de datos (database.py)
          │
          ▼
      PostgreSQL (models/)
```

### Patrones de diseño

- **Adapter** — `patterns/adapter/city_gps_adapter.py`: convierte ciudades conocidas de Ecuador a coordenadas. Si una ciudad no está en el catálogo, utiliza Quito como alternativa.
- **Strategy** — `patterns/strategy/gps_tracking_strategy.py`: permite consultar coordenadas guardadas (`real`) o calcular una ubicación simulada entre origen y destino (`simulado`).
- **Observer** — `patterns/observer/trip_observer.py`: distribuye eventos de cambios de ruta a los observadores de auditoría y notificación. Las notificaciones son simuladas y se mantienen en memoria.
- **Decorator** — `patterns/decorator/viaje_visual_decorator.py`: añade indicadores visuales de riesgo a las respuestas de monitoreo según el retraso del viaje.

## Estructura del proyecto

```text
.
├── core/
│   ├── config.py                 # Configuración desde variables de entorno
│   └── security.py               # Contraseñas, JWT y autorización por rol
├── models/
│   └── models.py                 # Modelos y enumeraciones SQLAlchemy
├── patterns/
│   ├── adapter/                  # Adaptación de ciudades a coordenadas GPS
│   ├── decorator/                # Datos visuales para el monitoreo
│   ├── observer/                 # Auditoría y notificaciones de eventos
│   └── strategy/                 # Estrategias de ubicación GPS
├── routers/
│   ├── auth.py                   # Autenticación y perfil
│   ├── monitoreo.py              # Seguimiento y monitoreo de viajes
│   ├── transportistas.py         # Transportistas y documentos
│   └── viajes.py                 # Gestión de viajes
├── schemas/                      # Esquemas de validación Pydantic
├── uploads/                      # Directorio para archivos estáticos
├── utils/
│   └── auditoria.py              # Registro de acciones
├── database.py                   # Motor y sesiones SQLAlchemy
├── main.py                       # Aplicación FastAPI
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Imagen Docker
└── vercel.json                   # Configuración de Vercel
```

## Requisitos

- Python 3.10 o superior.
- PostgreSQL instalado y en ejecución.
- PowerShell para seguir los comandos de instalación de Windows.

El repositorio no incluye `docker-compose.yml`; PostgreSQL debe ejecutarse por separado.

<a id="instalacion-local-en-windows"></a>

## Instalación local en Windows

Ejecuta los siguientes pasos desde la carpeta raíz del proyecto.

### 1. Crear la base de datos

Con PostgreSQL instalado y activo, crea una base de datos vacía:

```powershell
psql -U postgres -c "CREATE DATABASE transcontrol;"
```

Si la base de datos ya existe, omite este paso. Ten a mano las credenciales y el host de PostgreSQL.

### 2. Crear y activar el entorno virtual

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell impide activar el entorno, puedes ejecutar los programas directamente desde `.venv\Scripts\` o aplicar la política de ejecución permitida en tu equipo.

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Crear el archivo de entorno

Crea un archivo `.env` en la raíz del proyecto y configura la conexión a tu PostgreSQL:

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

Genera una clave aleatoria para `SECRET_KEY` con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

La recuperación de contraseña por correo requiere configurar `SMTP_USER` y `SMTP_PASS` con credenciales SMTP válidas.

### 5. Iniciar el servidor

```powershell
python -m uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. La opción `--reload` es para desarrollo local, no para producción.

## Variables de entorno

| Variable | Descripción | Ejemplo local |
| --- | --- | --- |
| `DATABASE_URL` | URL de conexión a PostgreSQL. | `postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/transcontrol` |
| `SECRET_KEY` | Clave para firmar tokens JWT. | Clave aleatoria, larga y privada |
| `ALGORITHM` | Algoritmo de firma JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Vigencia del token en minutos. | `60` |
| `APP_NAME` | Nombre de la aplicación. | `TransControl` |
| `DEBUG` | Indicador de depuración. | `true` |
| `UPLOAD_DIR` | Directorio montado como `/uploads`. | `uploads` |
| `MAX_FILE_SIZE_MB` | Límite de tamaño para documentos PDF. | `2` |
| `SMTP_USER` | Usuario de la cuenta SMTP. | Vacío si no se usa correo |
| `SMTP_PASS` | Contraseña SMTP o contraseña de aplicación. | Vacío si no se usa correo |

No subas `.env` ni credenciales reales al repositorio.

## Uso de la API

Con el servidor iniciado:

- **Swagger UI:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **ReDoc:** [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)
- **Estado de la aplicación:** [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/)
- **Health check:** [`http://127.0.0.1:8000/health`](http://127.0.0.1:8000/health)

### Autenticación

1. Envía `username` (correo o cédula) y `password` a `POST /api/auth/login`.
2. Copia el valor de `access_token` de la respuesta.
3. En Swagger, pulsa **Authorize** e introduce `Bearer <access_token>`.

La mayoría de las operaciones requiere un token válido; algunas también requieren un rol específico.

### Cuentas de demostración

Al iniciar, la aplicación crea las tablas que falten y prepara estas cuentas si sus roles aún no tienen usuario:

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Gerente | `admin@transcontrol.ec` | `Admin1234!` |
| Secretaria | `secretaria@transcontrol.ec` | `Admin1234!` |
| Coordinador | `coordinador@transcontrol.ec` | `Admin1234!` |
| Transportista | `transportista@transcontrol.ec` | `Admin1234!` |

> [!WARNING]
> Son credenciales públicas de prueba. Cámbialas o elimina la inicialización de usuarios de demostración antes de desplegar la aplicación.

## Endpoints

Los endpoints de negocio están agrupados bajo `/api`. Consulta `/docs` para ver los esquemas de petición y respuesta completos.

### Autenticación — `/api/auth`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/login` | Iniciar sesión con correo o cédula. |
| `POST` | `/registro` | Registrar una cuenta. |
| `POST` | `/recuperar-password` | Solicitar recuperación de contraseña; requiere SMTP para enviar correo. |
| `GET` | `/me` | Consultar el perfil autenticado. |
| `PUT` | `/me` | Actualizar el perfil autenticado. |

### Transportistas — `/api/transportistas`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/` | Crear un transportista. |
| `GET` | `/` | Listar transportistas; admite `solo_activos`. |
| `GET` | `/{transportista_id}` | Consultar un transportista. |
| `PUT` | `/{transportista_id}` | Editar un transportista. |
| `DELETE` | `/{transportista_id}` | Desactivar un transportista. |
| `PATCH` | `/{transportista_id}/activar` | Activar un transportista. |
| `DELETE` | `/{transportista_id}/permanente` | Eliminarlo permanentemente. |
| `POST` | `/{transportista_id}/documentos` | Subir un documento PDF. |
| `GET` | `/{transportista_id}/documentos` | Consultar sus documentos. |
| `PUT` | `/{transportista_id}/documentos/{doc_id}/revisar` | Aprobar o rechazar un documento. |
| `GET` | `/{transportista_id}/documentos/{doc_id}/descargar` | Descargar o visualizar el PDF con `?inline=true`. |

### Viajes — `/api/viajes`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/` | Crear un viaje. |
| `GET` | `/` | Listar viajes; admite filtros de estado, transportista y fechas. |
| `GET` | `/{viaje_id}` | Consultar un viaje. |
| `PATCH` | `/{viaje_id}/asignar` | Asignar un transportista. |
| `PATCH` | `/{viaje_id}/reprogramar` | Registrar un retraso y reprogramar. |
| `PATCH` | `/{viaje_id}/cancelar` | Cancelar un viaje con una causa. |
| `PATCH` | `/{viaje_id}/planificar-ruta` | Actualizar origen, destino y ruta. |
| `PATCH` | `/{viaje_id}` | Actualizar datos generales del viaje. |

### Monitoreo — `/api/monitoreo`

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/viajes-en-ejecucion` | Listar viajes asignados o en ejecución. |
| `POST` | `/viajes/{viaje_id}/iniciar` | Iniciar un viaje asignado. |
| `POST` | `/viajes/{viaje_id}/completar` | Completar un viaje en ejecución. |
| `PATCH` | `/viajes/{viaje_id}/ruta` | Modificar la ruta de un viaje en ejecución. |
| `GET` | `/ubicacion/{viaje_id}` | Consultar GPS; admite `strategy_type=real` o `strategy_type=simulado`. |
| `GET` | `/notificaciones-log` | Consultar notificaciones simuladas en memoria. |
| `GET` | `/auditoria` | Consultar registros de auditoría. |

## Datos y archivos

Los modelos principales representan usuarios, transportistas, documentos, viajes y auditoría. `database.py` configura el motor y las sesiones SQLAlchemy; al iniciar, `main.py` crea las tablas que todavía no existan. Esto no sustituye las migraciones de esquema en producción.

Los PDF cargados por la API se guardan como bytes en PostgreSQL, en `documentos.contenido_pdf` (`BYTEA`). No se guardan en `uploads`. El montaje `/uploads` sirve archivos estáticos del directorio configurado y es independiente del almacenamiento de documentos. En Vercel el sistema de archivos puede ser de solo lectura o efímero.

## Docker

Construye la imagen desde la raíz del repositorio:

```powershell
docker build -t transcontrol-api .
```

Ejecuta el contenedor con las variables definidas en `.env`:

```powershell
docker run --rm -p 8000:8000 --env-file .env transcontrol-api
```

`DATABASE_URL` debe apuntar a una base PostgreSQL accesible desde el contenedor. Si PostgreSQL corre en el equipo Windows, normalmente el host debe ser `host.docker.internal` en lugar de `localhost`. La API quedará en `http://localhost:8000`.

El repositorio no incluye una imagen de PostgreSQL ni una configuración de Docker Compose.

## Despliegue en Vercel

El archivo `vercel.json` configura `main.py` como función Python y dirige las rutas a la aplicación. Antes de desplegar:

1. Configura `DATABASE_URL`, `SECRET_KEY` y las demás variables en Vercel.
2. Usa una base PostgreSQL externa accesible desde el entorno serverless.
3. Configura SMTP si necesitas recuperación de contraseña.
4. Considera que los archivos locales pueden ser de solo lectura o efímeros.

<a id="recomendaciones-de-produccion"></a>

## Recomendaciones de producción

- Reemplaza la clave JWT de desarrollo y no publiques credenciales.
- Cambia o desactiva las cuentas de demostración.
- Restringe CORS a los dominios autorizados; actualmente permite cualquier origen.
- Ejecuta Uvicorn en modo de producción, sin `--reload`.
- Implementa y aplica migraciones al modificar el esquema. Alembic está en las dependencias, pero el repositorio no incluye revisiones ni configuración de migraciones.
- Evalúa el almacenamiento de PDFs en PostgreSQL según el volumen esperado de documentos.
