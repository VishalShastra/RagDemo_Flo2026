# Usage: .\scripts\call_api.ps1 "How many PTO days do I get?"
# Needs LANGFLOW_API_KEY (Settings > Langflow API Keys). Reads .env if present.
param([string]$Question = "How many PTO days do I get?")

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        if (-not [Environment]::GetEnvironmentVariable($name.Trim())) {
            [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim())
        }
    }
}

$url = if ($env:LANGFLOW_URL) { $env:LANGFLOW_URL } else { "http://127.0.0.1:7860" }
$flow = if ($env:FLOW_ID) { $env:FLOW_ID } else { "onboarding-rag" }
$body = @{ input_value = $Question; input_type = "chat"; output_type = "chat" } | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "$url/api/v1/run/$($flow)?stream=false" `
    -Headers @{ "x-api-key" = $env:LANGFLOW_API_KEY } -ContentType "application/json" -Body $body -TimeoutSec 600

foreach ($run in $response.outputs) {
    foreach ($out in $run.outputs) {
        $msg = $out.results.message
        Write-Host "===== $($msg.sender_name) =====" -ForegroundColor Cyan
        Write-Host "$($msg.text)`n"
    }
}
