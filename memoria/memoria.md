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
- 2026-10-17 — Prioridade de rota em vídeo: MCP do app aberto > conector cloud > scripts ffmpeg locais. Sempre manter um projeto editável (EDL/XML).
- 2026-10-17 — O agente instala sozinho só atualizações do que já foi aprovado e skills auditadas. **MCPs/programas novos só com OK do usuário.**
- 2026-10-17 — A memória local privada fica em `~/.claude/memoria/` e é a fonte da verdade no PC. Esta pasta do repositório guarda só o que pode ser público.
- 2026-10-17 — Sistema de memória:
  - `memoria.md` + `INDEX.md` importados em todo CLAUDE.md;
  - hook `memoria_hook.py` detecta correções e preferências;
  - hook `registrar_conversa.py` salva cada sessão em `conversas/`;
  - o agente regenera `skills.md`, `mcps.md` e `agentes.md` todo dia.
- 2026-10-17 — Todo agente/subagente novo deve ler `memoria.md` e `INDEX.md` e ser registrado em `agentes.md`.
