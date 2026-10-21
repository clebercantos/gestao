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
- 2026-10-17 — Validação completa no PC após o PR #2: saúde 28/28, 7 skills, 3 tarefas com código 0, lock testado com 2 execuções simultâneas, hooks e memória OK, 7 MCPs conectados (opusclip incluído). O `install` não copiava o `pipeline.*` para `~/.claude/video-ai-pack/tools` (corrigido no .ps1 e no .sh). O conector "claude.ai Adobe" mudou de nome e precisa ser desativado também por esse nome no projeto `gestao`.
- 2026-10-17 — `pipeline.ps1` validado no Windows (presets reels e youtube): ENTREGA com vídeo, SRT, EDL e LUT; áudio dentro do alvo. O worktree `gestao-pr2` no PC precisa de `git fetch` + checkout da ponta da branch antes de testar.
- 2026-10-17 — A API do Premiere (via MCP) não aplica LUT `.cube`: aplique manualmente em Lumetri > Creative > Look, ou use o Resolve, onde a API aceita LUT.
- 2026-10-17 — PowerShell 7 passa argumento vazio (`""`) para comandos nativos e o 5.1 descarta: monte arrays de argumentos (`@pyv`) em vez de `& py $v`.
- 2026-10-17 — No PC há Python 3.15 e 3.12: faster-whisper/ctranslate2 só funcionam no **3.12**. Scripts com transcrição rodam com `py -3.12`; instalador e agente escolhem o 3.12 automaticamente.
- 2026-10-17 — Resolve Studio 21.1.1.10 validado via API de scripting (python do venv do davinci-resolve-mcp com RESOLVE_SCRIPT_API/LIB): criar projeto, importar mídia, criar timeline e apagar o projeto temporário funcionam; o Python do agente de saúde é o 3.12.10 e a saúde deu 28/28.
- 2026-10-17 — Teste da primeira sessão PASSOU: Premiere (MCP premiere-pro via CEP: create_project, import_media, create_sequence_from_clips, split_clip, set_sequence_in_out_points + export_sequence range in_to_out = 3,000 s H.264) e After Effects 26.5 (ae_do: comp.create, keyframe.add, render.start com output "Lossless" .avi = 1 s 1920x1080; o módulo padrão .mp4 precisa do AME).
- 2026-10-17 — Os scripts do pack rodam via `py script.py` e o shebang `#!/usr/bin/env python3` faz o launcher escolher o Python 3.13 (o `py` padrão é 3.15, sem wheel do `av`). Não pinar versões: a decodificação por ffmpeg já isola o faster-whisper do av.
- 2026-10-17 — Em scripts Python no Windows, `Path.write_text/read_text` sem `encoding="utf-8"` usa cp1252: sempre explicitar.
- 2026-10-17 — Conector **Filmit** na conta: controla AE, Premiere (`pr_*`) e Resolve (`dv_*`) pelo painel Filmit dentro do app (aba MCP → Connect). Plano free tem 50 ações/dia. Ler o estado antes de editar e duplicar a sequência antes de mudanças grandes.
- 2026-10-17 — MCP do Resolve correto é `npx davinci-resolve-mcp setup` (samuelgursky); o pacote PyPI `davinci-resolve-mcp` é outro projeto e quebra com mcp 2.x. Registrar com o python do venv em AppData (o exe não fica no PATH). Resolve exige Preferences > General > External scripting = Local.
- 2026-10-17 — faster-whisper 1.2.1 quebra com `av`>=17 (`metadata_errors`) quando auto-editor atualiza o av: decodificar o áudio com ffmpeg (numpy f32le 16k) e passar o array. Corrigido em decupagem.py e legendas.py.
- 2026-10-17 — WhisperModel device "auto" escolhe CUDA e falha sem `cublas64_12.dll`: padrão agora é CPU (env VIDEO_WHISPER_DEVICE=cuda para GPU).
- 2026-10-17 — ffmpeg 9 removeu `-filter_complex_script`: usar `-filter_complex` inline (ou `-/filter_complex arquivo`). Corrigido em decupagem.py (--render).
- 2026-10-17 — PowerShell 5.1 precisa de BOM nos .ps1 com acentos; os 3 instaladores agora têm BOM.
- 2026-10-17 — Instalar muitas skills custa tokens fixos em toda sessão (só as descrições de 100 skills ≈ 10,2k tokens) e faz os gatilhos competirem. A solução adotada foi um cofre + roteador que carrega de 2 a 5 skills por pedido.
- 2026-10-17 — Os números de instalação no skills.sh são inflados por packs (HyperFrames, inference.sh, RunComfy) e por espelhos/clones. É preciso deduplicar e ponderar.
- 2026-10-17 — "caption" em skills costuma ser texto de post de rede social, não legenda de vídeo. Para legenda, exija contexto de vídeo, SRT ou transcrição.
- 2026-10-17 — No Windows PowerShell 5.1, `Set-Content -Encoding UTF8` grava **BOM** e `Get-Content` sem `-Encoding` lê como ANSI. Use `[IO.File]::WriteAllText(..., UTF8Encoding($false))` e `Get-Content -Encoding UTF8`.
- 2026-10-17 — Hooks Python no Windows: force `sys.stdout/stdin.reconfigure(encoding="utf-8")`, senão o cp1252 quebra com acentos e com `→`.
- 2026-10-17 — No Windows, prefira `py` a `python`, porque `python` pode ser o atalho da Microsoft Store.
- 2026-10-17 — Com `powershell -File`, listas `a,b` chegam como uma string só. Faça `-split ','` nos parâmetros.
- 2026-10-17 — Colorgrade em ffmpeg: o balanço de branco precisa vir **antes** de esticar os níveis (senão o desvio é amplificado). O gray-world nos meios-tons funcionou melhor que a correção por U/V.
- 2026-10-17 — Sessões na nuvem (claude.ai/code) não acessam o computador local. O acesso exige o Claude Desktop ou `claude remote-control` rodando no PC.
- 2026-10-17 — O repositório `clebercantos/gestao` é **público**: não versionar conversas, credenciais nem dados pessoais nele.

