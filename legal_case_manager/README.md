# Sistema de Gestión de Casos Legales (PA)

Taller práctico: diseño de base de datos → programación en Python con Flask
y SQLAlchemy (conector ORM) → exposición de la información mediante una
**API REST**, con una **interfaz web** (HTML/CSS/JS servidos por el mismo
Flask) que consume esa API.

Inspirado en un prototipo de gestión de expedientes legales para
aseguradoras (login, agenda del día, expedientes pendientes/en curso/cerrados),
pero con diseño propio ("Legajo"): sidebar oscuro, expedientes mostrados
como fólios con franja de color por estado, y números de expediente en
tipografía monoespaciada como un sello de juzgado.

## Pantallas incluidas

- **Login** (`/login`) — autenticación contra la API con JWT.
- **Panel principal** (`/dashboard`) — contadores Pendientes/En curso/Cerrados
  + expedientes recientes + agenda del día.
- **Expedientes** (`/expedientes`) — listado con filtros (texto, estado,
  aseguradora), crear/editar/eliminar mediante modal.
- **Agenda** (`/agenda`) — eventos por fecha, crear nuevos eventos.
- **Catálogos** (`/catalogos`) — administrar aseguradoras y juzgados.

## 1. Contenido del repositorio

```
legal_case_manager/
├── app/
│   ├── __init__.py         # application factory
│   ├── config.py           # configuración (BD, secretos)
│   ├── extensions.py       # instancia de SQLAlchemy
│   ├── models.py           # modelos ORM (mapean el esquema de la BD)
│   ├── auth_utils.py       # hash de contraseñas y JWT
│   ├── routes/              # blueprints = endpoints de la API REST
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── aseguradoras.py
│   │   ├── juzgados.py
│   │   ├── expedientes.py
│   │   ├── agenda.py
│   │   ├── dashboard.py
│   │   ├── catalogos.py
│   │   └── web.py           # sirve las páginas HTML de la interfaz
│   ├── templates/            # páginas HTML (Jinja2)
│   │   ├── _rail.html        # menú lateral reutilizable
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── expedientes.html
│   │   ├── agenda.html
│   │   └── catalogos.html
│   └── static/
│       ├── css/styles.css
│       └── js/                # api.js + un .js por página
├── docs/
│   └── diagrama_er.mermaid  # diagrama entidad-relación
├── tests/
│   └── test_api.py          # pruebas automatizadas (pytest)
├── schema.sql                # esquema SQL puro (DDL) de la base de datos
├── seed_demo.py              # carga de datos de ejemplo
├── run.py                    # punto de entrada
├── requirements.txt
├── LECCIONES_APRENDIDAS.md
└── README.md
```

## 2. Diseño de la base de datos

Motor usado en el taller: **SQLite** (por simplicidad, cero configuración).
El esquema es estándar y funciona igual en PostgreSQL o MySQL cambiando
solo el `DATABASE_URL`.

Entidades principales:

| Tabla                 | Propósito                                             |
|------------------------|--------------------------------------------------------|
| `roles`                | Catálogo de roles de usuario                           |
| `usuarios`             | Cuentas que acceden al sistema (login)                  |
| `aseguradoras`         | Catálogo de aseguradoras                                |
| `juzgados`             | Catálogo de juzgados / tribunales                       |
| `estados_expediente`   | Catálogo: Pendiente / En curso / Cerrado                |
| `expedientes`          | Entidad central: cada caso legal                        |
| `agenda`               | Eventos/audiencias de un expediente ("agenda del día")  |

Ver el diagrama completo en [`docs/diagrama_er.mermaid`](docs/diagrama_er.mermaid)
y el DDL completo en [`schema.sql`](schema.sql).

## 3. Instalación

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Cargar datos de ejemplo

```bash
python seed_demo.py
```

Crea un usuario de prueba: **usuario** `jperez` / **contraseña** `Password123`,
además de aseguradoras, juzgados y expedientes de muestra.

## 5. Levantar la aplicación

```bash
python run.py
```

- **Interfaz web**: abre `http://localhost:5000/login` en el navegador.
- **API REST**: disponible en `http://localhost:5000/api/...` (ver sección 7).

## 6. Autenticación

La API usa **JWT** (Bearer token). Todos los endpoints, excepto
`/api/health` y `/api/auth/*`, requieren el header:

```
Authorization: Bearer <token>
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "jperez", "password": "Password123"}'
```

Respuesta:
```json
{ "token": "eyJhbGciOi...", "usuario": { "id_usuario": 1, "nombre_completo": "Lic. Juan Pérez", ... } }
```

## 7. Endpoints principales

| Método | Ruta                          | Descripción                                    |
|--------|-------------------------------|-------------------------------------------------|
| POST   | `/api/auth/registro`          | Crear un usuario                                 |
| POST   | `/api/auth/login`             | Iniciar sesión y obtener token                    |
| GET    | `/api/usuarios`               | Listar usuarios                                   |
| GET    | `/api/aseguradoras`           | Listar aseguradoras                               |
| POST   | `/api/aseguradoras`           | Crear aseguradora                                 |
| GET    | `/api/juzgados`               | Listar juzgados                                   |
| POST   | `/api/juzgados`               | Crear juzgado                                     |
| GET    | `/api/expedientes`            | Listar expedientes (con filtros)                  |
| POST   | `/api/expedientes`            | Crear expediente                                  |
| GET    | `/api/expedientes/<id>`       | Obtener un expediente                             |
| PUT    | `/api/expedientes/<id>`       | Actualizar un expediente                          |
| DELETE | `/api/expedientes/<id>`       | Eliminar un expediente                            |
| GET    | `/api/agenda`                 | Agenda del día (usar `?fecha=` o `?todos=1`)      |
| POST   | `/api/agenda`                 | Crear evento en la agenda                         |
| GET    | `/api/dashboard`               | Resumen: contadores + agenda del día              |

Filtros disponibles en `GET /api/expedientes`:
`?estado=Pendiente`, `?aseguradora=<id>`, `?juzgado=<id>`, `?q=texto`.

### Ejemplo: crear un expediente

```bash
curl -X POST http://localhost:5000/api/expedientes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "numero_expediente": "EXP-2019-010",
        "asegurado_nombre": "MARIA GONZALEZ",
        "id_aseguradora": 1,
        "id_juzgado": 1,
        "id_estado": 1
      }'
```

### Ejemplo: panel de resumen (equivalente al dashboard del prototipo)

```bash
curl http://localhost:5000/api/dashboard -H "Authorization: Bearer <token>"
```

```json
{
  "fecha": "2026-07-11",
  "contadores": { "Pendiente": 1, "En curso": 1, "Cerrado": 1 },
  "agenda_del_dia": [
    { "titulo": "Audiencia preliminar", "numero_expediente": "EXP-2019-001", ... }
  ]
}
```

## 8. Pruebas

```bash
pytest -v
```

## 9. Diferencias respecto al prototipo original

- Es un **servicio backend puro (API REST)**, sin interfaz gráfica: el
  taller pide entregar la información vía API, no una réplica visual del
  mockup.
- Autenticación con **JWT** en vez de sesión de formulario web.
- Modelo de datos normalizado con catálogos (aseguradoras, juzgados,
  estados) en lugar de texto libre en cada expediente.
- Incluye módulo de **agenda** como entidad propia relacionada a cada
  expediente, en vez de datos embebidos en el expediente.
- Baja lógica (`activo = false`) para catálogos y usuarios, preservando
  la integridad referencial del historial de expedientes.
