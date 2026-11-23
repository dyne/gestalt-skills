[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[0-9A-Za-z][0-9A-Za-z.+_-]*$')][string]$Version,
    [ValidateSet('Classic', 'Silent')][string]$InstallerProfile = 'Classic',
    [string]$Compiler = $env:ISCC,
    [string]$Python = $env:PYTHON,
    [string]$Stage
)

$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $Python = (Get-Command python, python3 -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1).Source
    if (-not $Python) { throw 'Install Python 3.10+ or set PYTHON to its executable path.' }
}
if (-not $Compiler) {
    $command = Get-Command ISCC.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        $Compiler = $command.Source
    } elseif (${env:ProgramFiles(x86)}) {
        $Compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    }
}
if (-not $Compiler -or -not (Get-Command $Compiler -CommandType Application -ErrorAction SilentlyContinue)) {
    throw 'Install the project-supported Inno Setup compiler or set ISCC to the full path to ISCC.exe.'
}
$include = New-TemporaryFile
try {
    & $Python -B (Join-Path $PSScriptRoot 'product_metadata.py') inno --product (Join-Path $PSScriptRoot 'product.json') --version $Version --output $include.FullName
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    $defines = @("/DMyAppVersion=$Version", "/DProductInclude=$($include.FullName)")
    if ($Stage) {
        $folder = Get-Item -LiteralPath $Stage
        if (-not $folder.PSIsContainer) { throw "Expected stage directory at $Stage" }
        $defines += "/DStageDir=$($folder.FullName)"
    }
    if ($InstallerProfile -eq 'Silent') { $defines += '/DStreamlined' }
    & $Compiler @defines (Join-Path $PSScriptRoot 'installer.iss')
    exit $LASTEXITCODE
} finally {
    Remove-Item -LiteralPath $include.FullName
}
