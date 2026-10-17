# Video AI Pack — Claude + Premiere + After Effects + Resolve

Pack de instalação que faz o Claude (Claude Code e, em parte, Claude Desktop/Cowork) tratar
**todo pedido de vídeo** de forma automática e integrada: aprimora o prompt, escolhe a ferramenta
certa (MCP do app aberto, conector na nuvem ou ffmpeg local), decide decupagem, cor, legenda e ritmo
sozinho, e fecha com um checklist de QA.

> Pesquisa feita em 17/10/2026, cobrindo principalmente o que saiu ou foi atualizado entre 03/10 e 17/10/2026,
> mais as bases que continuam sendo referência. Quase todos os MCPs de Premiere e After Effects são
> **projetos da comunidade, não da Adobe**: veja o código e as permissões de cada um antes de usar em projeto de cliente.

---

## 1. O que a pesquisa encontrou

### Novidades das últimas 2 semanas
| Data | O quê | Por que importa |
|---|---|---|
| 09/10/2026 | **Higgsfield Katana**, editor de vídeo dentro do Claude via Higgsfield MCP (`https://mcp.higgsfield.ai/mcp`) | Motion graphics, vídeos de lançamento e edições estilizadas que continuam **editáveis no After Effects**. Precisa de plano pago (créditos Higgsfield). |
| ~12/10/2026 | **invideo MCP** (`https://mcp.invideo.io/mcp`), com relatos de uso real | Timeline com cortes, cor, mix, legendas palavra a palavra e checkpoints. Exporta projeto para **Premiere, Final Cut e Resolve**. |
| ~11/10/2026 | **premiere-pro-mcp** v1.24.x (leancoderkavy), com bridge UXP em preview para Premiere 25.6+ | É o MCP de Premiere mais completo: timeline, cor/LUT, legendas, keyframes, exportação e QA de entrega. |
| contínuo | **OpusClip MCP** (`https://mcp.opus.pro/mcp`) | Acha momentos virais, corta, legenda, reenquadra (9:16, 1:1) e agenda posts. |

