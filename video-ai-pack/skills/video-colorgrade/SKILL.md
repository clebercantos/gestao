---
name: video-colorgrade
description: Correção de cor e colorgrade automáticos — análise de exposição, níveis, balanço de branco, conversão LOG→Rec.709, looks (cinematic, quente, frio, P&B, vintage), shot match e exportação de LUT .cube para Premiere/Lumetri e DaVinci Resolve. Use para "colorgrade", "corrigir cor", "LUT", "look cinematográfico", "deixar mais quente", "igualar câmeras", "material em log".
---

# Colorgrade automático

Ordem técnica obrigatória (nunca aplique look antes da correção):
**1. Converter (LOG/HDR → Rec.709)** → **2. Balanço de branco** → **3. Níveis/exposição** → **4. Shot match** → **5. Look criativo** → **6. Acabamento (grão, vinheta, halation)**.

## Rota (escolha automática)
| Situação | Rota |
|---|---|
| Resolve aberto | Resolve MCP: crie nós nomeados `01_CST` (Color Space Transform), `02_WB`, `03_EXPO`, `04_MATCH`, `05_LOOK`, `06_GRAIN`; aplique `grade.cube` no nó LOOK; use CDL para ajustes finos. Use color groups p/ câmeras iguais. |
| Premiere aberto | Premiere MCP: `color_correct` (temp, tint, exposição, contraste) no clipe; `apply_lut` com `grade.cube` no Adjustment Layer de look. |
| Sem app / entrega rápida | Script local abaixo (gera filtro ffmpeg, LUT e render). |
| Referência de look (imagem/frame de filme) | Magnific `video_color_transfer` com a referência, ou `video_color_grade` / `video_luts_list` (estime custo antes). |
| Fotos/frames do mesmo projeto | Skill `adobe-batch-edit-photos` para manter consistência com o vídeo. |

## Script local

```bash
python3 ~/.claude/skills/video-colorgrade/scripts/analisar_cor.py VIDEO --look cinematic --apply
# material LOG com LUT oficial da câmera:
python3 ~/.claude/skills/video-colorgrade/scripts/analisar_cor.py VIDEO --lut SLog3_to_709.cube --look quente --apply
```
Gera `cor.json` (medições + decisões), `filtro.txt`, `grade.cube` (33³), `antes_depois.png`, `graded.mp4`.
**Sempre** abra `antes_depois.png` (Read) e avalie visualmente antes de entregar. Se a pele ficar
magenta/verde ou o céu estourar, ajuste e rode de novo.

## Escolha automática do look
| Conteúdo detectado / brief | Look |
|---|---|
| Institucional, tutorial, podcast | `natural` |
| Filme, clipe, publicidade, "cinematográfico" | `cinematic` |
| Documentário, gastronomia, lifestyle, pôr do sol | `quente` |
| Tech, saúde, noturno urbano | `frio` |
| Drama, arte, memória | `pb` |
| Nostalgia, moda retrô | `vintage` |

## Checagens de qualidade
- Tons de pele no **skin line** do vetorscópio (~123° / entre R e Y). Nunca empurre pele para fora disso por causa do look.
- Pretos: YLOW ≥ 16 (legal range) e sem esmagar detalhe; brancos ≤ 235, exceto especulares.
- Variação de luma entre planos (`variacao_luma_entre_amostras` > 25) → shot match plano a plano antes do look.
- HDR (PQ/HLG) → só entregue HDR se pedido; senão tone-map: `zscale=t=linear:npl=100,tonemap=hable,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`.
- LOG sem LUT oficial → o script aplica aproximação; avise que a LUT do fabricante dá resultado melhor.
