$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
$doc = $word.Documents.Open($docx, $false, $false)

function Find-Chapter([string]$prefix) {
    foreach ($p in $doc.Paragraphs) {
        $text = (($p.Range.Text -replace '[\r\a]+$','') -replace "`v",' ').Trim()
        $style = ''
        try { $style = $p.Range.Style.NameLocal } catch { }
        if ($style -like 'Heading 1*' -and $text -like "$prefix*") { return $p }
    }
    throw "$prefix not found"
}

$bab3 = Find-Chapter 'BAB III'
$bab4 = Find-Chapter 'BAB IV'
$range3 = $doc.Range($bab3.Range.Start, $bab4.Range.Start)

foreach ($p in $range3.Paragraphs) {
    $style = ''
    try { $style = $p.Range.Style.NameLocal } catch { }
    if ($style -like 'Heading 1*') { $p.Format.OutlineLevel = 1 }
    elseif ($style -eq 'Heading 2') { $p.Format.OutlineLevel = 2 }
    elseif ($style -eq 'Heading 3') { $p.Format.OutlineLevel = 3 }
    else { $p.Format.OutlineLevel = 10 }
}
foreach ($table in $range3.Tables) {
    foreach ($cell in $table.Range.Cells) {
        foreach ($p in $cell.Range.Paragraphs) { $p.Format.OutlineLevel = 10 }
    }
}

foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
$doc.Repaginate()
$doc.Save()
Write-Output "PAGES=$($doc.ComputeStatistics(2))"
$save = 0
$saveRef = [ref]$save
$doc.Close($saveRef)
$word.Quit()