## Decisões em vigor
- 2026-10-17 — O usuário autorizou usar o PC dele como for preciso para continuar o trabalho e validar as configurações, sem pedir permissão a cada passo (a sessão local só roda sem prompts se ele puser o modo Auto). Continuam exigindo aviso: apagar mídia ou dados, publicar, force-push e gastar créditos pagos.
- 2026-10-17 — Validado no PC: Premiere via MCP `premiere-pro` (CEP), After Effects 26.5 (render `.mp4` exige o AME; sem ele use "Lossless" `.avi`), Resolve Studio 21.1.1.10 via API (python do venv do davinci-resolve-mcp), `pipeline.ps1` (reels e youtube) e saúde do agente 28/28.
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

## Decisões em vigor
- 2026-10-18 — Plugins ativados no projeto via `.claude/settings.json`:
  - **Caveman Mode: Short Answers** (diretório da Anthropic): `claude plugin install caveman-mode-short-answers@anthropic-plugin-directory` (o nome `caveman@...` instala outro, o do Ali Akram). Liga com `/caveman`; desliga com "normal answers".
  - **Ruflo** do GitHub (ruvnet/ruflo, antigo claude-flow; não o "Ruflo AI Team" do diretório): ruflo-core (MCP 300+ ferramentas, hooks em Bash/Edit), ruflo-console (`/ruflo`) e ruflo-mods. No PC: `claude plugin marketplace add ruvnet/ruflo` e `claude plugin install ruflo-core@ruflo` (idem console/mods). Precisa de `node`; o estado local (`.claude-flow/`) fica fora do Git.
- 2026-10-17 — O agente pode instalar/configurar no PC o que for necessário (MCPs, CLIs) sem pedir a cada vez. Substitui a regra anterior ("MCP novo só com OK"). Continuam exigindo aviso: gastar créditos (> ~US$ 5), publicar, force-push e apagar dados do usuário.
- 2026-10-17 — No PC, o projeto `gestao` foi isolado: ficam só `magnific-plugins` (rota principal para Premiere/AE/Resolve), `premiere-pro`, `aftereffects`, `davinci-resolve`, `opusclip` e Claude Docs. Filmit, Adobe, Canva, Gmail/Drive/Calendar e `data:*` estão desativados ali.
- 2026-10-17 — Rota em vídeo: MCP do app aberto > conector cloud > scripts ffmpeg locais; sempre manter um projeto editável (EDL/XML). Para "faz tudo"/lotes, `pipeline.py`/`pipeline.ps1` (sem tokens) e o Claude revisa o `decisoes.md`.
- 2026-10-17 — Memória: `memoria.md` + `INDEX.md` importados em todo CLAUDE.md; hooks `memoria_hook.py` (detecta correções) e `registrar_conversa.py` (salva sessões em `conversas/`); o agente regenera `skills.md`, `mcps.md` e `agentes.md` todo dia. Agente/subagente novo lê `memoria.md` e `INDEX.md` e entra em `agentes.md`.
- 2026-10-21 — Assuntos do **Colégio Interativo** têm repositório, memória, agentes, skills e MCPs próprios em repositório privado separado; não registrar nada do colégio aqui (este repo é público).
- 2026-10-17 — O usuário autorizou o agente a instalar/configurar o que for necessário no PC (MCPs, CLIs) sem pedir a cada vez; continuam exigindo aviso: gastar créditos pagos (> ~US$ 5), publicar, force-push e apagar dados do usuário.
- 2026-10-17 — No PC, o projeto `gestao` foi isolado pelo usuário: ficam só `magnific-plugins` (rota principal para Premiere/AE/Resolve), `premiere-pro`, `aftereffects`, `davinci-resolve`, `opusclip` e Claude Docs. Filmit, Adobe, Canva, Gmail/Drive/Calendar e os `data:*` estão desativados ali (as outras pastas não mudaram).
- 2026-10-17 — Para "faz tudo"/lotes, use o `pipeline.py`/`pipeline.ps1` (sem tokens); o Claude entra para revisar o `decisoes.md` e ajustar no app.
- 2026-10-17 — Prioridade de rota em vídeo: MCP do app aberto > conector cloud > scripts ffmpeg locais. Sempre manter um projeto editável (EDL/XML).
- ~~2026-10-17 — O agente instala sozinho só atualizações do que já foi aprovado e skills auditadas. MCPs/programas novos só com OK do usuário.~~ (substituída abaixo)
- 2026-10-17 — A memória local privada fica em `~/.claude/memoria/` e é a fonte da verdade no PC. Esta pasta do repositório guarda só o que pode ser público.
- 2026-10-17 — Sistema de memória:
  - `memoria.md` + `INDEX.md` importados em todo CLAUDE.md;
  - hook `memoria_hook.py` detecta correções e preferências;
  - hook `registrar_conversa.py` salva cada sessão em `conversas/`;
  - o agente regenera `skills.md`, `mcps.md` e `agentes.md` todo dia.
- 2026-10-17 — Todo agente/subagente novo deve ler `memoria.md` e `INDEX.md` e ser registrado em `agentes.md`.
