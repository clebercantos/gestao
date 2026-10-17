# Video AI Pack — pipeline de edição com um comando (Windows)
#
#   .\pipeline.ps1 -Video D:\bruto\entrevista.mp4 -Preset reels
#   .\pipeline.ps1 -Pasta D:\VideoAI                     # processa o que estiver em D:\VideoAI\entrada e sai
#   .\pipeline.ps1 -Pasta D:\VideoAI -Registrar -Preset youtube   # vigia a pasta a cada 10 min (Agendador)
#   .\pipeline.ps1 -Remover                              # tira a vigilância do Agendador
param(
  [string]$Video = '',
  [string]$Pasta = '',
  [ValidateSet('reels', 'youtube', 'tv', 'podcast')][string]$Preset = 'youtube',
  [ValidateSet('', 'natural', 'cinematic', 'quente', 'frio', 'pb', 'vintage')][string]$Look = '',
  [string]$Trilha = '',
  [switch]$SemTranscricao,
  [switch]$Registrar,
  [switch]$Remover
)
$ErrorActionPreference = 'Continue'
$env:PYTHONUTF8 = '1'
# Agendador não herda o PATH novo: soma o do registro ao atual
$env:Path = $env:Path + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
$TaskPath = '\VideoAIAgent\'

if ($Remover) {
  Unregister-ScheduledTask -TaskPath $TaskPath -TaskName 'Pipeline' -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host 'Vigilância da pasta removida do Agendador.'
  return
}

# Python 3.12 primeiro (transcrição); caminho real do exe, nunca o atalho da Microsoft Store
$Py = $null
foreach ($v in '-3.12', '-3.11', '-3.10', '') {
  if (-not (Get-Command py -ErrorAction SilentlyContinue)) { break }
  $pyv = @(); if ($v) { $pyv += $v }   # nunca passar argumento vazio (PS 7 o envia como "")
  $exe = (& py @pyv -c "import sys; print(sys.executable)" 2>$null | Select-Object -Last 1)
  if ($exe -and (Test-Path $exe)) { $Py = $exe; break }
}
if (-not $Py) { Write-Error 'Python 3.10–3.12 não encontrado (winget install Python.Python.3.12)'; exit 1 }

$script = Join-Path $PSScriptRoot 'pipeline.py'
$pyArgs = @($script, '--preset', $Preset)
if ($Look) { $pyArgs += '--look', $Look }
if ($Trilha) { $pyArgs += '--trilha', $Trilha }
if ($SemTranscricao) { $pyArgs += '--sem-transcricao' }

if ($Registrar) {
  if (-not $Pasta) { Write-Error 'Use -Registrar junto com -Pasta'; exit 1 }
  foreach ($d in 'entrada', 'saida', 'processados', 'erros') { New-Item -ItemType Directory -Force (Join-Path $Pasta $d) | Out-Null }
  $ps = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
  $argList = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Pasta `"$Pasta`" -Preset $Preset"
  if ($Look) { $argList += " -Look $Look" }
  if ($SemTranscricao) { $argList += ' -SemTranscricao' }
  $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
  $trigger.Repetition = (New-ScheduledTaskTrigger -Once -At '00:00' -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 1)).Repetition
  $daily = New-ScheduledTaskTrigger -Daily -At '00:00'
  $daily.Repetition = $trigger.Repetition
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 6) -MultipleInstances IgnoreNew
  $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
  Register-ScheduledTask -TaskPath $TaskPath -TaskName 'Pipeline' -Force -Settings $settings -Principal $principal `
    -Action (New-ScheduledTaskAction -Execute $ps -Argument $argList) -Trigger @($trigger, $daily) `
    -Description "Video AI Pack: processa vídeos soltos em $Pasta\entrada (preset $Preset)" | Out-Null
  Write-Host "Vigilância ativa: solte vídeos em $Pasta\entrada; resultados em $Pasta\saida (verifica a cada 10 min)."
  return
}

if ($Pasta) { $pyArgs += '--monitorar', $Pasta }
elseif ($Video) { $pyArgs = @($script, $Video) + $pyArgs[1..($pyArgs.Count - 1)] }
else { Write-Error 'Informe -Video ou -Pasta'; exit 1 }
& $Py @pyArgs
exit $LASTEXITCODE
