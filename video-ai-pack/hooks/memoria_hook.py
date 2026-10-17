#!/usr/bin/env python3
"""UserPromptSubmit hook: transforma correções, preferências e "lembre disso" em memória permanente.

Quando a mensagem parece uma correção ("não, está errado", "na verdade…"), uma preferência
("prefiro", "a partir de agora", "nunca use") ou um pedido de lembrar ("anote", "salve na memória"),
injeta a instrução de registrar em memoria.md. Mensagens comuns passam sem custo.
"""
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

MEM = Path(os.environ.get("CLAUDE_MEMORIA") or Path.home() / ".claude" / "memoria")
GATILHO = (r"^(nao|errado|incorreto|negativo)\b|esta errad|ta errad|voce errou|nao e (assim|isso)|nao era isso|nao foi isso"
           r"|na verdade|corrig|prefiro|eu prefiro|sempre que|de agora em diante|a partir de agora|daqui pra frente"
           r"|nunca (mais )?(faca|use|coloque)|nao (faca|use|coloque) mais|pare de|lembr[ae]|anot[ae]|guard[ae] (isso|essa)"
           r"|salv[ae] (isso |essa |isto )?na (sua )?memoria|para a memoria|memoriz|aprenda|grave isso"
           r"|^(no|wrong)\b|actually|remember (this|that)|from now on")


def norm(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
    except Exception:
        return
    p = norm(prompt.strip())
    if not p or p.startswith("/") or not re.search(GATILHO, p):
        return
    arquivo = MEM / "memoria.md"
    ctx = (f"[Memória] Esta mensagem parece correção, preferência ou pedido para lembrar. Além de atender ao pedido, "
           f"registre o aprendizado em {arquivo} na seção certa (Correções recebidas / Perfil e preferências / "
           f"Aprendizados técnicos / Decisões em vigor): 1 linha com a data de hoje (AAAA-MM-DD), sem dados sensíveis; "
           f"se contradiz uma linha antiga, risque a antiga (~~…~~) e aponte a nova. Se não houver aprendizado real, não grave. "
           f"Ao final, diga em 1 linha o que foi salvo.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
