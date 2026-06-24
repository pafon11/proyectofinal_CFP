# ML Dashboard

Dashboard web centralizado para ejecutar 3 modelos de ML/Regresión desde el navegador.

## Modelos incluidos

| Modelo | Archivo | Descripción |
|--------|---------|-------------|
| 🌲 Forest COVID-19 | `models/forest_covid.py` | Random Forest · clasificación de pacientes |
| 💾 Regresión Backup | `models/regresion1.py` | Predicción de tamaño de backup según usuarios |
| 🚚 Regresión Entrega | `models/regresion2.py` | Predicción de tiempo de entrega según distancia |

---

## Instalación local

```bash
# 1. Clonar el proyecto
git clone https://github.com/TU_USUARIO/ml-dashboard.git
cd ml-dashboard

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python app.py
```

Abre **http://localhost:5000** en tu navegador.

---

## ⚙️ Configuración de bases de datos

Los modelos se conectan a MySQL con estas credenciales por defecto:

| Modelo | Host | User | Password | Base de datos |
|--------|------|------|----------|---------------|
| Backup | localhost | root | root123 | almacen |
| Entrega | localhost | root | root123 | entregas_db |
| COVID | localhost | root | (vacío) | Covid19_final |

Para cambiar las credenciales, edita directamente los archivos en `models/`.

### Variables de entorno (opcional para producción)

Puedes externalizar las credenciales con variables de entorno y modificar los modelos para leerlas:

```python
import os
host = os.environ.get("DB_HOST", "localhost")
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "root123")
```

---

## 🚀 Deploy en Render.com

### Paso 1 — Subir a GitHub

```bash
git init
git add .
git commit -m "feat: ML Dashboard inicial"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ml-dashboard.git
git push -u origin main
```

### Paso 2 — Crear Web Service en Render

1. Ve a **https://render.com** e inicia sesión (o crea cuenta gratis).
2. Haz clic en **"New +"** → **"Web Service"**.
3. Conecta tu cuenta de GitHub y selecciona el repositorio `ml-dashboard`.
4. Render detectará automáticamente el archivo `render.yaml`.

### Paso 3 — Configurar el servicio

| Campo | Valor |
|-------|-------|
| Name | `ml-dashboard` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free (o el que prefieras) |

### Paso 4 — Variables de entorno en Render

En la pestaña **"Environment"** del servicio, agrega las variables de tu base de datos:

```
DB_HOST      = tu-host-mysql
DB_USER      = tu-usuario
DB_PASSWORD  = tu-contraseña
```

> ⚠️ **Nota sobre la base de datos en producción**: Render no incluye MySQL. Necesitas una base de datos externa accesible desde internet. Opciones gratuitas:
> - **PlanetScale** (MySQL compatible)
> - **Railway** (MySQL/PostgreSQL)
> - **Clever Cloud** (MySQL)
>
> Una vez que tengas el host externo, actualiza las variables de entorno y los archivos de modelo.

### Paso 5 — Deploy

Haz clic en **"Create Web Service"**. Render instalará las dependencias y levantará la app.

Tu URL pública será algo como:
```
https://ml-dashboard-xxxx.onrender.com
```

### Deploy automático

Cada vez que hagas `git push` a `main`, Render redesplegará automáticamente.

---

## Estructura del proyecto

```
ml-dashboard/
├── app.py                  # Flask app principal
├── requirements.txt        # Dependencias Python
├── render.yaml             # Configuración de deploy
├── .gitignore
├── models/
│   ├── __init__.py
│   ├── forest_covid.py     # Modelo Random Forest COVID-19
│   ├── regresion1.py       # Regresión Lineal - Backup
│   └── regresion2.py       # Regresión Lineal - Entrega
├── templates/
│   ├── index.html          # Dashboard principal
│   ├── forest.html         # Página Forest COVID
│   ├── regresion1.html     # Página Regresión Backup
│   └── regresion2.html     # Página Regresión Entrega
└── static/
    └── style.css           # Estilos del dashboard
```

---

## Agregar nuevos modelos

1. Agrega tu archivo de modelo en `models/nuevo_modelo.py`
2. Crea un adaptador en `app.py` (sigue el patrón de `run_regresion1`)
3. Agrega la ruta Flask
4. Crea la plantilla HTML en `templates/nuevo.html`
5. Agrega la tarjeta en `templates/index.html`
