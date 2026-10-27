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

foreach ($table in $range3.Tables) {
    foreach ($cell in $table.Range.Cells) {
        foreach ($p in $cell.Range.Paragraphs) {
            $p.Range.Style = $doc.Styles.Item('Normal')
            $p.Format.OutlineLevel = 10
            $p.Range.Font.Name = 'Times New Roman'
            $p.Range.Font.Size = 10.5
            $p.Format.FirstLineIndent = 0
            $p.Format.LeftIndent = 0
            $p.Format.SpaceBefore = 0
            $p.Format.SpaceAfter = 0
            $p.Format.LineSpacingRule = 0
            $p.Format.LineSpacing = 12
        }
    }
}
foreach ($shape in $range3.InlineShapes) {
    if ($shape.Width -gt 350) {
        $p = $shape.Range.Paragraphs.Item(1)
        $p.Range.Style = $doc.Styles.Item('Normal')
        $p.Format.OutlineLevel = 10
        $p.Format.Alignment = 1
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
