import argparse
import pandas as pd
import networkx as nx
from atproto import Client
import time

def fetch_posts_and_replies(client, handles, limit_per_user, delay=1.0, max_replies_per_post=None):
    all_posts = []
    seen_uris = set()
    for handle in handles:
        print(f"📥 Descargando posts de: {handle}")
        try:
            feed = client.app.bsky.feed.get_author_feed({'actor': handle, 'limit': limit_per_user})
            posts = feed.feed
            for item in posts:
                post_data = item.post
                post_uri = post_data.uri
                if post_uri in seen_uris:
                    continue
                seen_uris.add(post_uri)

                main_post = {
                    'id': post_data.uri.split("/")[-1],
                    'date': post_data.record.created_at,
                    'name': handle,
                    'username': handle,
                    'text': post_data.record.text,
                    'url': f"https://bsky.app/profile/{handle}/post/{post_data.uri.split('/')[-1]}",
                    'referenced_post_id': post_data.record.reply.parent.uri.split("/")[-1] if post_data.record.reply else None,
                    'referenced_username': post_data.record.reply.parent.uri.split("/")[2] if post_data.record.reply else None,
                    'referenced_post_type': 'replied_to' if post_data.record.reply else None,
                    'referenced_post_url': f"https://bsky.app/profile/{post_data.record.reply.parent.uri.split('/')[2]}/post/{post_data.record.reply.parent.uri.split('/')[-1]}" if post_data.record.reply else None,
                    'like_count': None,
                    'reply_count': None,
                    'repost_count': None,
                    'links': [],
                    'alt_texts': []
                }
                all_posts.append(main_post)


                # Detectar quotes
                if hasattr(post_data.record, "embed") and hasattr(post_data.record.embed, "record"):
                    try:
                        quoted = post_data.record.embed.record
                        quoted_user = getattr(getattr(quoted, "author", None), "handle", None)
                        quoted_uri = getattr(quoted, "uri", None)
                        if quoted_user and quoted_uri:
                            quote_data = {
                                'id': post_data.uri.split('/')[-1],
                                'date': post_data.record.created_at,
                                'name': post_data.author.handle,
                                'username': post_data.author.handle,
                                'text': post_data.record.text,
                                'url': f"https://bsky.app/profile/{post_data.author.handle}/post/{post_data.uri.split('/')[-1]}",
                                'referenced_post_id': quoted_uri.split("/")[-1],
                                'referenced_username': quoted_user,
                                'referenced_post_type': 'reply_or_quote',
                                'referenced_post_url': f"https://bsky.app/profile/{quoted_user}/post/{quoted_uri.split('/')[-1]}",
                                'like_count': None,
                                'reply_count': None,
                                'repost_count': None,
                                'links': [],
                                'alt_texts': []
                            }
                            all_posts.append(quote_data)
                    except Exception as e:
                        print(f"[!] Error al procesar quote de {quoted_user}: {e}")

                # Fetch replies to this post
                try:
                    thread = client.app.bsky.feed.get_post_thread({'uri': post_uri})
                    replies = thread.thread.replies or []
                    for i, reply_item in enumerate(replies):
                        if max_replies_per_post is not None and i >= max_replies_per_post:
                            break
                        if hasattr(reply_item, 'post'):
                            reply_post = reply_item.post
                            reply_uri = reply_post.uri
                            if reply_uri in seen_uris:
                                continue
                            seen_uris.add(reply_uri)

                            author = reply_post.author.handle
                            reply_data = {
                                'id': reply_uri.split("/")[-1],
                                'date': reply_post.record.created_at,
                                'name': author,
                                'username': author,
                                'text': reply_post.record.text,
                                'url': f"https://bsky.app/profile/{author}/post/{reply_uri.split('/')[-1]}",
                                'referenced_post_id': post_data.uri.split("/")[-1],
                                'referenced_username': handle,
                                'referenced_post_type': 'reply_or_quote',
                                'referenced_post_url': f"https://bsky.app/profile/{handle}/post/{post_data.uri.split('/')[-1]}",
                                'like_count': None,
                                'reply_count': None,
                                'repost_count': None,
                                'links': [],
                                'alt_texts': []
                            }
                            all_posts.append(reply_data)
                except Exception as e:
                    print(f"⚠️ No se pudieron traer respuestas para {post_uri}: {e}")

                time.sleep(delay)
        except Exception as e:
            print(f"❌ Error al descargar de {handle}: {e}")
    return all_posts


def build_graph(posts):
    G = nx.DiGraph()
    for post in posts:
        src = post.get("username")
        tgt = post.get("referenced_username")
        rel_type = post.get("referenced_post_type")

        if src:
            G.add_node(src)
        if tgt:
            G.add_node(tgt)

        if src and tgt and rel_type:
            G.add_edge(src, tgt, type=rel_type,
                       text=post.get("text", "")[:100],
                       source_post=post.get("url"),
                       target_post=post.get("referenced_post_url"),
                       date=str(post.get("date")))

    # Agregar atributos de nodos (conteo de posts como ejemplo)
    from collections import Counter
    count_posts = Counter(p['username'] for p in posts if p.get('username'))
    nx.set_node_attributes(G, count_posts, "post_count")
    followers = {post['username']: post.get('followersCount') for post in posts if 'followersCount' in post}
    nx.set_node_attributes(G, followers, 'followersCount')
    follows = {post['username']: post.get('followsCount') for post in posts if 'followsCount' in post}
    nx.set_node_attributes(G, follows, 'followsCount')
    posts = {post['username']: post.get('postsCount') for post in posts if 'postsCount' in post}
    nx.set_node_attributes(G, posts, 'postsCount')
    topics = {post['username']: post.get('topicLabel') for post in posts if 'topicLabel' in post}
    nx.set_node_attributes(G, topics, 'topicLabel')
    created = {post['username']: str(post['date']) for post in posts if 'date' in post}
    nx.set_node_attributes(G, created, 'created_at')

    return G

def main():
    parser = argparse.ArgumentParser(description="Descarga posts y replies de Bluesky y genera red reply/quote")
    parser.add_argument('--handle', required=True, help="Tu handle de Bluesky")
    parser.add_argument('--app-password', required=True, help="Tu app password de Bluesky")
    parser.add_argument('--targets', nargs='+', required=True, help="Lista de handles objetivo")
    parser.add_argument('--limit', type=int, default=100, help="Número de posts por usuario objetivo")
    parser.add_argument('--output-prefix', default='bluesky_extended', help="Prefijo para los ficheros de salida")
    parser.add_argument('--max-replies-per-post', type=int, default=None, help="Número máximo de replies por post original")
    args = parser.parse_args()

    print("🔐 Autenticando...")
    client = Client()
    client.login(args.handle, args.app_password)
    print(f"[+] Login exitoso como {client.me}")

    posts = fetch_posts_and_replies(client, [h.lstrip('@') for h in args.targets if h.strip()], args.limit, max_replies_per_post=args.max_replies_per_post)

    print("💾 Guardando Excel...")
    df = pd.DataFrame(posts)
    if not df.empty and 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.tz_localize(None)
    else:
        print("⚠️ No se han descargado posts o falta la columna 'date'.")
    df.to_excel(f"{args.output_prefix}.xlsx", index=False)

    print("🔗 Construyendo grafo...")
    G = build_graph(posts)
    nx.write_graphml(G, f"{args.output_prefix}.graphml")
    nx.write_gexf(G, f"{args.output_prefix}.gexf")
    
    print("✅ Exportación completada.")

if __name__ == "__main__":
    main()
