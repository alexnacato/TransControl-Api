# Metodología de pruebas automatizadas

**Parcial 1 · Actividad 2 · TransControl API**  
**Borrador para convertir en documento LaTeX de 4 a 6 páginas**  
**Fecha de preparación:** 21 de octubre de 2026

> Este documento distingue evidencia observada de trabajo pendiente. Los ejemplos de pruebas y del ejecutor son una propuesta para copiar al repositorio y validar. No se ejecutaron en esta preparación pytest, Bandit, pip-audit ni pruebas HTTP; por tanto, no se presentan cifras ni resultados como si ya se hubieran obtenido.

## 1. Objetivo y aplicación seleccionada

El objetivo es establecer un ciclo repetible para identificar, confirmar, corregir y volver a comprobar fallas de seguridad en TransControl API. La aplicación se mantiene como caso de trabajo para los tres parciales. Las pruebas deben ejecutarse únicamente en el laboratorio autorizado, contra datos sintéticos y una base local desechable.

La API está construida con FastAPI, SQLAlchemy y PostgreSQL. La configuración de conexión se centraliza en `database.py` a través de `DATABASE_URL`; el arranque de `main.py` crea tablas e intenta crear cuentas de demostración. El README documenta el inicio local con `python -m uvicorn main:app --reload`. La versión del intérprete consultada en esta sesión fue **Python 3.13.16**. La documentación del proyecto declara compatibilidad con Python 3.10 o superior, mientras que `requirements.txt` fija versiones de varias dependencias de aplicación.

En el código revisado no se encontró un directorio ni archivos de pruebas existentes. `pytest`, `httpx`, Bandit y pip-audit no aparecen en `requirements.txt` y no están instalados en el `.venv` consultado. Ese entorno sí reportó Python 3.13.16, FastAPI 0.115.6 y SQLAlchemy 2.0.36. Pylance tenía seleccionado otro intérprete (Python 3.15), que no resolvía las dependencias de la aplicación; por tanto, se debe seleccionar explícitamente `.venv` y confirmar las versiones antes de ejecutar.

El archivo `.env` local no debe copiarse al informe ni a evidencias: puede contener secretos o una URL de base de datos. No se inspeccionó su contenido ni se usó la base de datos configurada para preparar este borrador.

## 2. Comparación y selección de técnicas

| Técnica | Qué comprueba | Herramienta seleccionada | Alcance y limitación |
| --- | --- | --- | --- |
| SAST (análisis estático) | Patrones inseguros en el código sin ejecutar la aplicación. | **Bandit** | Compatible con el código Python. Cada alerta es candidata; se revisa el contexto y se registra como confirmada, falso positivo o pendiente. |
| SCA (análisis de dependencias) | Versiones declaradas de paquetes y avisos de vulnerabilidad conocidos. | **pip-audit** | Audita `requirements.txt`; requiere acceso a fuentes de avisos durante la ejecución. No detecta fallas lógicas propias de la API. |
| DAST (pruebas dinámicas) | Comportamiento de la aplicación al procesar solicitudes. | **pytest + FastAPI TestClient** | Ejercita rutas y validaciones localmente. Es una prueba dinámica a nivel de aplicación, no evalúa proxy, TLS, red ni despliegue productivo como lo haría un escaneo externo. |
| Autorización | Acceso permitido o denegado según identidad, rol y propiedad del objeto. | **pytest + TestClient** | Comprueba explícitamente usuario sin token, rol y acceso a recursos propios/ajenos. No se considera cubierta solo por tener autenticación JWT. |

La selección permite una ejecución económica y repetible sin desplegar la API ni enviar tráfico a terceros. No se propone escanear producción ni utilizar datos reales. Para ampliar DAST en otra etapa se podría evaluar OWASP ZAP contra una instancia local aislada, pero no es necesario para el primer ciclo y no se afirma que se haya utilizado.

## 3. Alcance, preparación y casos de prueba

### Alcance incluido

- Registro y validación de usuarios en `/api/auth/registro`.
- Autenticación requerida por `/api/auth/me`.
- Autorización por usuario sobre el detalle de un viaje en `/api/viajes/{viaje_id}`.
- Escaneo estático de los módulos Python de la API.
- Revisión de vulnerabilidades conocidas en las dependencias declaradas.

### Fuera de alcance

