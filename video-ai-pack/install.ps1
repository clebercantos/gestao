# Video AI Pack — instalador Windows (PowerShell 5.1+ / 7)
#
#   .\install.ps1                          # skills + hook automático + CLAUDE.md + deps Python
#   .\install.ps1 -Mcp all                 # + MCPs (premiere, ae, resolve, opusclip, invideo, higgsfield)
#   .\install.ps1 -Mcp premiere,ae         # só os escolhidos
#   .\install.ps1 -Apps premiere,resolve -Apis elevenlabs -Budget 7000   # o que você usa (roteador)
#   .\install.ps1 -NoSync                  # não baixa o cofre das 100 skills agora
#   .\install.ps1 -Community               # + skills completas Remotion, auto-editor, motion-design (LobzyJay)
#   .\install.ps1 -Uninstall
param(
  [string[]]$Mcp = @(),
  [switch]$Community,
  [switch]$Uninstall,
  [switch]$SkipPip,
  [switch]$NoSync,
  [string[]]$Apps = @(),
  [string[]]$Apis = @(),
  [int]$Budget = 0
)
# Continue: no Windows PowerShell 5.1, stderr de comandos nativos (claude, npx, pip) com 'Stop' vira erro fatal
$ErrorActionPreference = 'Continue'
# aceita listas vindas de -File / Agendador ("premiere,ae") além de arrays
$Mcp = @($Mcp -split ',' | Where-Object { $_ })
$Apps = @($Apps -split ',' | Where-Object { $_ })
$Apis = @($Apis -split ',' | Where-Object { $_ })
$Pack = $PSScriptRoot
$ClaudeHome = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $HOME '.claude' }
$PackHome = Join-Path $ClaudeHome 'video-ai-pack'
$OldHookDir = Join-Path $ClaudeHome 'hooks\video-ai-pack'
$Skills = 'video-orquestrador','video-decupagem','video-colorgrade','video-legendas','video-motion','video-entrega','video-audio'
function Say($m) { Write-Host "▸ $m" -ForegroundColor Magenta }
function Warn($m) { Write-Host "! $m" -ForegroundColor Yellow }
function Has($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }

# Python 3.12 primeiro: faster-whisper/ctranslate2 não têm pacotes para 3.13+ (3.15 quebra a transcrição).
# Usa o caminho real do executável; 'python' puro pode ser o atalho da Microsoft Store.
$Py = $null
foreach ($v in '-3.12', '-3.11', '-3.10', '') {
  if (-not (Get-Command py -ErrorAction SilentlyContinue)) { break }
  $pyv = @(); if ($v) { $pyv += $v }   # nunca passar argumento vazio (PS 7 o envia como "")
  $exe = (& py @pyv -c "import sys; print(sys.executable)" 2>$null | Select-Object -Last 1)
  if ($exe -and (Test-Path $exe)) { $Py = $exe; break }
}
if (-not $Py -and (Get-Command python -ErrorAction SilentlyContinue)) { $Py = 'python' }
if (-not $Py) { throw 'Python 3.10–3.12 é obrigatório (winget install Python.Python.3.12)' }
$SettingsPath = Join-Path $ClaudeHome 'settings.json'

# UTF-8 sem BOM: o Set-Content -Encoding UTF8 do PowerShell 5.1 grava BOM, que quebra parsers JSON
function Write-Utf8([string]$path, [string]$text) { [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($false))) }

