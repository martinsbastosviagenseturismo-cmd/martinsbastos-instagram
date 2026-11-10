"""Envia um post (carrossel/imagem + story opcional) ao Zernio como RASCUNHO.

Uso: python3 zernio.py <pasta_com_jpgs> <legenda.txt>
Arquivos *_story.jpg viram Story; os demais (em ordem) viram o post do feed.
Sem scheduledFor/publishNow => o Zernio salva como rascunho.
"""
import json, os, pathlib, sys, urllib.request

KEY = os.environ.get("ZERNIO_API_KEY") or pathlib.Path("~/.zernio/key").expanduser().read_text().strip()
ACCOUNT = "6af24526b4772ff9a2eb8254"  # @martinsbastosviagens
API = "https://zernio.com/api/v1"


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def upload(f):
    p = call("POST", "/media/presign", {"filename": f.name, "contentType": "image/jpeg", "size": f.stat().st_size})
    req = urllib.request.Request(p["uploadUrl"], method="PUT", data=f.read_bytes(), headers={"Content-Type": "image/jpeg"})
    urllib.request.urlopen(req, timeout=120).read()
    return p["publicUrl"]


def main(folder, caption_file, extra=None):
    files = sorted(pathlib.Path(folder).glob("*.jpg"))
    feed = [f for f in files if not f.stem.endswith("_story")]
    story = [f for f in files if f.stem.endswith("_story")]
    feed_urls = [{"type": "image", "url": upload(f)} for f in feed]
    platforms = [{"platform": "instagram", "accountId": ACCOUNT}]
    if story:
        platforms.append({"platform": "instagram", "accountId": ACCOUNT,
                          "customMedia": [{"type": "image", "url": upload(story[0])}],
                          "platformSpecificData": {"contentType": "story"}})
    body = {"content": pathlib.Path(caption_file).read_text().strip(), "mediaItems": feed_urls,
            "platforms": platforms, "timezone": "America/Sao_Paulo"}
    if extra:
        body.update(extra)
    r = call("POST", "/posts", body)
    post = r.get("post", r)
    print(json.dumps({"id": post.get("_id"), "status": post.get("status"), "media": [m["url"] for m in feed_urls]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
