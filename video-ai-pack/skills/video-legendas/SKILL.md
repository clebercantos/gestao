---
name: video-legendas
description: "Legendas automáticas: transcrição, SRT/VTT profissional, estilos karaokê/Hormozi/minimal, glossário e burn-in."
---

# Legendas automáticas

Sempre legende **o corte final** (depois da decupagem/montagem), nunca o bruto.
Se a skill `video-decupagem` já gerou `transcricao.json` do corte final, reutilize com `--json`.

## Rota (escolha automática)
| Situação | Rota |
|---|---|
| Premiere aberto | Gere `legendas.srt` com o script e importe via Premiere MCP (`create_caption_track` / import de SRT). Estilo via Essential Graphics/caption style da marca. |
| Projeto Remotion / motion | Skill `/remotion-captions` (legendas animadas como componente). |
| Clipes sociais em lote | OpusClip MCP (caption animado + reframe) ou invideo MCP (word-by-word). |
| Local / entrega rápida | Script abaixo com `--burn`. |

## Script local
```bash
L=~/.claude/skills/video-legendas/scripts/legendas.py
python3 $L VIDEO --estilo padrao                   # SRT+VTT+ASS (YouTube, cursos, institucional)
python3 $L VIDEO --estilo karaoke --burn           # Reels/TikTok/Shorts, palavra destacada
python3 $L VIDEO --estilo minimal --burn           # caixa semitransparente, sóbrio
python3 $L VIDEO --json corte/transcricao.json --glossario termos.txt --cor-destaque 00E5FF
```

## Escolha automática do estilo
- Vertical 9:16 ou brief "viral/dinâmico" → `karaoke` (1 linha, 2–4 palavras, CAIXA ALTA, destaque amarelo `FFD400` ou cor da marca, ~30% acima da base para fugir da UI do app).
- 16:9 YouTube/curso → `padrao` + entregar SRT separado (melhor para SEO e acessibilidade).
- Institucional/luxo/documentário → `minimal`.

## Revisão obrigatória (aprimoramento por LLM)
Depois de gerar, leia `legendas.srt` e corrija você mesmo:
1. Nomes próprios, marcas, siglas e termos técnicos (crie/atualize `termos.txt` com `errado=certo`).
2. Pontuação e maiúsculas segundo a norma PT-BR; números até dez por extenso, acima em algarismos.
3. Remova vícios de linguagem que sobraram ("né", "tipo") se não alteram o sentido.
4. Quebra de linha em unidade de sentido (não separe artigo do substantivo, preposição do complemento).
5. Re-rode com `--json` editado se mudou o texto, para manter tempos consistentes.

## Traduções
Para legendas em outro idioma: traduza `transcricao.json` mantendo os tempos por segmento,
reduzindo o texto para caber em 17 CPS (legenda é adaptação, não tradução literal), e gere com `--lang` do destino.
