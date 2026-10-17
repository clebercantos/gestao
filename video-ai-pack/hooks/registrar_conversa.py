#!/usr/bin/env python3
"""SessionEnd hook: salva o resumo de cada conversa do Claude Code em ~/.claude/memoria/conversas/.

Gera um .md pesquisável (pedidos do usuário, respostas do Claude, arquivos alterados, ferramentas)
e acrescenta uma linha em conversas/INDEX.md. Remove segredos óbvios (chaves de API, tokens, senhas).
Fica só no seu computador: não é enviado a lugar nenhum.
"""
import collections
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

MEM = Path(os.environ.get("CLAUDE_MEMORIA") or Path.home() / ".claude" / "memoria")
SEGREDOS = [
    (r"sk-[A-Za-z0-9_-]{16,}", "sk-***"), (r"gh[pousr]_[A-Za-z0-9]{20,}", "gh*_***"), (r"AKIA[0-9A-Z]{16}", "AKIA***"),
    (r"xox[abpr]-[A-Za-z0-9-]{10,}", "xox*-***"), (r"(?i)(senha|password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S+", r"\1=***"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "jwt***"),
]
RUIDO = re.compile(r"<(system-reminder|task-notification|command-name|command-message|command-args|local-command-stdout)>|^\[Request interrupted|^Tool loaded\.?$")


def limpo(t, n):
    for rx, rep in SEGREDOS:
        t = re.sub(rx, rep, t)
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def textos(content):
    if isinstance(content, str):
        return [content]
    return [b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]


def resumir(transcript):
    turnos, ferramentas, arquivos, inicio, fim = [], collections.Counter(), [], None, None
    with open(transcript, encoding="utf-8", errors="replace") as f:
        for linha in f:
            try:
                e = json.loads(linha)
            except ValueError:
                continue
            ts = e.get("timestamp")
            if ts:
                inicio, fim = inicio or ts, ts
            msg = e.get("message") or {}
            if e.get("type") == "user" and not e.get("isMeta"):
                for t in textos(msg.get("content")):
                    if t.strip() and not RUIDO.search(t):
                        turnos.append({"pedido": t, "respostas": []})
            elif e.get("type") == "assistant":
                for b in msg.get("content") or []:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and b.get("text", "").strip() and turnos:
                        turnos[-1]["respostas"].append(b["text"])
                    elif b.get("type") == "tool_use":
                        ferramentas[b.get("name", "?")] += 1
                        fp = (b.get("input") or {}).get("file_path")
                        if fp and b.get("name") in ("Write", "Edit", "MultiEdit", "NotebookEdit") and fp not in arquivos:
                            arquivos.append(fp)
    return turnos, ferramentas, arquivos, inicio, fim


def main():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    tp = d.get("transcript_path")
    if not tp or not Path(tp).exists():
        return
    turnos, ferramentas, arquivos, inicio, fim = resumir(tp)
    if not turnos:
        return
    agora = dt.datetime.now()
    sid = (d.get("session_id") or "sessao")[:8]
    titulo = limpo(turnos[0]["pedido"].splitlines()[0], 80)
    pasta = MEM / "conversas"
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{agora:%Y-%m-%d_%H%M%S}_{sid}.md"
    L = [f"# {agora:%Y-%m-%d %H:%M} — {titulo}", "",
         f"- Pasta: `{d.get('cwd', '')}` · sessão `{d.get('session_id', '')}` · fim: {d.get('reason', '')}",
         f"- Início/fim: {inicio} → {fim} · {len(turnos)} pedido(s)", ""]
    for i, t in enumerate(turnos, 1):
        L += [f"## {i}. Pedido", "", limpo(t["pedido"], 1500), ""]
        if t["respostas"]:
            L += ["**Resposta final do Claude:**", "", limpo(t["respostas"][-1], 2500), ""]
    if arquivos:
        L += ["## Arquivos criados/alterados", ""] + [f"- `{a}`" for a in arquivos] + [""]
    if ferramentas:
        L += ["## Ferramentas usadas", "", ", ".join(f"{k} ×{v}" for k, v in ferramentas.most_common())]
    (pasta / nome).write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(pasta / "INDEX.md", "a", encoding="utf-8") as f:
        f.write(f"- {agora:%Y-%m-%d %H:%M} — {titulo} — [{nome}]({nome})\n")


if __name__ == "__main__":
    main()
