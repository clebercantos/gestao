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

## Pendências abertas
- [ ] Usuário: revisar e mesclar o PR #1.
- [ ] Usuário: rodar `instalar-agente.ps1` no Windows, fazer login no `claude` e autorizar os conectores (`/mcp` e o conector Adobe no claude.ai).
- [ ] Testar no Windows real: winget, Agendador, notificações, detecção de apps e `--transcribe`.
- [ ] Opcional: ajustar o roteador para não incluir `yt-shorts` em pedidos de exportação ("anima logo no AE e exporta pro Reels").
- [ ] Opcional: repositório **privado** para sincronizar a memória entre PC e nuvem (`instalar-agente.ps1 -RepoMemoria <url>`).
