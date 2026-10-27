param(
    [int]$StartPage = 1,
    [int]$EndPage = 0
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class ClipboardMetafile {
    [DllImport("user32.dll")] public static extern bool OpenClipboard(IntPtr hWndNewOwner);
    [DllImport("user32.dll")] public static extern bool CloseClipboard();
    [DllImport("user32.dll")] public static extern IntPtr GetClipboardData(uint uFormat);
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CopyEnhMetaFile(IntPtr hemfSrc, string lpszFile);
    [DllImport("gdi32.dll")] public static extern bool DeleteEnhMetaFile(IntPtr hemf);
}
'@

$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$outDir = 'D:\dl-paper\tmp_bab3\word-page-renders'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false
    $doc = $word.Documents.Open($docx, $false, $true)
    $pages = $doc.ComputeStatistics(2)
    if ($EndPage -le 0 -or $EndPage -gt $pages) { $EndPage = $pages }

    for ($page = $StartPage; $page -le $EndPage; $page++) {
        $startRange = $doc.GoTo(1, 1, $page)
        if ($page -lt $pages) {
            $nextRange = $doc.GoTo(1, 1, $page + 1)
            $endPos = $nextRange.Start - 1
        } else {
            $endPos = $doc.Content.End - 1
        }
        $pageRange = $doc.Range($startRange.Start, $endPos)
        [System.Windows.Forms.Clipboard]::Clear()
        $pageRange.Select()
        $word.Selection.CopyAsPicture()
        Start-Sleep -Milliseconds 800

        $pngPath = Join-Path $outDir ('page-{0:D2}.png' -f $page)
        $img = [System.Windows.Forms.Clipboard]::GetImage()
        if ($null -ne $img) {
            $img.Save($pngPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $img.Dispose()
        } else {
            $emfPath = Join-Path $outDir ('page-{0:D2}.emf' -f $page)
            if (-not [ClipboardMetafile]::OpenClipboard([IntPtr]::Zero)) { throw "Cannot open clipboard for page $page" }
            try {
                $handle = [ClipboardMetafile]::GetClipboardData(14)
                if ($handle -eq [IntPtr]::Zero) {
                    Write-Output "SKIP page ${page}: enhanced metafile missing"
                    continue
                }
                $copy = [ClipboardMetafile]::CopyEnhMetaFile($handle, $emfPath)
                if ($copy -eq [IntPtr]::Zero) {
                    Write-Output "SKIP page ${page}: cannot copy enhanced metafile"
                    continue
                }
                [ClipboardMetafile]::DeleteEnhMetaFile($copy) | Out-Null
            } finally {
                [ClipboardMetafile]::CloseClipboard() | Out-Null
            }
            $metafile = New-Object System.Drawing.Imaging.Metafile($emfPath)
            $bitmap = New-Object System.Drawing.Bitmap($metafile.Width, $metafile.Height)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.Clear([System.Drawing.Color]::White)
            $graphics.DrawImage($metafile, 0, 0, $bitmap.Width, $bitmap.Height)
            $bitmap.Save($pngPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $graphics.Dispose()
            $bitmap.Dispose()
            $metafile.Dispose()
            Remove-Item -LiteralPath $emfPath -Force
        }
        Write-Output $pngPath
    }
} finally {
    if ($null -ne $doc) {
        $save = 0
        $saveRef = [ref]$save
        try { $doc.Close($saveRef) } catch { }
    }
    if ($null -ne $word) { try { $word.Quit() } catch { } }
}
