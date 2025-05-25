
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
