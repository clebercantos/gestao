---
name: video-motion
description: "Motion design: títulos, lower thirds, logo e transições via After Effects MCP, Remotion ou Higgsfield."
---

# Motion design

## Rota (escolha automática)
| Situação | Rota |
|---|---|
| After Effects aberto | AE MCP (`@kumoproductions/mcp-aftereffects` ou `TheLlamainator/after-effects-mcp`) + skill `aftereffects-motion` (LobzyJay). Sempre: `ae_context` → planejar → operação agrupada com undo → render de frame para revisão (Read no PNG) → salvar versão `_v###`. |
| AE fechado mas usuário quer projeto AE | Gere `.jsx` (ExtendScript) com comentários e instrua `File > Scripts > Run Script File`. |
| Gráficos gerados por IA editáveis no AE | Higgsfield MCP (Katana, lançado 09/10/2026; `https://mcp.higgsfield.ai/mcp`, consome créditos). |
| Vídeo programático, dados, templates em lote | Remotion + skills oficiais (`npx skills add remotion-dev/skills`; `/remotion-create`, `/remotion-render`). |
| Peça social rápida a partir de design | Adobe `animate_design` (Express) ou Canva (`import-claude-motion-from-url`). |

## Princípios (aplique sem o usuário pedir)
- **Easing:** nunca linear em UI/títulos. Entrada `easeOutCubic/Expo` (influência 70–85%), saída `easeInCubic`. Em AE: velocity graph com influência 75% na chegada.
- **Duração:** micro (ícones) 6–10 frames; textos 12–18 frames de entrada; lower third total 4–6 s; logo reveal 2–3 s.
- **Stagger:** 2–4 frames entre letras/palavras/itens.
- **Hierarquia:** 1 movimento principal por vez; secundários começam 20–30% depois.
- **Safe areas:** title safe 90%; em 9:16 deixe 15% de topo e 25% de base livres (UI dos apps).
- **Motion blur** ligado em elementos rápidos; shutter 180°.
- **Tipografia:** máx. 2 famílias; use `adobe-fonts` / `font_recommend` para escolher pares licenciáveis.
- **Consistência de marca:** se houver brand kit (Magnific `brand_kit_get`, Canva `list-brand-kits`), use cores/fontes dele.

## Expressões AE úteis (cole via MCP)
```js
// Overshoot/bounce na chegada (aplicar em Position/Scale)
amp=.06; freq=3; decay=6; n=0;
if (numKeys>0){ n=nearestKey(time).index; if(key(n).time>time) n--; }
if (n>0){ t=time-key(n).time; v=velocityAtTime(key(n).time-thisComp.frameDuration/10);
  value + v*amp*Math.sin(freq*t*2*Math.PI)/Math.exp(decay*t); } else value;
```
```js
// Wiggle controlado por slider
wiggle(effect("Freq")("Slider"), effect("Amp")("Slider"))
```
```js
// Contador numérico (Source Text)
Math.round(linear(time, inPoint, inPoint+1.5, 0, effect("Valor")("Slider"))).toLocaleString("pt-BR")
```

## QA de motion
Renderize frames-chave (início, meio, fim de cada animação) e inspecione: texto legível ≥ 1,5 s parado,
nada fora da safe area, contraste do texto ≥ 4.5:1 sobre o fundo, sem pulos de keyframe.
