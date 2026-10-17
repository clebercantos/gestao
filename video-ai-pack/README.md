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

### Top-100 skills da comunidade (comparadas e integradas)
Cruzei **5.490 skills** do skills.sh e do claudemarketplaces.com usando instalações, estrelas, auditorias de segurança
(Gen Agent Trust Hub, Socket, Snyk), data de lançamento e o **tamanho real de cada SKILL.md em tokens**.
Removi os espelhos e fiz a curadoria pela aderência ao fluxo Premiere/AE/Resolve. Ranking completo, metodologia e achados:
**[`catalogo/CATALOGO.md`](catalogo/CATALOGO.md)**. Dados brutos: [`catalogo/skills.json`](catalogo/skills.json).

| Categoria | Destaques (nota) |
|---|---|
| Decupagem | `auto-editor-export` (84,6, gera XML para Premiere/Resolve) · `auto-editor` (81,6) · `resolve-rough-cut` / `resolve-tighten-recording` · `video-use` |
| Cor | `resolve-color` (77,5) · `color-grading-finishing` (70,2). Categoria mais fraca, coberta pela skill própria `video-colorgrade` |
| Legendas | `remotion-captions` (87,7) · `openai/transcribe` (79,6) · `auto-editor-transcribe` (77,0) · `skill-captions` |
| Motion / AE | `hyperframes-animation` (85,9) · `iart-ai/after-effects` (79,4) · `motion-art-direction` · `lobzyjay/motion-design` |
| Apps | `resolve-session` (78,6) · `flue/premiere` · `premiere-pro-mcp` · `edit-premiere-project` · `capcut-edit` |
| Programático | Remotion oficial (create/render/best-practices) · HyperFrames (core/media-use) |

**Por que não instalar as 100?** Só as descrições somariam ~10,2k tokens fixos em toda sessão, e várias skills
disputariam o mesmo gatilho. O pack guarda as 100 num **cofre** fora de `~/.claude/skills` (custo fixo zero).
A cada pedido de vídeo, o **roteador** escolhe as 2 a 5 melhores para aquelas intenções e apps, dentro de um orçamento (padrão 7k tokens).
Pedidos que não são de vídeo não custam nada.

---

## 2. Como funciona

```
 Você: "decupa esse vídeo, cor cinematic e legenda pro Reels"
          │
          ▼
 [hook UserPromptSubmit]  video_intent.py  →  pack.py route
   detecta intenções (10 tipos) + apps (Premiere, Resolve, AE, Remotion…)
   escolhe 2–5 skills do top-100 no cofre, dentro do orçamento de tokens,
   e injeta a lista exata (com caminhos) no contexto
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
| Roteador + cofre | `tools/pack.py` + `catalogo/skills.json` | Escolhe as skills do top-100 por pedido; `sync`, `route`, `list`, `install`, `config`, `stats` |
| Catálogo | `catalogo/CATALOGO.md` | Ranking comparativo das 100 skills com metodologia e achados |
| Orquestrador | `skills/video-orquestrador` | Aprimora o prompt, monta a tabela de roteamento e define a ordem do pipeline |
| Decupagem | `skills/video-decupagem` + `decupagem.py` | Corta silêncios, fillers e retakes; gera log com timecode, EDL e rough cut |
| Cor | `skills/video-colorgrade` + `analisar_cor.py` | Mede a imagem, corrige balanço de branco, níveis e exposição, aplica 6 looks e exporta **LUT .cube** |
| Legendas | `skills/video-legendas` + `legendas.py` | SRT/VTT (42 car., 2 linhas, 17 CPS), ASS karaokê/padrão/minimal, glossário, burn-in |
| Motion | `skills/video-motion` | Rotas AE/Remotion/Higgsfield, easing, durações, expressões prontas |
| Entrega | `skills/video-entrega` | Presets por plataforma, loudness e checklist de QA |
| Áudio | `skills/video-audio` + `audio.py` | Limpeza de voz (ruído medido), loudness por plataforma (−14/−23/−16 LUFS), trilha com ducking |
| Regras globais | `config/CLAUDE.md.snippet` | Prioridades, segurança da mídia original, limite de gasto |
| Prompts | `prompts/biblioteca.md` | Modelos prontos para Premiere, Resolve, AE, vertical e legendas |
| Agente Windows | `agente/` | `instalar-agente.ps1` (instala tudo e agenda), `agente.py`/`agente.ps1` (saúde, manutenção, descoberta), subagente `video-ai-mantenedor` |

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
| `--apps premiere,resolve,aftereffects` | Apps que você tem. O roteador libera as skills que dependem deles mesmo quando o pedido não cita o app |
| `--apis elevenlabs,openai,…` | APIs pagas que você usa. Sem isso, as skills de API ficam de fora |
| `--budget 7000` | Teto de tokens de skills externas por pedido |
| `--no-sync` | Não baixa o cofre agora (rode depois `pack.py sync`) |
| `--community` | Instala as skills **completas** (com scripts) de Remotion e auto-editor e as de motion do LobzyJay |
| `--uninstall` | Remove tudo e deixa o resto do `settings.json` e do `CLAUDE.md` como estava |

O instalador é idempotente: rodar de novo atualiza sem duplicar.

### Video AI Agent: instalação e manutenção automáticas no Windows
Um único script instala tudo e deixa um agente cuidando da instalação sozinho.
Não precisa de administrador. Abra o **PowerShell** (não precisa de admin) e rode:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
git clone https://github.com/clebercantos/gestao.git $env:USERPROFILE\gestao
cd $env:USERPROFILE\gestao\video-ai-pack\agente
.\instalar-agente.ps1 -Apps premiere,aftereffects,resolve -Mcp premiere,ae,resolve
```
(Sem o Git instalado, baixe o ZIP do repositório e rode o script de dentro da pasta `video-ai-pack\agente`. O script instala o Git e o resto.)