- Cualquier instancia productiva, sistema ajeno o base de datos cuya autorización no esté confirmada.
- Correo SMTP real, subida de documentos reales y pruebas de carga.
- Afirmaciones sobre la exposición efectiva de una configuración de producción.
- El comportamiento de infraestructura, navegador, proxy y red externa.

### Preparación segura

1. Usar el repositorio y una rama de trabajo del curso; registrar rama y commit con `git branch --show-current` y `git rev-parse HEAD`.
2. Seleccionar Python 3.13.16 en `.venv` (o registrar el intérprete autorizado que se utilice) y registrar versiones de dependencias y herramientas.
3. Instalar las herramientas de desarrollo en ese entorno. No actualizar dependencias de producción silenciosamente como parte de la preparación.
4. Las pruebas propuestas fijan `DATABASE_URL` a un archivo SQLite temporal **antes de importar `main`**. El `TestClient` ejecuta el evento de arranque, por lo que esta precaución evita que las pruebas usen la base configurada en `.env`.
5. Utilizar identificadores, correos y viajes sintéticos. El archivo de base temporal se elimina al terminar el proceso pytest.
6. Guardar salida y códigos de retorno en `evidence/before/` y `evidence/after/`; nunca guardar `.env`, contraseñas reales, tokens válidos ni información personal.

### Casos mínimos

Los dos primeros hallazgos de la tabla son **candidatos observados en revisión estática previa**, no resultados de pruebas dinámicas. La revisión previa está en `analisis-amenazas-parcial-1.md`. La prueba debe confirmar si el comportamiento se reproduce en el entorno aislado.

| ID | Caso | Entrada / identidad sintética | Resultado seguro esperado |
| --- | --- | --- | --- |
| T1 | Acceso sin autenticación | `GET /api/auth/me`, sin token | `401 Unauthorized`. |
| T2 | Token inválido | `GET /api/auth/me`, token aleatorio inválido | `401 Unauthorized`. |
| T3 | Entrada inválida de registro | Cédula con formato incorrecto en `/api/auth/registro` | `422 Unprocessable Entity`; no se crea usuario. |
| T4 | Escalamiento de rol al registrarse | Registro público solicitando `GERENTE` | Se rechaza, o solo se crea el rol público permitido; nunca se crea un gerente por registro público. |
| T5 | Acceso al objeto propio | Transportista A consulta un viaje sintético asignado a A | `200 OK`. |
| T6 | Acceso cruzado entre usuarios | Transportista A consulta un viaje sintético asignado a B | `403 Forbidden` o `404 Not Found`, según la política adoptada; no se entrega el viaje. |

Los casos T4 y T6 deben fallar en la versión vulnerable y pasar tras la corrección. Las pruebas T1–T3 y T5 comprueban controles que deben mantenerse. Los códigos de estado aceptables para T4/T6 se deben fijar según la política elegida antes de comparar los resultados; no se debe cambiar el criterio entre ejecuciones para ocultar una regresión.

## 4. Hallazgos candidatos y correcciones previstas

La revisión del código encontró dos comportamientos que justifican las pruebas T4 y T6:

1. **Registro con rol privilegiado.** `UsuarioCreate` declara `rol` como texto y el endpoint de registro copia el valor recibido al nuevo usuario. El endpoint de registro no exige autenticación. La revisión de amenazas anterior ubica la evidencia en `schemas/auth_schemas.py` y `routers/auth.py`. La corrección prevista es que el registro público asigne siempre el rol público permitido (por ejemplo, `TRANSPORTISTA`) o rechace explícitamente cualquier otro rol; la asignación de roles privilegiados debe quedar en una operación administrativa autenticada y autorizada.
2. **Falta de autorización por objeto en viajes.** `GET /api/viajes/{viaje_id}` exige un usuario autenticado y busca el viaje por ID, pero en la implementación revisada no comprueba que el transportista sea propietario/asignado ni una autorización administrativa equivalente. La lista de viajes sí contiene un filtro especial para transportistas, pero eso no sustituye el control del endpoint de detalle. La corrección prevista es comprobar rol y pertenencia antes de devolver el objeto, conservando el acceso de los roles que legítimamente lo necesitan.

Estas observaciones se deben registrar como **confirmadas por inspección estática** hasta que T4 y T6 demuestren el comportamiento en pruebas. La alerta de una herramienta automática no basta para declararlas vulnerabilidades confirmadas.

## 5. Ejecución, clasificación, corrección y cierre

