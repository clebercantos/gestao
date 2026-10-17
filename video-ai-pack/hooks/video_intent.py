#!/usr/bin/env python3
"""UserPromptSubmit hook do Video AI Pack.

Para pedidos de vídeo, roda o roteador (pack.py) e injeta no contexto exatamente quais
skills carregar — as próprias do pack e as do cofre das 100 melhores — dentro do
orçamento de tokens. Pedidos que não são de vídeo passam sem custo nenhum.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "tools")]
import pack  # noqa: E402


def fonte(s):
    if s["arquivo"]:
        return f"Read {s['arquivo']}"
    if s["raw"]:
        raw = s["raw"] if s["raw"].startswith("http") else "https://raw.githubusercontent.com/" + s["raw"]
        return f"WebFetch {raw}"
    return f"instale: {s['instalar']}"


def main() -> None:
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
    except Exception:
        return
    if prompt.lstrip().startswith("/") or not pack.is_video(prompt):
        return
    try:
        r = pack.route(prompt)
    except SystemExit:  # catálogo ausente: segue só com as skills próprias
        r = {"intents": [], "apps": [], "own_skills": ["video-entrega"], "skills": [], "tokens_estimados": 0, "orcamento": 0}

    externas = "\n".join(
        f"- {s['id']} (nota {s['nota']}, ~{s['tokens']}t, {s['motivo']}; requer {s['requisito']}) → {fonte(s)}"
        for s in r["skills"]) or "- nenhuma (use só as skills do pack)"
    apps = f" | apps: {', '.join(r['apps'])}" if r["apps"] else ""
    ctx = f"""[Video AI Pack] Pedido de vídeo. Intenções: {', '.join(r['intents'])}{apps}.
1. Carregue a skill `video-orquestrador` e siga as 5 fases (Brief aprimorado → Inventário → Rota → Execução → QA).
2. Skills do pack para este pedido: {', '.join('`' + s + '`' for s in r['own_skills'])}.
3. Skills externas escolhidas pelo roteador (top-100 da comunidade, ~{r['tokens_estimados']}t de {r['orcamento']}t). Leia cada uma só quando a etapa dela chegar:
{externas}
   Se a skill citar scripts/references ausentes, rode `python3 ~/.claude/video-ai-pack/pack.py install <id>`.
4. Não carregue outras skills de vídeo sem motivo explícito (economia de tokens)."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
