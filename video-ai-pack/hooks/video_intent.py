#!/usr/bin/env python3
"""UserPromptSubmit hook do Video AI Pack.

Detecta pedidos de edição de vídeo / motion / cor / legenda e injeta contexto
para que o Claude carregue a skill `video-orquestrador`, aprimore o prompt e
acione automaticamente as skills, MCPs e conectores certos.

Entrada: JSON do Claude Code em stdin (campo "prompt").
Saída: JSON com hookSpecificOutput.additionalContext (ou nada, se não for vídeo).
"""
import json
import re
import sys
import unicodedata

INTENTS = {
    "decupagem": r"decupa|decupagem|rough ?cut|corte (seco|bruto)|silenc|jump ?cut|tirar (pausas|respira)|melhores (takes|momentos)|selecionar takes|retake|highlight|sizzle|cortes?\b",
    "colorgrade": r"color ?grad|colori[zs]a|corre[cç][aã]o de cor|grade\b|\blut\b|look cinem|cinematic|teal|orange|balan[cç]o de branco|white balance|exposi[cç][aã]o|\blog\b|rec ?709|slog|clog|vlog",
    "legenda": r"legenda|subtitle|caption|\bsrt\b|\bass\b|transcri|karaok|hormozi|closed caption",
    "motion": r"motion|after ?effects|\bae\b|anima[cç]|lower ?third|vinheta|kinetic|tipografia animada|remotion|keyframe|express[aã]o|logo reveal|intro|outro|transi[cç]",
    "audio": r"[aá]udio|ru[ií]do|noise|voz|dialogo|di[aá]logo|trilha|m[uú]sica|loudness|lufs|mixag",
    "entrega": r"export|render|entreg|reels|shorts|tiktok|9:16|vertical|youtube|instagram|formato|codec|h\.?264|h\.?265|prores",
    "app_premiere": r"premiere|\bppro\b|prproj",
    "app_resolve": r"resolve|davinci",
}
SKILL_FOR = {
    "decupagem": "video-decupagem",
    "colorgrade": "video-colorgrade",
    "legenda": "video-legendas",
    "motion": "video-motion",
    "audio": "video-decupagem",
    "entrega": "video-entrega",
}
VIDEO_GATE = r"v[ií]deo|video|clip|footage|filmag|timeline|sequ[eê]ncia|edi[cç][aã]o|editar|edit\b|montagem|premiere|after ?effects|resolve|davinci|reels|shorts|tiktok|youtube|\.mp4|\.mov|\.mxf|\.braw|\.r3d|legenda|colorgrad|motion|decupa"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return text


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    prompt = norm(data.get("prompt", ""))
    if prompt.startswith("/") or not re.search(VIDEO_GATE, prompt):
        return

    hits = [k for k, rx in INTENTS.items() if re.search(rx, prompt)]
    tarefas = [h for h in hits if not h.startswith("app_")] or ["decupagem", "colorgrade", "legenda", "entrega"]
    apps = [h[4:] for h in hits if h.startswith("app_")]
    skills = sorted({SKILL_FOR[t] for t in tarefas if t in SKILL_FOR} | {"video-entrega"})

    ctx = f"""[Video AI Pack] Pedido de vídeo detectado.
Intenções detectadas: {', '.join(tarefas)}{' | app alvo: ' + ', '.join(apps) if apps else ''}.
OBRIGATÓRIO antes de agir:
1. Carregue a skill `video-orquestrador` (Skill tool) e siga o pipeline dela.
2. Aprimore o prompt internamente com o template "Brief de Edição" da skill (objetivo, plataforma, duração, tom, referências, entregáveis). Preencha lacunas com os defaults da skill; só pergunte ao usuário se faltar o arquivo de mídia ou se a escolha for irreversível.
3. Carregue também as skills especialistas de cada intenção: {', '.join(skills)}.
4. Descubra as ferramentas disponíveis via ToolSearch (premiere, aftereffects, resolve, Adobe, Magnific, invideo, opusclip, higgsfield, canva) e escolha a rota pela tabela de roteamento da skill — app local aberto > MCP local > conector cloud > ffmpeg.
5. Decida automaticamente (decupagem, cor, legenda, ritmo) com base na análise da mídia e registre as decisões em um `decisoes.md` ao lado do projeto. Nunca sobrescreva o original: trabalhe em cópias/versões.
6. Finalize com o checklist de QA da skill `video-entrega`."""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx,
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
