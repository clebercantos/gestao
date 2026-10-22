# memoria.md — o que o Claude aprendeu trabalhando com você

> Lida em **toda** conversa (importada pelo CLAUDE.md). Regras de escrita:
> - Uma linha por item, com data `AAAA-MM-DD`. Mais recente no topo de cada seção. Junte itens sobre o mesmo assunto.
> - Correção recebida **substitui** a regra antiga (risque com `~~...~~` e explique em seguida).
> - Nada de senhas, tokens, e-mails ou dados de clientes. Esta cópia fica num repositório **público**;
>   detalhes privados vão só para `~/.claude/memoria/memoria.md` no seu computador (a fonte da verdade no PC).


## Perfil e preferências
- 2026-10-17 — Fala português do Brasil; respostas e documentos em PT-BR.
- 2026-10-17 — Trabalha com edição de vídeo (Trevisa Films): Adobe Premiere, After Effects, DaVinci Resolve, motion design, colorgrade, decupagem e legendas.
- 2026-10-17 — Usa **Windows** no computador local; acompanha as sessões na nuvem pelo app do Claude.
- 2026-10-17 — Fuso horário: **America/Sao_Paulo** (UTC−3). Horários que ele cita são locais; converta antes de agendar (01:20 BRT = 04:20 UTC).
- 2026-10-17 — Reinícios do Claude/Claude Code ficam para depois de 01:20. O plano tem limite de uso de 5 h, que pode pausar a sessão local no meio do trabalho.
- 2026-10-17 — Quer tudo **automático e autônomo**: prompt aprimorado, escolha da ferramenta e manutenção sem precisar pedir.
- 2026-10-17 — Quer correções e aprendizados como memória permanente (este arquivo), e skills, MCPs, agentes e conversas documentados em MD.
- 2026-10-17 — Prefere decisões baseadas em dados da comunidade (uso, qualidade, custo de tokens), não em listas genéricas.

## Correções recebidas
- 2026-10-18 — "caveman" = plugin **Caveman Mode: Short Answers** do diretório da Anthropic, não o caveman do GitHub (JuliusBrussee). Plugin com nome ambíguo: perguntar qual antes de instalar.

## Aprendizados técnicos (verificados)
- 2026-10-22 — A sessão na nuvem só consegue fazer push na própria branch: apagar branches dá HTTP 403, e apagar ou criar repositórios dá 403 na API. Essa limpeza o usuário faz no GitHub.
- 2026-10-17 — Validado no PC: Premiere via MCP `premiere-pro` (CEP: projeto, import, sequência, split, in/out, export H.264), After Effects 26.5 (comp, keyframe, render; `.mp4` exige o AME, sem ele use "Lossless" `.avi`), Resolve Studio 21.1.1.10 via API (python do venv do davinci-resolve-mcp), `pipeline.ps1` (reels e youtube: vídeo, SRT, EDL, LUT, áudio no alvo) e saúde do agente 28/28.
- 2026-10-17 — Validação após o PR #2: 7 skills, 3 tarefas com código 0, lock com 2 execuções simultâneas, hooks e memória OK, 7 MCPs conectados (opusclip incluído). O `install` não copiava o `pipeline.*` (corrigido no .ps1 e no .sh). O conector "claude.ai Adobe" mudou de nome e precisa ser desativado também por esse nome no projeto `gestao`.
- 2026-10-17 — A API do Premiere (via MCP) não aplica LUT `.cube`: aplique em Lumetri > Creative > Look, ou use o Resolve, cuja API aceita LUT.
- 2026-10-17 — MCP do Resolve correto: `npx davinci-resolve-mcp setup` (samuelgursky); o pacote PyPI de mesmo nome é outro projeto e quebra com mcp 2.x. Registre com o python do venv em AppData (o exe não fica no PATH). Resolve exige Preferences > General > External scripting = Local.
- 2026-10-17 — Conector **Filmit**: controla AE, Premiere (`pr_*`) e Resolve (`dv_*`) pelo painel Filmit no app (aba MCP → Connect). Plano free: 50 ações/dia. Ler o estado antes de editar e duplicar a sequência antes de mudanças grandes.
- 2026-10-17 — Python no PC: o `py` padrão é o 3.15 (sem wheel do `av`) e o shebang `python3` leva ao 3.13. faster-whisper/ctranslate2 só rodam no **3.12**: transcrição com `py -3.12` (instalador e agente já escolhem). Não pinar versões: decodificar via ffmpeg isola o faster-whisper do av.
- 2026-10-17 — faster-whisper 1.2.1 quebra com `av`>=17 (`metadata_errors`): decodifique o áudio com ffmpeg (numpy f32le 16k). Em "auto" ele escolhe CUDA e falha sem `cublas64_12.dll`: padrão CPU (`VIDEO_WHISPER_DEVICE=cuda` para GPU).
- 2026-10-17 — ffmpeg 9 removeu `-filter_complex_script`: use `-filter_complex` inline (ou `-/filter_complex arquivo`).
- 2026-10-17 — Encoding no Windows: Python sem `encoding="utf-8"` usa cp1252 (explicite em `read_text/write_text`; hooks fazem `sys.stdout/stdin.reconfigure(encoding="utf-8")`). PowerShell 5.1: `.ps1` com acento precisa de BOM; `Set-Content -Encoding UTF8` grava BOM e `Get-Content` sem `-Encoding` lê ANSI (use `[IO.File]::WriteAllText(..., UTF8Encoding($false))` e `Get-Content -Encoding UTF8`).
- 2026-10-17 — PowerShell: o 7 passa argumento vazio (`""`) a comandos nativos e o 5.1 descarta (monte arrays, `@pyv`); com `-File`, listas `a,b` chegam como uma string (`-split ','`). Prefira `py` a `python` (atalho da Microsoft Store).
- 2026-10-17 — Colorgrade em ffmpeg: balanço de branco **antes** de esticar os níveis (senão o desvio é amplificado); gray-world nos meios-tons funcionou melhor que a correção por U/V.
- 2026-10-17 — Muitas skills instaladas custam tokens fixos em toda sessão (100 descrições ≈ 10,2k tokens) e disputam gatilhos: por isso o cofre + roteador carrega 2 a 5 por pedido.
- 2026-10-17 — Instalações no skills.sh são infladas por packs (HyperFrames, inference.sh, RunComfy) e espelhos: deduplique e pondere. "caption" em skill costuma ser texto de post, não legenda de vídeo.
- 2026-10-17 — Sessões na nuvem (claude.ai/code) não acessam o PC: exige o Claude Desktop ou `claude remote-control` rodando nele.
- 2026-10-17 — O worktree `gestao-pr2` no PC precisa de `git fetch` + checkout da ponta da branch antes de testar.

