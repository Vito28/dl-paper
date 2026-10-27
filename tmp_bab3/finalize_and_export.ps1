$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$pdf = 'D:\dl-paper\tmp_bab3\bab3-review.pdf'

try {
    $word = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
    $createdWord = $false
} catch {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $createdWord = $true
}

$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
$doc = $word.Documents.Open($docx, $false, $false)

$i = 0
foreach ($toc in $doc.TablesOfContents) {
    $i++
    $toc.Update()
    Write-Output "UPDATED_TOC=$i"
}

$doc.Repaginate()
$doc.Save()

if (Test-Path $pdf) { Remove-Item -LiteralPath $pdf -Force }
$doc.ExportAsFixedFormat($pdf, 17)

Write-Output "PAGES=$($doc.ComputeStatistics(2)) TABLES=$($doc.Tables.Count) INLINE=$($doc.InlineShapes.Count) TOCS=$($doc.TablesOfContents.Count)"
$save = 0
$saveRef = [ref]$save
$doc.Close($saveRef)
$word.ScreenUpdating = $true
if ($createdWord) { $word.Quit() }

Get-Item $docx, $pdf | Select-Object FullName, Length, LastWriteTime
