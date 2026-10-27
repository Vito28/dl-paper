$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
$doc = $word.Documents.Open($docx, $false, $false)

$targets = @(
    'BAB IV HASIL DAN PEMBAHASAN',
    '4.1 Hasil',
    '4.2 Pembahasan',
    'BAB V PENUTUP',
    'DAFTAR PUSTAKA',
    'DAFTAR RIWAYAT HIDUP'
)

foreach ($p in $doc.Paragraphs) {
    $text = (($p.Range.Text -replace '[\r\a]+$','') -replace "`v",' ').Trim()
    if ($targets -contains $text) {
        try { $p.Range.ListFormat.RemoveNumbers() } catch { }
        if ($text -eq 'BAB IV HASIL DAN PEMBAHASAN') {
            $p.Format.PageBreakBefore = -1
        }
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
