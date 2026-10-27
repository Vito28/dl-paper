$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
$doc = $word.Documents.Open($docx, $false, $false)
$prefixes = @(
    'Mengunduh bagian User Reviews', 'Memvalidasi tipe dan rentang data', 'Menghitung review_length',
    'Membagi kelompok parent_asin', 'Mengestimasi hubungan usia-vote', 'Membentuk subset training bertingkat',
    'Mengekstraksi embedding title dan text', 'Menggabungkan embedding dengan fitur terstruktur',
    'Mengurutkan ulasan berdasarkan skor', 'Menyimpan artefak eksperimen'
)
$steps = New-Object System.Collections.Generic.List[object]
foreach ($p in $doc.Paragraphs) {
    $text = ($p.Range.Text -replace '[\r\a]+$','').Trim()
    foreach ($prefix in $prefixes) {
        if ($text.StartsWith($prefix)) { $steps.Add($p); break }
    }
}
if ($steps.Count -ne 10) { throw "Expected 10 steps, found $($steps.Count)" }
foreach ($p in $steps) {
    $p.Range.Style = $doc.Styles.Item('List Paragraph')
    $p.Format.OutlineLevel = 10
}
$stepRange = $doc.Range($steps[0].Range.Start, $steps[9].Range.End)
$stepRange.ListFormat.RemoveNumbers()
$template = $doc.ListTemplates.Add($false, 'Bab3MethodStepsFinal')
$level = $template.ListLevels.Item(1)
$level.NumberFormat = '%1.'
$level.NumberStyle = 0
$level.StartAt = 1
$level.NumberPosition = 0
$level.TextPosition = 36
$level.TabPosition = 36
$stepRange.ListFormat.ApplyListTemplateWithLevel($template, $false, 0, 2, 1)
$stepRange.ParagraphFormat.LeftIndent = 36
$stepRange.ParagraphFormat.FirstLineIndent = -18
$stepRange.ParagraphFormat.Alignment = 3
foreach ($p in $steps) { $p.Format.OutlineLevel = 10 }
foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
$doc.Repaginate()
$doc.Save()
Write-Output "PAGES=$($doc.ComputeStatistics(2))"
$save=0; $saveRef=[ref]$save; $doc.Close($saveRef); $word.Quit()
