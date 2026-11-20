# Agencia de Viajes Web

Aplicación web para la gestión de una agencia de viajes. Backend en **FastAPI** con **PostgreSQL**, vistas renderizadas con **Jinja2** y scripts de frontend escritos en **TypeScript** (compilados a JavaScript).

Rama de trabajo: `agencia-viajes-web`.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.14, FastAPI, Uvicorn |
| Base de datos | PostgreSQL 18 (Docker), `psycopg` 3 con `ConnectionPool` |
| Vistas | Jinja2 + CSS/JS estático |
| Frontend | TypeScript (`tsc`) → `static/js` |
| Sesiones | `SessionMiddleware` (cookie firmada, `itsdangerous`) |
| Contraseñas | `pwdlib` + bcrypt |
| PDF | `fpdf2` |
| Gestor de paquetes | [uv](https://docs.astral.sh/uv/) (Python) y npm (TypeScript) |

## Requisitos previos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (instalará Python 3.14 automáticamente según `.python-version`)
- [Node.js](https://nodejs.org/) y npm (solo para compilar TypeScript)
- [Docker](https://docs.docker.com/get-docker/) con Docker Compose (para PostgreSQL)

## Puesta en marcha

### 1. Clonar el repositorio

```bash
git clone -b agencia-viajes-web https://github.com/Katalax3/ProtoApp_AgenciaDeViajes.git
cd ProtoApp_AgenciaDeViajes
```

### 2. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env`:

```env
# Usuario de la aplicación (el que usa FastAPI)
DB_HOST=localhost
DB_NAME=agencia
DB_USER=agencia_app
DB_PASSWORD=una_contraseña
DB_PORT=5432

# Administrador de PostgreSQL (solo lo usa el contenedor al inicializar)
POSTGRES_USER=postgres_admin
POSTGRES_PASSWORD=otra_contraseña
```

Variables opcionales que lee `core/config.py` (tienen valor por defecto, pero **cámbialas fuera de desarrollo**):

```env
SECRET_KEY=cambia-esto          # firma de la cookie de sesión
SESSION_MAX_AGE=3600            # duración de la sesión en segundos
```

> `.env` está en `.gitignore`; no lo subas al repositorio.

### 3. Levantar la base de datos

```bash
docker compose up -d
```

En el **primer arranque** (volumen vacío) PostgreSQL ejecuta automáticamente lo que hay en `initdb/`:

1. `01-init-db-user.sh` crea el usuario de la aplicación (`DB_USER`) con permisos sobre `DB_NAME`.
2. `sql/02-create-tables.sql` crea todas las tablas como ese usuario.

> Los scripts de `initdb/` **solo corren si el volumen `postgres_data` está vacío**. Si cambias el esquema o las credenciales y quieres reiniciar desde cero:
>
> ```bash
> docker compose down -v   # ⚠️ borra todos los datos
> docker compose up -d
> ```

### 4. Instalar dependencias de Python

```bash
uv sync
```

### 5. Instalar y compilar TypeScript

```bash
npm install
npx tsc
```

Los archivos de `src/agencia_viajes_web/ts/` se compilan a `src/agencia_viajes_web/static/js/`. Los `.js` generados están versionados en el repo, así que este paso solo es obligatorio si modificas los `.ts`.

### 6. Ejecutar la aplicación

```bash
uv run fastapi dev src/agencia_viajes_web/main.py
```

- App: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

### 7. Crear el primer usuario

El esquema **no trae datos de ejemplo**, así que no existe ningún usuario inicial. Crea uno desde Swagger (`POST /usuario/`) o con `curl`:

```bash
curl -X POST http://127.0.0.1:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Admin",
    "paterno": "Prueba",
    "correo": "admin@example.com",
    "contrasena": "admin123",
    "tipo_usuario": "DBA"
  }'
```

Reglas del esquema para `tipo_usuario`:

- `DBA` y `Cliente`: `id_agencia` y `num_empleado` deben ir vacíos.
- `Empleado`: requiere `id_agencia` (debe existir una fila en `agencia`) y `num_empleado`.

Luego inicia sesión en `/` con ese correo y contraseña. Según el rol, se te redirige a su panel.

## Roles y rutas principales

| Rol | Panel | Qué hace |
|-----|-------|----------|
| `DBA` | `/dba/dashboard` | CRUD genérico de catálogos (`pais`, `parcialidad`, `banco`) vía `/dba/api/{tabla}` |
| `Empleado` | `/empleado/dashboard` | CRUD de viajes, consulta de ciudades y transportes, generación de PDF de un viaje (`/api/viajes/{id}/pdf`) |
| `Cliente` | — | Aún sin panel propio |

Otros routers: `/login` (login/logout), `/usuario`, `/viaje`, `/parcialidad`.

El acceso por rol se controla con la dependencia `require_role("<Rol>")` en `core/dependencies.py`. Si la sesión no es válida se redirige a `/`.

## Estructura del proyecto

```
.
├── docker-compose.yml          # PostgreSQL 18
├── initdb/
│   ├── 01-init-db-user.sh      # Crea el usuario de la app
│   └── sql/02-create-tables.sql# Esquema de la base de datos
├── pyproject.toml              # Dependencias Python (uv)
├── package.json / tsconfig.json# TypeScript
├── .env.example
└── src/agencia_viajes_web/
    ├── main.py                 # App FastAPI, middleware y archivos estáticos
    ├── core/
    │   ├── config.py           # Settings (pydantic-settings, lee .env)
    │   ├── database.py         # Construye la URL de conexión
    │   ├── conexion.py         # Pool de conexiones y dependencia get_db
    │   ├── dependencies.py     # require_role / control de acceso
    │   ├── security.py         # Hash y verificación de contraseñas
    │   └── templates.py        # Configuración de Jinja2
    ├── routers/                # Endpoints HTTP (uno por módulo)
    ├── repositories/           # Acceso a datos (SQL con psycopg)
    ├── templates/              # Plantillas Jinja2 (base, login, dashboards)
    ├── ts/                     # Código TypeScript (fuente)
    ├── types/api.d.ts          # Tipos compartidos de las respuestas de la API
    └── static/
        ├── css/
        └── js/                 # JavaScript compilado desde ts/
```

### Arquitectura en capas

```
Router (valida y responde)  →  Repository (SQL)  →  PostgreSQL
        ↑                              ↑
  Depends(get_db)               BaseRepo (CRUD genérico)
```

- **Routers**: reciben la petición, validan con modelos Pydantic y delegan al repositorio.
- **Repositories**: encapsulan el SQL. `BaseRepo` ofrece CRUD genérico (`obtener_todos`, `insertar_registro`, etc.) construido con `psycopg.sql` para evitar inyección SQL.
- **Conexión**: `Conexion().get_db` entrega una conexión del pool por petición y la libera al terminar.

## Guía de desarrollo

### Agregar un nuevo módulo (ejemplo: `reserva`)

1. **Tabla**: añádela en `initdb/sql/02-create-tables.sql` (si ya tienes datos, aplica el cambio manualmente con `psql` o recrea el volumen).
2. **Repositorio**: crea `repositories/reserva_repo.py`, heredando de `BaseRepo` si el CRUD genérico te basta.
3. **Router**: crea `routers/reserva_router.py` con su `APIRouter(prefix="/reserva")`, modelos Pydantic de entrada/salida y `Depends(db_manager.get_db)`.
4. **Registro**: incluye el router en `main.py` con `app.include_router(...)`.
5. **Protección**: si es solo para un rol, agrega `dependencies=[Depends(require_role("Empleado"))]` al router.

### Agregar o modificar una vista

1. Plantilla en `templates/` extendiendo `base.html`.
2. Estilos en `static/css/`.
3. Lógica en `ts/<vista>.ts`; si usa tipos de la API, defínelos en `types/api.d.ts`.
4. Compila: `npx tsc` (o `npx tsc --watch` mientras desarrollas).
5. Sirve la plantilla desde un router con `templates.TemplateResponse(request, "<archivo>.html")`.

> **No edites** los `.js` de `static/js/` a mano: se sobrescriben al compilar.

### Agregar una dependencia

```bash
uv add <paquete>          # Python
npm install -D <paquete>  # TypeScript / herramientas de frontend
```

### Convenciones del proyecto

- Nombres de dominio (tablas, módulos, variables) en español, `snake_case`.
- Commits con prefijo convencional, por ejemplo `fix(empleado): ...`.
- El nombre de un viaje debe cumplir el formato `Origen-Destino` (restricción `ck_formato_nombre` en la BD, p. ej. `Saltillo-Monterrey`).

## Problemas conocidos / pendientes

Cosas a tener en cuenta al seguir desarrollando:

- **Script de `pyproject.toml`**: declara `agencia-viajes-web = "agencia_viajes_web:main"`, pero `__init__.py` no define `main`. Ese comando no funciona; usa `fastapi dev` / `uvicorn` como se indica arriba.
- **`database.py` en la raíz**: duplica la configuración de `core/config.py` y `core/database.py`, y no lo usa la app. Candidato a eliminarse.
- **Sin datos semilla**: no hay usuarios, agencias ni catálogos iniciales; deben crearse a mano (ver paso 7).
- **`SECRET_KEY` por defecto** (`cookie_secret_key`): obligatorio cambiarla en cualquier entorno que no sea local.
- **Sin pruebas automatizadas**: `npm test` es un placeholder.
- **Registro de usuarios abierto**: `POST /usuario/` no exige autenticación; conviene restringirlo antes de exponer la app.
- **Manejo de errores de BD**: `BaseRepo` imprime el error y devuelve listas vacías; considera registrar con `logging` y propagar errores.

## Comandos útiles

```bash
docker compose up -d                              # levantar PostgreSQL
docker compose logs -f postgres                   # ver logs de la BD
docker exec -it postgres_agenciadeviajes psql -U <DB_USER> -d <DB_NAME>   # consola SQL
uv run fastapi dev src/agencia_viajes_web/main.py # servidor con recarga
npx tsc --watch                                   # compilar TS en vivo
```