### Bases recentes que entram no pack
| Ferramenta | Tipo | Uso no pack |
|---|---|---|
| [DaVinci Resolve 21.1](https://www.cgchannel.com/2026/09/blackmagic-design-releases-resolve-21-1/) (set/2026) | **MCP oficial** da Blackmagic | Controle do Resolve por linguagem natural (organizar mídia, editar, highlights) |
| [davinci-resolve-mcp](https://github.com/lordhoell/davinci-resolve-mcp) | MCP + skill da comunidade (440+ ferramentas, 16 de cor) | Nós, LUT, CDL, color groups, render |
| [mcp-aftereffects](https://github.com/kumoproductions/mcp-aftereffects) (Kumo) | MCP para AE 2024–2026 | Comps, layers, keyframes, expressões, render de frame |
| [after-effects-mcp](https://github.com/JUNKDOGE-JOE/after-effects-mcp) / TheLlamainator | MCP + painel CEP | Alternativa para AE |
| [motion-design-with-claude](https://github.com/LobzyJay/motion-design-with-claude) | Skills `motion-design`, `aftereffects-motion`, `blender-motion`, `motion-design-critique` | Princípios de motion e padrões de ExtendScript |
| [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills) | Skills oficiais | Vídeo programático, legendas animadas, render |
| [Adobe for creativity](https://developer.adobe.com/adobe-for-creativity/) (conector oficial, abr/2026) | Conector Claude | Quick Cut, resize/reframe, melhoria de voz, resumo de mídia, fontes, Express |
| Magnific (conector) | Conector Claude | `video_color_grade`, `video_color_transfer`, `video_magic_cut`, upscale, HDR, áudio |
| [video-captions](https://github.com/katareayush/video-captions), [video-prep](https://github.com/lucyfengcl-art/video-prep), [rough cut skill](https://github.com/vincentventalon/claude-code-video-editing-skill), auto-editor | Skills da comunidade | Serviram de referência para os scripts locais de decupagem e legenda |

**Conclusão:** nenhuma ferramenta faz tudo sozinha. O que falta é uma **camada de orquestração**:
algo que reconheça o pedido, transforme em especificação concreta, escolha a melhor rota disponível
e encadeie as etapas na ordem profissional. É isso que este pack faz.

---

## 2. Como funciona

```
 Você: "decupa esse vídeo, cor cinematic e legenda pro Reels"
          │
          ▼
 [hook UserPromptSubmit]  video_intent.py
   detecta intenções (decupagem, cor, legenda, motion, áudio, entrega, app alvo)
   e injeta instruções no contexto
          │
          ▼
 [skill video-orquestrador]
   1. Brief de Edição (aprimoramento do prompt + defaults)
   2. Inventário: ffprobe + ToolSearch (descobre MCPs/conectores ativos)
   3. Roteamento: app aberto (MCP) > conector cloud > ffmpeg local
   4. Execução encadeada ──► video-decupagem ─► video-colorgrade ─► video-motion ─► video-legendas
   5. decisoes.md + QA ───► video-entrega
```

| Componente | Arquivo | Função |
|---|---|---|
| Hook automático | `hooks/video_intent.py` | Liga o pack sozinho em qualquer pedido de vídeo, sem comando |
| Orquestrador | `skills/video-orquestrador` | Aprimora o prompt, monta a tabela de roteamento e define a ordem do pipeline |
| Decupagem | `skills/video-decupagem` + `decupagem.py` | Corta silêncios, fillers e retakes; gera log com timecode, EDL e rough cut |
| Cor | `skills/video-colorgrade` + `analisar_cor.py` | Mede a imagem, corrige balanço de branco, níveis e exposição, aplica 6 looks e exporta **LUT .cube** |
| Legendas | `skills/video-legendas` + `legendas.py` | SRT/VTT (42 car., 2 linhas, 17 CPS), ASS karaokê/padrão/minimal, glossário, burn-in |
| Motion | `skills/video-motion` | Rotas AE/Remotion/Higgsfield, easing, durações, expressões prontas |
| Entrega | `skills/video-entrega` | Presets por plataforma, loudness e checklist de QA |
| Regras globais | `config/CLAUDE.md.snippet` | Prioridades, segurança da mídia original, limite de gasto |
| Prompts | `prompts/biblioteca.md` | Modelos prontos para Premiere, Resolve, AE, vertical e legendas |

---

## 3. Instalação

Pré-requisitos: [Claude Code](https://code.claude.com), Python 3.9+, ffmpeg. Para MCPs locais: Node.js 20+ (Kumo AE pede 24+).

**macOS / Linux / WSL**
```bash
git clone https://github.com/clebercantos/gestao.git && cd gestao/video-ai-pack
./install.sh --mcp all --community
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/clebercantos/gestao.git; cd gestao\video-ai-pack
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1 -Mcp all -Community
```

| Opção | Efeito |
|---|---|
| (sem opções) | Skills + hook + CLAUDE.md + `faster-whisper` e `auto-editor` |
| `--mcp premiere,ae,resolve,opusclip,invideo,higgsfield` ou `all` | Registra os MCPs no escopo do usuário |
| `--community` | Remotion skills, auto-editor skill e as skills de motion do LobzyJay |
| `--uninstall` | Remove tudo e deixa o resto do `settings.json` e do `CLAUDE.md` como estava |

O instalador é idempotente: rodar de novo atualiza sem duplicar.

### Passos manuais (uma vez)
1. **Premiere:** depois do `--install-cep`, reinicie o Premiere e abra `Window > Extensions > MCP for Adobe Premiere Pro`. Para Claude Desktop, há um `.mcpb` na [release do projeto](https://github.com/leancoderkavy/premiere-pro-mcp).
2. **After Effects:** `Preferences > Scripting & Expressions > Allow Scripts to Write Files and Access Network`. No macOS, autorize o terminal em *Privacidade e Segurança > Automação*.
3. **Resolve:** o MCP da comunidade exige o Resolve aberto (alguns recursos são só do Studio). Para o **MCP oficial do 21.1**, siga o readme da Blackmagic e registre com `claude mcp add`.
4. **Conectores remotos** (OpusClip, invideo, Higgsfield): no Claude Code rode `/mcp` e faça o login OAuth. No claude.ai/Desktop, adicione em *Settings > Connectors > Add custom connector* com as URLs acima.
5. **Conectores que você já tem no claude.ai** (Adobe for creativity, Magnific, Canva) já entram no roteamento automaticamente. Só falta autorizar o Adobe se ele pedir login.

### Claude Desktop / Cowork
O hook roda só no Claude Code. No Desktop, use `config/claude_desktop_config.example.json` para os MCPs
e envie as pastas de `skills/` como skills personalizadas (*Settings > Capabilities > Skills*). O
orquestrador é acionado pela descrição da skill.

---

## 4. Uso

Peça em linguagem natural. Não precisa de comando:

```
decupa o entrevista.mp4, tira os erros e deixa 2 minutos com cor natural e legenda
transforma o podcast.mp4 em 3 reels com legenda karaokê
no Premiere, aplica um look cinematográfico na sequência "Final"
cria um lower third animado no After Effects com meu nome
```

Os scripts também funcionam sozinhos:
```bash
python3 ~/.claude/skills/video-decupagem/scripts/decupagem.py bruto.mp4 --transcribe --render
python3 ~/.claude/skills/video-colorgrade/scripts/analisar_cor.py bruto_decupagem/corte.mp4 --look cinematic --apply
python3 ~/.claude/skills/video-legendas/scripts/legendas.py graded.mp4 --estilo karaoke --burn
```

Mais modelos em [`prompts/biblioteca.md`](prompts/biblioteca.md).

---

## 5. Limites (leia antes de usar com cliente)
- Os MCPs de Premiere e AE são de terceiros, dependem de painel CEP/UXP e mudam com frequência. Fixe a versão em produção.
- A decupagem automática acerta bem em talking heads. Em ficção ou multicâmera, use como **pré-seleção** e revise.
- `analisar_cor.py` faz correção técnica e looks de base. Para pele e grade fino, use o Resolve MCP ou a LUT gerada como ponto de partida.
- Conectores cloud (Magnific, Higgsfield, OpusClip, invideo) consomem créditos. O orquestrador avisa antes de gastar mais de ~US$ 5.
- Remotion exige licença comercial para empresas com 4 ou mais funcionários. Confira em remotion.dev.

## Fontes
- Premiere: [leancoderkavy/premiere-pro-mcp](https://github.com/leancoderkavy/premiere-pro-mcp), [hetpatel-11/Adobe_Premiere_Pro_MCP](https://github.com/hetpatel-11/adobe_premiere_pro_mcp), [antipaster/Adobe-Premiere-Pro-MCP](https://github.com/antipaster/adobe-premiere-pro-mcp), [fuuuuuuma/premiere-skills](https://github.com/fuuuuuuma/premiere-skills)
- After Effects: [kumoproductions/mcp-aftereffects](https://github.com/kumoproductions/mcp-aftereffects), [JUNKDOGE-JOE/after-effects-mcp](https://github.com/JUNKDOGE-JOE/after-effects-mcp), [LobzyJay/motion-design-with-claude](https://github.com/LobzyJay/motion-design-with-claude), [Vagon: Claude Code + After Effects](https://vagon.io/blog/how-to-use-claude-code-with-after-effects), [Synthetic AE MCP](https://synthetic.com.ar/ae-mcp)
- Higgsfield: [Katana (09/10/2026)](https://www.ababnews.com/news/1e73c91f-9643-45d8-978c-28346cc36322), [Higgsfield help center](https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-claude), [AlphaSignal](https://alphasignal.ai/news/higgsfield-lets-claude-build-fully-editable-after-effects-projects)
- Resolve: [CG Channel, Resolve 21.1](https://www.cgchannel.com/2026/09/blackmagic-design-releases-resolve-21-1/), [lordhoell/davinci-resolve-mcp](https://github.com/lordhoell/davinci-resolve-mcp), [barckley75/resolve-claude-mcp](https://github.com/barckley75/resolve-claude-mcp)
- Conectores: [invideo MCP](https://invideo.io/mcp/), [OpusClip MCP](https://www.opus.pro/mcp), [Adobe for creativity](https://blog.adobe.com/en/publish/2026/04/28/adobe-for-creativity-connector), [OpenClip MCP](https://openclip.app/mcp)
- Skills: [Remotion skills](https://www.remotion.dev/docs/ai/skills), [video-captions](https://github.com/katareayush/video-captions), [video-prep](https://github.com/lucyfengcl-art/video-prep), [claude-code-video-editing-skill](https://github.com/vincentventalon/claude-code-video-editing-skill), [video-editing-skill](https://github.com/6missedcalls/video-editing-skill)
