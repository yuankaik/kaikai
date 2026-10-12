# Generic idempotent Windows startup task skeleton.
# NOTE: save this file as UTF-8 WITH BOM (PowerShell 5.1 reads no-BOM as ANSI/GBK -> Chinese/wide chars garble).
# Keep comments/logs in English to avoid any encoding issues.
$ErrorActionPreference = 'Stop'
$logFile = Join-Path $PSScriptRoot 'task.log'
$ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

function Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $logFile -Value "$ts  $msg" -Encoding UTF8
}

# Wait for network to be ready after logon (WiFi can lag)
Start-Sleep -Seconds 25

$maxTry = 3
$done = $false
for ($i = 1; $i -le $maxTry -and -not $done; $i++) {
    try {
        $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

        # 1. GET login/entry page, extract CSRF token
        $lp = Invoke-WebRequest -Uri 'https://example.com/login' -WebSession $session -UserAgent $ua -UseBasicParsing
        $token = [regex]::Match($lp.Content, 'name="_token" value="([^"]+)"').Groups[1].Value
        if (-not $token) { throw 'no token' }

        # 2. POST login
        $body = @{ _token = $token; email = 'you@example.com'; password = 'secret' }
        Invoke-WebRequest -Uri 'https://example.com/login' -Method Post -Body $body -WebSession $session -UserAgent $ua -UseBasicParsing | Out-Null

        # 3. Read a status page, check "already done today?" (idempotency gate)
        $d = Invoke-WebRequest -Uri 'https://example.com/dashboard' -WebSession $session -UserAgent $ua -UseBasicParsing
        $today = Get-Date -Format 'yyyy-MM-dd'
        if ($d.Content -match "$today.*(already-done-marker)") {
            Log "skip: already done today ($today)"
            $done = $true
            break
        }

        # 4. Perform the action (POST / click-equivalent)
        $actionToken = [regex]::Match($d.Content, 'action="https://example\.com/do" method="POST">\s*<input type="hidden" name="_token" value="([^"]+)"', 'Singleline').Groups[1].Value
        Invoke-WebRequest -Uri 'https://example.com/do' -Method Post -Body @{ _token = $actionToken } -WebSession $session -UserAgent $ua -UseBasicParsing | Out-Null

        # 5. Verify
        $d2 = Invoke-WebRequest -Uri 'https://example.com/dashboard' -WebSession $session -UserAgent $ua -UseBasicParsing
        if ($d2.Content -match 'success-marker') { Log 'done OK' }
        else { Log 'submitted (maybe already done)' }
        $done = $true
    }
    catch {
        Log "attempt $i failed: $($_.Exception.Message)"
        if ($i -lt $maxTry) { Start-Sleep -Seconds 20 }
    }
}
