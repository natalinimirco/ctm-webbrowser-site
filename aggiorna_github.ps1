# ============================================================
# CTM WEBBROWSER SITE - RESET + PUSH COMPLETO SU GITHUB
# ============================================================
#
# USO:
#   Eseguire PowerShell direttamente nella cartella del sito
#   e lanciare:
#
#       .\push_reset.ps1
#
# ATTENZIONE:
#   Questo script elimina il repository Git LOCALE (.git),
#   ricrea una nuova storia Git e forza il push su GitHub.
#
#   Il contenuto ATTUALE della cartella da cui viene eseguito
#   lo script diventa il NUOVO contenuto della repository.
# ============================================================

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# CONFIGURAZIONE
# ------------------------------------------------------------

$RepoUrl = "https://github.com/natalinimirco/ctm-webbrowser-site.git"
$Branch = "main"
$CommitMessage = "Aggiornamento completo sito CTM WebBrowser"

# IMPORTANTISSIMO:
# prende la cartella corrente da cui viene eseguito PowerShell
$ProjectPath = (Get-Location).Path

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " CTM WEBBROWSER SITE - RESET + PUSH COMPLETO" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Cartella sorgente:" -ForegroundColor Yellow
Write-Host " $ProjectPath"
Write-Host ""

Write-Host "Repository GitHub:" -ForegroundColor Yellow
Write-Host " $RepoUrl"
Write-Host ""

Write-Host "Branch: $Branch"
Write-Host ""

# ------------------------------------------------------------
# CONTROLLO GIT
# ------------------------------------------------------------

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {

    Write-Host "ERRORE: Git non è installato o non è nel PATH." -ForegroundColor Red

    Read-Host "Premi INVIO per chiudere"

    exit 1
}

# ------------------------------------------------------------
# CONTROLLO CARTELLA
# ------------------------------------------------------------

if (-not (Test-Path $ProjectPath)) {

    Write-Host "ERRORE: cartella progetto non trovata." -ForegroundColor Red

    Read-Host "Premi INVIO per chiudere"

    exit 1
}

# ------------------------------------------------------------
# MOSTRA I FILE CHE VERRANNO PUBBLICATI
# ------------------------------------------------------------

Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host " FILE PRESENTI NELLA CARTELLA" -ForegroundColor DarkCyan
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host ""

$Files = Get-ChildItem -Path $ProjectPath -File -Recurse -Force

Write-Host "Numero file trovati: $($Files.Count)" -ForegroundColor Green
Write-Host ""

foreach ($File in $Files) {

    $RelativePath = $File.FullName.Substring(
        $ProjectPath.Length
    ).TrimStart('\')

    Write-Host "  $RelativePath"
}

Write-Host ""

# ------------------------------------------------------------
# CONFERMA
# ------------------------------------------------------------

Write-Host "============================================================" -ForegroundColor Red
Write-Host " ATTENZIONE" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

Write-Host "Questa procedura:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Cancellerà .git locale"
Write-Host "  2. Ricreerà una repository Git completamente nuova"
Write-Host "  3. Aggiungerà TUTTI i file presenti nella cartella"
Write-Host "  4. Creerà un nuovo commit"
Write-Host "  5. FORZERÀ il push sul branch main di GitHub"
Write-Host ""
Write-Host "Il contenuto precedente del branch main verrà sostituito." -ForegroundColor Red
Write-Host ""

$Answer = Read-Host "Continuare? [S/N]"

if ($Answer.Trim() -notin @("S","s","SI","si","Si","sì","Sì")) {

    Write-Host ""
    Write-Host "Operazione annullata." -ForegroundColor Yellow

    Read-Host "Premi INVIO per chiudere"

    exit 0
}

# ------------------------------------------------------------
# 1. ELIMINA .GIT LOCALE
# ------------------------------------------------------------

Write-Host ""
Write-Host "[1/7] Eliminazione repository Git locale..." -ForegroundColor Cyan

$GitFolder = Join-Path $ProjectPath ".git"

if (Test-Path $GitFolder) {

    Remove-Item -Recurse -Force $GitFolder

    Write-Host "      .git eliminato." -ForegroundColor Green
}
else {

    Write-Host "      .git non presente. Nulla da eliminare." -ForegroundColor DarkGray
}

# ------------------------------------------------------------
# 2. CREA NUOVO REPOSITORY
# ------------------------------------------------------------

Write-Host ""
Write-Host "[2/7] Creazione nuovo repository Git..." -ForegroundColor Cyan

git init

if ($LASTEXITCODE -ne 0) {
    throw "git init fallito."
}

git branch -M $Branch

if ($LASTEXITCODE -ne 0) {
    throw "Impostazione branch main fallita."
}

# ------------------------------------------------------------
# 3. AGGIUNGI TUTTI I FILE
# ------------------------------------------------------------

Write-Host ""
Write-Host "[3/7] Aggiunta di TUTTI i file..." -ForegroundColor Cyan

git add .

if ($LASTEXITCODE -ne 0) {
    throw "git add fallito."
}

# ------------------------------------------------------------
# 4. COMMIT
# ------------------------------------------------------------

Write-Host ""
Write-Host "[4/7] Creazione commit..." -ForegroundColor Cyan

git commit -m $CommitMessage

if ($LASTEXITCODE -ne 0) {
    throw "git commit fallito."
}

# ------------------------------------------------------------
# 5. AGGIUNGI REMOTE
# ------------------------------------------------------------

Write-Host ""
Write-Host "[5/7] Configurazione repository GitHub..." -ForegroundColor Cyan

git remote add origin $RepoUrl

if ($LASTEXITCODE -ne 0) {
    throw "Configurazione origin fallita."
}

# ------------------------------------------------------------
# 6. CONTROLLO FINALE
# ------------------------------------------------------------

Write-Host ""
Write-Host "[6/7] CONTROLLO FINALE..." -ForegroundColor Cyan
Write-Host ""

git status

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " FILE CHE VERRANNO PUBBLICATI SU GITHUB" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

git ls-files

Write-Host ""
Write-Host "Totale file Git:" -ForegroundColor Yellow

$GitFiles = git ls-files

Write-Host $GitFiles.Count -ForegroundColor Green

# ------------------------------------------------------------
# 7. PUSH FORCE
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "[7/7] PUSH FORCE SU GITHUB..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Repository: $RepoUrl" -ForegroundColor Yellow
Write-Host "Branch:     $Branch" -ForegroundColor Yellow
Write-Host ""

git push -u origin $Branch --force

if ($LASTEXITCODE -ne 0) {

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host " PUSH FALLITO" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""

    Read-Host "Premi INVIO per chiudere"

    exit 1
}

# ------------------------------------------------------------
# FINE
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " PUSH COMPLETATO CON SUCCESSO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Repository aggiornata:" -ForegroundColor Green
Write-Host $RepoUrl
Write-Host ""

Write-Host "Branch: $Branch"
Write-Host ""

Write-Host "Working tree:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " IL CONTENUTO DELLA CARTELLA È ORA IL NUOVO MAIN" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Premi INVIO per chiudere"