O que ele faz:
1. Instala o que falta via `winget`: Git, Python 3.12, Node LTS e FFmpeg. Instala também o **Claude Code** (instalador oficial).
2. Instala o pack (skills, hook, roteador, cofre top-100), os MCPs escolhidos e o subagente `video-ai-mantenedor`.
3. Agenda três rotinas em **Agendador de Tarefas → VideoAIAgent**:

| Rotina | Quando | O que faz |
|---|---|---|
| Saude | ao fazer logon (+5 min) e a cada 6 h | Confere 20 itens (ferramentas, pack, hook, cofre, MCPs, apps, disco) e **repara sozinha** o que faltar |
| Manutencao | todo dia às 03:17 (ou quando o PC ligar) | `git pull` do pack com reinstalação se mudou, atualiza o cofre, pip, painel CEP do Premiere quando sai versão nova, `winget upgrade`, `claude update` e limpa logs |
| Descoberta | segundas às 09:13 | Monitora ~1.900 skills no skills.sh, versões de MCPs (npm/PyPI/GitHub) e roda uma **pesquisa semanal com o Claude na web**. Adota até 3 skills novas aprovadas nos critérios (auditoria limpa, nota ≥ 70, tokens ≤ 6k, escopo de vídeo) |

4. Mostra uma **notificação do Windows** quando há alerta. Os relatórios ficam em `%LOCALAPPDATA%\VideoAIAgent\relatorios\ultimo.md`, com um atalho na área de trabalho.

**Limite de segurança:** o agente aplica sozinho as atualizações do que você já aprovou e adota skills, que são só arquivos de instrução auditados.
**MCPs, conectores e programas novos** aparecem no relatório com o comando de instalação, mas só entram com o seu OK.
No Claude Code, você pode pedir: *"use o agente video-ai-mantenedor para revisar o relatório"*.

| Comando | Para quê |
|---|---|
| `powershell -File agente.ps1 -Modo status` | Último resumo |
| `powershell -File agente.ps1 -Modo tudo` | Roda tudo agora |
| `.\instalar-agente.ps1 -Desinstalar` | Remove tarefas, agente e pack (mantém Git, Python, Node e Claude) |
| `-SemPesquisaIA`, `-SemAtualizarSistema`, `-Branch <nome>` | Opções do instalador |

O ajuste fino fica em `%LOCALAPPDATA%\VideoAIAgent\config.json`: `auto_adotar`, `max_adocoes`, `nota_minima`, `min_installs`, `max_tokens_skill`, `retencao_dias` e `notificar`.

### Memória permanente (todas as conversas e agentes consultam)
O instalador cria `~/.claude/memoria/` e faz **toda** sessão do Claude Code ler esses arquivos (import no `~/.claude/CLAUDE.md`).
Isso vale também para os agentes, subagentes e o `claude -p` do agente agendado:

| Arquivo | O que guarda | Quem atualiza |
|---|---|---|
| `memoria.md` | preferências, **correções**, aprendizados e decisões (sempre carregado) | o Claude, quando você corrige ou ele aprende algo (o hook `memoria_hook.py` detecta "não, está errado", "prefiro", "lembre disso"…) |
| `INDEX.md` | mapa da memória e como buscar | instalador/agente |
| `skills.md` | todas as skills: pack, instaladas no PC, conta Claude, top-100, adotadas | agente (diário) |
| `mcps.md` | MCPs registrados (`claude mcp list`), conectores claude.ai, MCPs do pack, alternativas | agente (diário) |
| `agentes.md` | agentes, subagentes, hooks e automações ativos | agente (diário) |
| `conversas/` | resumo automático de **cada** sessão do Claude Code (pedidos, respostas, arquivos, ferramentas), com segredos mascarados | hook `registrar_conversa.py` (SessionEnd) |
| `historico/` | resumos curados das conversas importantes | o Claude |

- **Privacidade:** `~/.claude/memoria/` fica só no seu PC. Este repositório é **público**, por isso a pasta `memoria/` dele guarda apenas a versão sem dados sensíveis. É essa versão que as sessões na nuvem leem, via `CLAUDE.md` na raiz.
- **Sincronizar PC ↔ nuvem:** crie um repositório **privado** e instale com `.\instalar-agente.ps1 -RepoMemoria https://github.com/<voce>/<repo-privado>.git`. A manutenção diária faz commit, pull e push da memória.
- **Conversas no claude.ai (web/app):** elas não rodam no seu PC, então os hooks não as alcançam. Para que também consultem a memória, coloque o conteúdo de `memoria.md` nas instruções de um Projeto do claude.ai ou nas preferências do perfil.

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

Roteador na mão (útil no Claude Desktop, onde não há hook):
```bash
P=~/.claude/video-ai-pack/pack.py
python3 $P route "tira os silêncios do podcast no Resolve e exporta"   # o que seria carregado
python3 $P list --cat cor                                              # catálogo por categoria
python3 $P install resolve-color                                       # skill completa via npx skills add
python3 $P config --apps premiere,aftereffects --budget 5000
python3 $P sync --force                                                # atualiza o cofre
```
O cofre guarda skills de terceiros. O orquestrador as usa como **referência**: segue as técnicas,
mas pede confirmação antes de rodar comandos destrutivos ou de rede que elas sugerirem.

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
