# Lecciones Aprendidas — Taller: De Prototipo a API REST

**Proyecto:** Sistema de Gestión de Casos Legales (SGCL)
**Stack:** Python · Flask · SQLAlchemy · SQLite · JWT (PyJWT)

## 1. Objetivo del taller

Partiendo de un prototipo visual (pantallas de login y agenda de un
sistema de gestión de expedientes legales), el ejercicio consistió en:

1. Diseñar el modelo de datos que soportaría ese prototipo.
2. Implementarlo con un conector real (ORM) en Python.
3. Exponer la información mediante una API REST con Flask.

## 2. Del prototipo al modelo de datos

Lo primero fue **traducir la interfaz a entidades**. El mockup mostraba
columnas como "Aseguradora", "Juzgado" y contadores de "Pendientes /
En curso / Cerrados"; eso reveló directamente tres catálogos
(`aseguradoras`, `juzgados`, `estados_expediente`) y una tabla central
(`expedientes`) que los relaciona. La lección aquí fue que **una
pantalla bien diseñada ya contiene buena parte del modelo entidad-relación
implícito**: cada columna repetida en una tabla es candidata a catálogo
normalizado, y cada agrupación (la agenda del día) es candidata a tabla
propia relacionada por clave foránea.

También se decidió usar **baja lógica** (`activo = false`) en vez de
eliminar registros de catálogos o usuarios, porque un expediente antiguo
no debe perder su referencia a una aseguradora o abogado que ya no está
activo. Esto evitó violaciones de integridad referencial al momento de
las pruebas.

## 3. De SQL puro a ORM

Se escribió primero `schema.sql` en SQL puro para razonar el diseño sin
distracciones de sintaxis de un framework, y luego se tradujo a modelos
de SQLAlchemy. Esto ayudó a detectar errores de diseño temprano (por
ejemplo, decidir si `id_usuario_asignado` en `expedientes` debía ser
obligatorio u opcional) antes de escribir una sola línea de Python.

Usar SQLAlchemy como conector, en lugar de sentencias SQL crudas, redujo
errores de tipeo en columnas y facilitó las validaciones (`query.get()`,
relaciones `db.relationship`) sin sacrificar el control sobre el esquema.

## 4. Diseño de la API REST

Se organizó la API en **blueprints por recurso** (usuarios, aseguradoras,
juzgados, expedientes, agenda, dashboard), siguiendo convenciones REST:

- `GET` para lectura, `POST` para creación, `PUT` para actualización
  parcial, `DELETE` para baja.
- Los filtros de negocio (por estado, por aseguradora, por texto) se
  implementaron como **query params**, no como rutas nuevas
  (`/expedientes?estado=Pendiente` en vez de `/expedientes/pendientes`),
  lo que mantiene la API predecible y fácil de extender.
- Se agregó un endpoint `/api/dashboard` dedicado, en vez de forzar al
  cliente a hacer varias llamadas y calcular contadores del lado del
  frontend — replicando la utilidad real del panel del prototipo
  (Pendientes / En curso / Cerrados + agenda del día) pero calculada en
  el servidor, con una sola consulta agregada (`GROUP BY`).

## 5. Autenticación: obstáculo real y solución

El plan inicial era usar `Flask-JWT-Extended`, pero en el entorno del
taller esa librería entró en conflicto de versiones con `PyJWT` ya
instalado, generando un `ImportError` en tiempo de ejecución. En vez de
forzar la instalación de versiones específicas (frágil y poco portable),
se optó por **implementar la emisión/validación de JWT directamente con
PyJWT** mediante un decorador `@token_required` propio. Lección: cuando
una dependencia de alto nivel falla por conflictos de entorno, a menudo
es más robusto bajar un nivel de abstracción y usar la librería base
directamente, sobre todo si el equipo del taller replicará el entorno en
otras máquinas.

## 6. Errores encontrados y cómo se resolvieron

| Problema                                                              | Causa                                                    | Solución                                                                 |
|-------------------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------|
| `ImportError: cannot import name 'Options' from 'jwt.types'`            | Conflicto de versión entre `Flask-JWT-Extended` y `PyJWT` | Se reemplazó por una capa de autenticación propia usando `PyJWT` directo    |
| El servidor Flask se cerraba al ejecutar en segundo plano en la terminal | El proceso hijo del *reloader* de Flask no sobrevivía al cierre del shell padre | Se desactivó `debug`/`use_reloader` para pruebas en background, y se usó `Flask test_client()` para las pruebas automatizadas en vez de peticiones HTTP reales |
| Creación de expediente con catálogos inexistentes                        | No se validaban las llaves foráneas antes del `INSERT`   | Se agregó validación explícita (`Aseguradora.query.get(...)`, etc.) antes de persistir |
| Números de expediente duplicados                                        | Falta de restricción a nivel de aplicación                | Se agregó `UNIQUE` en la BD y verificación previa en el endpoint, devolviendo `409 Conflict` |

## 7. Pruebas automatizadas

Se optó por usar el `test_client` de Flask con una base de datos SQLite
**en memoria** (`sqlite:///:memory:`) para las pruebas, en lugar de un
servidor HTTP real. Esto hizo las pruebas rápidas, aisladas y
reproducibles (8 pruebas, ejecutadas en ~2 segundos), cubriendo
autenticación, autorización, creación de recursos, restricciones de
unicidad, filtros y el endpoint de dashboard.

## 8. Principales aprendizajes generales

- Un buen diseño de base de datos empieza por identificar catálogos y
  relaciones a partir del mockup o de los requisitos, no directamente
  escribiendo código.
- Separar `schema.sql` (diseño) de los modelos ORM (implementación)
  ayuda a documentar el "por qué" de cada tabla, no solo el "cómo".
- Una API REST bien pensada no es solo CRUD: los endpoints de agregación
  (como el dashboard) son los que realmente aportan valor de negocio y
  deben diseñarse con la misma intención que las pantallas del
  prototipo que reemplazan.
- Los conflictos de dependencias son parte normal del desarrollo; la
  respuesta correcta no siempre es "forzar la versión correcta", sino
  a veces simplificar la solución.
- Probar contra un `test_client` en memoria, en vez de un servidor real,
  hace que la suite de pruebas sea reproducible en cualquier máquina sin
  depender de puertos de red disponibles.
