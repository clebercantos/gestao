# Video AI Agent — instalação completa no Windows (Windows 10/11, PowerShell 5.1+)
#
# Instala os pré-requisitos (Git, Python, Node, FFmpeg, Claude Code), o Video AI Pack, os MCPs e o
# agente de manutenção, e agenda as rotinas no Agendador de Tarefas. Não precisa de administrador.
#
#   .\instalar-agente.ps1 -Apps premiere,aftereffects,resolve -Mcp premiere,ae,resolve
#   .\instalar-agente.ps1 -Apps premiere -Mcp premiere,opusclip -Apis elevenlabs -SemPesquisaIA
#   .\instalar-agente.ps1 -RepoMemoria https://github.com/<voce>/memoria-claude.git   # repo PRIVADO p/ sincronizar a memória
#   .\instalar-agente.ps1 -Desinstalar
#
# Rotinas agendadas:
#   Saúde + autorreparo   ao fazer logon (+5 min) e a cada 6 h
#   Manutenção            todo dia às 03:17 (ou na próxima vez que o PC ligar)
#   Descoberta            segunda-feira às 09:13 (monitora skills/MCPs/novidades e adota skills aprovadas)
param(
  [string[]]$Apps = @(),
  [string[]]$Mcp = @(),
  [string[]]$Apis = @(),
  [int]$Budget = 7000,
  [string]$RepoUrl = 'https://github.com/clebercantos/gestao.git',
  [string]$Branch = 'main',
  [string]$RepoMemoria = '',
  [switch]$SemPesquisaIA,
  [switch]$SemAtualizarSistema,
  [switch]$Desinstalar
)
$ErrorActionPreference = 'Continue'
$Apps = @($Apps -split ',' | Where-Object { $_ })
$Mcp = @($Mcp -split ',' | Where-Object { $_ })
$Apis = @($Apis -split ',' | Where-Object { $_ })
$AgentHome = Join-Path $env:LOCALAPPDATA 'VideoAIAgent'
$TaskPath = '\VideoAIAgent\'
function Say($m) { Write-Host "▸ $m" -ForegroundColor Magenta }
function Warn($m) { Write-Host "! $m" -ForegroundColor Yellow }
function Has($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + (Join-Path $HOME '.local\bin')
}

