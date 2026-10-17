#!/usr/bin/env python3
"""Gera os MDs de consulta da memória: skills.md, mcps.md, agentes.md e INDEX.md.

  memoria_md.py --dest DIR [--repo REPO_ROOT] [--claude-home DIR] [--scan]

--scan varre o que está instalado de verdade (skills, plugins, agentes, `claude mcp list`, tarefas do agente).
Sem --scan, gera só a parte documentada (a versão pública do repositório).
memoria.md e conversas/ nunca são sobrescritos: são escritos pelo Claude e pelos hooks.
"""
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def frontmatter(path):
    try:
        t = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return {}
    m = re.match(r"---\s*\n(.*?)\n---", t, re.S)
    if not m:
        return {}
    out = {}
    for k in ("name", "description", "tools"):
        mm = re.search(rf"^{k}:\s*(.+)$", m.group(1), re.M)
        if mm:
            out[k] = mm.group(1).strip().strip('"').strip("'")
    return out


def load(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def cut(s, n=140):
    s = re.sub(r"\s+", " ", s or "").replace("|", "/")
    return s if len(s) <= n else s[: n - 1] + "…"


def run(cmd, timeout=120):
    exe = shutil.which(cmd[0])
    if not exe:
        return ""
    try:
        return subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def gerar(dest, repo, claude_home, scan):
    dest.mkdir(parents=True, exist_ok=True)
    hoje = dt.date.today().isoformat()
    contas = load(repo / "memoria" / "contas.json", {})
    pack = repo / "video-ai-pack"
    catalog = load(claude_home / "video-ai-pack" / "skills.json", None) or load(pack / "catalogo" / "skills.json", {"skills": []})
    local = load(claude_home / "video-ai-pack" / "skills.local.json", {"skills": []})
    origem = "varredura deste computador + documentação" if scan else "documentação do repositório (sem varredura local)"

    # ---------------------------------------------------------------- skills.md
    S = [f"# Skills — referência completa", "", f"Atualizado em {hoje} · fonte: {origem}.",
         "Use para responder \"qual skill faz X?\" e para não recriar o que já existe. Busque com Ctrl+F / grep.", ""]
    S += ["## Skills do Video AI Pack (sempre instaladas)", "", "| Skill | Para quê |", "|---|---|"]
    for d in sorted((pack / "skills").glob("*/SKILL.md")):
        fm = frontmatter(d)
        S.append(f"| `{fm.get('name', d.parent.name)}` | {cut(fm.get('description'), 200)} |")
    if scan:
        inst = sorted((claude_home / "skills").glob("*/SKILL.md"))
        plug = sorted((claude_home / "plugins").glob("**/skills/*/SKILL.md"))
        S += ["", f"## Instaladas neste computador ({len(inst)} em ~/.claude/skills, {len(plug)} via plugins)", "",
              "| Skill | Onde | Para quê |", "|---|---|---|"]
        for d in inst + plug:
            fm = frontmatter(d)
            onde = "skills" if d in inst else "plugin " + d.parts[len((claude_home / 'plugins').parts)]
            S.append(f"| `{fm.get('name', d.parent.name)}` | {onde} | {cut(fm.get('description'))} |")
    S += ["", "## Skills da conta Claude (claude.ai e Claude Code)", "",
          "Disponíveis nas conversas do claude.ai e nas sessões Claude Code ligadas à conta.", ""]
    for grupo, nomes in contas.get("skills_conta", {}).items():
        S.append(f"- **{grupo}:** " + ", ".join(f"`{n}`" for n in nomes))
    S += ["", f"## Top-100 da comunidade (cofre do roteador, {len(catalog['skills'])} skills)", "",
          "Carregadas sob demanda pelo hook (2–5 por pedido). Detalhes e metodologia: `video-ai-pack/catalogo/CATALOGO.md`.", "",
          "| # | Nota | Skill | Categoria | Tokens | Requisito |", "|---|---|---|---|---|---|"]
    for s in catalog["skills"]:
        S.append(f"| {s['rank']} | {s['nota']} | `{s['id']}` | {s['categoria']} | {s.get('tokens_corpo') or 'n/d'} | {cut(s['requisito'], 50)} |")
    S += ["", f"## Adotadas automaticamente pelo agente ({len(local['skills'])})", ""]
    S += [f"- `{s['id']}` — nota {s['nota']}, {s['categoria']}, {s.get('tokens_corpo')} tokens ({s['requisito']})" for s in local["skills"]] or ["- nenhuma ainda"]
    (dest / "skills.md").write_text("\n".join(S) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- mcps.md
    M = ["# MCPs e conectores — referência completa", "", f"Atualizado em {hoje} · fonte: {origem}.", ""]
    if scan:
        out = run(["claude", "mcp", "list"], timeout=180)
        M += ["## Registrados no Claude Code deste computador (`claude mcp list`)", "", "```", out.strip() or "(claude não encontrado ou sem MCPs)", "```", ""]
    M += ["## Conectores da conta claude.ai", "", "| Conector | Uso | Status |", "|---|---|---|"]
    M += [f"| {c['nome']} | {cut(c['uso'], 160)} | {c['status']} |" for c in contas.get("conectores_claude_ai", [])]
    M += ["", "## MCPs do Video AI Pack", "", "| Nome | Tipo | Comando / URL | Observações |", "|---|---|---|---|"]
    M += [f"| `{m['nome']}` | {m['tipo']} | `{m['comando']}` | {cut(m['obs'], 160)} ([fonte]({m['fonte']})) |" for m in contas.get("mcps_pack", [])]
    M += ["", "Instalar/atualizar: `install.ps1 -Mcp premiere,ae,resolve,opusclip,invideo,higgsfield` (ou `all`). Remotos: login em `/mcp`.",
          "", "## Alternativas pesquisadas (não instaladas)", ""]
    M += [f"- [{m['nome']}]({m['fonte']})" for m in contas.get("mcps_alternativos", [])]
    M += ["", "Regra: MCP novo só é instalado com aprovação do usuário (ver `memoria.md` → Decisões)."]
    (dest / "mcps.md").write_text("\n".join(M) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- agentes.md
    A = ["# Agentes, hooks e automações", "", f"Atualizado em {hoje} · fonte: {origem}.", "",
         "## Video AI Agent (Windows, Agendador de Tarefas `\\VideoAIAgent\\`)", "",
         "| Rotina | Quando | Faz |", "|---|---|---|",
         "| Saude | logon +5 min e a cada 6 h | confere 20 itens e repara sozinho |",
         "| Manutencao | diária 03:17 | atualiza pack/cofre/pacotes/sistema, regenera estes MDs, sincroniza memória privada |",
         "| Descoberta | segunda 09:13 | monitora skills/MCPs/releases + pesquisa web via `claude -p`; adota até 3 skills auditadas |", "",
         "- Código: `video-ai-pack/agente/` (`agente.py`, `agente.ps1`, `instalar-agente.ps1`)",
         "- Dados: `%LOCALAPPDATA%\\VideoAIAgent\\` (`config.json`, `relatorios\\ultimo.md`, `logs\\`, `estado\\`)",
         "- Manual: `powershell -File agente.ps1 -Modo status|saude|manutencao|descoberta|tudo`", "",
         "## Subagentes do Claude Code", "", "| Agente | Para quê |", "|---|---|"]
    agentes = sorted((claude_home / "agents").glob("*.md")) if scan else []
    agentes = agentes or [HERE / "video-ai-mantenedor.md"]
    A += [f"| `{frontmatter(a).get('name', a.stem)}` | {cut(frontmatter(a).get('description'), 200)} |" for a in agentes]
    A += ["", "## Hooks instalados (`~/.claude/settings.json`)", "",
          "| Evento | Script | Faz |", "|---|---|---|",
          "| UserPromptSubmit | `video_intent.py` | detecta pedido de vídeo e injeta as skills certas (roteador, orçamento de tokens) |",
          "| UserPromptSubmit | `memoria_hook.py` | detecta correção/preferência/\"lembre disso\" e manda registrar em `memoria.md` |",
          "| SessionEnd | `registrar_conversa.py` | salva o resumo de cada conversa em `~/.claude/memoria/conversas/` (privado) |"]
    if scan:
        hooks = load(claude_home / "settings.json", {}).get("hooks", {})
        A += ["", "Registrados agora:", ""] + [f"- {ev}: " + ", ".join(h.get("command", "")[-60:] for g in grupos for h in g.get("hooks", []))
                                             for ev, grupos in hooks.items()]
        cfg = load(Path(__import__("os").environ.get("LOCALAPPDATA", Path.home())) / "VideoAIAgent" / "config.json", None)
        if cfg:
            A += ["", "Config do agente:", "", "```json", json.dumps(cfg, ensure_ascii=False, indent=2), "```"]
    A += ["", "## Automações na nuvem (sessões claude.ai/code)", "",
          "- PR #1 `clebercantos/gestao`: sessão inscrita nos eventos do PR (CI, revisões) e com check-ins de segurança agendados.",
          "- Sessões na nuvem leem `CLAUDE.md` e `memoria/` do repositório (versão pública da memória)."]
    (dest / "agentes.md").write_text("\n".join(A) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- INDEX.md + sementes
    privado = scan
    I = ["# Índice da memória", "",
         "Consulte antes de responder. Para buscar: `grep -ri \"termo\" <pasta da memória>` (PowerShell: `Select-String -Path <pasta>\\* -Pattern termo -Recurse`).", "",
         "| Arquivo | Conteúdo | Quem escreve |", "|---|---|---|",
         "| `memoria.md` | preferências, **correções**, aprendizados e decisões (sempre carregado) | Claude, a cada correção/aprendizado |",
         "| `skills.md` | todas as skills: pack, instaladas, conta Claude, top-100, adotadas | agente (diário) |",
         "| `mcps.md` | MCPs registrados, conectores claude.ai, MCPs do pack e alternativas | agente (diário) |",
         "| `agentes.md` | agentes, subagentes, hooks e automações | agente (diário) |",
         "| `historico/` | resumos curados das conversas importantes | Claude |"]
    if privado:
        I.append("| `conversas/` | resumo automático de **toda** sessão Claude Code deste PC (privado) | hook SessionEnd |")
    I += ["", "Regras: veja `memoria.md`. Correção do usuário → registrar em `memoria.md` na hora, com data."]
    (dest / "INDEX.md").write_text("\n".join(I) + "\n", encoding="utf-8")
    seed = repo / "memoria"
    if dest.resolve() != seed.resolve():
        if not (dest / "memoria.md").exists() and (seed / "memoria.md").exists():
            shutil.copy2(seed / "memoria.md", dest / "memoria.md")
        (dest / "historico").mkdir(exist_ok=True)
        for h in (seed / "historico").glob("*.md"):
            if not (dest / "historico" / h.name).exists():
                shutil.copy2(h, dest / "historico" / h.name)
    return [dest / n for n in ("skills.md", "mcps.md", "agentes.md", "INDEX.md")]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--repo", default=str(HERE.parent.parent))
    ap.add_argument("--claude-home", default=str(Path.home() / ".claude"))
    ap.add_argument("--scan", action="store_true")
    a = ap.parse_args()
    for f in gerar(Path(a.dest), Path(a.repo), Path(a.claude_home), a.scan):
        print("gerado:", f)


if __name__ == "__main__":
    main()