1. **Línea base:** ejecutar las pruebas y análisis en el commit registrado antes de corregir. Conservar cada salida completa y su código de retorno. Una prueba de regresión de seguridad que falle en la línea base es evidencia útil del defecto, no un motivo para ocultar o eliminar la prueba.
2. **Clasificación:** deduplicar hallazgos por causa raíz, ruta afectada y evidencia. Registrar identificador, severidad, archivo/símbolo, evidencia, estado, decisión y referencia a la prueba. Distinguir `confirmado`, `falso positivo` y `pendiente`. Para falsos positivos, documentar el motivo y la aprobación; no añadir exclusiones silenciosas.
3. **Confirmación manual:** contrastar el comportamiento HTTP con el código, revisar si se creó o filtró un registro sintético y verificar que la prueba usó el intérprete/base aislados. No inferir impacto de producción a partir de la base local.
4. **Corrección:** implementar cambios pequeños para T4 y T6; mantener las pruebas originales como regresión. Documentar archivos y commit de corrección.
5. **Repetición:** volver a ejecutar **el mismo script, los mismos casos, los mismos umbrales, dependencias y configuración**. Registrar commit y versiones nuevos. No modificar una prueba para hacerla pasar sin justificar el cambio y mostrar ambos criterios.
6. **Cierre:** comparar salidas antes/después; confirmar que T4 y T6 pasan y T1–T3/T5 no retroceden; revisar manualmente nuevos hallazgos de Bandit y pip-audit; adjuntar evidencia redactada de secretos y datos personales.

### Criterio de fallo del pipeline

El script devuelve código distinto de cero si cualquiera de las herramientas falla, detecta hallazgos según su comportamiento/configuración predeterminada o no puede ejecutarse. No se deben añadir umbrales ni exclusiones entre la ejecución inicial y la final. Durante la línea base se esperan fallos T4/T6; se conservan como resultado inicial y se explica el estado. Para el cierre, las regresiones deben pasar.

Una alerta no se exceptúa por ser molesta. La excepción requiere ID del hallazgo, justificación técnica, alcance, riesgo residual, responsable, aprobación docente/equipo y fecha de expiración o revisión. Si pip-audit no puede consultar avisos por falta de red, registrar `bloqueado por entorno`, no `sin vulnerabilidades`. Los archivos de evidencia se conservan con fecha, commit y versiones, idealmente junto al repositorio académico sin incluir secretos.

## 6. Registro de resultados (completar después de ejecutar)

No rellenar esta tabla por estimación. Copiar los códigos de retorno y resultados de las ejecuciones reales. La ejecución “antes” y “después” deben corresponder a commits distintos identificados.

| Medición | Antes de corregir | Después de corregir |
| --- | --- | --- |
| Fecha/hora y etiqueta de ejecución | `[completar]` | `[completar]` |
| Rama y commit | `[completar]` | `[completar]` |
| Python, pytest, FastAPI, Bandit y pip-audit | `[versiones observadas]` | `[versiones observadas]` |
| T1–T6 | `[pasa/falla por ID; no inventar]` | `[pasa/falla por ID; no inventar]` |
| Bandit: alertas por severidad y estado de triage | `[resultado y archivo de evidencia]` | `[resultado y archivo de evidencia]` |
| pip-audit: dependencias vulnerables / error de consulta | `[resultado y archivo de evidencia]` | `[resultado y archivo de evidencia]` |
| Código de salida de cada herramienta / pipeline | `[completar]` | `[completar]` |
| Hallazgos confirmados, corregidos y excepciones | `[IDs]` | `[IDs]` |

## 7. Instrucciones reproducibles en Windows

Desde la raíz del repositorio, con el entorno `.venv` activado:

```powershell
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
git branch --show-current
git rev-parse HEAD
python -m pip install pytest httpx bandit pip-audit
python -m pip show fastapi sqlalchemy pydantic pytest httpx bandit pip-audit
python -m pip freeze > requirements-lab.lock
```

Registrar las versiones observadas en el informe. Para que una segunda persona obtenga un entorno reproducible, conservar `requirements-lab.lock` generado en el laboratorio autorizado y usarlo al repetir. No escribir versiones supuestas en el informe.

Crear los archivos indicados en el apéndice de código y luego ejecutar:

```powershell
$env:RUN_LABEL = "before"
.\scripts\run_security_checks.ps1
```

