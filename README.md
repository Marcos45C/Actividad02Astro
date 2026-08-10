# Ejemplo 01: de Django clásico a una API

Base de trabajo para retomar una aplicación Django renderizada en el servidor y, durante la clase, hacerla evolucionar hacia una API consumida desde React.

El repositorio comienza con dos aplicaciones independientes:

- `backend/`: Django, el modelo `Activity`, SQLite y una vista HTML clásica.
- `frontend/`: Vite + React + TypeScript recién inicializado, todavía sin integración con Django.

## Puesta en marcha local

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

### 2. Frontend

En otra terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

Abrir <http://127.0.0.1:5173/>.

## Puesta en marcha con Docker Compose

Docker Compose queda preparado para uso futuro; no es necesario para seguir la primera clase.

```bash
docker compose up --build
```

El backend queda disponible en <http://127.0.0.1:8000/> y el frontend en <http://127.0.0.1:5173/>. El comando del backend aplica las migraciones y carga los datos de muestra antes de iniciar el servidor.

Para detener ambos servicios:

```bash
docker compose down
```

## Verificación rápida

```bash
cd backend
python manage.py test

cd ../frontend
pnpm build
```

## Punto de partida didáctico

En este corte todavía no hay una API JSON ni comunicación entre ambos proyectos. Django consulta SQLite y produce el HTML completo. La evolución hacia `GET /activities` y el consumo con `fetch` se realiza a partir de esta base.
