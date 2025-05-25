
import argparse
import csv
import time
from collections import deque

import spacy
from atproto import Client
import networkx as nx
from tqdm import tqdm

# Cargar modelo spaCy
nlp = spacy.load("en_core_web_sm")

# Listas de términos por categoría
TECH = {"ai", "artificial intelligence", "machine learning", "data", "technology", "model"}
ART = {"art", "illustration", "creative", "music", "painting"}
POLITICS = {"politics", "government", "activism", "law"}
LIT = {"writer", "book", "literature", "author"}
CLIMATE = {"climate", "environment", "eco", "green"}

def extract_topic_label(description):
    doc = nlp(description.lower())
    lemmas = set([token.lemma_ for token in doc if not token.is_stop])

    if lemmas & TECH:
        return "tech"
    elif lemmas & ART:
        return "art"
    elif lemmas & POLITICS:
        return "politics"
    elif lemmas & LIT:
        return "literature"
    elif lemmas & CLIMATE:
        return "climate"
    return "other"

def fetch_paginated_follows(client, target_user, direction='follows', limit_total=None, delay=0.0):
    results = []
    cursor = None
    limit = 100

    with tqdm(desc=f"{direction.capitalize()} de {target_user}", unit="usuarios", leave=False) as pbar:
        while True:
            params = {'actor': target_user, 'limit': limit}
            if cursor:
                params['cursor'] = cursor

            try:
                if direction == 'follows':
                    response = client.app.bsky.graph.get_follows(params)
                    page_data = response.follows
                    cursor = response.cursor
                else:
                    response = client.app.bsky.graph.get_followers(params)
                    page_data = response.followers
                    cursor = response.cursor
            except Exception as e:
                print(f"[!] Error al traer {direction} de {target_user}: {e}")
                break

            results.extend(page_data)
            pbar.update(len(page_data))

            if not cursor or (limit_total and len(results) >= limit_total):
                break

            if delay > 0:
                time.sleep(delay)

    return results[:limit_total] if limit_total else results

def add_user_node(G, user_data, direction, source_user, edge_list):
    user_handle = user_data.handle
    if user_handle not in G:
        G.add_node(user_handle,
                   displayName=user_data.display_name or "",
                   description=user_data.description or "",
                   avatar=user_data.avatar or "",
                   followersCount=getattr(user_data, "followers_count", 0),
                   followsCount=getattr(user_data, "follows_count", 0),
                   postsCount=getattr(user_data, "posts_count", 0),
                   topicLabel=extract_topic_label(user_data.description or ""))

    if direction == 'follows':
        G.add_edge(source_user, user_handle)
        edge_list.append((source_user, user_handle, 'follows'))
    else:
        G.add_edge(user_handle, source_user)
        edge_list.append((user_handle, source_user, 'followed_by'))

def export_to_csv(G, edge_list, node_file, edge_file):
    with open(node_file, 'w', newline='', encoding='utf-8') as f_nodes:
        writer = csv.writer(f_nodes)
        writer.writerow(['handle', 'displayName', 'description', 'avatar',
                         'followersCount', 'followsCount', 'postsCount', 'topicLabel'])
        for node, attrs in G.nodes(data=True):
            writer.writerow([
                node,
                attrs.get('displayName', ''),
                attrs.get('description', ''),
                attrs.get('avatar', ''),
                attrs.get('followersCount', 0),
                attrs.get('followsCount', 0),
                attrs.get('postsCount', 0),
                attrs.get('topicLabel', 'other')
            ])

    with open(edge_file, 'w', newline='', encoding='utf-8') as f_edges:
        writer = csv.writer(f_edges)
        writer.writerow(['source', 'target', 'relation'])
        for edge in edge_list:
            writer.writerow(edge)

def fetch_full_network(handle, app_password, target_user, output_prefix="bluesky_graph", limit=100, depth=2, delay=0.0):
    client = Client()
    print("[*] Autenticando...")
    client.login(handle, app_password)

    print(f"[*] Resolviendo DID de {target_user}...")
    did = client.com.atproto.identity.resolve_handle(target_user).did

    G = nx.DiGraph()
    edge_list = []

    visited = set()
    queue = deque()
    queue.append((target_user, 1))

    G.add_node(target_user,
               displayName=target_user,
               description="",
               avatar="",
               followersCount=0,
               followsCount=0,
               postsCount=0,
               topicLabel="other")

    progress_users = tqdm(desc="Usuarios explorados", unit="usuarios")

    while queue:
        current_user, current_depth = queue.popleft()
        if current_user in visited:
            continue
        visited.add(current_user)

        progress_users.update(1)

        if current_user != target_user and delay > 0:
            time.sleep(delay)

        print(f"[{current_depth}] Explorando: {current_user}")
        follows = fetch_paginated_follows(client, current_user, 'follows', limit, delay)
        for follow in follows:
            add_user_node(G, follow, 'follows', current_user, edge_list)
            if current_depth < depth:
                queue.append((follow.handle, current_depth + 1))

        followers = fetch_paginated_follows(client, current_user, 'followers', limit, delay)
        for follower in followers:
            add_user_node(G, follower, 'followers', current_user, edge_list)
            if current_depth < depth:
                queue.append((follower.handle, current_depth + 1))

    progress_users.close()

    print(f"[*] Total nodos: {len(G.nodes())}, aristas: {len(G.edges())}")

    gexf_file = f"{output_prefix}.gexf"
    node_csv = f"{output_prefix}_nodes.csv"
    edge_csv = f"{output_prefix}_edges.csv"

    print(f"[*] Guardando grafo en {gexf_file}...")
    nx.write_gexf(G, gexf_file)

    print(f"[*] Exportando nodos a {node_csv} y relaciones a {edge_csv}...")
    export_to_csv(G, edge_list, node_csv, edge_csv)

    print("[✓] Finalizado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga red social de Bluesky y exporta a Gephi + CSV.")
    parser.add_argument("--handle", required=True, help="Tu handle de Bluesky (ej. tuusuario.bsky.social)")
    parser.add_argument("--app-password", required=True, help="Contraseña de aplicación de Bluesky")
    parser.add_argument("--target", required=True, help="Usuario objetivo (ej. @bob.bsky.social)")
    parser.add_argument("--output-prefix", default="bluesky_graph", help="Prefijo de los archivos de salida")
    parser.add_argument("--limit", type=int, default=100, help="Límite máximo de nodos por tipo por usuario")
    parser.add_argument("--depth", type=int, default=2, help="Profundidad máxima de exploración")
    parser.add_argument("--delay", type=float, default=0.0, help="Tiempo (en segundos) entre usuarios y páginas (ej: 1.5)")

    args = parser.parse_args()

    fetch_full_network(
        handle=args.handle,
        app_password=args.app_password,
        target_user=args.target,
        output_prefix=args.output_prefix,
        limit=args.limit,
        depth=args.depth,
        delay=args.delay
    )
