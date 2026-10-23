# Vídeo institucional | proxy com IA, aprovação e master 4K

**Objetivo:** retirar a afirmação sobre a 17ª maior construtora do Brasil e a cena correspondente, sem alterar outras partes do institucional.

## Por que o processo roda no Windows

O original tem aproximadamente 528 MB e pertence a um cliente. Não subir vídeos privados para repositório GitHub **público**. O repositório hospeda somente código e testes sintéticos. O Google Drive pode armazenar as prévias se uma conta autorizada permitir gravação, mas não é necessário.

A automação usa FFmpeg + faster-whisper localmente. ArtCraft é ferramenta opcional para imagens/vídeos gerados; ChatCut é editor opcional. Nenhuma das duas integrações é condição para executar esta correção.

## Fluxo em dois comandos

1. Copie o MP4 original para `Downloads` ou `Vídeos` do Windows e execute no PowerShell:

```powershell
cd "$env:USERPROFILE\gestao"
git pull origin main
powershell -ExecutionPolicy Bypass -File .\video-ai-pack\tools\automatizar-video.ps1
```

A rotina descobre o vídeo exato se houver **uma única** correspondência nessas pastas. Se estiver em outro local, passe `-Video "F:\Caminho\institucional.mp4"`.

2. Ela gera, numa pasta `REVISAO_institucional` ao lado do MP4 original:

- `proxy_720p.mp4`, mantendo FPS e referências temporais
- `transcricao.txt` e `palavras.json`, alinhamento por palavras
- `revisao.json`, trechos candidatos, início e fim propostos, **aprovado: false**
- `PREVIA_COMPLETA_720p_*_.mp4` e `AMOSTRA_DA_EMENDA_*_.mp4`, geradas quando houver um único candidato

3. **Aprovação**: assista à amostra. Confira corte em início e fim de oração, contexto, música, texto de ranking e B-roll. Edite os campos `inicio` e `fim` de `revisao.json` se necessário. Se mudar os timecodes, execute novamente o comando de preparo: os arquivos de prévia recebem nomes com timecodes para evitar confundir as versões. Quando aprovar, troque somente `"aprovado": false` para `"aprovado": true`.

4. Exporte o master 4K:

```powershell
powershell -ExecutionPolicy Bypass -File .\video-ai-pack\tools\automatizar-video.ps1 -Finalizar
```

Para NVENC RTX 3090: acrescente `-UsarGPU` ao comando final. O resultado será `FINAL_4K_*.mp4` com `QA_FINAL.json`. Original, proxy e versões aprovadas ficam guardados. Nenhum arquivo preexistente é sobrescrito.

## Google Drive, se já houver rclone configurado

Usando um remote OAuth previamente autorizado (`rclone listremotes`) acrescente ao comando de preparo e de exportação `-DriveRemoto "gdrive:Trevisa/RevisaoCliente"`. A rotina envia somente amostra, transcrição e revisão ao preparar, e o MP4 editado ao finalizar. Não envia o original automaticamente. **Nunca inclua tokens ou vídeos de clientes no GitHub.**

## Qualidade editorial

- A retirada da frase inteira pode deixar um corte na música caso voz+trilha estejam fundidas no MP4. O FFmpeg aplica um micro-crossfade no áudio, mas **não garante** continuidade musical perfeita. Se a emenda ficar perceptível, restaure a trilha limpa a partir das pistas originais, ou faça a mixagem no Premiere/ChatCut.
- A eliminação visual pode precisar de B-roll **real** de outra parte do vídeo. A rotina não inventa cenas nem gera alteração artificial no documental.
- O arquivo final usa H.264 SDR com qualidade alta. Se a origem for 10/12 bits ou HDR, a exportação **bloqueia**, pois converter tudo para 8 bits degradaria a qualidade. Finalize HDR mantendo espaço de cor e profundidade no Premiere/Resolve.
- O QA automático comprova resolução, duração esperada e presença de áudio. Ainda é preciso assistir e ouvir o vídeo.

## Requisitos e segurança

Windows 11, FFmpeg e ffprobe no PATH, Python 3.12 e espaço em disco para pelo menos original+proxy+export. O iniciador instala apenas os pacotes Python ausentes de transcrição, sem modificar o vídeo. Pode baixar pesos públicos do Whisper na primeira execução. CUDA não é exigido: modelo `small` em CPU é padrão estável.

Em caso de execução em sessão cloud do ChatGPT, não confundir `/mnt/data` com o Windows do usuário. O GitHub não executa scripts no desktop sem um agente/runner explicitamente instalado naquele computador.
