# Conversa 2026-10-17 — Video AI Pack, top-100 skills, agente Windows e memória

Sessão Claude Code na nuvem · repositório `clebercantos/gestao` · branch `claude/video-editing-plugins-research-973wsr` ·
PR [#1](https://github.com/clebercantos/gestao/pull/1) (rascunho).

## Pedidos e entregas (em ordem)

### 1. Pesquisa de plugins/skills/MCPs de vídeo + pack integrado
**Pedido:** pesquisar as novidades das últimas 2 semanas (Claude, Premiere, After Effects, motion, prompts) e montar um pack que
trabalhe automaticamente em cada pedido: aprimorar o prompt e escolher sozinho decupagem, colorgrade, legendas etc.

**Achados (out/2026):**
- Higgsfield Katana (09/10, via MCP).
- invideo MCP.
- premiere-pro-mcp v1.24.
- OpusClip MCP.
- MCP oficial no DaVinci Resolve 21.1.
- MCPs de After Effects (Kumo, TheLlamainator).
- Skills Remotion oficiais.
- Conector Adobe for creativity.

**Entrega:** `video-ai-pack/` com:
- hook `UserPromptSubmit`;
- skill `video-orquestrador` (Brief de Edição → Inventário → Rota → Execução → QA);
- skills especialistas de decupagem, colorgrade, legendas, motion e entrega;
- scripts testados:
  - `decupagem.py`: silêncio, fillers, retakes → EDL e rough cut;
  - `analisar_cor.py`: WB, níveis, exposição, 6 looks e LUT `.cube`;
  - `legendas.py`: SRT/VTT PT-BR, ASS karaokê/padrão/minimal, burn-in;
- instaladores `install.sh`/`install.ps1`;
- biblioteca de prompts.

### 2. As 100 melhores skills, comparadas e integradas
**Pedido:** comparar as 100 melhores skills por comunidade, uso, qualidade e tokens; integrar e ativar de forma otimizada.

**Método:**
- **Dados:** 5.490 skills (skills.sh + claudemarketplaces.com) → 697 relevantes únicas → 105 curadas → 100.
- **Critérios da nota:** comunidade 30, aderência 35, segurança 15 (auditorias Trust Hub/Socket/Snyk), tokens 15 (SKILL.md real) e frescor 5.

**Entrega:**
- `video-ai-pack/catalogo/CATALOGO.md` e `skills.json`;
- cofre local + roteador `tools/pack.py`, que carrega de 2 a 5 skills por pedido com orçamento de 7k tokens;
- descrições próprias enxutas (~590 → ~210 tokens fixos).

**Conclusões:**
- cor é a maior lacuna;
- o Resolve tem o melhor ecossistema (10 skills `samuelgursky`);
- instalações são infladas por packs.

### 3. "O que precisa ser feito agora?"
- Revisar/mesclar o PR.
- Instalar localmente.
- Configurar o painel do Premiere e as preferências do AE.
- Fazer o login `/mcp`.
- Testar com um vídeo real.
- Autorizar o conector Adobe no claude.ai.

### 4. Agente no Windows para instalar, monitorar e manter
**Entrega:** `video-ai-pack/agente/`:
- `instalar-agente.ps1`:
  - instala via winget Git, Python, Node e FFmpeg, mais o Claude Code;
  - instala o pack, os MCPs e o subagente `video-ai-mantenedor`;
  - agenda Saúde (logon + 6 h), Manutenção (diária 03:17) e Descoberta (segunda 09:13).
- `agente.py`: saúde com autorreparo, manutenção e descoberta. A descoberta usa skills.sh, npm/PyPI/GitHub e pesquisa web com `claude -p`, e adota até 3 skills auditadas por rodada.

**Correções Windows:** BOM, cp1252, alias do `python`, listas via `-File` e MCPs `@latest`.

### 5. Memória permanente e MDs de consulta (esta etapa)
**Pedido:**
- salvar correções e aprendizados em `memoria.md`;
- registrar as conversas;
- gerar MDs de skills, MCPs e agentes;
- fazer todas as conversas e agentes consultarem esses arquivos;
- acessar o computador do usuário.

**Limitação:** a sessão na nuvem não alcança o PC; a parte local é feita pelo instalador e pelo agente.

**Decisão:** o repositório é **público**, então conversas e dados pessoais ficam só em `~/.claude/memoria/` (privado). O repositório guarda apenas a memória pública.

### 6. Sessão local via Remote Control
- Prompt de continuação salvo em `PROMPT-LOCAL.md`.
- O usuário ligou `claude remote-control` no PC (DESKTOP-VE4ABKU), e a sessão na nuvem enviou a tarefa para a sessão local.
- A sessão local instalou tudo e corrigiu bugs reais do Windows:
  - transcrição com `av`>=17;
  - CUDA sem cublas;
  - ffmpeg 9 sem `-filter_complex_script`;
  - cp1252 em JSON/SRT;
  - MCP do Resolve: o pacote certo é o samuelgursky via `npx davinci-resolve-mcp setup`;
  - BOM nos `.ps1`.
- Ela registrou os aprendizados em `memoria.md` e no histórico `2026-10-17_instalacao-local.md`.

### 7. Ajustes da nuvem após revisar os commits locais
- Python 3.12 fixado no instalador e no agente.
- A manutenção parou de reinstalar o pacote PyPI errado do Resolve.
- Conector **Filmit** (AE/Premiere/Resolve) integrado ao roteamento e à memória.
- Depois da mesclagem do PR, o agente passa sozinho a seguir a `main`.
- `instrucoes-claude-ai.md` com o texto para as conversas web consultarem a memória.

### 8. Bateria de testes com os apps abertos em projetos de teste
- **Passaram:**
  - Premiere (MCP `premiere-pro` via CEP: projeto, import, sequência, split, in/out, export H.264);
  - After Effects 26.5 (comp, keyframes, render Lossless; `.mp4` exige o AME);
  - Resolve Studio 21.1.1.10 (projeto, import, timeline);
  - Saúde do agente: 28/28;
  - pipeline decupagem → cor → legendas com fala TTS.
- O usuário pediu que **reinícios do Claude** fiquem para **depois de 01:20** (horário local).

## Pendências abertas
**Usuário:**
- [ ] Aprovar os pedidos de permissão pendentes na sessão local (PowerShell e brainferno-adobe).
- [ ] Filmit: painel Filmit no Premiere/AE → aba MCP → Connect (até agora nenhum app conectado).
- [ ] `/mcp` no Claude Code local: OpusClip e conector Adobe; autorizar o Adobe for creativity no claude.ai.
- [ ] Premiere: manter um único painel CEP do MCP rodando. After Effects: abrir sem `-m` e permitir scripts.
- [ ] **Depois de 01:20:** reiniciar o app do Claude/Claude Code para carregar o MCP do Resolve e os hooks novos.
- [ ] Colar `memoria/instrucoes-claude-ai.md` no perfil ou projeto do claude.ai.
- [ ] Revisar e mesclar o PR #1.
- [ ] Opcional: repositório privado para a memória (`-RepoMemoria`).

**A conferir (sessão local, depois das aprovações):**
- [ ] Filmit: testes `pr_*`, `dv_*` e AE depois do Connect.
- [ ] As 3 tarefas agendadas com LastTaskResult = 0.
- [ ] `~/.claude/memoria/conversas/` recebendo as sessões.
- [ ] Notificação do Windows e pesquisa semanal com `claude -p` (primeira Descoberta real).