function Set-Hook([bool]$add) {
  # hooks do pack: roteador de vídeo, memória (correções) e registro de conversas
  $ours = [ordered]@{ UserPromptSubmit = @('video_intent.py', 'memoria_hook.py'); SessionEnd = @('registrar_conversa.py') }
  $s = if ((Test-Path $SettingsPath) -and (Get-Content $SettingsPath -Raw -Encoding UTF8).Trim()) {
    Get-Content $SettingsPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { [pscustomobject]@{} }
  if (-not $s.PSObject.Properties['hooks']) { $s | Add-Member hooks ([pscustomobject]@{}) }
  foreach ($event in $ours.Keys) {
    $scripts = $ours[$event]
    $groups = @()
    if ($s.hooks.PSObject.Properties[$event]) {
      $groups = @($s.hooks.$event | Where-Object { $cmds = @($_.hooks.command) -join ' '; -not ($scripts | Where-Object { $cmds -like "*$_*" }) })
    }
    if ($add) {
      foreach ($sc in $scripts) {
        $timeout = if ($event -eq 'SessionEnd') { 30 } else { 10 }
        $groups += [pscustomobject]@{ hooks = @([pscustomobject]@{ type = 'command'; command = "`"$Py`" `"$(Join-Path $PackHome $sc)`""; timeout = $timeout }) }
      }
    }
    $s.hooks.PSObject.Properties.Remove($event)
    if ($groups.Count) { $s.hooks | Add-Member $event $groups }
  }
  if (-not @($s.hooks.PSObject.Properties).Count) { $s.PSObject.Properties.Remove('hooks') }
  New-Item -ItemType Directory -Force (Split-Path $SettingsPath) | Out-Null
  Write-Utf8 $SettingsPath ($s | ConvertTo-Json -Depth 20)
}

function Set-ClaudeMd([bool]$add) {
  $f = Join-Path $ClaudeHome 'CLAUDE.md'
  $txt = if (Test-Path $f) { Get-Content $f -Raw -Encoding UTF8 } else { '' }
  $txt = [regex]::Replace($txt, '(?s)\r?\n?<!-- video-ai-pack:start -->.*?<!-- video-ai-pack:end -->\r?\n?', "`n")
  if ($add) {
    $snip = (Get-Content (Join-Path $Pack 'config\CLAUDE.md.snippet') -Raw -Encoding UTF8).Trim()
    $txt = $txt.TrimEnd() + "`n`n<!-- video-ai-pack:start -->`n$snip`n<!-- video-ai-pack:end -->`n"
  }
  Write-Utf8 $f $txt.TrimStart()
}

function Add-Mcp($name, [string[]]$mcpArgs) {
  & claude mcp remove --scope user $name 2>$null | Out-Null
  & claude mcp add --scope user @mcpArgs
  if ($LASTEXITCODE -eq 0) { Say "MCP $name registrado" } else { Warn "falha ao registrar MCP $name" }
}

if ($Uninstall) {
  foreach ($s in $Skills) { Remove-Item -Recurse -Force (Join-Path $ClaudeHome "skills\$s") -ErrorAction SilentlyContinue }
  Remove-Item -Recurse -Force $PackHome, $OldHookDir -ErrorAction SilentlyContinue
  Set-Hook $false; Set-ClaudeMd $false
  Say "A pasta $(Join-Path $ClaudeHome 'memoria') foi mantida (é sua memória). Apague manualmente se quiser."
  if (Has 'claude') { foreach ($m in 'premiere-pro','aftereffects','davinci-resolve','opusclip','invideo','higgsfield') { & claude mcp remove --scope user $m 2>$null | Out-Null } }
  Say 'Video AI Pack removido.'; return
}

Say 'Checando dependências'
if (-not (Has 'ffmpeg')) { Warn 'ffmpeg não encontrado — winget install Gyan.FFmpeg' }
if (-not (Has 'node'))   { Warn 'Node.js 20+ não encontrado — winget install OpenJS.NodeJS.LTS' }
if (-not (Has 'claude')) { Warn "CLI 'claude' não encontrada — MCPs não serão registrados" }
if (-not $SkipPip) {
  Say 'Instalando faster-whisper e auto-editor'
  & $Py -m pip install --user --quiet --upgrade faster-whisper auto-editor
  if ($LASTEXITCODE -ne 0) { Warn 'pip falhou — instale manualmente: pip install faster-whisper auto-editor' }
}

Say "Instalando skills em $ClaudeHome\skills"
New-Item -ItemType Directory -Force (Join-Path $ClaudeHome 'skills') | Out-Null
foreach ($s in $Skills) {
  $dst = Join-Path $ClaudeHome "skills\$s"
  Remove-Item -Recurse -Force $dst -ErrorAction SilentlyContinue
  Copy-Item -Recurse (Join-Path $Pack "skills\$s") $dst
}

Say "Instalando roteador e catálogo das 100 skills em $PackHome"
Remove-Item -Recurse -Force $OldHookDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $PackHome | Out-Null
Copy-Item (Join-Path $Pack 'tools\pack.py'), (Join-Path $Pack 'catalogo\skills.json') $PackHome -Force
Copy-Item (Join-Path $Pack 'hooks\*.py') $PackHome -Force
New-Item -ItemType Directory -Force (Join-Path $PackHome 'tools') | Out-Null
Copy-Item (Join-Path $Pack 'tools\pipeline.*') (Join-Path $PackHome 'tools') -Force
$PackPy = Join-Path $PackHome 'pack.py'
$cfg = @()
if ($Apps.Count) { $cfg += '--apps', ($Apps -join ',') }
if ($Apis.Count) { $cfg += '--apis', ($Apis -join ',') }
if ($Budget -gt 0) { $cfg += '--budget', "$Budget" }
if ($cfg.Count) { & $Py $PackPy config @cfg | Out-Null }
if (-not $NoSync) {
  Say 'Baixando o cofre (SKILL.md das 100 skills, ~1 MB, custo fixo zero)'
  & $Py $PackPy sync
}
Say 'Registrando hooks: roteamento de vídeo, memória (correções) e registro de conversas'
Set-Hook $true

Say 'Adicionando regras ao CLAUDE.md global'
Set-ClaudeMd $true

if ($Mcp.Count -and (Has 'claude')) {
  if ($Mcp -contains 'all') { $Mcp = 'premiere','ae','resolve','opusclip','invideo','higgsfield' }
  foreach ($m in $Mcp) {
    switch ($m) {
      'premiere'   { Add-Mcp 'premiere-pro' @('premiere-pro','--','npx','-y','premiere-pro-mcp@latest'); & npx -y premiere-pro-mcp@latest --install-cep }
      'ae'         { Add-Mcp 'aftereffects' @('aftereffects','--','npx','-y','@kumoproductions/mcp-aftereffects@latest')
                     Warn "AE: ative Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network'" }
      'resolve'    { # samuelgursky (o pacote PyPI davinci-resolve-mcp é outro projeto e quebra com mcp 2.x)
                     'n' | & npx -y davinci-resolve-mcp setup
                     $RD = Join-Path $env:LOCALAPPDATA 'davinci-resolve-mcp'
                     Add-Mcp 'davinci-resolve' @('davinci-resolve','--',"$RD\venv\Scripts\python.exe","$RD\src\server.py")
                     Warn "Resolve: Preferences > General > 'External scripting using' = Local (versão gratuita: Workspace > Scripts > resolve_bridge)" }
      'opusclip'   { Add-Mcp 'opusclip'   @('--transport','http','opusclip','https://mcp.opus.pro/mcp') }
      'invideo'    { Add-Mcp 'invideo'    @('--transport','http','invideo','https://mcp.invideo.io/mcp') }
      'higgsfield' { Add-Mcp 'higgsfield' @('--transport','http','higgsfield','https://mcp.higgsfield.ai/mcp') }
      default      { Warn "MCP desconhecido: $m" }
    }
  }
  Say 'MCPs remotos pedem login OAuth: abra o Claude Code e rode /mcp'
}

if ($Community) {
  Say 'Instalando skills da comunidade'
  if (Has 'npx') { & npx -y skills add https://github.com/remotion-dev/skills; & npx -y skills add https://github.com/WyattBlue/auto-editor }
  if (Has 'git') {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("mdc" + [guid]::NewGuid())
    & git clone --depth 1 https://github.com/LobzyJay/motion-design-with-claude.git $tmp
    if ($LASTEXITCODE -eq 0) { Copy-Item -Recurse -Force (Join-Path $tmp 'skills\*') (Join-Path $ClaudeHome 'skills') }
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
  }
}

# Memória permanente: ~/.claude/memoria (memoria.md nunca é sobrescrita; skills/mcps/agentes.md são regenerados)
Say "Gerando memória e MDs de consulta em $(Join-Path $ClaudeHome 'memoria')"
& $Py (Join-Path $Pack 'agente\memoria_md.py') --dest (Join-Path $ClaudeHome 'memoria') --repo (Split-Path $Pack -Parent) --claude-home $ClaudeHome --scan | Out-Null

& $Py $PackPy stats
Say 'Video AI Pack instalado. Reinicie o Claude Code e teste:'
Write-Host '   "decupa o video.mp4, colorgrade cinematic e legenda karaokê pra Reels"'
