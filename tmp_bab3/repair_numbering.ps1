$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$flowSvg = 'D:\dl-paper\tmp_bab3\metodologi-flow.svg'

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$createdWord = $true
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

function Set-ParagraphText($p, [string]$text) {
    $r = $p.Range.Duplicate
    $r.End = $r.End - 1
    $r.Text = $text
}

$bab3 = Find-Chapter 'BAB III'
$bab4 = Find-Chapter 'BAB IV'
$range3 = $doc.Range($bab3.Range.Start, $bab4.Range.Start)

# Remove accidental continuation numbering from every Bab III paragraph and table cell.
foreach ($p in $range3.Paragraphs) { try { $p.Range.ListFormat.RemoveNumbers() } catch { } }
foreach ($table in $range3.Tables) {
    foreach ($cell in $table.Range.Cells) { try { $cell.Range.ListFormat.RemoveNumbers() } catch { } }
}

# Use explicit chapter/subsection labels because the inherited template's multilevel list is unstable.
foreach ($p in $range3.Paragraphs) {
    $text = (($p.Range.Text -replace '[\r\a]+$','') -replace "`v",' ').Trim()
    switch ($text) {
        'BAB III METODOLOGI PENELITIAN' { Set-ParagraphText $p "BAB III`vMETODOLOGI PENELITIAN" }
        'Metodologi Penelitian' { Set-ParagraphText $p '3.1 Metodologi Penelitian' }
        'Analisis Masalah' { Set-ParagraphText $p '3.1.1 Analisis Masalah' }
        'Rancangan Penelitian' { Set-ParagraphText $p '3.1.2 Rancangan Penelitian' }
        'Sampling / Metode Pemilihan Sampel' { Set-ParagraphText $p '3.1.3 Sampling / Metode Pemilihan Sampel' }
        'Metode Pengumpulan Data' { Set-ParagraphText $p '3.1.4 Metode Pengumpulan Data' }
        'Alat-alat Penelitian' { Set-ParagraphText $p '3.1.5 Alat-alat Penelitian' }
        'Teknik Analisis dan Rencana Strategi' { Set-ParagraphText $p '3.1.6 Teknik Analisis dan Rencana Strategi' }
    }
}

# Re-find the chapter range after text-length changes.
$bab3 = Find-Chapter 'BAB III'
$bab4 = Find-Chapter 'BAB IV'
$range3 = $doc.Range($bab3.Range.Start, $bab4.Range.Start)

$stepStarts = @(
    'Mengunduh bagian User Reviews',
    'Memvalidasi tipe dan rentang data',
    'Menghitung review_length',
    'Membagi kelompok parent_asin',
    'Mengestimasi hubungan usia-vote',
    'Membentuk subset training bertingkat',
    'Mengekstraksi embedding title dan text',
    'Menggabungkan embedding dengan fitur terstruktur',
    'Mengurutkan ulasan berdasarkan skor',
    'Menyimpan artefak eksperimen'
)
$stepParas = New-Object System.Collections.Generic.List[object]
foreach ($p in $range3.Paragraphs) {
    $text = ($p.Range.Text -replace '[\r\a]+$','').Trim()
    foreach ($prefix in $stepStarts) {
        if ($text.StartsWith($prefix)) { $stepParas.Add($p); break }
    }
}
if ($stepParas.Count -ne 10) { throw "Expected 10 methodology steps, found $($stepParas.Count)" }

$stepRange = $doc.Range($stepParas[0].Range.Start, $stepParas[9].Range.End)
$listTemplate = $doc.ListTemplates.Add($true, 'Bab3MethodSteps')
$level = $listTemplate.ListLevels.Item(1)
$level.NumberFormat = '%1.'
$level.NumberStyle = 0
$level.StartAt = 1
$level.NumberPosition = 0
$level.TextPosition = 36
$level.TabPosition = 36
$level.ResetOnHigher = 0
$stepRange.ListFormat.ApplyListTemplateWithLevel($listTemplate, $false, 0, 2, 1)
$stepRange.ParagraphFormat.LeftIndent = 36
$stepRange.ParagraphFormat.FirstLineIndent = -18
$stepRange.ParagraphFormat.Alignment = 3

# Restore real bullets to the final reproducibility checklist only.
$bulletStarts = @(
    'Menetapkan seed untuk split produk',
    'Menyimpan konfigurasi checkpoint',
    'Menyimpan model usia',
    'Menggunakan early stopping',
    'Menjalankan pemeriksaan otomatis'
)
$bulletParas = New-Object System.Collections.Generic.List[object]
foreach ($p in $range3.Paragraphs) {
    $text = ($p.Range.Text -replace '[\r\a]+$','').Trim()
    foreach ($prefix in $bulletStarts) {
        if ($text.StartsWith($prefix)) { $bulletParas.Add($p); break }
    }
}
if ($bulletParas.Count -eq 5) {
    $bulletRange = $doc.Range($bulletParas[0].Range.Start, $bulletParas[4].Range.End)
    $bulletRange.ListFormat.ApplyBulletDefault()
    $bulletRange.ParagraphFormat.LeftIndent = 36
    $bulletRange.ParagraphFormat.FirstLineIndent = -18
    $bulletRange.ParagraphFormat.Alignment = 3
}

# Replace the flowchart with the corrected SVG while retaining its anchor paragraph.
foreach ($shape in @($range3.InlineShapes)) {
    if ($shape.Width -gt 350) {
        $anchor = $shape.Range.Start
        $shape.Delete()
        $r = $doc.Range($anchor, $anchor)
        $newShape = $doc.InlineShapes.AddPicture($flowSvg, $false, $true, $r)
        $newShape.LockAspectRatio = -1
        $newShape.Width = 410
        $newShape.AlternativeText = 'Diagram alir metodologi penelitian'
        $newShape.Range.Paragraphs.Item(1).Format.Alignment = 1
        break
    }
}

foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
$doc.Repaginate()
$doc.Save()

Write-Output "PAGES=$($doc.ComputeStatistics(2)) TABLES=$($doc.Tables.Count) INLINE=$($doc.InlineShapes.Count) TOCS=$($doc.TablesOfContents.Count)"
$save = 0
$saveRef = [ref]$save
$doc.Close($saveRef)
$word.ScreenUpdating = $true
if ($createdWord) { $word.Quit() }
