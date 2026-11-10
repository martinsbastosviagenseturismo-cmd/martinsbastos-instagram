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
    else:
        raise ValueError(k)
    return f"<html><head><meta charset='utf-8'><style>{CSS % {'H': H}}</style></head><body><div class='page'>{inner}</div></body></html>"


def main(src, out):
    data = json.loads(pathlib.Path(src).read_text())
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for i, s in enumerate(data["slides"], 1):
            H = 1920 if s["kind"] == "story" else 1350
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
