
# Bluesky Reply & Quote Network Export

Este script permite descargar interacciones (respuestas y citas) entre usuarios de [Bluesky](https://bsky.app), construir una red social dirigida y exportar los resultados a formatos compatibles con análisis en Gephi y en Python.

## ✨ Funcionalidad

A partir de una lista de handles públicos de Bluesky, el script:

- Descarga hasta N posts por usuario
- Extrae replies y quotes hacia esos posts
- Construye un grafo dirigido de relaciones entre usuarios
- Añade atributos relevantes a los nodos y aristas
- Exporta:
  - `nombre.graphml`: red en formato Gephi
  - `nombre.xlsx`: todos los datos en una hoja Excel

## 🛠️ Requisitos

Python 3.10+ con las siguientes dependencias:

- `atproto`, `networkx`, `pandas`, `openpyxl`, `spacy`, `tqdm`, `datetime`

Puedes instalarlas automáticamente con:

```bash
bash setup_env.sh
```

En Windows:

```bat
setup_env_windows.bat
```

Además, deberás descargar el modelo de spaCy:

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Uso

```bash
python bluesky_to_gephi.py \
  --handle tu_handle.bsky.social \
  --app-password tu_app_password \
  --targets @usuario1.bsky.social @usuario2.bsky.social ... \
  --limit 100 \
  --output-prefix nombre_dataset \
  --max-replies-per-post 10
```

### Argumentos

| Parámetro               | Descripción                                                    |
|------------------------|----------------------------------------------------------------|
| `--handle`             | Tu handle de Bluesky (ej: `usuario.bsky.social`)               |
| `--app-password`       | App password generado desde [app passwords](https://bsky.app/settings/app-passwords) |
| `--targets`            | Lista de handles objetivo (usuarios de los que quieres los posts) |
| `--limit`              | Número máximo de posts a descargar por usuario objetivo        |
| `--output-prefix`      | Prefijo para los ficheros generados                            |
| `--max-replies-per-post` | Máximo número de replies a conservar por post original         |

## 📁 Archivos de salida

- `PREFIX.graphml`: red lista para cargar en Gephi
- `PREFIX.xlsx`: tabla tabular combinada para análisis en Jupyter

## 🎯 Casos de uso

- Análisis de homofilia y asortatividad
- Detección de comunidades por modularidad (en Gephi)
- Clustering no supervisado (en Python)
- Análisis temporal (con `created_at`)
- Visualización y filtrado de temas (`topicLabel`)

## 🧪 Sugerencia

Después de generar los datos, puedes usar Gephi para visualizar la red y Python (Jupyter) para aplicar técnicas de clustering y análisis.

---

Autor: Adaptado para fines académicos por un estudiante del Máster de Ingeniería y Ciencia de Datos (UNED).
