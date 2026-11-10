"""Cria um post no Zernio (carrossel/imagem + story opcional) usando imagens já enviadas a este repositório.

Uso:
  python3 tools/zernio.py posts/<pasta>               -> salva como RASCUNHO
  python3 tools/zernio.py posts/<pasta> 2026-11-11T19:00:00  -> AGENDA (horário de Brasília)

A pasta precisa conter: legenda.txt (ou caption*.txt) e os .jpg. Arquivos *_story.jpg viram Story;
os demais (em ordem alfabética) viram o post do feed. O story é publicado às 12h do mesmo dia.
Faça commit + push da pasta ANTES de rodar (o Zernio busca as imagens no GitHub).
Chave: variável ZERNIO_API_KEY ou arquivo ~/.zernio/key.
"""
import json, os, pathlib, sys, urllib.request, urllib.error

KEY = os.environ.get("ZERNIO_API_KEY") or pathlib.Path("~/.zernio/key").expanduser().read_text().strip()
ACCOUNT = "6af24526b4772ff9a2eb8254"  # @martinsbastosviagens
API = "https://zernio.com/api/v1"
RAW = "https://raw.githubusercontent.com/martinsbastosviagenseturismo-cmd/martinsbastos-instagram/main/"


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Zernio {e.code}: {e.read().decode()[:1500]}")


def main(folder, when=None):
    folder = pathlib.Path(folder)
    rel = folder.as_posix().split("posts/", 1)[1]
    files = sorted(folder.glob("*.jpg"))
    cap = next(iter(sorted(folder.glob("legenda*.txt")) + sorted(folder.glob("caption*.txt"))))
    feed = [f for f in files if not f.stem.endswith("_story")]
    story = [f for f in files if f.stem.endswith("_story")]
    url = lambda f: RAW + "posts/" + rel + "/" + f.name
    entry = {"platform": "instagram", "accountId": ACCOUNT}
    platforms = [dict(entry)]
    if story:
        st = {**entry, "customMedia": [{"type": "image", "url": url(story[0])}],
              "platformSpecificData": {"contentType": "story"}}
        if when:
            st["scheduledFor"] = when[:10] + "T12:00:00"
        platforms.append(st)
    body = {"content": cap.read_text().strip(), "mediaItems": [{"type": "image", "url": url(f)} for f in feed],
            "platforms": platforms, "timezone": "America/Sao_Paulo"}
    if when:
        body["scheduledFor"] = when
    post = call("POST", "/posts", body).get("post", {})
    print(json.dumps({"id": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor"),
                      "platforms": [(p.get("platformSpecificData") or {}).get("contentType", "feed") + ":" + str(p.get("scheduledFor") or p.get("status")) for p in post.get("platforms", [])]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