Después de aplicar y guardar las correcciones en un commit nuevo, repetir exactamente el mismo comando con `$env:RUN_LABEL = "after"`. El script guarda logs y JUnit en `evidence/<etiqueta>/`; conservar esa carpeta fuera del informe si contiene información que no deba compartirse. El runner no inicia Uvicorn: pytest usa `TestClient` y una base SQLite temporal. El comando normal para levantar la API, si se necesita una demostración local separada, es `python -m uvicorn main:app --reload`; no se debe usar contra una base de producción para este trabajo.

### Cómo preparar las 4–6 páginas en LaTeX

Usar las secciones 1–6 como cuerpo del informe. Dejar el código completo en archivos del repositorio y citar sus rutas en el texto; incluir solo fragmentos breves o mover el listado a un apéndice si el docente lo permite. Añadir portada, tabla de herramientas/versiones, matriz T1–T6, resultados antes/después y evidencias numeradas. Mantener explícita la diferencia entre análisis estático, prueba ejecutada y hallazgo confirmado. No contar esta plantilla como evidencia de ejecución.

## Apéndice A. Código propuesto para las pruebas

Crear `tests/conftest.py`. Su función es apuntar a una base temporal antes de importar la app; no reemplazar la URL de la base compartida en `.env` para otros usos.

```python
import os
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.TemporaryDirectory(prefix="transcontrol-tests-")
_TEST_DB_PATH = Path(_TEST_DB_DIR.name, "test.sqlite3")

# Debe establecerse antes de importar main, database o cualquier router.
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "solo-para-pruebas-locales-no-reutilizar"
os.environ["SMTP_USER"] = ""
os.environ["SMTP_PASS"] = ""
```

Crear `tests/test_security_regression.py`. Estas pruebas son un punto de partida basado en las rutas y modelos revisados; ejecutarlas primero en la base temporal y ajustar únicamente si un esquema real difiere, registrando cualquier cambio. Los dos tests de seguridad T4 y T6 se esperan rojos antes de corregir los hallazgos.

```python
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import tardío: conftest.py ya configuró DATABASE_URL.
    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    from database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _new_carrier_and_trip(db):
    from models.models import (
        EstadoViajeEnum,
        RolEnum,
        Transportista,
        Usuario,
        Viaje,
    )

    suffix = uuid4().hex
    user = Usuario(
        cedula=str(1_000_000_000 + uuid4().int % 8_999_999_999),
        nombres=f"Usuario de prueba {suffix[:8]}",
        correo=f"carrier-{suffix}@example.test",
        hashed_password="no-se-usa-en-estas-pruebas",
        rol=RolEnum.TRANSPORTISTA,
        activo=True,
    )
    db.add(user)
    db.flush()

    carrier = Transportista(usuario_id=user.id)
    db.add(carrier)
    db.flush()

    trip = Viaje(
        codigo=f"T-{suffix[:16]}",
        transportista_id=carrier.id,
        creado_por_id=user.id,
        tipo_mercancia="Carga sintética",
        peso_total_kg=1,
        origen="QUITO",
        destino="GUAYAQUIL",
        estado=EstadoViajeEnum.TRANSPORTISTA_ASIGNADO,
    )
    db.add(trip)
    db.commit()
    return user, trip


def _bearer_for(user):
    from core.security import create_access_token

    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401


def test_registration_rejects_invalid_input(client):
    response = client.post(
        "/api/auth/registro",
        json={
            "cedula": "no-es-cedula",
            "nombres": "Persona sintética",
            "correo": f"invalid-{uuid4().hex}@example.test",
            "password": "clave-sintetica",
        },
    )
    assert response.status_code == 422


def test_public_registration_cannot_create_gerente(client, db):
    from models.models import RolEnum, Usuario

    suffix = uuid4().hex
    email = f"role-test-{suffix}@example.test"
    response = client.post(
        "/api/auth/registro",
        json={
            "cedula": str(1_000_000_000 + uuid4().int % 8_999_999_999),
            "nombres": "Usuario sintético",
            "correo": email,
            "password": "clave-sintetica-segura",
            "rol": "GERENTE",
        },
    )

    persisted = db.query(Usuario).filter(Usuario.correo == email).one_or_none()
    assert persisted is None or persisted.rol != RolEnum.GERENTE
    if response.status_code == 201:
        assert response.json()["rol"] == "TRANSPORTISTA"
    else:
        assert response.status_code in {400, 403, 422}


def test_carrier_can_read_own_trip(client, db):
    user, trip = _new_carrier_and_trip(db)
    response = client.get(
        f"/api/viajes/{trip.id}",
        headers=_bearer_for(user),
    )
    assert response.status_code == 200


def test_carrier_cannot_read_another_carriers_trip(client, db):
    from models.models import RolEnum, Usuario

    owner, trip = _new_carrier_and_trip(db)
    suffix = uuid4().hex
    other = Usuario(
        cedula=str(1_000_000_000 + uuid4().int % 8_999_999_999),
        nombres=f"Otro usuario {suffix[:8]}",
        correo=f"other-{suffix}@example.test",
        hashed_password="no-se-usa-en-estas-pruebas",
        rol=RolEnum.TRANSPORTISTA,
        activo=True,
    )
    db.add(other)
    db.commit()
    assert owner.id != other.id

    response = client.get(
        f"/api/viajes/{trip.id}",
        headers=_bearer_for(other),
    )
    assert response.status_code in {403, 404}
```

