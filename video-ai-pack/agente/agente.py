#!/usr/bin/env python3
"""Video AI Agent: monitoramento, instalação e manutenção automática do Video AI Pack.

Modos:
  saude [--reparar]   confere ferramentas, pack, hook, cofre, MCPs e apps; repara o que faltar
  manutencao          atualiza repositório, pack, cofre, pacotes Python/npm, sistema e limpa logs
  descoberta          monitora o ecossistema (skills.sh, npm, PyPI, GitHub, pesquisa por IA),
                      adota skills novas aprovadas nos critérios e gera relatório
  memoria             regenera skills.md/mcps.md/agentes.md e sincroniza a memória privada (se tiver repo)
  tudo                saude --reparar + manutencao + descoberta
  status              mostra o último resumo

O agente instala sozinho só o que é seguro: atualizações de componentes já aprovados e skills
(arquivos de instrução) auditadas. MCPs/executáveis novos entram no relatório com o comando de
instalação, para você aprovar.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

WIN = os.name == "nt"
HERE = Path(__file__).resolve().parent
AGENT_HOME = Path(os.environ.get("VIDEO_AGENT_HOME") or (
    Path(os.environ.get("LOCALAPPDATA", Path.home())) / "VideoAIAgent" if WIN else Path.home() / ".local/share/video-ai-agent"))
CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME") or Path.home() / ".claude")
PACK_HOME = CLAUDE_HOME / "video-ai-pack"
MEMORIA = CLAUDE_HOME / "memoria"
CFG_PATH = AGENT_HOME / "config.json"
STATE = AGENT_HOME / "estado"
REPORTS = AGENT_HOME / "relatorios"
LOGS = AGENT_HOME / "logs"
OWN_SKILLS = ["video-orquestrador", "video-decupagem", "video-colorgrade", "video-legendas", "video-motion", "video-entrega", "video-audio"]
MCP_NAMES = {"premiere": "premiere-pro", "ae": "aftereffects", "resolve": "davinci-resolve",
             "opusclip": "opusclip", "invideo": "invideo", "higgsfield": "higgsfield"}
# resolve: samuelgursky via npx (o pacote PyPI "davinci-resolve-mcp" é outro projeto e quebra com mcp 2.x)
NPM_PKGS = {"premiere": "premiere-pro-mcp", "ae": "@kumoproductions/mcp-aftereffects", "resolve": "davinci-resolve-mcp"}
PYPI_PKGS = {}
GH_REPOS = ["leancoderkavy/premiere-pro-mcp", "kumoproductions/mcp-aftereffects", "samuelgursky/davinci-resolve-mcp",
            "remotion-dev/skills", "heygen-com/hyperframes", "WyattBlue/auto-editor", "browser-use/video-use"]
WINGET_IDS = ["Gyan.FFmpeg", "OpenJS.NodeJS.LTS", "Git.Git", "Python.Python.3.12"]
QUERIES = ["video editing", "video edit", "premiere", "after effects", "davinci resolve", "color grading", "lut",
           "subtitles", "captions", "transcribe", "ffmpeg", "motion graphics", "motion design", "lottie", "remotion",
           "hyperframes", "rough cut", "silence", "podcast edit", "reels", "shorts", "youtube clip", "b-roll", "voiceover"]
RELEVANT = r"video|edit|caption|subtit|colou?r|lut|grade|premiere|after-?effects|davinci|resolve|ffmpeg|motion|lottie|remotion|hyperframes|transcri|whisper|reel|short|podcast|b-?roll|clip|montage|cut|voice|sfx"
NOISE = r"swiftui|react-native|tailwind|accessibility|app-store|unity|godot|phaser|lark|kubernetes|slides|ppt"
DEFAULT_CFG = {
    "repo_dir": "", "branch": "main", "apps": [], "apis": [], "mcps": [], "budget": 7000,
    "auto_adotar": True, "max_adocoes": 3, "min_installs": 300, "nota_minima": 70, "max_tokens_skill": 6000,
    "atualizar_sistema": True, "pesquisa_ia": True, "retencao_dias": 30, "notificar": True,
    "memoria_repo": "",  # repositório git PRIVADO opcional para sincronizar ~/.claude/memoria entre PC e nuvem
}


# ----------------------------------------------------------------- utilidades
def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    LOGS.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    with open(LOGS / f"agente_{dt.date.today():%Y%m}.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8-sig"))  # tolera BOM de arquivos editados no Windows
    except (OSError, ValueError):
        return default


def save_json(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def cfg():
    c = dict(DEFAULT_CFG)
    c.update(load_json(CFG_PATH, {}))
    return c


def which(name):
    return shutil.which(name)


def run(cmd, timeout=600, cwd=None):
    """Executa sem shell; resolve .cmd/.exe no Windows. Retorna (código, saída)."""
    exe = which(cmd[0]) or cmd[0]
    try:
        p = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=cwd, env={**os.environ, "PYTHONUTF8": "1"})
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def http_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "video-ai-agent", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def http_text(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "video-ai-agent"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


class Lock:
    """Uma execução por vez. Tarefas agendadas que se sobrepõem (ex.: Saúde no logon + Manutenção)
    esperam a outra terminar em vez de falhar: falha com código 1 apareceria como erro no Agendador."""
    ESPERA_MAX = 45 * 60
    VENCIDO = 2 * 3600

    def __enter__(self):
        AGENT_HOME.mkdir(parents=True, exist_ok=True)
        self.p = AGENT_HOME / "agente.lock"
        inicio = time.time()
        while True:
            try:
                fd = os.open(self.p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)  # criação atômica
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.p.stat().st_mtime > self.VENCIDO:  # trava esquecida por queda/desligamento
                        self.p.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.time() - inicio > self.ESPERA_MAX:
                    log("outra execução do agente segue em andamento há mais de 45 min — esta rodada foi pulada")
                    sys.exit(0)
                time.sleep(15)

    def __exit__(self, *a):
        self.p.unlink(missing_ok=True)


class Report:
    def __init__(self, modo):
        self.modo, self.lines, self.alertas = modo, [f"# Video AI Agent — {modo} — {now()}", ""], []

    def add(self, *lines):
        self.lines += lines

    def alert(self, msg):
        self.alertas.append(msg)
        log("ALERTA: " + msg)

    def save(self):
        REPORTS.mkdir(parents=True, exist_ok=True)
        body = "\n".join(self.lines + (["", "## Alertas", *[f"- {a}" for a in self.alertas]] if self.alertas else [])) + "\n"
        path = REPORTS / f"{dt.date.today()}_{self.modo}.md"
        path.write_text(body, encoding="utf-8")
        (REPORTS / "ultimo.md").write_text(body, encoding="utf-8")
        save_json(STATE / "ultimo_resumo.json", {"modo": self.modo, "quando": now(), "alertas": self.alertas,
                                                  "relatorio": str(path)})
        log(f"relatório: {path}")
        return path


# ----------------------------------------------------------------- instalador
def repo_pack_dir(c):
    d = Path(c["repo_dir"]) / "video-ai-pack" if c["repo_dir"] else HERE.parent
    return d if (d / "install.sh").exists() else None


def run_installer(c, rep, extra=()):
    d = repo_pack_dir(c)
    if not d:
        rep.alert("repositório do pack não encontrado (config repo_dir) — não foi possível reinstalar")
        return False
    if WIN:
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(d / "install.ps1")]
        if c["apps"]:
            cmd += ["-Apps", ",".join(c["apps"])]
        if c["apis"]:
            cmd += ["-Apis", ",".join(c["apis"])]
        if c["mcps"]:
            cmd += ["-Mcp", ",".join(c["mcps"])]
        cmd += ["-Budget", str(c["budget"]), *extra]
    else:
        cmd = ["bash", str(d / "install.sh"), "--budget", str(c["budget"])]
        if c["apps"]:
            cmd += ["--apps", ",".join(c["apps"])]
        if c["apis"]:
            cmd += ["--apis", ",".join(c["apis"])]
        if c["mcps"]:
            cmd += ["--mcp", ",".join(c["mcps"])]
        cmd += list(extra)
    log("executando instalador: " + " ".join(cmd))
    rc, out = run(cmd, timeout=1800)
    (LOGS / "ultimo_instalador.log").write_text(out, encoding="utf-8")
    if rc:
        rep.alert(f"instalador terminou com código {rc} (veja logs/ultimo_instalador.log)")
    return rc == 0


def pack_cmd(*args, timeout=600):
    return run([sys.executable, str(PACK_HOME / "pack.py"), *args], timeout=timeout)


# ----------------------------------------------------------------- saúde
def detect_apps():
    found = {}
    if WIN:
        pf = [Path(os.environ.get("ProgramFiles", r"C:\Program Files"))]
        for name, pat in (("premiere", "Adobe/Adobe Premiere Pro*"), ("aftereffects", "Adobe/Adobe After Effects*")):
            hits = sorted(p for base in pf for p in base.glob(pat))
            if hits:
                found[name] = hits[-1].name
        res = pf[0] / "Blackmagic Design" / "DaVinci Resolve" / "Resolve.exe"
        if res.exists():
            found["resolve"] = "DaVinci Resolve"
    else:
        for name, pat in (("premiere", "/Applications/Adobe Premiere Pro*"), ("aftereffects", "/Applications/Adobe After Effects*"),
                          ("resolve", "/Applications/DaVinci Resolve*")):
            hits = sorted(Path("/").glob(pat.lstrip("/")))
            if hits:
                found[name] = hits[-1].name
    return found


def saude(reparar=False):
    c, rep = cfg(), Report("saude")
    checks, acoes = [], set()

    def chk(item, ok, detalhe="", acao=None):
        checks.append((item, ok, detalhe))
        if not ok and acao:
            acoes.add(acao)

    for t in ("git", "node", "npx", "ffmpeg", "ffprobe", "claude"):
        path = which(t)
        out = run([t, "-version" if t.startswith("ff") else "--version"], timeout=60)[1] if path else ""
        ver = out.splitlines()[0][:70] if out else ""
        chk(f"ferramenta {t}", bool(path), ver or "não encontrado — rode instalar-agente.ps1")
    # o teste real é o import do faster_whisper abaixo; aqui só orienta (3.15 não tem wheels do ctranslate2/av)
    chk("python", True, sys.version.split()[0] + ("" if sys.version_info < (3, 14) else
        " — se a transcrição falhar, use 3.12: winget install Python.Python.3.12"))
    for f in ("pack.py", "skills.json", "video_intent.py"):
        chk(f"pack: {f}", (PACK_HOME / f).exists(), str(PACK_HOME / f), "instalador")
    n = len(list((PACK_HOME / "vault").glob("*.md"))) if (PACK_HOME / "vault").exists() else 0
    chk("cofre de skills", n >= 80, f"{n} arquivos", "sync")
    settings = load_json(CLAUDE_HOME / "settings.json", {})
    hook_ok = "video_intent.py" in json.dumps(settings.get("hooks", {}))
    chk("hook UserPromptSubmit", hook_ok, str(CLAUDE_HOME / "settings.json"), "instalador")
    miss = [s for s in OWN_SKILLS if not (CLAUDE_HOME / "skills" / s / "SKILL.md").exists()]
    chk("skills do pack", not miss, "faltando: " + ", ".join(miss) if miss else f"{len(OWN_SKILLS)}/{len(OWN_SKILLS)}", "instalador")
    md = CLAUDE_HOME / "CLAUDE.md"
    chk("regras no CLAUDE.md", md.exists() and "video-ai-pack:start" in md.read_text(encoding="utf-8", errors="replace"),
        str(md), "instalador")
    hooks_txt = json.dumps(settings.get("hooks", {}))
    for sc in ("memoria_hook.py", "registrar_conversa.py"):
        chk(f"hook {sc}", sc in hooks_txt, "registrado" if sc in hooks_txt else "ausente", "instalador")
    chk("memória (memoria.md)", (MEMORIA / "memoria.md").exists(), str(MEMORIA / "memoria.md"), "instalador")
    faltam = [f for f in ("INDEX.md", "skills.md", "mcps.md", "agentes.md") if not (MEMORIA / f).exists()]
    chk("MDs de consulta", not faltam, "faltando: " + ", ".join(faltam) if faltam else "INDEX, skills, mcps, agentes", "memoria")
    for mod in ("faster_whisper", "auto_editor"):
        rc, _ = run([sys.executable, "-c", f"import {mod}"], timeout=120)
        chk(f"python: {mod}", rc == 0, "ok" if rc == 0 else "não instalado", "pip")
    if c["mcps"] and which("claude"):
        rc, out = run(["claude", "mcp", "list"], timeout=180)
        for m in c["mcps"]:
            name = MCP_NAMES.get(m, m)
            chk(f"MCP {name}", name in out, "registrado" if name in out else "ausente", "instalador")
    apps = detect_apps()
    for a in ("premiere", "aftereffects", "resolve"):
        chk(f"app {a}", a in apps or a not in c["apps"], apps.get(a, "não detectado" + (" (configurado!)" if a in c["apps"] else "")))
    free = shutil.disk_usage(CLAUDE_HOME if CLAUDE_HOME.exists() else Path.home()).free / 2**30
    chk("espaço em disco", free > 5, f"{free:.1f} GB livres")

    if reparar and acoes:
        log(f"reparando: {sorted(acoes)}")
        if "instalador" in acoes:
            run_installer(c, rep)
        if "pip" in acoes:
            pip_upgrade(c, rep)
        if "sync" in acoes and "instalador" not in acoes and (PACK_HOME / "pack.py").exists():
            pack_cmd("sync")
        if "memoria" in acoes:
            memoria(c, rep)
        return saude(reparar=False)  # reconfere e gera o relatório final

    falhas = [(i, d) for i, ok, d in checks if not ok]
    rep.add(f"**{len(checks) - len(falhas)}/{len(checks)} itens ok**", "", "| Item | Status | Detalhe |", "|---|---|---|",
            *[f"| {i} | {'✅' if ok else '❌'} | {d} |" for i, ok, d in checks])
    for i, d in falhas:
        rep.alert(f"{i}: {d}")
    rep.save()
    return not falhas


# ----------------------------------------------------------------- manutenção
def pip_upgrade(c, rep):
    pkgs = ["faster-whisper", "auto-editor"] + [PYPI_PKGS[m] for m in c["mcps"] if m in PYPI_PKGS]
    rc, out = run([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--quiet", *pkgs], timeout=1800)
    if rc and "externally-managed" in out:
        rc, out = run([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--quiet", "--break-system-packages", *pkgs], timeout=1800)
    rep.add(f"- pip ({', '.join(pkgs)}): {'ok' if rc == 0 else 'falhou'}")
    if rc:
        rep.alert("pip falhou: " + out[-200:])


def memoria(c, rep):
    """Regenera os MDs de consulta e sincroniza a memória privada (git) se configurada."""
    d = repo_pack_dir(c)
    if d:
        sys.path.insert(0, str(HERE))
        import memoria_md
        memoria_md.gerar(MEMORIA, d.parent, CLAUDE_HOME, scan=True)
        n = len(list((MEMORIA / "conversas").glob("2*.md"))) if (MEMORIA / "conversas").exists() else 0
        rep.add(f"- memória: skills.md, mcps.md, agentes.md e INDEX.md regenerados; {n} conversas registradas")
    if (MEMORIA / ".git").exists():
        g = ["git", "-C", str(MEMORIA)]
        run([*g, "add", "-A"])
        if run([*g, "diff", "--cached", "--quiet"])[0]:
            run([*g, "commit", "-m", f"memoria: atualização automática {now()}"])
        rc, out = run([*g, "pull", "--rebase", "--autostash"], timeout=300)
        rc2, out2 = run([*g, "push"], timeout=300) if rc == 0 else (rc, out)
        rep.add(f"- memória sincronizada com o repositório privado: {'ok' if rc2 == 0 else 'falhou'}")
        if rc2:
            rep.alert("sincronização da memória falhou: " + (out2 or out)[-200:])


def manutencao():
    c, rep = cfg(), Report("manutencao")
    st = load_json(STATE / "versoes.json", {})
    rep.add("## Ações")
    d = repo_pack_dir(c)
    if d and (d.parent / ".git").exists():
        repo = str(d.parent)
        before = run(["git", "-C", repo, "rev-parse", "HEAD"])[1]
        rc, _ = run(["git", "-C", repo, "fetch", "origin", c["branch"]], timeout=300)
        if rc and c["branch"] != "main":
            # a branch do PR some depois da mesclagem: passa a seguir a main
            if run(["git", "-C", repo, "fetch", "origin", "main"], timeout=300)[0] == 0 and \
                    run(["git", "-C", repo, "checkout", "main"], timeout=120)[0] == 0:
                rep.alert(f"branch '{c['branch']}' não existe mais no GitHub (PR mesclado?) — o agente passou a seguir a main")
                c["branch"] = "main"
                cfg_salvo = load_json(CFG_PATH, {})
                cfg_salvo["branch"] = "main"
                save_json(CFG_PATH, cfg_salvo)
        rc, out = run(["git", "-C", repo, "merge", "--ff-only", f"origin/{c['branch']}"], timeout=300)
        after = run(["git", "-C", repo, "rev-parse", "HEAD"])[1]
        if rc:
            rep.alert("git: não deu para atualizar sem conflito (alterações locais?) — " + out[-160:])
        if before != after:
            rep.add(f"- repositório atualizado {before[:7]} → {after[:7]}; reinstalando o pack")
            run_installer(c, rep, ["-NoSync"] if WIN else ["--no-sync"])
        else:
            rep.add(f"- repositório já atualizado ({after[:7]})")
    else:
        rep.alert("repositório git do pack não configurado — atualizações automáticas do pack desativadas")
    if (PACK_HOME / "pack.py").exists():
        rc, out = pack_cmd("sync", "--force", timeout=900)
        rep.add(f"- cofre: {out.splitlines()[-1] if out else rc}")
    pip_upgrade(c, rep)
    memoria(c, rep)
    if which("npm"):
        for m, pkg in NPM_PKGS.items():
            if m not in c["mcps"]:
                continue
            rc, ver = run(["npm", "view", pkg, "version"], timeout=120)
            ver = ver.strip().splitlines()[-1] if rc == 0 and ver else ""
            if ver and ver != st.get(pkg):
                rep.add(f"- {pkg}: {st.get(pkg, '—')} → {ver}")
                if m == "premiere":
                    rc2, _ = run(["npx", "-y", f"{pkg}@{ver}", "--install-cep"], timeout=900)
                    rep.add(f"  - painel CEP do Premiere atualizado: {'ok' if rc2 == 0 else 'falhou'}")
                elif m == "resolve" and st.get(pkg):
                    rep.alert(f"MCP do Resolve tem versão nova ({ver}): rode `npx -y davinci-resolve-mcp setup` com o Resolve fechado")
                st[pkg] = ver
    if c["atualizar_sistema"]:
        if WIN and which("winget"):
            for wid in WINGET_IDS:
                rc, out = run(["winget", "upgrade", "--id", wid, "--exact", "--silent", "--accept-package-agreements",
                               "--accept-source-agreements", "--disable-interactivity"], timeout=1800)
                if "No available upgrade" not in out and "Nenhuma atualização" not in out and "No installed package" not in out:
                    rep.add(f"- winget {wid}: {'atualizado' if rc == 0 else 'sem mudança/erro ' + str(rc)}")
        if which("claude"):
            rc, out = run(["claude", "update"], timeout=900)
            rep.add(f"- Claude Code: {out.splitlines()[-1] if out else rc}")
    cutoff = time.time() - c["retencao_dias"] * 86400
    removed = 0
    for folder in (LOGS, REPORTS):
        for f in folder.glob("*"):
            if f.is_file() and f.name != "ultimo.md" and f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
    rep.add(f"- limpeza: {removed} arquivos antigos removidos")
    save_json(STATE / "versoes.json", st)
    rep.save()


# ----------------------------------------------------------------- descoberta
def skills_sh_snapshot():
    snap = {}
    for q in QUERIES:
        try:
            data = http_json(f"https://skills.sh/api/search?q={urllib.parse.quote(q)}&limit=100")
        except Exception as e:  # rede instável: segue com o que veio
            log(f"skills.sh '{q}': {e}")
            continue
        for s in data.get("skills", []):
            snap[s["id"]] = {"installs": s.get("installs", 0), "source": s["source"], "skill": s["skillId"]}
        time.sleep(0.3)
    return snap


def skill_page(sid):
    import html as H
    h = http_text(f"https://skills.sh/{sid}")
    m = re.search(r'<meta name="description" content="([^"]*)"', h)
    t = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    L = [x.strip() for x in H.unescape(re.sub(r"<[^>]+>", "\n", t)).split("\n") if x.strip()]

    def after(k):
        return L[L.index(k) + 1] if k in L and L.index(k) + 1 < len(L) else None
    aud = {}
    if "Security Audits" in L:
        i = L.index("Security Audits")
        for k in range(i + 1, min(i + 12, len(L) - 1), 2):
            if L[k + 1] not in ("Pass", "Warn", "Fail"):
                break
            aud[L[k]] = L[k + 1]
    inst = re.search(r"npx skills add (\S+) --skill (\S+)", " ".join(L))
    return {"desc": H.unescape(m.group(1)) if m else "", "stars": after("GitHub Stars"), "audits": aud,
            "repo": re.sub(r"^https://github\.com/", "", inst.group(1)).removesuffix(".git") if inst else None}


def find_skill_md(repo, skill):
    for br in ("main", "master"):
        for p in (f"skills/{skill}", skill, f".claude/skills/{skill}", f"skills/.curated/{skill}", ""):
            url = f"https://raw.githubusercontent.com/{repo}/{br}/{p + '/' if p else ''}SKILL.md"
            try:
                body = http_text(url, timeout=15)
            except Exception:
                continue
            if body.lstrip().startswith("---"):
                return url, body
    return None, None


def num(s):
    m = re.match(r"([\d.]+)\s*([KM]?)", str(s or "").replace(",", ""))
    return float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)] if m else 0


# "caption" sozinho pega texto de post de rede social; legenda exige contexto de vídeo/áudio
DESC_NOISE = r"deploy|microservice|kubernetes|post copy|copywrit|social media caption|caption (for|of) (a |an |the |your )?(post|photo|image)|seo\b|ad copy|hashtag|game|unity|godot"
CAT_RX = {"cor": r"colou?r ?grad|\blut\b|colou?r correct", "legendas": r"subtit|\bsrt\b|\bvtt\b|transcri|whisper|burn(ed)?[- ]in|(video|animated|word[- ]level) captions?",
          "decupagem": r"rough ?cut|silence|jump ?cut|trim|highlight|edit (a |the )?video|video edit|filler",
          "motion": r"motion|after ?effects|lottie|kinetic|animation", "apps": r"premiere|davinci|resolve|capcut|final cut",
          "programatico": r"remotion|hyperframes", "audio": r"\btts\b|voice|music|sound effect|podcast|audio",
          "social": r"reels|shorts|tiktok|youtube|instagram", "analise": r"watch|understand|analy[sz]", "ffmpeg": r"ffmpeg"}
APP_RX = {"premiere": r"premiere", "resolve": r"davinci|resolve", "aftereffects": r"after ?effects", "remotion": r"remotion",
          "hyperframes": r"hyperframes", "capcut": r"capcut"}


def avaliar(sid, info, c):
    import math
    page = skill_page(sid)
    repo = page["repo"] or info["source"]
    raw, body = find_skill_md(repo, info["skill"])
    text = (info["skill"] + " " + page["desc"]).lower()
    cat = next((k for k, rx in CAT_RX.items() if re.search(rx, text)), None)
    app = next((k for k, rx in APP_RX.items() if re.search(rx, text)), None)
    fails = sum(v == "Fail" for v in page["audits"].values())
    warns = sum(v == "Warn" for v in page["audits"].values())
    tokens = len(re.sub(r"^---.*?---", "", body or "", count=1, flags=re.S)) // 4 if body else None
    fit = 0.85 if cat in ("cor", "legendas", "decupagem", "motion", "apps") else 0.75 if cat else 0.4
    com = 18 * min(1, math.log10(info["installs"] + 1) / math.log10(5e6)) + 12 * min(1, math.log10(num(page["stars"]) + 1) / math.log10(70000))
    ef = 7 if tokens is None else 15 if tokens <= 1000 else 12 if tokens <= 2000 else 9 if tokens <= 3500 else 5 if tokens <= 6000 else 2
    nota = round(com + 35 * fit + max(0, 15 - 6 * fails - 2 * warns) + ef + 5, 1)
    motivos = []
    if fails or warns > 1 or len(page["audits"]) < 2:
        motivos.append(f"auditoria insuficiente ({page['audits'] or 'sem dados'})")
    if not raw:
        motivos.append("SKILL.md não localizado")
    if tokens and tokens > c["max_tokens_skill"]:
        motivos.append(f"pesada ({tokens} tokens)")
    if not cat:
        motivos.append("categoria não reconhecida")
    if re.search(DESC_NOISE, text):
        motivos.append("fora do escopo de edição (descrição)")
    if not re.search(r"video|vídeo|footage|clip|timeline|subtit|audio|motion|animation|film", text):
        motivos.append("descrição não menciona vídeo/áudio")
    if nota < c["nota_minima"]:
        motivos.append(f"nota {nota} < {c['nota_minima']}")
    return {"id": sid, "nome": info["skill"], "repo": repo, "categoria": cat or "outros", "nota": nota,
            "tier": "ouro" if nota >= 75 else "prata" if nota >= 65 else "bronze", "installs": info["installs"],
            "stars_repo": int(num(page["stars"])), "auditoria": {"fail": fails, "warn": warns}, "tokens_corpo": tokens,
            "tokens_descricao": len(page["desc"]) // 4 + 8, "raw": raw, "app": app, "api": None,
            "requisito": f"adotada pelo agente em {dt.date.today()}" + (f" ({app})" if app else ""),
            "descricao": page["desc"][:220], "instalar": f"npx skills add https://github.com/{repo} --skill {info['skill']}",
            "adotar": not motivos, "motivos": motivos}


def pesquisa_ia(rep):
    prompt = ("Pesquise na web as novidades dos últimos 7 dias sobre ferramentas de IA para edição de vídeo usadas com Claude: "
              "MCP servers e skills para Adobe Premiere Pro, After Effects, DaVinci Resolve, CapCut, Remotion, HyperFrames, "
              "colorgrade, legendas, decupagem e motion design; conectores (Adobe, Higgsfield, invideo, OpusClip, Magnific). "
              "Responda em português do Brasil, em Markdown, com no máximo 15 itens: nome, o que mudou, data, link oficial "
              "e se vale instalar (sim/não/avaliar) para um editor que usa Premiere, After Effects e Resolve. "
              "Não invente: só itens com fonte verificável.")
    rc, out = run(["claude", "-p", prompt, "--allowedTools", "WebSearch", "WebFetch", "--output-format", "text"], timeout=1500)
    if rc == 0 and out:
        rep.add("", "## Pesquisa da semana (Claude + web)", "", out)
    else:
        rep.alert("pesquisa por IA falhou (claude -p): " + out[-200:])


def descoberta():
    c, rep = cfg(), Report("descoberta")
    prev = load_json(STATE / "skills_snapshot.json", {})
    snap = skills_sh_snapshot()
    if not snap:
        rep.alert("skills.sh inacessível — descoberta adiada")
        rep.save()
        return
    catalog = load_json(PACK_HOME / "skills.json", {"skills": []})["skills"]
    local_path = PACK_HOME / "skills.local.json"
    local = load_json(local_path, {"skills": []})
    known = {s["id"] for s in catalog} | {s["id"] for s in local["skills"]}
    rel = {k: v for k, v in snap.items() if re.search(RELEVANT, k.lower()) and not re.search(NOISE, k.lower())}
    rep.add(f"Skills monitoradas: {len(snap)} ({len(rel)} relevantes para vídeo)", "")

    if not prev:
        rep.add("Primeira execução: linha de base criada. Novidades aparecem a partir da próxima rodada.")
    else:
        novas = sorted((k for k in rel if k not in prev and k not in known and rel[k]["installs"] >= c["min_installs"]),
                       key=lambda k: -rel[k]["installs"])[:15]
        subindo, vistos = [], set()
        for k, d in sorted(((k, rel[k]["installs"] - prev[k]["installs"]) for k in rel if k in prev), key=lambda x: -x[1]):
            if rel[k]["skill"] not in vistos:
                vistos.add(rel[k]["skill"])
                subindo.append((k, d))
        subindo = subindo[:10]
        rep.add("## Skills novas relevantes", "")
        adotadas = []
        if not novas:
            rep.add("Nenhuma nova acima do limite de instalações.")
        for sid in novas:
            try:
                a = avaliar(sid, rel[sid], c)
            except Exception as e:
                rep.add(f"- `{sid}`: erro ao avaliar ({e})")
                continue
            adotar = a["adotar"] and c["auto_adotar"]
            rep.add(f"- `{sid}` — nota {a['nota']}, {a['installs']} instalações, {a['tokens_corpo'] or 'n/d'} tokens, "
                    f"{a['categoria']}: {'**ADOTADA**' if adotar else 'não adotada — ' + '; '.join(a['motivos']) if a['motivos'] else 'aprovada (auto_adotar desligado)'}")
            if adotar and len(adotadas) >= c["max_adocoes"]:
                rep.add(f"  - limite de {c['max_adocoes']} adoções por rodada atingido; fica para a próxima")
                adotar = False
            if adotar:
                a.pop("adotar")
                a.pop("motivos")
                a["rank"] = 1000 + len(local["skills"])
                local["skills"].append(a)
                adotadas.append(sid)
        if adotadas:
            save_json(local_path, local)
            pack_cmd("sync")
            rep.alert(f"{len(adotadas)} skill(s) nova(s) adotada(s): {', '.join(adotadas)}")
        alta = [f"- `{k}` +{d}" for k, d in subindo if d > 0] or ["- sem variação relevante"]
        rep.add("", "## Em alta na semana (instalações a mais)", "", *alta)
    save_json(STATE / "skills_snapshot.json", snap)

    # versões de MCPs e repositórios acompanhados
    st = load_json(STATE / "releases.json", {})
    rep.add("", "## MCPs e repositórios acompanhados", "")
    for m, pkg in NPM_PKGS.items():
        try:
            v = http_json(f"https://registry.npmjs.org/{urllib.parse.quote(pkg, safe='@')}/latest")["version"]
        except Exception:
            continue
        novo = st.get(pkg) and st[pkg] != v
        rep.add(f"- npm `{pkg}`: {v}{' (NOVA — atualizada na manutenção diária)' if novo else ''}")
        st[pkg] = v
    for m, pkg in PYPI_PKGS.items():
        try:
            v = http_json(f"https://pypi.org/pypi/{pkg}/json")["info"]["version"]
        except Exception:
            continue
        rep.add(f"- PyPI `{pkg}`: {v}{' (NOVA)' if st.get(pkg) and st[pkg] != v else ''}")
        st[pkg] = v
    for repo in GH_REPOS:
        try:
            r = http_json(f"https://api.github.com/repos/{repo}/releases/latest")
            tag, when = r.get("tag_name"), (r.get("published_at") or "")[:10]
        except Exception:
            try:
                tag, when = None, http_json(f"https://api.github.com/repos/{repo}")["pushed_at"][:10]
            except Exception:
                continue
        key = f"gh:{repo}"
        val = tag or when
        if st.get(key) and st[key] != val:
            rep.alert(f"{repo}: nova versão {val}")
        rep.add(f"- GitHub `{repo}`: {tag or 'sem release'} ({when})")
        st[key] = val
    save_json(STATE / "releases.json", st)

    if c["pesquisa_ia"] and which("claude") and prev:  # na linha de base o login do Claude ainda pode não existir
        pesquisa_ia(rep)
    rep.save()


def status():
    r = load_json(STATE / "ultimo_resumo.json", None)
    if not r:
        print("nenhuma execução registrada ainda")
        return
    print(f"último: {r['modo']} em {r['quando']} | alertas: {len(r['alertas'])} | {r['relatorio']}")
    for a in r["alertas"]:
        print(" -", a)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    modo = a[0] if a else "status"
    if modo == "status":
        return status()
    if modo not in ("saude", "manutencao", "descoberta", "memoria", "tudo"):
        sys.exit(__doc__)
    with Lock():
        log(f"início: {modo}")
        try:
            if modo in ("saude", "tudo"):
                saude(reparar="--reparar" in a or modo == "tudo")
            if modo in ("manutencao", "tudo"):
                manutencao()
            if modo in ("descoberta", "tudo"):
                descoberta()
            if modo == "memoria":
                rep = Report("memoria")
                memoria(cfg(), rep)
                rep.save()
        except Exception as e:  # nunca morre calado: registra e alerta
            rep = Report(modo + "-erro")
            rep.alert(f"falha inesperada: {e!r}")
            rep.save()
            raise
        log(f"fim: {modo}")


if __name__ == "__main__":
    main()
