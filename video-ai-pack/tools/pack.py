#!/usr/bin/env python3
"""Video AI Pack — roteador de skills + cofre local (vault) das 100 melhores skills de vídeo.

Em vez de instalar 100 skills (cada uma custaria tokens fixos em toda sessão e competiria
pelo gatilho), o pack guarda os SKILL.md num cofre fora de ~/.claude/skills e, a cada pedido,
o roteador escolhe só as 2–5 relevantes dentro de um orçamento de tokens.

Uso:
  pack.py sync [--force]                 baixa os SKILL.md do catálogo para o cofre
  pack.py route "pedido" [--json]        mostra quais skills seriam carregadas
  pack.py list [--cat X] [--tier ouro]   lista o catálogo
  pack.py install ID|RANK [args...]      instala a skill completa (scripts/references) via `npx skills add`
  pack.py config [--apps premiere,resolve,aftereffects] [--apis elevenlabs,openai] [--budget 6000]
  pack.py stats                          custo de tokens: pack vs. instalar tudo
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
# instalado: pack.py, skills.json, config.json e vault/ ficam juntos em ~/.claude/video-ai-pack
HOME = Path(os.environ.get("VIDEO_PACK_HOME") or (HERE if (HERE / "skills.json").exists() else Path.home() / ".claude" / "video-ai-pack"))
CATALOG = next((p for p in (HERE / "skills.json", HERE.parent / "catalogo" / "skills.json", HOME / "skills.json") if p.exists()), None)
VAULT = HOME / "vault"
CONFIG = HOME / "config.json"
DEFAULT_CFG = {"apps": [], "apis": [], "budget": 7000, "max_skills": 5}
UNKNOWN_TOKENS = 2500

INTENTS = {
    "decupagem": r"decupa|rough ?cut|corte (seco|bruto)|cortar|corta\b|silenc|jump ?cut|pausas|respira|melhores (takes|momentos|partes)|takes?\b|retake|highlight|sizzle|montagem|montar|enxugar|tighten|edita|editar|edição",
    "cor": r"color ?grad|colori[zs]|\bcor(es)?\b|\bgrade\b|\bluts?\b|look|cinematogr|cinematic|teal|balan[cç]o de branco|white balance|exposi[cç]|\blog\b|rec ?709|s-?log|c-?log|v-?log",
    "legendas": r"legenda|subtitle|caption|\bsrt\b|\bvtt\b|transcri|karaok|hormozi",
    "motion": r"motion|after ?effects|\bae\b|anima|lower ?third|vinheta|kinetic|tipografia|keyframe|express[aã]o|logo|intro\b|outro\b|transi[cç]|lottie|t[ií]tulo",
    "audio": r"[aá]udio|ru[ií]do|noise|\bvoz\b|locu[cç]|narra|trilha|m[uú]sica|sfx|efeito sonoro|loudness|lufs|mixag|podcast",
    "entrega": r"export|render|entreg|formato|codec|h\.?26[45]|prores|bitrate|vers[aã]o (para|pra)",
    "social": r"reels?\b|shorts?\b|tiktok|vertical|9:16|instagram|thumbnail|miniatura|viral|gancho|\bhook\b|youtube seo",
    "programatico": r"remotion|hyperframes|program[aá]tic|template de v[ií]deo|em lote|v[ií]deo com (react|c[oó]digo)",
    "analise": r"assist[ae]|analis[ae]|resum[aoi]|entender o v[ií]deo|o que acontece|baixa[r]? (o )?v[ií]deo|yt-dlp|frames?\b",
    "geracao": r"ger(e|ar|a) (um )?(v[ií]deo|b-?roll|cena|clipe)|text[o]?[- ]to[- ]video|image[m]?[- ]to[- ]video|veo|kling|sora|seedance|avatar|b-?roll gerad",
}
APPS = {
    "premiere": r"premiere|\bppro\b|prproj",
    "resolve": r"davinci|\bresolve\b|fusion|fairlight",
    "aftereffects": r"after ?effects|\bae\b|\.aep\b|extendscript",
    "remotion": r"remotion",
    "hyperframes": r"hyperframes",
    "capcut": r"capcut|jianying",
}
APIS = {"elevenlabs": r"elevenlabs", "openai": r"openai|whisper api", "higgsfield": r"higgsfield",
        "inference": r"inference\.sh", "google": r"\bveo\b|gemini", "fal": r"fal\.ai|\bfal\b",
        "noiz": r"noiz", "deepgram": r"deepgram", "eachlabs": r"eachlabs"}
VIDEO_GATE = r"v[ií]deo|video|clip|footage|filmag|timeline|sequ[eê]ncia|edi[cç][aã]o|editar|montagem|premiere|after ?effects|resolve|davinci|reels|shorts|tiktok|youtube|\.(mp4|mov|mxf|braw|r3d|mkv)\b|legenda|colorgrad|motion|decupa|remotion|hyperframes|lottie|podcast"
# skills próprias do pack que cobrem cada intenção
OWN = {"decupagem": "video-decupagem", "cor": "video-colorgrade", "legendas": "video-legendas",
       "motion": "video-motion", "entrega": "video-entrega", "social": "video-entrega"}
# categorias do catálogo consultadas por intenção (em ordem de preferência)
CATS = {"decupagem": ["decupagem"], "cor": ["cor"], "legendas": ["legendas"], "motion": ["motion"],
        "audio": ["audio"], "entrega": ["entrega"], "social": ["social", "entrega"],
        "programatico": ["programatico"], "analise": ["analise"], "geracao": ["geracao"]}
# skill de entrada de cada app (carregada sempre que o app é citado)
APP_ENTRY = {"premiere": ["leancoderkavy/premiere-pro-mcp/edit-premiere-project", "hetpatel-11/adobe_premiere_pro_mcp/premiere-pro-mcp"],
             "resolve": ["samuelgursky/davinci-resolve-mcp/resolve-session"],
             "aftereffects": ["iart-ai/motion-design-skills/after-effects"],
             "remotion": ["remotion-dev/skills/remotion-best-practices"],
             "hyperframes": ["heygen-com/hyperframes/hyperframes"],
             "capcut": ["renezander030/capcut-cli/capcut-edit"]}


def load_catalog():
    if not CATALOG:
        sys.exit("catálogo skills.json não encontrado (rode o instalador)")
    return json.loads(CATALOG.read_text())["skills"]


def load_cfg():
    cfg = dict(DEFAULT_CFG)
    try:
        cfg.update(json.loads(CONFIG.read_text()))
    except (OSError, ValueError):
        pass
    return cfg


def vault_path(sid):
    return VAULT / (sid.replace("/", "__") + ".md")


def norm(text):
    """minúsculas e sem acentos: 'Silêncios' -> 'silencios' (os regex aceitam as duas formas)."""
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def is_video(prompt):
    return bool(re.search(VIDEO_GATE, norm(prompt)))


def detect(prompt):
    p = norm(prompt)
    intents = [k for k, rx in INTENTS.items() if re.search(rx, p)]
    apps = [k for k, rx in APPS.items() if re.search(rx, p)]
    apis = [k for k, rx in APIS.items() if re.search(rx, p)]
    return intents, apps, apis


def route(prompt, cfg=None, catalog=None):
    cfg = cfg or load_cfg()
    catalog = catalog or load_catalog()
    by_id = {s["id"]: s for s in catalog}
    intents, apps, apis = detect(prompt)
    if not intents:
        intents = ["decupagem", "cor", "legendas", "entrega"]
    allowed_apps = set(apps) or set(cfg["apps"])
    allowed_apis = set(apis) | set(cfg["apis"])

    def ok(s):
        if s["app"] and s["app"] not in allowed_apps:
            return False
        if s["api"] and s["api"] not in allowed_apis:
            return False
        return True

    def cost(s):
        return s["tokens_corpo"] or UNKNOWN_TOKENS

    picked, used = [], 0

    def take(s, motivo):
        nonlocal used
        if s["id"] in {p["id"] for p, _ in picked} or len(picked) >= cfg["max_skills"]:
            return False
        if used + cost(s) > cfg["budget"]:
            return False
        picked.append((s, motivo))
        used += cost(s)
        return True

    # 1) skill de entrada dos apps citados explicitamente
    for a in apps:
        for sid in APP_ENTRY.get(a, []):
            if sid in by_id and take(by_id[sid], f"app citado: {a}"):
                break
    # 2) melhor skill por intenção; app citado tem prioridade dentro da categoria
    ranked = sorted(catalog, key=lambda s: -s["nota"])
    for it in intents:
        cands = [s for s in ranked if s["categoria"] in CATS.get(it, []) and ok(s)]
        cands.sort(key=lambda s: (s["app"] not in apps if apps else False, -s["nota"]))
        for s in cands:
            if take(s, f"intenção: {it}"):
                break
    # 3) segunda opção para intenções principais, se sobrar orçamento
    for it in intents[:2]:
        for s in [s for s in ranked if s["categoria"] in CATS.get(it, []) and ok(s)][1:3]:
            if take(s, f"reforço: {it}"):
                break
    own = sorted({OWN[i] for i in intents if i in OWN} | {"video-entrega"})
    return {"intents": intents, "apps": apps, "apis": sorted(allowed_apis), "own_skills": own,
            "skills": [dict(id=s["id"], nota=s["nota"], tokens=cost(s), motivo=m, requisito=s["requisito"],
                            arquivo=str(vault_path(s["id"])) if vault_path(s["id"]).exists() else None,
                            raw=s["raw"], instalar=s["instalar"]) for s, m in picked],
            "tokens_estimados": used, "orcamento": cfg["budget"]}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "video-ai-pack"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def cmd_sync(force=False):
    VAULT.mkdir(parents=True, exist_ok=True)
    ok = skip = fail = 0
    for s in load_catalog():
        dst = vault_path(s["id"])
        if not s["raw"]:
            skip += 1
            continue
        if dst.exists() and not force:
            ok += 1
            continue
        url = s["raw"] if s["raw"].startswith("http") else f"https://raw.githubusercontent.com/{s['raw']}"
        try:
            body = fetch(url)
            header = (f"<!-- video-ai-pack vault | {s['id']} | nota {s['nota']} | {s['requisito']}\n"
                      f"     fonte: {url}\n     skill completa (scripts/references): {s['instalar']} -->\n\n")
            dst.write_text(header + body, encoding="utf-8")
            ok += 1
        except Exception as e:  # rede, 404, etc.
            print(f"  falhou {s['id']}: {e}", file=sys.stderr)
            fail += 1
    print(f"cofre: {ok} ok, {skip} sem SKILL.md direto (use `pack.py install`), {fail} falhas → {VAULT}")


def cmd_list(cat=None, tier=None):
    for s in load_catalog():
        if (cat and s["categoria"] != cat) or (tier and s["tier"] != tier):
            continue
        t = s["tokens_corpo"] if s["tokens_corpo"] else "n/d"
        print(f"{s['rank']:3} {s['nota']:5} {s['tier']:6} {s['categoria']:12} {str(t):>6}t  {s['id']}  [{s['requisito']}]")


def cmd_install(key, extra):
    cat = load_catalog()
    s = next((x for x in cat if x["id"] == key or str(x["rank"]) == key or x["nome"] == key), None)
    if not s:
        sys.exit(f"skill não encontrada: {key}")
    cmd = ["npx", "-y", "skills", "add", f"https://github.com/{s['repo']}", "--skill", s["nome"], *extra]
    print("$", " ".join(cmd))
    sys.exit(subprocess.call(cmd))


def cmd_config(args):
    cfg = load_cfg()
    it = iter(args)
    for a in it:
        v = next(it, "")
        if a == "--apps":
            cfg["apps"] = [x for x in v.split(",") if x]
        elif a == "--apis":
            cfg["apis"] = [x for x in v.split(",") if x]
        elif a == "--budget":
            cfg["budget"] = int(v)
        elif a == "--max":
            cfg["max_skills"] = int(v)
    HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2))
    print(json.dumps(cfg, indent=2))


def cmd_stats():
    cat = load_catalog()
    desc = sum((s["tokens_descricao"] or 60) for s in cat)
    body = [s["tokens_corpo"] for s in cat if s["tokens_corpo"]]
    n = lambda x: f"{x:,}".replace(",", ".")
    print(f"Instalar as 100 como skills: ~{n(desc)} tokens fixos por sessão (só descrições) + gatilhos concorrentes")
    print(f"Video AI Pack: ~250 tokens fixos (6 descrições próprias) + até {n(load_cfg()['budget'])} por pedido de vídeo, 0 fora dele")
    print(f"Corpo dos SKILL.md: mediana {n(sorted(body)[len(body) // 2])} t | maior {n(max(body))} t | soma {n(sum(body))} t")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "sync":
        cmd_sync("--force" in a)
    elif a[0] == "route":
        r = route(" ".join(x for x in a[1:] if x != "--json"))
        print(json.dumps(r, ensure_ascii=False, indent=2) if "--json" in a else
              "\n".join(f"{s['nota']:5} ~{s['tokens']:>5}t  {s['id']}  ({s['motivo']})" for s in r["skills"])
              + f"\nintenções={r['intents']} apps={r['apps']} total≈{r['tokens_estimados']}t / {r['orcamento']}t")
    elif a[0] == "list":
        cmd_list(a[a.index("--cat") + 1] if "--cat" in a else None, a[a.index("--tier") + 1] if "--tier" in a else None)
    elif a[0] == "install" and len(a) > 1:
        cmd_install(a[1], a[2:])
    elif a[0] == "config":
        cmd_config(a[1:])
    elif a[0] == "stats":
        cmd_stats()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
