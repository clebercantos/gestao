# Video AI Agent — execução no Windows (chamado pelo Agendador de Tarefas)
#   agente.ps1 -Modo saude|manutencao|descoberta|memoria|tudo|status
param([ValidateSet('saude', 'manutencao', 'descoberta', 'memoria', 'tudo', 'status')][string]$Modo = 'saude')
$ErrorActionPreference = 'Continue'
$env:PYTHONUTF8 = '1'
# o Agendador não herda o PATH atualizado da sessão: recarrega do registro (inclui ~\.local\bin do Claude Code)
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + (Join-Path $HOME '.local\bin')

$AgentHome = Join-Path $env:LOCALAPPDATA 'VideoAIAgent'
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
if (-not $Py) { Write-Error 'Python não encontrado'; exit 1 }

$pyArgs = @((Join-Path $PSScriptRoot 'agente.py'), $Modo)
if ($Modo -eq 'saude') { $pyArgs += '--reparar' }
& $Py @pyArgs
$code = $LASTEXITCODE

function Show-Toast([string]$titulo, [string]$texto) {
  try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $t = $xml.GetElementsByTagName('text')
    $t.Item(0).AppendChild($xml.CreateTextNode($titulo)) | Out-Null
    $t.Item(1).AppendChild($xml.CreateTextNode($texto)) | Out-Null
    $appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
  } catch { }  # PowerShell 7 não expõe WinRT; o relatório continua disponível
}

$cfg = Get-Content (Join-Path $AgentHome 'config.json') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue | ConvertFrom-Json
$resumo = Get-Content (Join-Path $AgentHome 'estado\ultimo_resumo.json') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue | ConvertFrom-Json
if ($Modo -ne 'status' -and ($null -eq $cfg -or $cfg.notificar) -and $resumo -and $resumo.alertas.Count) {
  $txt = ($resumo.alertas | Select-Object -First 2) -join ' | '
  if ($resumo.alertas.Count -gt 2) { $txt += " (+$($resumo.alertas.Count - 2))" }
  Show-Toast "Video AI Agent — $Modo" $txt
}
exit $code
