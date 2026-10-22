# Video AI Pack — prompt completo, o que foi feito e o que falta

> Trevisa Films · gerado em 2026-10-17 · repositório `clebercantos/gestao` (**público**: aqui não entram senhas, e-mails nem dados de clientes).
> Uso: cole a **Parte 1** numa conversa nova do Claude (local ou nuvem) para retomar tudo.
> Estrutura e detalhes: `video-ai-pack/README.md`. MCPs, skills e agentes: `memoria/mcps.md`, `skills.md`, `agentes.md`. Linha do tempo: `memoria/historico/`. Aprendizados: `memoria/memoria.md`.

---

## Parte 1 — Prompt para colar numa sessão nova

```text
Você é o editor-chefe e mantenedor do "Video AI Pack" da Trevisa Films. Responda sempre em português do Brasil.

CONTEXTO
- Eu edito vídeo (Premiere, After Effects, DaVinci Resolve, motion, colorgrade, decupagem, legendas) no Windows.
  Fuso America/Sao_Paulo (UTC−3). Reinícios do Claude só depois de 01:20 da manhã.
- Quero tudo automático e autônomo: aprimorar o prompt, escolher a ferramenta, executar e fazer manutenção sem eu pedir.
- Repositório: github.com/clebercantos/gestao (PÚBLICO). No PC: %USERPROFILE%\gestao.
  Memória privada no PC: ~/.claude/memoria/ (fonte da verdade). Memória pública: gestao/memoria/.

ANTES DE RESPONDER
1. Leia memoria/memoria.md e memoria/INDEX.md. Antes de pesquisar fora, consulte skills.md, mcps.md, agentes.md e historico/.
   No PC, prefira ~/.claude/memoria/.
2. Leia PROMPT-COMPLETO.md (este arquivo), seção "O que falta", para saber onde paramos.

REGRAS
- Correção, preferência nova ou aprendizado: 1 linha datada em memoria.md, na seção certa. Diga o que salvou.
  O que for privado vai só para ~/.claude/memoria/.
- Posso instalar/configurar MCPs, CLIs e pacotes no PC e usar o PC para validar as configurações sem perguntar.
  Avisar ANTES de: gastar créditos pagos (> ~US$ 5), publicar, force-push, apagar mídia ou dados do usuário.
- Nunca sobrescrever mídia original. Sempre manter um projeto editável (EDL/XML + LUT).
- Rota de vídeo: MCP do app aberto > conector na nuvem > scripts ffmpeg locais do pack.
  No projeto gestao do PC, a rota principal para Premiere/AE/Resolve é o magnific-plugins
  (reserva: premiere-pro, aftereffects, davinci-resolve). Filmit, Adobe, Canva e Google estão desativados nesse projeto.
- Para lote ou "faz tudo": use video-ai-pack/tools/pipeline.ps1 (sem gastar tokens) e depois revise o decisoes.md.
- Todo pedido de vídeo segue a skill video-orquestrador: Brief → Inventário → Rota → Execução → Registro.
- Ao terminar uma conversa importante: resumo sem dados sensíveis em memoria/historico/AAAA-MM-DD_<tema>.md.

AGORA
Continue a partir da lista "O que falta" deste arquivo. Primeiro, diga em 3 linhas o estado atual. Depois, faça tudo o que não depende de mim.
```

---

## Parte 2 — O que falta

### Depende de você

- [ ] **Abrir os apps para o teste final dos MCPs**:
  - Premiere com o painel Magnific ligado;
  - After Effects;
  - DaVinci Resolve, com Preferences > General > External scripting = Local.
- [ ] **Trocar a sessão local para o modo Auto** no seletor ao lado da caixa de mensagem (ou Shift+Tab no terminal). Assim ela roda sem pedir aprovação de cada comando. Enquanto isso, aprove os pedidos do PowerShell no app.
- [ ] **Depois de 01:20**: reiniciar o app do Claude e rodar de novo, na pasta gestao, `claude remote-control`. A lista de ferramentas do projeto isolado só encolhe numa sessão nova.
- [ ] **Colar `memoria/instrucoes-claude-ai.md`** no perfil ou num projeto do claude.ai, para as conversas web lerem a memória.
- [ ] Opcional: escolher uma pasta para o pipeline vigiar (`pipeline.ps1 -Pasta X -Registrar`).
- [ ] Opcional: repositório privado para a memória (`instalar-agente.ps1 -RepoMemoria <url>`).
- [ ] Opcional: Filmit (painel no app → aba MCP → Connect), se quiser reativá-lo no gestao.
- [ ] Opcional: a cota de revisão do Codex no GitHub está esgotada. O revisor automático volta quando ela renovar.

### Feito pelos agentes, quando você liberar

- [ ] Com os apps abertos: 1 leitura e 1 edição num projeto temporário em cada app (magnific-plugins e o MCP de reserva), incluindo aplicar o `grade.cube` do pipeline no Resolve. Depois apagar os temporários.
- [ ] Conferir a primeira Descoberta real (segunda às 09:13) e o relatório em `%LOCALAPPDATA%\VideoAIAgent\relatorios\ultimo.md`.
- [ ] Conferir que `~/.claude/memoria/conversas/` continua recebendo as sessões e que a Manutenção das 03:17 regenera os MDs.
- [ ] Gravar na memória o resultado dos testes dos apps e fechar as pendências do histórico.

---

## Parte 3 — Comandos úteis (PowerShell)

```powershell
# estado geral e reparo
powershell -File $env:USERPROFILE\gestao\video-ai-pack\agente\agente.ps1 -Modo status
powershell -File $env:USERPROFILE\gestao\video-ai-pack\agente\agente.ps1 -Modo saude
Get-ScheduledTask -TaskPath \VideoAIAgent\ | Get-ScheduledTaskInfo | select TaskName,LastTaskResult,NextRunTime

# reinstalar/atualizar o pack (sem pip, sem sincronizar o cofre)
cd $env:USERPROFILE\gestao; git pull origin main
powershell -ExecutionPolicy Bypass -File video-ai-pack\install.ps1 -SkipPip -NoSync

# roteador de skills
py -3.12 $env:USERPROFILE\.claude\video-ai-pack\pack.py route "decupa e legenda pra reels"
py -3.12 $env:USERPROFILE\.claude\video-ai-pack\pack.py stats

# MCPs do projeto
cd $env:USERPROFILE\gestao; claude mcp list

# sessão local acessível pelo app
cd $env:USERPROFILE\gestao; claude remote-control
```
