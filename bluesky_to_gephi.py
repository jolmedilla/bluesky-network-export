import argparse
import csv
import time
import os
import re
import networkx as nx
import spacy
from atproto import Client
from tqdm import tqdm
from collections import deque

nlp = spacy.load("en_core_web_sm")

TECH = {"ai", "artificial intelligence", "machine learning", "data", "technology", "model"}
ART = {"art", "illustration", "creative", "music", "painting"}
POLITICS = {"politics", "government", "activism", "law"}
LIT = {"writer", "book", "literature", "author"}
CLIMATE = {"climate", "environment", "eco", "green"}

def clean_text(text):
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

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

def compute_assortativity(G):
    print("\n[*] Cálculo de asortatividad:")
    try:
        r_deg = nx.degree_assortativity_coefficient(G)
        print(f"- Asortatividad por grado: {r_deg:.4f}")
    except Exception as e:
        print(f"  [!] Error en grado: {e}")
    for attr in ["followersCount", "followsCount", "postsCount"]:
        try:
            r = nx.numeric_assortativity_coefficient(G, attr)
            print(f"- Asortatividad por {attr}: {r:.4f}")
        except Exception as e:
            print(f"  [!] Error en {attr}: {e}")
    try:
        r_cat = nx.attribute_assortativity_coefficient(G, "topicLabel")
        print(f"- Asortatividad categórica por topicLabel: {r_cat:.4f}")
    except Exception as e:
        print(f"  [!] Error en topicLabel: {e}")

def fetch_full_network(handle, app_password, target_user, output_prefix="bluesky_graph", limit=100, depth=2, delay=0.0):
    client = Client()
    print("[*] Autenticando...")
    client.login(handle, app_password)

    if target_user.startswith("@"):
        target_user = target_user[1:]

    print(f"[*] Resolviendo DID de {target_user}...")
    client.com.atproto.identity.resolve_handle({"handle": target_user})

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
        for direction in ['follows', 'followers']:
            results = fetch_paginated_follows(client, current_user, direction, limit, delay)
            for user in results:
                user_handle = user.handle
                if user_handle not in G:
                    G.add_node(user_handle,
                        displayName=clean_text(user.display_name or ""),
                        description=clean_text(user.description or ""),
                        avatar=user.avatar or "",
                        followersCount=getattr(user, "followers_count", 0),
                        followsCount=getattr(user, "follows_count", 0),
                        postsCount=getattr(user, "posts_count", 0),
                        topicLabel=extract_topic_label(user.description or ""))
                if direction == 'follows':
                    G.add_edge(current_user, user_handle)
                else:
                    G.add_edge(user_handle, current_user)
    progress_users.close()
    print(f"[*] Total nodos: {len(G.nodes())}, aristas: {len(G.edges())}")
    return G

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
                response = getattr(client.app.bsky.graph, f"get_{direction}")(params)
                page_data = getattr(response, direction)
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

def export_graph(G, prefix):
    gexf_file = f"{prefix}.gexf"
    node_csv = f"{prefix}_nodes.csv"
    edge_csv = f"{prefix}_edges.csv"

    print(f"[*] Exportando a {gexf_file}, {node_csv}, {edge_csv}")
    nx.write_gexf(G, gexf_file)

    with open(node_csv, "w", newline='', encoding='utf-8') as fn:
        writer = csv.writer(fn)
        writer.writerow(['handle', 'displayName', 'description', 'avatar',
                         'followersCount', 'followsCount', 'postsCount', 'topicLabel'])
        for n, d in G.nodes(data=True):
            writer.writerow([
                n,
                clean_text(d.get("displayName", "")),
                clean_text(d.get("description", "")),
                d.get("avatar", ""),
                d.get("followersCount", 0),
                d.get("followsCount", 0),
                d.get("postsCount", 0),
                d.get("topicLabel", "other")
            ])
    with open(edge_csv, "w", newline='', encoding='utf-8') as fe:
        writer = csv.writer(fe)
        writer.writerow(["source", "target"])
        for s, t in G.edges():
            writer.writerow([s, t])

def clean_existing_files(prefix):
    files = [f"{prefix}.gexf", f"{prefix}_nodes.csv", f"{prefix}_edges.csv"]
    for file in files:
        if os.path.exists(file):
            print(f"[*] Limpiando archivo: {file}")
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = clean_text(content)
            with open(file, "w", encoding="utf-8") as f:
                f.write(cleaned)
        else:
            print(f"[!] Archivo no encontrado: {file}")

def load_graph_from_gexf(prefix):
    path = f"{prefix}.gexf"
    print(f"[*] Cargando grafo desde {path}")
    return nx.read_gexf(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bluesky Network Export Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    exp = subparsers.add_parser("export")
    exp.add_argument("--handle", required=True)
    exp.add_argument("--app-password", required=True)
    exp.add_argument("--target", required=True)
    exp.add_argument("--output-prefix", default="bluesky_graph")
    exp.add_argument("--limit", type=int, default=100)
    exp.add_argument("--depth", type=int, default=2)
    exp.add_argument("--delay", type=float, default=0.0)

    clean = subparsers.add_parser("clean")
    clean.add_argument("--input-prefix", required=True)

    assort = subparsers.add_parser("assortativity")
    assort.add_argument("--input-prefix", required=True)

    args = parser.parse_args()

    if args.command == "export":
        G = fetch_full_network(
            handle=args.handle,
            app_password=args.app_password,
            target_user=args.target,
            output_prefix=args.output_prefix,
            limit=args.limit,
            depth=args.depth,
            delay=args.delay
        )
        export_graph(G, args.output_prefix)

    elif args.command == "clean":
        clean_existing_files(args.input_prefix)

    elif args.command == "assortativity":
        G = load_graph_from_gexf(args.input_prefix)
        compute_assortativity(G)