## Decisões em vigor
- 2026-10-21 — Assuntos do **Colégio Interativo** têm repositório, memória, agentes, skills e MCPs próprios em repositório privado separado; não registrar nada do colégio aqui (este repo é público).
- 2026-10-18 — Plugins ativados no projeto via `.claude/settings.json`:
  - **Caveman Mode: Short Answers** (diretório da Anthropic): `claude plugin install caveman-mode-short-answers@anthropic-plugin-directory` (o nome `caveman@...` instala outro, o do Ali Akram). Liga com `/caveman`; desliga com "normal answers".
  - **Ruflo** do GitHub (ruvnet/ruflo, antigo claude-flow; não o "Ruflo AI Team" do diretório): ruflo-core (MCP 300+ ferramentas, hooks em Bash/Edit), ruflo-console (`/ruflo`) e ruflo-mods. No PC: `claude plugin marketplace add ruvnet/ruflo` e `claude plugin install ruflo-core@ruflo` (idem console/mods). Precisa de `node`; o estado local (`.claude-flow/`) fica fora do Git.
- 2026-10-17 — O usuário autorizou usar o PC e instalar/configurar o que for necessário (MCPs, CLIs) sem pedir a cada passo (a sessão local só roda sem prompts no modo Auto). Substitui a regra anterior ("MCP novo só com OK"). Continuam exigindo aviso: gastar créditos pagos (> ~US$ 5), publicar, force-push e apagar mídia ou dados do usuário.
- 2026-10-17 — No PC, o projeto `gestao` foi isolado: ficam só `magnific-plugins` (rota principal para Premiere/AE/Resolve), `premiere-pro`, `aftereffects`, `davinci-resolve`, `opusclip` e Claude Docs. Filmit, Adobe, Canva, Gmail/Drive/Calendar e `data:*` estão desativados ali (as outras pastas não mudaram).
- 2026-10-17 — Rota em vídeo: MCP do app aberto > conector cloud > scripts ffmpeg locais; sempre manter um projeto editável (EDL/XML). Para "faz tudo"/lotes, `pipeline.py`/`pipeline.ps1` (sem tokens) e o Claude revisa o `decisoes.md`.
- 2026-10-17 — Memória: `~/.claude/memoria/` (privada) é a fonte da verdade no PC; esta pasta guarda só o que pode ser público. `memoria.md` + `INDEX.md` importados em todo CLAUDE.md; hooks `memoria_hook.py` (detecta correções) e `registrar_conversa.py` (salva sessões em `conversas/`); o agente regenera `skills.md`, `mcps.md` e `agentes.md` todo dia. Agente/subagente novo lê `memoria.md` e `INDEX.md` e entra em `agentes.md`.
- 2026-10-17 — O repositório `clebercantos/gestao` é **público**: não versionar conversas, credenciais nem dados pessoais nele.