# ------------------------------------------------------------------ desinstalar
if ($Desinstalar) {
  Say 'Removendo tarefas agendadas'
  Get-ScheduledTask -TaskPath $TaskPath -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
  $repoPack = Join-Path $AgentHome 'repo\video-ai-pack\install.ps1'
  $local = Join-Path (Split-Path $PSScriptRoot -Parent) 'install.ps1'
  $inst = if (Test-Path $local) { $local } elseif (Test-Path $repoPack) { $repoPack } else { $null }
  if ($inst) { Say 'Removendo o Video AI Pack'; & powershell -NoProfile -ExecutionPolicy Bypass -File $inst -Uninstall }
  Remove-Item -Recurse -Force (Join-Path $HOME '.claude\agents\video-ai-mantenedor.md'), (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Video AI Agent.lnk') -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $AgentHome -ErrorAction SilentlyContinue
  Say 'Video AI Agent removido. (Git, Python, Node, FFmpeg e Claude Code foram mantidos.)'
  return
}

# ------------------------------------------------------------------ 1. pré-requisitos
Say 'Verificando pré-requisitos'
if (-not (Has 'winget')) {
  Warn 'winget não encontrado. Instale o "App Installer" pela Microsoft Store e rode de novo.'
  return
}
$deps = @(
  @{ cmd = 'git'; id = 'Git.Git' },
  @{ cmd = 'py'; id = 'Python.Python.3.12' },
  @{ cmd = 'node'; id = 'OpenJS.NodeJS.LTS' },
  @{ cmd = 'ffmpeg'; id = 'Gyan.FFmpeg' }
)
foreach ($d in $deps) {
  if (Has $d.cmd) { Say "$($d.cmd) ok"; continue }
  Say "Instalando $($d.id)"
  winget install --id $d.id --exact --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
  Refresh-Path
}
if (-not (Has 'claude')) {
  Say 'Instalando Claude Code (instalador oficial)'
  Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
  Refresh-Path
}
Refresh-Path
foreach ($c in 'git', 'py', 'node', 'ffmpeg', 'claude') {
  if (-not (Has $c)) { Warn "$c ainda não está no PATH — feche e abra o PowerShell e rode este script de novo."; return }
}

# ------------------------------------------------------------------ 2. repositório do pack
New-Item -ItemType Directory -Force $AgentHome | Out-Null
$here = Split-Path $PSScriptRoot -Parent               # ...\video-ai-pack
$repoRoot = Split-Path $here -Parent
if (Test-Path (Join-Path $repoRoot '.git')) {
  Say "Usando o repositório local: $repoRoot"
} else {
  $repoRoot = Join-Path $AgentHome 'repo'
  if (Test-Path (Join-Path $repoRoot '.git')) {
    git -C $repoRoot fetch origin $Branch; git -C $repoRoot checkout $Branch; git -C $repoRoot merge --ff-only "origin/$Branch"
  } else {
    Say "Clonando $RepoUrl ($Branch)"
    git clone --branch $Branch $RepoUrl $repoRoot
  }
  if (-not (Test-Path (Join-Path $repoRoot 'video-ai-pack\install.ps1'))) { Warn 'Clone falhou ou branch sem o pack. Use -Branch com a branch certa.'; return }
}
$packDir = Join-Path $repoRoot 'video-ai-pack'
$agentDir = Join-Path $packDir 'agente'

# ------------------------------------------------------------------ 3. configuração do agente
$cfgPath = Join-Path $AgentHome 'config.json'
$cfg = if (Test-Path $cfgPath) { Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { [pscustomobject]@{} }
$set = @{
  repo_dir = $repoRoot; branch = (git -C $repoRoot rev-parse --abbrev-ref HEAD); apps = @($Apps); apis = @($Apis); mcps = @($Mcp)
  budget = $Budget; pesquisa_ia = (-not $SemPesquisaIA); atualizar_sistema = (-not $SemAtualizarSistema)
}
if ($RepoMemoria) { $set.memoria_repo = $RepoMemoria }
foreach ($k in $set.Keys) { $cfg | Add-Member -Force -NotePropertyName $k -NotePropertyValue $set[$k] }
[IO.File]::WriteAllText($cfgPath, ($cfg | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
Say "Configuração salva em $cfgPath"

# ------------------------------------------------------------------ 3b. memória privada sincronizada (opcional)
$memDir = Join-Path $HOME '.claude\memoria'
if ($RepoMemoria -and -not (Test-Path (Join-Path $memDir '.git'))) {
  Say "Conectando a memória ao repositório privado $RepoMemoria"
  $tmp = "$memDir.clone"
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
  git clone $RepoMemoria $tmp
  if (Test-Path (Join-Path $tmp '.git')) {
    if (Test-Path $memDir) { Copy-Item (Join-Path $memDir '*') $tmp -Recurse -Force -Exclude '.git' }  # mantém o que já existia no PC
    Remove-Item -Recurse -Force $memDir -ErrorAction SilentlyContinue
    Move-Item $tmp $memDir
  } else { Warn 'Não foi possível clonar o repositório da memória (ele precisa existir e ser seu). Seguindo sem sincronizar.' }
}

# ------------------------------------------------------------------ 4. Video AI Pack
Say 'Instalando o Video AI Pack (skills, hook, roteador, cofre, MCPs)'
$instArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $packDir 'install.ps1'), '-Budget', "$Budget")
if ($Apps.Count) { $instArgs += '-Apps', ($Apps -join ',') }
if ($Apis.Count) { $instArgs += '-Apis', ($Apis -join ',') }
if ($Mcp.Count) { $instArgs += '-Mcp', ($Mcp -join ',') }
& powershell @instArgs

# subagente do Claude Code para manutenção conversada ("use o agente video-ai-mantenedor")
$agentsDir = Join-Path $HOME '.claude\agents'
New-Item -ItemType Directory -Force $agentsDir | Out-Null
Copy-Item (Join-Path $agentDir 'video-ai-mantenedor.md') $agentsDir -Force

# ------------------------------------------------------------------ 5. tarefas agendadas
Say 'Agendando rotinas no Agendador de Tarefas'
$ps = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$runner = Join-Path $agentDir 'agente.ps1'
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
function Add-Task($nome, $modo, $triggers, $descr) {
  $action = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`" -Modo $modo"
  Register-ScheduledTask -TaskPath $TaskPath -TaskName $nome -Action $action -Trigger $triggers -Settings $settings `
    -Principal $principal -Description $descr -Force | Out-Null
  Say "  tarefa '$nome' agendada"
}
$logon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$logon.Delay = 'PT5M'
# diário à 00:05 repetindo a cada 6 h por 1 dia = a cada 6 h para sempre (padrão aceito em todas as versões do Agendador)
$cada6h = New-ScheduledTaskTrigger -Daily -At '00:05'
$cada6h.Repetition = (New-ScheduledTaskTrigger -Once -At '00:05' -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 1)).Repetition
Add-Task 'Saude' 'saude' @($logon, $cada6h) 'Video AI Agent: confere e repara o Video AI Pack, MCPs e dependências'
Add-Task 'Manutencao' 'manutencao' @(New-ScheduledTaskTrigger -Daily -At '03:17') 'Video AI Agent: atualiza pack, cofre de skills, pacotes e ferramentas'
Add-Task 'Descoberta' 'descoberta' @(New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At '09:13') 'Video AI Agent: monitora novidades de IA para vídeo e adota skills aprovadas'

# atalho na área de trabalho para o último relatório
try {
  $lnk = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Video AI Agent.lnk'))
  $lnk.TargetPath = Join-Path $AgentHome 'relatorios'
  $lnk.Description = 'Relatórios do Video AI Agent (ultimo.md = mais recente)'
  $lnk.Save()
} catch { }

# ------------------------------------------------------------------ 6. primeira execução
Say 'Primeira execução: saúde (com reparo) e linha de base da descoberta'
& $ps -NoProfile -ExecutionPolicy Bypass -File $runner -Modo saude
& $ps -NoProfile -ExecutionPolicy Bypass -File $runner -Modo descoberta

Write-Host ''
Say 'Video AI Agent instalado e ativo.'
Write-Host "  Relatórios:  $AgentHome\relatorios\ultimo.md  (atalho 'Video AI Agent' na área de trabalho)"
Write-Host "  Tarefas:     Agendador de Tarefas > Biblioteca > VideoAIAgent"
Write-Host "  Manual:      powershell -File `"$runner`" -Modo tudo"
Write-Host "  Memória:     $memDir  (memoria.md, INDEX.md, skills.md, mcps.md, agentes.md, conversas\)"
Write-Host ''
Warn 'Falta só você: rode  claude  uma vez para fazer login, depois /mcp para autorizar os conectores remotos.'