## Apéndice B. Ejecutor único propuesto

Crear `scripts/run_security_checks.ps1`. Se detiene si no existe el intérprete indicado, pero continúa entre análisis para conservar todas las salidas. Cualquier código de retorno distinto de cero hace que el script finalice con error.

```powershell
$ErrorActionPreference = "Stop"

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "No existe $python. Selecciona o crea el entorno virtual del laboratorio."
}

$label = $env:RUN_LABEL
if ([string]::IsNullOrWhiteSpace($label)) {
    $label = Get-Date -Format "yyyyMMdd-HHmmss"
}
$evidenceDir = Join-Path "evidence" $label
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
$script:failed = $false

function Invoke-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $log = Join-Path $evidenceDir "$Name.log"
    "COMMAND: $python $($Arguments -join ' ')" | Set-Content $log
    & $python @Arguments 2>&1 | Tee-Object -FilePath $log -Append
    $code = $LASTEXITCODE
    "EXIT_CODE=$code" | Add-Content $log
    if ($code -ne 0) {
        $script:failed = $true
    }
}

"RUN_LABEL=$label" | Set-Content (Join-Path $evidenceDir "metadata.txt")
"DATE=$(Get-Date -Format o)" | Add-Content (Join-Path $evidenceDir "metadata.txt")
"PYTHON=$(& $python --version 2>&1)" | Add-Content (Join-Path $evidenceDir "metadata.txt")
"BRANCH=$(git branch --show-current)" | Add-Content (Join-Path $evidenceDir "metadata.txt")
"COMMIT=$(git rev-parse HEAD)" | Add-Content (Join-Path $evidenceDir "metadata.txt")
& $python -m pip freeze | Set-Content (Join-Path $evidenceDir "pip-freeze.txt")

Invoke-Check -Name "pytest" -Arguments @(
    "-m", "pytest", "-q",
    "--junitxml", (Join-Path $evidenceDir "pytest-junit.xml")
)
Invoke-Check -Name "bandit" -Arguments @(
    "-m", "bandit", "-r", "main.py", "core", "routers",
    "schemas", "models", "patterns", "utils", "database.py", "-f", "json"
)
Invoke-Check -Name "pip-audit" -Arguments @(
    "-m", "pip_audit", "-r", "requirements.txt", "--format", "json"
)

if ($script:failed) {
    Write-Error "Una o más verificaciones fallaron. Revisa $evidenceDir."
    exit 1
}

Write-Host "Todas las verificaciones terminaron correctamente. Evidencia: $evidenceDir"
exit 0
```

## Referencias de contexto en el repositorio

- `requirements.txt`: versiones fijadas de dependencias de aplicación.
- `README.md`: requisitos, configuración de base de datos y comando de inicio local.
- `database.py`: creación del motor desde `DATABASE_URL` y sesiones SQLAlchemy.
- `main.py`: registro de routers y evento de inicialización.
- `core/security.py`: JWT, usuario actual y verificación de roles.
- `routers/auth.py` y `schemas/auth_schemas.py`: registro y esquema de usuario.
- `routers/viajes.py`: consulta de lista y detalle de viajes.
- `models/models.py`: roles y relaciones de usuario, transportista y viaje.
- `analisis-amenazas-parcial-1.md`: análisis previo; sus observaciones sirven como candidatos a reproducir, no como resultados de este ciclo.
