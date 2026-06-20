# Windows setup script for Runekeeper
# Run as Administrator in PowerShell
Write-Host "Runekeeper setup starting..." -ForegroundColor Cyan

function Install-WithWinget($id, $name) {
    Write-Host "Checking $name..."
    if (-not (Get-Command $id -ErrorAction SilentlyContinue)) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "Installing $name via winget..."
            winget install --id $id -e --source winget -h
        } else {
            Write-Host "winget is not available. Please install $name manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "$name appears installed."
    }
}

# Install Git, Python, ffmpeg if missing (uses winget)
Install-WithWinget "Git.Git" "Git"
Install-WithWinget "Python.Python.3" "Python 3"
Install-WithWinget "Gyan.FFmpeg" "ffmpeg"

# Pause briefly to let PATH update
Start-Sleep -Seconds 2

# repo settings
$repoUrl = "https://github.com/oyintanda-zongwana/Runekeeper.git"
$branch = "enhancement/discord-features"
$targetDir = Join-Path $env:USERPROFILE "Runekeeper"

# clone or update repo
if (-not (Test-Path $targetDir)) {
    Write-Host "Cloning repository to $targetDir ..."
    git clone $repoUrl $targetDir
} else {
    Write-Host "Repository already exists at $targetDir. Fetching updates..."
    Push-Location $targetDir
    git fetch origin
    Pop-Location
}

Push-Location $targetDir

# checkout branch
Write-Host "Checking out branch $branch ..."
git fetch origin
git checkout $branch 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout -b $branch origin/$branch 2>$null
}
git pull origin $branch

# Create venv
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
} else {
    Write-Host "Virtual environment exists."
}

# Activate venv in this script session
$activate = Join-Path $PWD ".venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
} else {
    Write-Host "Activation script not found at $activate" -ForegroundColor Yellow
}

# Upgrade pip and install requirements
Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found; continuing."
}

# Ensure yt-dlp installed
Write-Host "Installing yt-dlp..."
pip install yt-dlp

# Ask user for env values
Write-Host ""
Write-Host "Now I will create a .env file. You will be prompted for values."
$discordToken = Read-Host -Prompt "Enter DISCORD_TOKEN (your bot token) - REQUIRED"
if ([string]::IsNullOrWhiteSpace($discordToken)) {
    Write-Host "No token provided. Aborting." -ForegroundColor Red
    Exit 1
}
$brawEndpoint = Read-Host -Prompt "Enter BRAWLHALLA_API_ENDPOINT (optional; leave blank if none) - must include {handle}"
$brawKey = Read-Host -Prompt "Enter BRAWLHALLA_API_KEY (optional; leave blank if none)"
$dbUrl = "sqlite:///runekeeper.db"

# write .env
$envContent = @()
$envContent += "DISCORD_TOKEN=$discordToken"
$envContent += "DATABASE_URL=$dbUrl"
if (-not [string]::IsNullOrWhiteSpace($brawEndpoint)) {
    $envContent += "BRAWLHALLA_API_ENDPOINT=$brawEndpoint"
}
if (-not [string]::IsNullOrWhiteSpace($brawKey)) {
    $envContent += "BRAWLHALLA_API_KEY=$brawKey"
}
$envContent += "BRAWLHALLA_POLL_INTERVAL=60"

$envPath = Join-Path $PWD ".env"
Write-Host "Writing .env to $envPath"
$envContent | Out-File -FilePath $envPath -Encoding ASCII -Force

# create a convenient start script (batch) in repo root
$batPath = Join-Path $PWD "runekeeper_start.bat"
$batText = @"
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python -m bot.core
"@
Set-Content -Path $batPath -Value $batText -Encoding ASCII

# Start the bot in a new window (detached)
Write-Host "Starting bot in a new window..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c start `"$batPath`"" 

Write-Host ""
Write-Host "Setup complete. The bot should be starting (a new window launched)." -ForegroundColor Green
Write-Host "If the bot window closes or you see errors, open the created runekeeper_start.bat or run 'python -m bot.core' in the repository venv to view logs."
Write-Host "Repo path: $targetDir"
Write-Host "To update later: cd $targetDir ; git fetch origin ; git checkout $branch ; git pull origin $branch"
Pop-Location
