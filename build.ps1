# Render every section in video order, then stitch into build/final.mp4.
#
#   .\build.ps1          # 480p15 nhap (mac dinh)
#   .\build.ps1 -qh      # 1080p60 ban cuoi
#
# Yeu cau: conda activate graphdm; pip install -r requirements.txt

[CmdletBinding()]
param(
    [switch] $ql,
    [switch] $qm,
    [switch] $qh,
    [switch] $qk
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$selectedQualities = @(
    if ($ql) { '-ql' }
    if ($qm) { '-qm' }
    if ($qh) { '-qh' }
    if ($qk) { '-qk' }
)

if ($selectedQualities -and ($selectedQualities.Count -gt 1)) {
    throw 'Chi duoc chon mot muc chat luong: -ql | -qm | -qh | -qk.'
}

$quality = if ($selectedQualities -and ($selectedQualities.Count -eq 1)) {
    $selectedQualities[0]
}
else {
    '-ql'
}
$resolutions = @{
    '-ql' = '480p15'
    '-qm' = '720p30'
    '-qh' = '1080p60'
    '-qk' = '2160p60'
}
$resolution = $resolutions[$quality]

# Thu tu section trong video. Them section moi thi them vao day.
$sections = @(
    'sections/s1_trucmai/s1_trucmai.py'
    'sections/s2_hoangphan/s2_hoangphan.py'
    'sections/s3_nhutanh/s3_nhutanh.py'
    'sections/s4_trannguyen/s4_trannguyen.py'
    'sections/s5_thienlam/s5_thienlam.py'
)

function Assert-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [string] $Hint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Khong tim thay $Name. $Hint"
    }
}

function Assert-NativeSuccess {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Step
    )

    if ($LASTEXITCODE -ne 0) {
        throw "$Step that bai (exit code $LASTEXITCODE)."
    }
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string] $Text,

        [switch] $Append
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    if ($Append) {
        [System.IO.File]::AppendAllText($Path, $Text, $encoding)
    }
    else {
        [System.IO.File]::WriteAllText($Path, $Text, $encoding)
    }
}

