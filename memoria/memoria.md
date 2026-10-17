# memoria.md — o que o Claude aprendeu trabalhando com você

> Lida em **toda** conversa (importada pelo CLAUDE.md). Regras de escrita:
> - Uma linha por item, com data `AAAA-MM-DD`. Mais recente no topo de cada seção.
> - Correção recebida **substitui** a regra antiga (risque com `~~...~~` e explique em seguida).
> - Nada de senhas, tokens, e-mails ou dados de clientes. Esta cópia fica num repositório **público**;
>   detalhes privados vão só para `~/.claude/memoria/memoria.md` no seu computador.

## Perfil e preferências
- 2026-10-17 — Fala português do Brasil; respostas e documentos em PT-BR.
- 2026-10-17 — Trabalha com edição de vídeo (Trevisa Films): Adobe Premiere, After Effects, DaVinci Resolve, motion design, colorgrade, decupagem e legendas.
- 2026-10-17 — Usa **Windows** no computador local; acompanha as sessões na nuvem pelo app do Claude.
- 2026-10-17 — Quer tudo **automático e autônomo**: prompt aprimorado, escolha da ferramenta e manutenção sem precisar pedir.
- 2026-10-17 — Quer que correções e aprendizados virem memória permanente (este arquivo), e que conversas, skills, MCPs e agentes fiquem documentados em MD para consulta.
- 2026-10-17 — Prefere decisões baseadas em dados da comunidade (uso, qualidade, custo de tokens), não em listas genéricas.

## Correções recebidas
- (nenhuma ainda; registre aqui toda vez que o usuário disser que algo estava errado)

## Aprendizados técnicos (verificados)
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
- 2026-10-17 — O usuário autorizou o agente a instalar/configurar o que for necessário no PC (MCPs, CLIs) sem pedir a cada vez; continuam exigindo aviso: gastar créditos pagos (> ~US$ 5), publicar, force-push e apagar dados do usuário.
- 2026-10-17 — Prioridade de rota em vídeo: MCP do app aberto > conector cloud > scripts ffmpeg locais. Sempre manter um projeto editável (EDL/XML).
- ~~2026-10-17 — O agente instala sozinho só atualizações do que já foi aprovado e skills auditadas. MCPs/programas novos só com OK do usuário.~~ (substituída abaixo)
- 2026-10-17 — A memória local privada fica em `~/.claude/memoria/` e é a fonte da verdade no PC. Esta pasta do repositório guarda só o que pode ser público.
- 2026-10-17 — Sistema de memória:
  - `memoria.md` + `INDEX.md` importados em todo CLAUDE.md;
  - hook `memoria_hook.py` detecta correções e preferências;
  - hook `registrar_conversa.py` salva cada sessão em `conversas/`;
  - o agente regenera `skills.md`, `mcps.md` e `agentes.md` todo dia.
- 2026-10-17 — Todo agente/subagente novo deve ler `memoria.md` e `INDEX.md` e ser registrado em `agentes.md`.
