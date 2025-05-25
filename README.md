
# Bluesky Network Export (versión extendida)

Este script permite descargar la red social (seguidores y seguidos) de cualquier usuario público de [Bluesky](https://bsky.app), y exportarla a archivos compatibles con [Gephi](https://gephi.org) y CSV para su análisis.

Esta versión añade atributos estructurales y temáticos para análisis de homofilia y asortatividad, tal como se requiere en prácticas académicas como las del Máster en Ingeniería y Ciencia de Datos de la UNED.

## Características

- Exporta relaciones `followers` y `follows`
- Soporte de exploración recursiva por niveles (`--depth`)
- Control de tasa (`--delay`) para evitar bloqueos de la API
- Exporta atributos enriquecidos de cada nodo:
  - `followersCount`
  - `followsCount`
  - `postsCount`
  - `topicLabel` (categoría temática simple basada en la biografía)
- Salida en `.gexf`, `.csv` (nodos y aristas)
- Compatible con Gephi para análisis de redes sociales

## Instalación

```bash
pip install atproto networkx tqdm
```

## Ejemplo de uso

```bash
python bluesky_to_gephi_extended.py \
  --handle tuusuario.bsky.social \
  --app-password xxxx-xxxx-xxxx-xxxx \
  --target @otro.bsky.social \
  --output-prefix salida \
  --limit 100 \
  --depth 2 \
  --delay 1.0
```

## Archivos generados

- `salida.gexf`: red para Gephi
- `salida_nodes.csv`: nodos con atributos (incluyendo conteos y etiquetas temáticas)
- `salida_edges.csv`: relaciones dirigidas entre usuarios

## Atributos exportados por nodo

| Atributo         | Descripción                                     |
|------------------|-------------------------------------------------|
| handle           | Identificador único del usuario                 |
| displayName      | Nombre visible del perfil                       |
| description      | Biografía textual del usuario                   |
| avatar           | URL de imagen de perfil                         |
| followersCount   | Número de seguidores                            |
| followsCount     | Número de cuentas a las que sigue              |
| postsCount       | Número de publicaciones                        |
| topicLabel       | Etiqueta temática estimada desde la biografía  |

## Ejemplos de etiquetas temáticas (`topicLabel`)

- `tech`: menciona IA, datos, modelos, etc.
- `art`: arte, música, creatividad
- `politics`: política, activismo
- `literature`: libros, poesía, escritura
- `climate`: ecología, medio ambiente
- `other`: sin tema detectado

## Licencia

MIT


## Cómo usar `topicLabel` en Gephi

Una vez importes el archivo `salida_nodes.csv` o el `.gexf` en Gephi, podrás trabajar con la columna `topicLabel` para analizar homofilia y asortatividad temática.

### 1. Visualización por tema

- En la pestaña **Appearance**, elige **Nodes > Partition > topicLabel**.
- Aplica diferentes colores a cada valor (`tech`, `art`, `politics`, etc.).
- Esto te permitirá ver comunidades temáticas visualmente.

### 2. Cálculo de asortatividad

- Ve a **Statistics > Assortativity**.
- Elige `topicLabel` como atributo categórico.
- Ejecuta el cálculo para obtener el **coeficiente de homofilia** temática:
  - Valor cercano a **1**: usuarios de temas similares se conectan entre sí.
  - Valor cercano a **0**: las conexiones no dependen del tema.
  - Valor negativo: usuarios de temas distintos tienden a conectarse.

### 3. Filtrado o agrupamiento

- Puedes usar **Filters > Attributes > topicLabel** para seleccionar un subconjunto de nodos de un tema concreto.
- También puedes exportar por separado subgrafos de cada tema si lo necesitas para análisis comparativo.

Este enfoque te permite estudiar asortatividad dentro de clases semánticas aproximadas sin necesidad de etiquetado manual ni NLP avanzado.