function Normalize-Clip {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Source,

        [Parameter(Mandatory = $true)]
        [string] $Destination
    )

    $audioInfo = (& ffprobe -v error -select_streams a `
        -show_entries stream=codec_type -of csv=p=0 $Source 2>$null | Out-String).Trim()
    Assert-NativeSuccess "ffprobe $Source"

    if ($audioInfo -match 'audio') {
        $null = & ffmpeg -y -loglevel error -i $Source `
            -c:v copy -c:a aac -b:a 128k -ar 48000 -ac 2 `
            -af apad -shortest $Destination
    }
    else {
        $null = & ffmpeg -y -loglevel error -i $Source `
            -f lavfi -i 'anullsrc=channel_layout=stereo:sample_rate=48000' `
            -shortest -c:v copy -c:a aac -b:a 128k $Destination
    }
    Assert-NativeSuccess "Chuan hoa $Source"
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($env:CONDA_DEFAULT_ENV -ne 'graphdm') {
        throw 'Chua kich hoat conda env graphdm. Chay: conda activate graphdm'
    }

    Assert-Command -Name 'python' -Hint 'Chay: conda activate graphdm'
    Assert-Command -Name 'ffmpeg' -Hint 'Hay cai ffmpeg va them vao PATH.'
    Assert-Command -Name 'ffprobe' -Hint 'ffprobe duoc cai kem ffmpeg; hay them vao PATH.'

    # Goi Manim qua Python de khong phu thuoc manim.exe co the con tro toi
    # Python cua mot conda env cu sau khi env duoc sao chep hoac doi ten.
    $pythonCommand = Get-Command python -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $pythonPath = $pythonCommand.Source
    $null = & $pythonPath -c 'import manim'
    if ($LASTEXITCODE -ne 0) {
        throw 'Khong import duoc manim trong env graphdm. Chay: pip install -r requirements.txt'
    }

    $buildDir = Join-Path $PSScriptRoot 'build'
    $normDir = Join-Path $buildDir 'norm'
    $concatPath = Join-Path $buildDir 'concat.txt'
    $finalMp4 = Join-Path $buildDir 'final.mp4'
    $finalSrt = Join-Path $buildDir 'final.srt'
    $finalMkv = Join-Path $buildDir 'final.mkv'

    New-Item -ItemType Directory -Force -Path $buildDir, $normDir | Out-Null
    Write-Utf8NoBom -Path $concatPath -Text ''
    Remove-Item -LiteralPath $finalSrt, $finalMkv -Force -ErrorAction SilentlyContinue

    $clipCount = 0
    foreach ($section in $sections) {
        if (-not (Test-Path -LiteralPath $section -PathType Leaf)) {
            Write-Warning "Thieu file $section - bo qua"
            continue
        }

        Write-Host "==> render $section"
        & $pythonPath -m manim $quality -a $section
        Assert-NativeSuccess "Render $section"

        $stem = [System.IO.Path]::GetFileNameWithoutExtension($section)
        $sceneNames = foreach ($line in Get-Content -LiteralPath $section) {
            if ($line -match '^class ([A-Za-z0-9_]+)\(') {
                $Matches[1]
            }
        }

        foreach ($scene in $sceneNames) {
            $mp4 = Join-Path $PSScriptRoot "media/videos/$stem/$resolution/$scene.mp4"
            if (-not (Test-Path -LiteralPath $mp4 -PathType Leaf)) {
                Write-Warning "Thieu output $mp4"
                continue
            }

            $normalizedFileName = [System.IO.Path]::GetFileName($mp4)
            $normalized = Join-Path $normDir $normalizedFileName
            Normalize-Clip -Source $mp4 -Destination $normalized

            $concatFileName = [System.IO.Path]::GetFileName($normalized)
            $concatEntry = "file '../build/norm/$concatFileName'`n"
            Write-Utf8NoBom -Path $concatPath -Text $concatEntry -Append
            $clipCount++
        }
    }

    if ($clipCount -eq 0) {
        throw 'Khong co clip nao de ghep. Kiem tra output render o tren.'
    }

    Write-Host '==> ghep video'
    & ffmpeg -y -loglevel error -f concat -safe 0 -i $concatPath `
        -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 `
        -movflags '+faststart' $finalMp4
    Assert-NativeSuccess 'Ghep video'

    Write-Host '==> ghep phu de'
    & $pythonPath tools/merge_srt.py $concatPath $finalSrt
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'Bo qua phu de vi tools/merge_srt.py bao loi.'
    }

    if (Test-Path -LiteralPath $finalSrt -PathType Leaf) {
        Write-Host '==> dong goi softsub (MKV)'
        & ffmpeg -y -loglevel error -i $finalMp4 -i $finalSrt `
            -c copy -c:s srt $finalMkv
        if ($LASTEXITCODE -ne 0) {
            Write-Warning 'Khong tao duoc file MKV.'
        }
    }
    else {
        Write-Warning 'Khong tim thay final.srt - bo qua file MKV.'
    }

    $stamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $snapshotDir = Join-Path $PSScriptRoot "media/videos/$stamp"
    New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
    Copy-Item -LiteralPath $finalMp4 -Destination (Join-Path $snapshotDir 'final.mp4')
    Copy-Item -LiteralPath $concatPath -Destination (Join-Path $snapshotDir 'concat.txt')
    if (Test-Path -LiteralPath $finalSrt -PathType Leaf) {
        Copy-Item -LiteralPath $finalSrt -Destination (Join-Path $snapshotDir 'final.srt')
    }
    if (Test-Path -LiteralPath $finalMkv -PathType Leaf) {
        Copy-Item -LiteralPath $finalMkv -Destination (Join-Path $snapshotDir 'final.mkv')
    }

    $durationText = (& ffprobe -v error -show_entries format=duration `
        -of default=nw=1:nk=1 $finalMp4 | Out-String).Trim()
    Assert-NativeSuccess 'Doc thoi luong final.mp4'
    $duration = [double]::Parse(
        $durationText,
        [System.Globalization.CultureInfo]::InvariantCulture
    )
    $minutes = [math]::Floor($duration / 60)
    $seconds = [math]::Floor($duration) % 60
    $durationFormatted = '{0}:{1:00}' -f $minutes, $seconds

    $gitCommit = 'khong phai git repo'
    $gitBranch = '-'
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $commitOutput = (& git rev-parse --short HEAD 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -eq 0) {
            $gitCommit = $commitOutput
            & git diff --quiet 2>$null
            if ($LASTEXITCODE -eq 1) {
                $gitCommit += ' (co thay doi chua commit)'
            }
        }

        $branchOutput = (& git rev-parse --abbrev-ref HEAD 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -eq 0) {
            $gitBranch = $branchOutput
        }
    }

    $infoLines = @(
        "Thoi diem : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        "Chat luong: $quality ($resolution)"
        "Thoi luong: $durationFormatted"
        "Git       : $gitCommit"
        "Nhanh     : $gitBranch"
        ''
        'Scene theo thu tu:'
    )
    $infoLines += Get-Content -LiteralPath $concatPath | ForEach-Object {
        '  ' + ($_ -replace "^file '\.\./", '' -replace "'$", '')
    }
    $infoText = ($infoLines -join "`r`n") + "`r`n"
    Write-Utf8NoBom -Path (Join-Path $snapshotDir 'INFO.txt') -Text $infoText

    Write-Host ''
    Write-Host 'Xong: build/final.mp4, kem build/final.mkv (softsub)'
    Write-Host "Snapshot: $snapshotDir"
    Write-Host "Thoi luong: $durationFormatted"
}
finally {
    Pop-Location
}
