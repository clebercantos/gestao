# ArtCraft, ChatCut e corte pontual no Windows

Atualizado em 22/10/2026. Fontes oficiais:
- ArtCraft: https://github.com/storytold/artcraft e https://getartcraft.com
- ChatCut Agent Plugin: https://github.com/ChatCut-Inc/agent-plugin
- ChatCut/Claude Code: https://github.com/ChatCut-Inc/agent-plugin/blob/main/docs/claude-code-install.md

## O que é cada ferramenta

**ArtCraft** é um programa desktop (Rust/Tauri) para criação de imagens e vídeos.
Não é um MCP do ChatGPT e não substitui uma timeline com áudio mixado.
A versão estável Windows conferida na pesquisa foi v0.41.0, com instalador
`ArtCraft_0.41.0_x64-setup.exe`. O script consulta a release mais recente
antes de baixar. Ele só inicia automaticamente arquivos com Authenticode válido;
se a assinatura não for validada, imprime a URL oficial para inspeção manual.

**ChatCut** oferece plugin oficial de agente para Claude Code e Codex,
com edição de timeline, transcrição, legendas, importação e exportação.
MCP hospedado: `https://api.chatcut.io/api/external-mcp/mcp`.
Exige conta ChatCut e autorização OAuth pelo usuário. O arquivo de plugin
no GitHub **não significa plugin instalado no Windows ou conectado nesta conversa**.
Os projetos ficam sujeitos às regras/limites do serviço ChatCut.

**Corte pontual FFmpeg** é fallback local para cortar um intervalo definido,
mantendo o restante do filme e criando arquivo separado.
Não é um editor semântico: faster-whisper sugere o intervalo, mas a montagem
precisa revisar início, fim, gráficos na tela e coerência narrativa.

## Instalar no notebook/desktop Windows

Abra **PowerShell** no próprio computador, com Git, Claude Code/Codex e
Python/FFmpeg conforme as ferramentas que escolher.

```powershell
cd "$env:USERPROFILE\gestao"
git pull origin main
powershell -ExecutionPolicy Bypass -File ".\video-ai-pack\tools\instalar-artcraft-chatcut.ps1" -ArtCraft -ChatCutClaude -ChatCutCodex
```

Os flags podem ser usados individualmente. Ao instalar ChatCut:
1. Autorize OAuth no navegador que for aberto pelo Claude Code/Codex.
2. Confira `claude mcp get plugin:chatcut:chatcut` e/ou
   `codex mcp get chatcut`.
3. Abra uma conversa **nova** no respectivo cliente: ferramentas carregadas
   na sessão atual não aparecem automaticamente. O Claude Code usa
   `claude plugin install chatcut@chatcut-inc` a partir do marketplace
   `https://github.com/ChatCut-Inc/agent-plugin.git`.
4. Opcional: para adicionar o ChatCut ao Codex, o script registra o MCP
   HTTPS e pede autenticação: `codex mcp login chatcut`.

Não colocar tokens, OAuth, vídeos privados ou arquivos de clientes neste
repositório público.

## Corte com IA local (sem modificar o vídeo original)

Use o vídeo local no Windows, sem precisar enviá-lo ao GitHub.

```powershell
cd "$env:USERPROFILE\gestao"
py -3.12 .\video-ai-pack\tools\corte-pontual.py "D:\VIDEOS\institucional.mp4" --buscar "17 maior construtora do Brasil"
```

O comando produz `institucional_CORTE.plano.json` com transcrição, candidatos
e timecodes. Confira os segundos sugeridos reproduzindo 2 s antes e 2 s
depois no Premiere/ChatCut. Ajuste para retirar a oração inteira sem deixar
uma frase incompleta. Se houver texto na tela associado à fala, descarte
também esse take ou substitua por um B-roll real já existente.

Após confirmar o intervalo:

```powershell
py -3.12 .\video-ai-pack\tools\corte-pontual.py "D:\VIDEOS\institucional.mp4" --inicio 42.20 --fim 47.30 --render --nvenc
```

**42.20 e 47.30 são valores ilustrativos, não timecodes do vídeo do cliente.**
O script usa corte visual seco e micro-crossfade de 0,16 s na faixa de áudio
mixada. Cria `*_CORTE.mp4` e JSON de auditoria; nunca sobrescreve a entrada
nem uma saída preexistente. O original e o restante da narrativa continuam
intactos, mas uma trilha já mixada pode apresentar mudança de andamento
musical, mesmo com crossfade. Para continuidade musical perfeita, obtenha
a trilha/stems ou edite as pistas independentes no Premiere, Audition ou ChatCut
e cubra a emenda visual com B-roll existente. Não tente gerar elementos visuais
para simular uma cena documental sem sinalizar isso ao responsável.

### Verificação de qualidade

- Confirmar que a frase sobre o ranking desapareceu também de eventuais
  títulos, lettering, legendas e imagens.
- Assistir 5 s antes e 5 s depois do ponto, conferindo gramática e continuidade.
- Ouvir com fones para detectar salto de batida, cortes de palavra ou ruídos.
- Conferir vídeo e áudio até o fim e comparar resolução, fps, cor e loudness
  da exportação com o original via `ffprobe`. A exportação H.264 em yuv420p
  é destinada a SDR; validar à parte caso a fonte seja HDR/10-bit.
- Se houver projeto Premiere/Resolve original, priorizar edição das pistas,
  com trilha contínua, em vez de editar um único MP4 achatado.

## Limitações de ambiente

O GitHub versiona scripts, documentação e projeto; não executa a instalação
no computador pessoal. O ChatGPT desta conversa não ganha acesso ao Windows
ou às ferramentas ChatCut só porque as referências foram adicionadas ao repo.
Se o executor remoto apresentar `caas.internal.errors.ClientError` até para
`ls`, é falha de infraestrutura da sessão, não evidência de MP4 corrompido.
Nessa situação use o ambiente Windows local e os comandos oficiais acima.
