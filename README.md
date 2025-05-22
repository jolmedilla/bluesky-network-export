
# Bluesky Network Export

Este script permite descargar la red social (seguidores y seguidos) de cualquier usuario público de [Bluesky](https://bsky.app), y exportarla a archivos compatibles con [Gephi](https://gephi.org) y CSV para su análisis.

## Características

- Exporta seguidores y seguidos (`followers`, `follows`)
- Soporte de exploración recursiva por niveles (`--depth`)
- Control de tasa (`--delay`) para evitar bloqueos de la API
- Progreso visual con `tqdm`
- Salida en `.gexf`, `.csv` (nodos y aristas)

## Instalación

```bash
pip install atproto networkx tqdm
```

## Ejemplo de uso

```bash
python bluesky_to_gephi.py \
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
- `salida_nodes.csv`: información de cada nodo (usuario)
- `salida_edges.csv`: conexiones (`follows` y `followed_by`)

## Licencia

MIT
