# Conversa 2026-10-17 — Instalação local no Windows e correções

Sessão Claude Code local · branch `claude/video-editing-plugins-research-973wsr`. Continuação de [video-ai-pack](2026-10-17_video-ai-pack.md).

## Feito
- Pré-requisitos conferidos (git, py, node, ffmpeg, claude); pack, hooks, memória e 3 tarefas agendadas já estavam instalados.
- Teste de ponta a ponta com clipe sintético (vídeo + fala TTS): decupagem, colorgrade e legendas passam.
- DaVinci Resolve MCP trocado pelo projeto samuelgursky (`npx davinci-resolve-mcp setup`); conectou no Resolve Studio.
- GitHub CLI instalado e autenticado; commits enviados.

## Bugs corrigidos
- faster-whisper quebrava com `av`>=17: áudio agora decodificado via ffmpeg.
- Whisper em "auto" escolhia CUDA sem cublas: padrão CPU (`VIDEO_WHISPER_DEVICE`).
- ffmpeg 9 removeu `-filter_complex_script`: grafo inline.
- Texto repetido em trechos da decupagem: agora usa as palavras de cada trecho.
- JSON/SRT gravados em cp1252 no Windows: tudo UTF-8 explícito.
- Roteador: "exporta pro Reels" não puxa mais skill de conteúdo social.
- Instaladores `.ps1` com BOM; instalador do Resolve usa o pacote correto.

## Validado depois
- Premiere (CEP) e After Effects 26.5: teste da primeira sessão passou (export de 3 s e render de 1 s conferidos no ffprobe).
- Resolve Studio 21.1: API de scripting validada (projeto, importação, timeline); falta testar como ferramenta MCP (precisa reiniciar o app; teste agendado).
- Agente de saúde 28/28; `.ps1` sem erros de sintaxe.
- Histórico do Git limpo de mídia de teste (`_teste/` agora no .gitignore).

## Pendências
- [ ] Usuário: `/mcp` do conector Adobe (rejeitou as credenciais na reconexão; opcional).
- [ ] Usuário: fechar o `TEMP_TESTE_CLAUDE.prproj` no Premiere sem salvar.
- [ ] Reiniciar o app do Claude e testar o MCP do Resolve (agendado 2026-10-18 01:20).
- [ ] Usuário: revisar e mesclar o PR #1.