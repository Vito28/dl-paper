$ErrorActionPreference = 'Stop'
$docx = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
$doc = $word.Documents.Open($docx, $false, $false)
$toc = $doc.TablesOfContents.Item(1)
$toc.UpperHeadingLevel = 1
$toc.LowerHeadingLevel = 3
$toc.Update()
for ($i = 2; $i -le $doc.TablesOfContents.Count; $i++) { $doc.TablesOfContents.Item($i).Update() }
$doc.Repaginate()
$doc.Save()
Write-Output "PAGES=$($doc.ComputeStatistics(2))"
$save = 0
$saveRef = [ref]$save
$doc.Close($saveRef)
$word.Quit()
