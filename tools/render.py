"""Renderiza slides da Martins Bastos (1080x1350 feed, 1080x1920 story) a partir de um JSON.

Uso: python3 render.py post.json saida_dir
post.json: {"slides":[{"kind":"cover|tip|cta|story", ...campos}]}
"""
import base64, json, sys, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
LOGO = "data:image/png;base64," + base64.b64encode((HERE / "logo.png").read_bytes()).decode()

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Montserrat:wght@400;500;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:%(H)dpx;overflow:hidden;font-family:'Montserrat',sans-serif;color:#4A3426;
 background:radial-gradient(ellipse at 50%% 35%%,#FBF5EA 0%%,#F6EBDA 55%%,#EEDCC3 100%%)}
.page{position:relative;width:1080px;height:%(H)dpx;padding:90px 96px;display:flex;flex-direction:column}
.kicker{font-weight:600;letter-spacing:.32em;font-size:24px;color:#A97C45;text-transform:uppercase}
h1{font-family:'Playfair Display',serif;font-weight:700;font-size:92px;line-height:1.05;color:#3E2B1F}
h1 em{font-style:italic;font-weight:600;color:#A97C45}
h2{font-family:'Playfair Display',serif;font-weight:700;font-size:72px;line-height:1.08;color:#3E2B1F}
p.body{font-size:36px;line-height:1.5;color:#5A4334;font-weight:500}
.num{font-family:'Playfair Display',serif;font-style:italic;font-size:220px;line-height:.9;color:#C9A574;opacity:.85}
.rule{width:120px;height:4px;background:#B8894D;border-radius:2px;margin:36px 0}
.logo{width:300px}
.foot{position:absolute;left:96px;right:96px;bottom:70px;display:flex;justify-content:space-between;align-items:center;font-size:24px;letter-spacing:.24em;font-weight:600;color:#A97C45;text-transform:uppercase}
.foot img{width:170px}
.plane{position:absolute;right:90px;top:90px;font-size:56px;color:#B8894D;opacity:.7}
.card{background:rgba(255,255,255,.55);border:2px solid rgba(184,137,77,.35);border-radius:28px;padding:44px 48px}
.hl{background:linear-gradient(transparent 62%%,rgba(201,165,116,.45) 62%%)}
.btn{display:inline-block;background:#4A3426;color:#FBF5EA;font-weight:600;font-size:34px;padding:26px 46px;border-radius:60px;letter-spacing:.02em}
"""

def slide_html(s, H):
    k = s["kind"]
    if k == "cover":
        inner = f"""
        <div style="display:flex;justify-content:center;margin-top:10px"><img class="logo" src="{LOGO}"></div>
        <div style="margin-top:auto;margin-bottom:auto;text-align:center">
          <div class="kicker">{s.get('kicker','')}</div>
          <h1 style="margin-top:34px">{s['title']}</h1>
          <div class="rule" style="margin:40px auto"></div>
          <p class="body">{s.get('subtitle','')}</p>
        </div>
        <div style="text-align:center" class="kicker">Arraste para o lado &nbsp;→</div>"""
    elif k == "single":  # post de imagem única (frase, destino, enquete) — sem "arraste para o lado"
        opts = "".join(f'<div class="card" style="padding:26px 40px;margin-top:20px;text-align:left"><p class="body" style="font-size:34px">{o}</p></div>' for o in s.get("options", []))
        inner = f"""
        <div style="display:flex;justify-content:center;margin-top:10px"><img class="logo" src="{LOGO}"></div>
        <div style="margin-top:auto;margin-bottom:auto;text-align:center">
          <div class="kicker">{s.get('kicker','')}</div>
          <h1 style="margin-top:34px;font-size:{s.get('size',88)}px">{s['title']}</h1>
          <div class="rule" style="margin:40px auto"></div>
          {f'<p class="body">{s["subtitle"]}</p>' if s.get('subtitle') else ''}
          {opts}
        </div>
        <div style="text-align:center" class="kicker">{s.get('footer','Salve e compartilhe com quem viaja com você')}</div>"""
    elif k == "tip":
        inner = f"""
        <div class="plane">✈</div>
        <div style="margin-top:auto;margin-bottom:auto;padding-bottom:80px">
        <div class="num">{s['n']}</div>
        <h2 style="margin-top:10px">{s['title']}</h2>
        <div class="rule"></div>
        <p class="body">{s['text']}</p>
        {f'<div class="card" style="margin-top:46px"><p class="body" style="font-size:32px"><b>Dica Martins Bastos:</b> {s["extra"]}</p></div>' if s.get('extra') else ''}
        </div>
        <div class="foot"><span>{s.get('page','')}</span><img src="{LOGO}"></div>"""
    elif k == "cta":
        inner = f"""
        <div style="display:flex;justify-content:center"><img class="logo" style="width:380px" src="{LOGO}"></div>
        <div style="margin:auto 0;text-align:center">
          <h2>{s['title']}</h2>
          <div class="rule" style="margin:40px auto"></div>
          <p class="body">{s['text']}</p>
          <div style="margin-top:56px"><span class="btn">{s.get('button','Chama no WhatsApp')}</span></div>
          <p class="body" style="margin-top:34px;font-weight:700;color:#3E2B1F">{s.get('contact','')}</p>
        </div>
        <div style="text-align:center" class="kicker">Salve e compartilhe com quem viaja com você</div>"""
    elif k == "story":
        inner = f"""
        <div style="display:flex;justify-content:center;margin-top:120px"><img class="logo" style="width:380px" src="{LOGO}"></div>
        <div style="margin:auto 0;text-align:center">
          <div class="kicker">{s.get('kicker','')}</div>
          <h1 style="margin-top:40px;font-size:104px">{s['title']}</h1>
          <div class="rule" style="margin:48px auto"></div>
          <p class="body" style="font-size:40px">{s.get('text','')}</p>
        </div>
        <div style="text-align:center;margin-bottom:170px"><span class="btn">{s.get('button','Novo post no feed ✈')}</span></div>"""
    elif k in PHOTO_KINDS:
        return photo_html(s, H)
    else:
        raise ValueError(k)
    return f"<html><head><meta charset='utf-8'><style>{CSS % {'H': H}}</style></head><body><div class='page'>{inner}</div></body></html>"


# ---------------------------------------------------------------------------
# Linha "Cartão-postal" (v2): slides com foto. Campo "photo" = caminho da imagem
# (relativo ao post.json ou à raiz do repositório). "credit" = crédito da foto.
# ---------------------------------------------------------------------------
PHOTO_KINDS = {"photo_cover", "postcard", "photo_tip", "versus", "photo_cta", "photo_story"}
BASE = pathlib.Path(".")

def img(path):
    p = pathlib.Path(path)
    for c in (BASE / p, HERE.parent / p, p):
        if c.exists():
            mime = "png" if c.suffix.lower() == ".png" else "jpeg"
            return f"data:image/{mime};base64," + base64.b64encode(c.read_bytes()).decode()
    raise FileNotFoundError(path)

PCSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,500;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:%(H)dpx;overflow:hidden;font-family:'Montserrat',sans-serif;background:#F6EBDA;color:#3E2B1F}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(25,15,8,.35) 0%%,rgba(25,15,8,0) 28%%,rgba(25,15,8,0) 42%%,rgba(25,15,8,.82) 100%%)}
.kick{font-weight:700;letter-spacing:.3em;font-size:24px;text-transform:uppercase;color:#E9C48E}
.kick.dark{color:#A97C45}
.disp{font-family:'Playfair Display',serif;font-weight:800;line-height:1.02;letter-spacing:-.01em}
.disp em{font-style:italic;font-weight:600;color:#E9C48E}
.dark .disp em,.disp.dk em{color:#A97C45}
.lead{font-size:34px;line-height:1.45;font-weight:500}
.badge{position:absolute;width:150px;height:150px;border-radius:50%%;background:#FBF5EA;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.badge img{width:128px}
.credit{position:absolute;font-size:16px;letter-spacing:.06em;color:rgba(255,255,255,.75)}
.credit.dk{color:#9C8470}
.pill{display:inline-block;background:#FBF5EA;color:#3E2B1F;font-weight:700;font-size:32px;padding:24px 44px;border-radius:60px}
.swipe{font-weight:700;letter-spacing:.28em;font-size:22px;text-transform:uppercase;color:#FBF5EA}
.num{font-family:'Playfair Display',serif;font-style:italic;font-weight:600;color:#C9A574}
.rule{width:110px;height:4px;background:#C9A574;border-radius:2px}
.stamp{position:absolute;border:3px dashed rgba(169,124,69,.55);border-radius:14px;padding:12px 18px;font-weight:700;font-size:20px;letter-spacing:.2em;color:#A97C45;text-transform:uppercase;transform:rotate(-6deg)}
"""

def photo_html(s, H):
    k = s["kind"]
    cr = s.get("credit", "")
    if k in ("photo_cover", "photo_story", "photo_cta"):
        story = k == "photo_story"
        cta = k == "photo_cta"
        size = s.get("size", 118 if story else 104)
        extra = ""
        if cta:
            extra = f"""<div style="margin-top:44px"><span class="pill">{s.get('button','Chama no WhatsApp')}</span></div>
            <p style="margin-top:26px;font-size:40px;font-weight:700;color:#FBF5EA">{s.get('contact','(22) 99883-9397')}</p>"""
        elif story:
            extra = f"""<div style="margin-top:60px"><span class="pill">{s.get('button','Confira no feed ✈')}</span></div>"""
        foot = "" if (story or cta) else f'<div class="swipe" style="margin-top:46px">{s.get("swipe","Arraste para o lado  →")}</div>'
        bottom = 260 if story else 90
        shade = "linear-gradient(180deg,rgba(25,15,8,.45) 0%,rgba(25,15,8,.55) 100%)" if cta else ""
        inner = f"""<div class="bg" style="background-image:url('{img(s['photo'])}');background-position:{s.get('pos','center')}"></div>
        <div class="shade" {f'style="background:{shade}"' if shade else ''}></div>
        <div class="badge" style="top:{150 if story else 64}px;left:64px"><img src="{LOGO}"></div>
        <div style="position:absolute;left:84px;right:84px;bottom:{bottom}px;color:#FBF5EA{';text-align:center' if cta else ''}">
          <div class="kick">{s.get('kicker','')}</div>
          <h1 class="disp" style="font-size:{size}px;margin-top:26px">{s['title']}</h1>
          {f'<p class="lead" style="margin-top:28px;color:#F3E6D3">{s["text"]}</p>' if s.get('text') else ''}
          {extra}{foot}
        </div>
        {f'<div class="credit" style="top:{170 if story else 84}px;right:64px">{cr}</div>' if cr else ''}"""
    elif k == "postcard":
        inner = f"""<div class="bg" style="height:830px;background-image:url('{img(s['photo'])}');background-position:{s.get('pos','center')}"></div>
        {f'<div class="credit" style="top:790px;left:64px">{cr}</div>' if cr else ''}
        <div style="position:absolute;top:830px;left:0;right:0;bottom:0;background:#FBF5EA;padding:70px 84px 0">
          <div class="kick dark">{s.get('kicker','')}</div>
          <h1 class="disp dk" style="font-size:{s.get('size',76)}px;margin-top:20px">{s['title']}</h1>
          {f'<p class="lead" style="margin-top:22px;font-size:30px;color:#5A4334">{s["text"]}</p>' if s.get('text') else ''}
        </div>
        <div class="badge" style="top:755px;right:84px"><img src="{LOGO}"></div>
        {f'<div class="stamp" style="bottom:56px;right:84px">{s["stamp"]}</div>' if s.get('stamp') else ''}"""
    elif k == "photo_tip":
        inner = f"""<div class="bg" style="height:600px;background-image:url('{img(s['photo'])}');background-position:{s.get('pos','center')}"></div>
        {f'<div class="credit" style="top:560px;left:64px">{cr}</div>' if cr else ''}
        <div style="position:absolute;top:600px;left:0;right:0;bottom:0;background:#FBF5EA;padding:0 84px">
          <div class="num" style="font-size:200px;line-height:1;margin-top:-110px;text-shadow:0 4px 24px rgba(0,0,0,.25);color:#FBF5EA">{s['n']}</div>
          <h2 class="disp dk" style="font-size:74px;margin-top:24px">{s['title']}</h2>
          <div class="rule" style="margin:30px 0"></div>
          <p class="lead" style="font-size:36px;color:#5A4334">{s['text']}</p>
        </div>
        <div style="position:absolute;left:84px;right:84px;bottom:56px;display:flex;justify-content:space-between;align-items:center">
          <span class="kick dark" style="font-size:20px">{s.get('page','')}</span><img src="{LOGO}" style="width:120px"></div>"""
    elif k == "versus":
        a, b = s["options"]
        def half(o, side):
            return f"""<div style="position:absolute;top:0;bottom:0;{side}:0;width:540px;overflow:hidden">
              <div class="bg" style="background-image:url('{img(o['photo'])}');background-position:{o.get('pos','center')}"></div>
              <div class="bg" style="background:linear-gradient(180deg,rgba(25,15,8,0) 45%,rgba(25,15,8,.8) 100%)"></div>
              <div style="position:absolute;left:44px;right:44px;bottom:90px;color:#FBF5EA">
                <div class="kick" style="font-size:22px">{o.get('kicker','')}</div>
                <div class="disp" style="font-size:72px;margin-top:12px">{o['label']}</div>
                <p style="font-size:26px;margin-top:12px;line-height:1.4;font-weight:500">{o.get('text','')}</p></div></div>"""
        inner = f"""{half(a,'left')}{half(b,'right')}
        <div style="position:absolute;top:0;left:0;right:0;background:#FBF5EA;padding:46px 64px 40px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.2)">
          <div class="kick dark" style="font-size:22px">{s.get('kicker','')}</div>
          <h1 class="disp dk" style="font-size:64px;margin-top:14px">{s['title']}</h1></div>
        <div style="position:absolute;left:470px;top:760px;width:140px;height:140px;border-radius:50%;background:#FBF5EA;display:flex;align-items:center;justify-content:center;font-family:'Playfair Display';font-style:italic;font-size:58px;font-weight:600;color:#A97C45;box-shadow:0 10px 30px rgba(0,0,0,.3)">ou</div>"""
    return f"<html><head><meta charset='utf-8'><style>{PCSS % {'H': H}}</style></head><body><div style='position:relative;width:1080px;height:{H}px;overflow:hidden'>{inner}</div></body></html>"


def main(src, out):
    global BASE
    data = json.loads(pathlib.Path(src).read_text())
    BASE = pathlib.Path(src).parent
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for i, s in enumerate(data["slides"], 1):
            H = 1920 if s["kind"].endswith("story") else 1350
            pg = b.new_page(viewport={"width": 1080, "height": H})
            pg.set_content(slide_html(s, H), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            f = out / f"{i:02d}_{s['kind']}.jpg"
            pg.screenshot(path=str(f), type="jpeg", quality=92)
            files.append(str(f)); pg.close()
        b.close()
    print("\n".join(files))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
