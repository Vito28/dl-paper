$ErrorActionPreference = 'Stop'

$reference = 'D:\dl-paper\documents\_clone_test.docx'
$output = 'D:\dl-paper\documents\Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset - Bab III.docx'
$flowSvg = 'D:\dl-paper\tmp_bab3\metodologi-flow.svg'

if (Test-Path $output) { Remove-Item -LiteralPath $output -Force }

try {
    $word = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
    $createdWord = $false
} catch {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $createdWord = $true
}

$word.DisplayAlerts = 0
$doc = $word.Documents.Add($reference)

function Find-ChapterParagraph([string]$prefix) {
    foreach ($p in $doc.Paragraphs) {
        $text = (($p.Range.Text -replace '[\r\a]+$','') -replace "`v", ' ').Trim()
        $styleName = ''
        try { $styleName = $p.Range.Style.NameLocal } catch { }
        if ($styleName -like 'Heading 1*' -and $text -like "$prefix*") { return $p }
    }
    throw "Heading $prefix tidak ditemukan."
}

$bab3 = Find-ChapterParagraph 'BAB III'
$bab4 = Find-ChapterParagraph 'BAB IV'

# Simplify the template title while preserving its paragraph/style.
$titleRange = $bab3.Range.Duplicate
$titleRange.End = $titleRange.End - 1
$titleRange.Text = "BAB III`vMETODOLOGI PENELITIAN"

$start = $bab3.Range.End
$end = $bab4.Range.Start
$doc.Range($start, $end).Delete()
$script:pos = $start

function Set-Font($range, [double]$size = 12, [int]$bold = 0, [int]$italic = 0) {
    $range.Font.Name = 'Times New Roman'
    $range.Font.NameAscii = 'Times New Roman'
    $range.Font.NameOther = 'Times New Roman'
    $range.Font.Size = $size
    $range.Font.Bold = $bold
    $range.Font.Italic = $italic
}

function Add-Paragraph(
    [string]$text,
    [string]$style = 'Normal',
    [int]$alignment = 3,
    [double]$firstIndent = 35.45,
    [double]$spaceBefore = 0,
    [double]$spaceAfter = 0,
    [int]$keepWithNext = 0,
    [string]$boldPrefix = ''
) {
    $s = $script:pos
    $r = $doc.Range($s, $s)
    $r.InsertAfter($text + "`r")
    $p = $doc.Range($s, $s + $text.Length + 1).Paragraphs.Item(1)
    try { $p.Range.Style = $doc.Styles.Item($style) } catch { }
    Set-Font $p.Range 12 0 0
    $p.Format.Alignment = $alignment
    $p.Format.FirstLineIndent = $firstIndent
    $p.Format.LeftIndent = 0
    $p.Format.RightIndent = 0
    $p.Format.SpaceBefore = $spaceBefore
    $p.Format.SpaceAfter = $spaceAfter
    $p.Format.LineSpacingRule = 1
    $p.Format.LineSpacing = 18
    $p.Format.WidowControl = -1
    $p.Format.KeepWithNext = $keepWithNext
    if ($boldPrefix -and $text.StartsWith($boldPrefix)) {
        $br = $doc.Range($s, $s + $boldPrefix.Length)
        $br.Bold = -1
    }
    $script:pos = $p.Range.End
    return $p
}

function Add-Heading([string]$text, [string]$style) {
    $p = Add-Paragraph $text $style 0 0 6 0 -1
    Set-Font $p.Range 14 -1 0
    $p.Format.LineSpacingRule = 1
    $p.Format.LineSpacing = 18
    return $p
}

function Add-Equation([string]$text) {
    $p = Add-Paragraph $text 'Normal' 1 0 6 6 0
    Set-Font $p.Range 12 -1 0
    return $p
}

function Add-Bullets([string[]]$items) {
    $listStart = $script:pos
    foreach ($item in $items) {
        $p = Add-Paragraph $item 'List Paragraph' 3 0 0 0 0
        $p.Format.LeftIndent = 71.45
        $p.Format.FirstLineIndent = -18
    }
    $listRange = $doc.Range($listStart, $script:pos)
    $listRange.ListFormat.ApplyBulletDefault()
    Set-Font $listRange 12 0 0
    $listRange.ParagraphFormat.Alignment = 3
    $listRange.ParagraphFormat.LineSpacingRule = 1
    $listRange.ParagraphFormat.LineSpacing = 18
}

function Add-Numbered([string[]]$items) {
    $listStart = $script:pos
    foreach ($item in $items) {
        $p = Add-Paragraph $item 'List Paragraph' 3 0 0 0 0
        $p.Format.LeftIndent = 71.45
        $p.Format.FirstLineIndent = -18
    }
    $listRange = $doc.Range($listStart, $script:pos)
    $listRange.ListFormat.ApplyNumberDefault()
    Set-Font $listRange 12 0 0
    $listRange.ParagraphFormat.Alignment = 3
    $listRange.ParagraphFormat.LineSpacingRule = 1
    $listRange.ParagraphFormat.LineSpacing = 18
}

function Add-Caption([string]$text, [string]$style) {
    $p = Add-Paragraph $text $style 1 0 6 6 -1
    Set-Font $p.Range 11 -1 0
    return $p
}

function Add-Table([object[]]$rows, [double[]]$widths) {
    $rowCount = $rows.Count
    $colCount = $widths.Count
    $r = $doc.Range($script:pos, $script:pos)
    $table = $doc.Tables.Add($r, $rowCount, $colCount)
    $table.AllowAutoFit = $false
    $table.Borders.Enable = 1
    $table.TopPadding = 4
    $table.BottomPadding = 4
    $table.LeftPadding = 4
    $table.RightPadding = 4
    for ($c = 1; $c -le $colCount; $c++) {
        $table.Columns.Item($c).Width = $widths[$c - 1]
    }
    for ($i = 1; $i -le $rowCount; $i++) {
        for ($j = 1; $j -le $colCount; $j++) {
            $cell = $table.Cell($i, $j)
            $cell.Range.Text = [string]$rows[$i - 1][$j - 1]
            $cell.VerticalAlignment = 1
            Set-Font $cell.Range 10.5 0 0
            $cell.Range.ParagraphFormat.Alignment = if ($j -eq 1 -and $colCount -gt 2) { 1 } else { 0 }
            $cell.Range.ParagraphFormat.FirstLineIndent = 0
            $cell.Range.ParagraphFormat.LeftIndent = 0
            $cell.Range.ParagraphFormat.SpaceBefore = 0
            $cell.Range.ParagraphFormat.SpaceAfter = 0
            $cell.Range.ParagraphFormat.LineSpacingRule = 0
            $cell.Range.ParagraphFormat.LineSpacing = 12
        }
    }
    $table.Rows.Item(1).HeadingFormat = -1
    foreach ($cell in $table.Rows.Item(1).Cells) {
        $cell.Shading.BackgroundPatternColor = 14277081
        $cell.Range.Font.Bold = -1
        $cell.Range.ParagraphFormat.Alignment = 1
    }
    $after = $doc.Range($table.Range.End, $table.Range.End)
    $after.InsertAfter("`r")
    $script:pos = $after.End
    return $table
}

function Add-FlowFigure([string]$path) {
    $r = $doc.Range($script:pos, $script:pos)
    $shape = $doc.InlineShapes.AddPicture($path, $false, $true, $r)
    $shape.LockAspectRatio = -1
    $shape.Width = 410
    $p = $shape.Range.Paragraphs.Item(1)
    $p.Format.Alignment = 1
    $p.Format.SpaceBefore = 6
    $p.Format.SpaceAfter = 0
    $p.Format.KeepWithNext = -1
    $after = $doc.Range($shape.Range.End, $shape.Range.End)
    $after.InsertAfter("`r")
    $script:pos = $after.End
    return $shape
}

Add-Heading 'Metodologi Penelitian' 'Heading 2' | Out-Null
Add-Paragraph 'Penelitian ini menggunakan pendekatan kuantitatif eksperimental untuk membangun dan mengevaluasi sistem pemeringkatan kebermanfaatan ulasan produk. Objek penelitian adalah ulasan pada Amazon Reviews 2023, sedangkan unit pemeringkatan adalah sekumpulan ulasan yang memiliki parent_asin yang sama. Setiap ulasan diberi satu skor oleh model, kemudian skor tersebut digunakan untuk mengurutkan ulasan hanya di dalam produk yang sama. Rancangan penelitian menekankan tiga hal, yaitu generalisasi pada produk yang tidak terlihat selama pelatihan, pengukuran dan pengendalian bias usia ulasan, serta pengujian kontribusi embedding BLaIR dan fitur terstruktur melalui baseline dan ablasi.' | Out-Null
Add-Paragraph 'Tahapan penelitian meliputi analisis masalah, pengumpulan data sekunder, validasi dan preprocessing, pembagian data product-disjoint, pembentukan target, analisis usia-vote, ekstraksi embedding BLaIR-RoBERTa-Base, feature fusion, pelatihan MLP dengan pairwise ranking loss, dan evaluasi. Review_age digunakan untuk analisis paparan dan pembentukan target, tetapi tidak menjadi fitur model utama ketika inferensi. Dengan batasan tersebut, skor yang dihasilkan diarahkan untuk merepresentasikan kualitas relatif ulasan yang lebih intrinsik, bukan prediksi jumlah vote kumulatif pada horizon tertentu.' | Out-Null

Add-Heading 'Analisis Masalah' 'Heading 3' | Out-Null
Add-Paragraph 'Produk populer dapat memiliki ratusan hingga ribuan ulasan, sedangkan pengguna umumnya hanya membaca sebagian kecil ulasan yang ditempatkan pada posisi teratas. Helpful_vote dapat digunakan sebagai sinyal perilaku untuk mengetahui ulasan yang dianggap berguna, tetapi jumlahnya bersifat kumulatif dan dipengaruhi kesempatan paparan. Ulasan lama berpeluang mengumpulkan vote lebih banyak daripada ulasan baru walaupun kualitas informasinya setara. Selain itu, produk yang populer memiliki pola vote berbeda dari produk yang kurang populer. Dengan demikian, penggunaan helpful_vote secara langsung tanpa pengendalian dapat membuat model mempelajari lamanya paparan atau popularitas produk alih-alih kualitas isi ulasan.' | Out-Null
Add-Paragraph 'Permasalahan kedua adalah kebocoran produk. Apabila ulasan dari produk yang sama tersebar ke training dan testing, model dapat memperoleh petunjuk yang terlalu spesifik terhadap produk dan menghasilkan estimasi performa yang optimistis. Penelitian ini karena itu membagi data berdasarkan parent_asin. Seluruh ulasan suatu produk hanya boleh berada pada satu split, sedangkan asin diperiksa untuk mengurangi risiko varian yang berhubungan tersebar pada split berbeda.' | Out-Null
Add-Paragraph 'Permasalahan ketiga adalah pemisahan manfaat representasi dan arsitektur. Kinerja model yang baik belum dapat langsung diatribusikan kepada BLaIR apabila tidak dibandingkan dengan TF-IDF, model linear, MLP, serta konfigurasi tanpa fitur terstruktur. Rancangan baseline dan ablasi diperlukan agar kontribusi embedding, model nonlinear, dan fitur tambahan dapat ditafsirkan secara terpisah.' | Out-Null
Add-Caption 'Tabel 3.1 Formulasi input, proses, dan keluaran penelitian' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Komponen','Uraian'),
    @('Input','Judul dan isi ulasan, rating, status verified_purchase, timestamp, helpful_vote, parent_asin, dan asin dari Amazon Reviews 2023.'),
    @('Proses','Validasi data; preprocessing; product-disjoint split; analisis usia-vote; pembentukan target dan pasangan; embedding BLaIR; feature fusion; training MLP; serta evaluasi ranking.'),
    @('Keluaran','Skor ranking per ulasan, urutan ulasan per parent_asin, hasil baseline dan ablasi, kurva hubungan usia-vote, serta metrik generalisasi pada produk baru.'),
    @('Kendala utama','Vote nol yang dominan, distribusi long-tail, perbedaan ukuran produk, bias paparan, keterbatasan komputasi, dan tidak tersedianya riwayat waktu setiap vote.'),
    @('Kriteria keberhasilan','Peningkatan metrik ranking yang konsisten terhadap baseline pada test product-disjoint, disertai interval kepercayaan dan analisis performa menurut kelompok usia.')
) @(120,300) | Out-Null

Add-Heading 'Rancangan Penelitian' 'Heading 3' | Out-Null
Add-Paragraph 'Rancangan penelitian disusun sebagai alur berurutan dengan titik keputusan yang hanya menggunakan training dan validation. Data test disimpan hingga seluruh aturan preprocessing, target, pasangan, hyperparameter, ambang relevansi, dan model terbaik telah ditetapkan. Diagram alir pada Gambar 3.1 menunjukkan hubungan antara sumber data, pengendalian usia, pembentukan representasi, pelatihan, dan evaluasi.' | Out-Null
Add-FlowFigure $flowSvg | Out-Null
Add-Caption 'Gambar 3.1 Diagram alir penelitian' 'Judul Gambar' | Out-Null
Add-Paragraph 'Pelaksanaan penelitian dilakukan melalui langkah-langkah berikut.' | Out-Null
Add-Numbered @(
    'Mengunduh bagian User Reviews dari Amazon Reviews 2023 dan mencatat kategori, URL, tanggal pengambilan, checksum, ukuran berkas, serta skema kolom.',
    'Memvalidasi tipe dan rentang data, menangani nilai kosong, membersihkan teks secara konservatif, menghapus duplikasi, dan memeriksa timestamp serta identitas produk.',
    'Menghitung review_length, word_count, title_length, dan review_age_days; selanjutnya mendeskripsikan distribusi helpful_vote, usia, serta ukuran kelompok produk.',
    'Membagi kelompok parent_asin menjadi training, validation, dan testing dengan proporsi awal 80:10:10 serta melakukan pemeriksaan kebocoran parent_asin, asin, dan duplikasi teks lintas split.',
    'Mengestimasi hubungan usia-vote pada training, menghasilkan prediksi out-of-fold untuk koreksi target training, lalu menerapkan fungsi usia yang dibekukan pada validation dan testing.',
    'Membentuk subset training bertingkat, pasangan ranking dalam produk yang sama, dan varian age-matched atau berbobot tanpa memindahkan produk antarsplit.',
    'Mengekstraksi embedding title dan text menggunakan checkpoint hyp1231/blair-roberta-base, kemudian menyimpan embedding beserta metadata konfigurasi.',
    'Menggabungkan embedding dengan fitur terstruktur yang tersedia saat inferensi dan melatih model baseline serta MLP RankNet.',
    'Mengurutkan ulasan berdasarkan skor di setiap parent_asin, menghitung metrik per produk, melakukan macro-average, dan menganalisis performa menurut usia serta ukuran produk.',
    'Menyimpan artefak eksperimen, seed, konfigurasi, model, log, pembagian data, dan hasil evaluasi sehingga eksperimen dapat direproduksi.'
)

Add-Heading 'Sampling / Metode Pemilihan Sampel' 'Heading 3' | Out-Null
Add-Paragraph 'Data penelitian merupakan data sekunder, sehingga tidak dilakukan sampling responden lapangan. Populasi operasional adalah seluruh ulasan valid pada kategori Amazon Reviews 2023 yang dipilih. Sampel eksperimen dibentuk setelah pembersihan dan pembagian produk. Pemilihan kategori dilakukan berdasarkan ketersediaan atribut wajib, kecukupan produk dengan lebih dari satu ulasan, dan keterjangkauan komputasi; keputusan kategori serta jumlah baris sebelum dan sesudah filter dicatat secara eksplisit.' | Out-Null
Add-Paragraph 'Unit sampling adalah parent_asin, bukan baris ulasan. Daftar parent_asin diacak menggunakan seed tetap, kemudian dialokasikan sekitar 80% untuk training, 10% untuk validation, dan 10% untuk testing. Karena ukuran setiap produk berbeda, proporsi jumlah ulasan tidak harus tepat 80:10:10. Produk pada validation dan testing tidak boleh muncul pada training. Jika asin yang sama atau pasangan varian yang teridentifikasi muncul pada lebih dari satu split, seluruh kelompok terkait dipindahkan ke satu split atau dikeluarkan sesuai aturan yang ditetapkan sebelum eksperimen.' | Out-Null
Add-Paragraph 'Model pairwise memerlukan sekurang-kurangnya dua ulasan dari produk yang sama dengan target berbeda. Produk yang tidak menghasilkan pasangan preferensi tetap dicatat dalam statistik data, tetapi tidak digunakan untuk pembentukan pasangan training. Validation dan testing mempertahankan distribusi alami; SMOTE tidak digunakan karena interpolasi pada embedding dapat menghasilkan ulasan sintetis dan pasangan yang tidak memiliki makna kelompok.' | Out-Null
Add-Caption 'Tabel 3.2 Rancangan split dan sampel training bertingkat' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Bagian','Unit alokasi','Proporsi/ukuran','Fungsi'),
    @('Training','parent_asin','sekitar 80% produk','Pelatihan model, fit preprocessing, model usia, dan pembentukan target out-of-fold.'),
    @('Validation','parent_asin','sekitar 10% produk','Pemilihan hyperparameter, aturan pasangan, batas usia, threshold MAP, dan early stopping.'),
    @('Testing','parent_asin','sekitar 10% produk','Evaluasi akhir satu kali pada produk yang tidak terlihat.'),
    @('E1-E5','review dalam training pool','100k; 250k; 500k; 750k; 1M','Mengukur pengaruh skala dengan subset nested dan validation/testing yang tetap.')
) @(55,105,100,160) | Out-Null
Add-Paragraph 'Subset E1 sampai E5 dibuat secara nested jika jumlah data memenuhi: E1 merupakan bagian E2, E2 merupakan bagian E3, dan seterusnya. Sampling dibatasi per produk agar produk yang sangat besar tidak mendominasi, sekaligus menjaga representasi tingkat target dan kelompok usia. Identitas baris serta parent_asin setiap subset disimpan agar seluruh model menggunakan sampel yang sama.' | Out-Null

Add-Heading 'Metode Pengumpulan Data' 'Heading 3' | Out-Null
Add-Paragraph 'Data dikumpulkan melalui studi dokumentasi terhadap Amazon Reviews 2023 yang dipublikasikan pada https://amazon-reviews-2023.github.io/ dan dijelaskan dalam publikasi BLAIR [2]. Berkas User Reviews diunduh dari sumber resmi. Setiap berkas dicatat nama, kategori, versi atau tanggal akses, ukuran, jumlah baris, checksum, serta skema aktualnya. Pencatatan tersebut diperlukan karena dataset berskala besar dapat tersedia dalam beberapa kategori dan format.' | Out-Null
Add-Paragraph 'Atribut wajib diverifikasi sebelum pemrosesan. Timestamp diperiksa satuannya; contoh resmi menggunakan Unix timestamp dalam milidetik, tetapi implementasi tidak mengasumsikan satuan sebelum validasi rentang tanggal. Baris dengan timestamp tidak valid, identitas produk kosong, atau teks yang tidak dapat digunakan ditangani berdasarkan aturan terdokumentasi. Nilai helpful_vote dipastikan berupa bilangan tidak negatif dan rating diperiksa berada pada rentang yang diizinkan dataset.' | Out-Null
Add-Caption 'Tabel 3.3 Atribut data dan perannya dalam penelitian' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Atribut','Peran','Digunakan saat inferensi utama'),
    @('title','Judul ulasan dan bagian input encoder','Ya'),
    @('text','Isi ulasan dan bagian input encoder','Ya'),
    @('rating','Fitur terstruktur','Ya'),
    @('verified_purchase','Fitur terstruktur kategorikal/biner','Ya'),
    @('timestamp','Perhitungan review_age dan analisis paparan','Tidak'),
    @('helpful_vote','Pembentukan target dan evaluasi','Tidak'),
    @('parent_asin','Kelompok ranking dan unit split','Tidak sebagai fitur'),
    @('asin','Pemeriksaan varian dan kebocoran','Tidak sebagai fitur')
) @(105,225,90) | Out-Null
Add-Paragraph 'Item Metadata tidak menjadi kebutuhan model utama. Metadata hanya dapat ditambahkan pada eksperimen lanjutan, misalnya untuk analisis per kategori. Ketidaktersediaannya tidak mengubah definisi input, target, split, atau evaluasi utama.' | Out-Null

Add-Heading 'Alat-alat Penelitian' 'Heading 3' | Out-Null
Add-Paragraph 'Penelitian memerlukan perangkat keras untuk penyimpanan dataset, ekstraksi embedding, dan pelatihan model, serta perangkat lunak untuk pengolahan data, pemodelan statistik, deep learning, dan pencatatan eksperimen. Spesifikasi aktual CPU, RAM, GPU, VRAM, sistem operasi, kapasitas penyimpanan, dan waktu proses dicatat pada saat implementasi. Encoder dibekukan dan embedding disimpan ke disk untuk mengurangi pengulangan komputasi pada eksperimen skala dan ablasi.' | Out-Null
Add-Caption 'Tabel 3.4 Perangkat dan perangkat lunak penelitian' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Jenis','Alat','Peruntukan'),
    @('Perangkat keras','CPU multi-core dan RAM yang memadai','Preprocessing, agregasi per produk, pembentukan pasangan, dan analisis statistik.'),
    @('Perangkat keras','GPU NVIDIA berkemampuan CUDA dan VRAM yang memadai','Ekstraksi embedding BLaIR dan pelatihan MLP.'),
    @('Perangkat keras','Penyimpanan SSD','Menyimpan dataset, embedding, split, checkpoint, dan log eksperimen.'),
    @('Perangkat lunak','Python dan environment terisolasi','Bahasa implementasi serta penguncian dependensi.'),
    @('Perangkat lunak','PyTorch dan Hugging Face Transformers','Inferensi encoder BLaIR dan pelatihan neural.'),
    @('Perangkat lunak','Pandas/Polars, NumPy, dan scikit-learn','Pemrosesan data, transformasi fitur, baseline, dan metrik.'),
    @('Perangkat lunak','statsmodels/SciPy','Model count, korelasi, interval kepercayaan, dan uji statistik.'),
    @('Perangkat lunak','Matplotlib/Seaborn','Visualisasi distribusi, kurva usia-vote, dan hasil eksperimen.'),
    @('Perangkat lunak','Git dan pencatat eksperimen','Kontrol versi kode, konfigurasi, seed, dan artefak hasil.')
) @(85,135,200) | Out-Null
Add-Paragraph 'Versi library, checkpoint, tokenizer, commit kode, dan konfigurasi environment dibekukan pada setiap run. Jika keterbatasan memori mengharuskan pemrosesan bertahap, data dibaca secara streaming atau per shard, embedding disimpan dalam tipe numerik yang terdokumentasi, dan kesetaraan hasil terhadap sampel kecil diverifikasi.' | Out-Null

Add-Heading 'Teknik Analisis dan Rencana Strategi' 'Heading 3' | Out-Null
Add-Paragraph 'Teknik analisis menggabungkan statistik deskriptif, pemodelan count untuk hubungan usia-vote, learning to rank, dan evaluasi berbasis kelompok produk. Seluruh keputusan yang dapat memengaruhi performa ditentukan menggunakan training dan validation. Tahapan teknisnya dijelaskan sebagai berikut.' | Out-Null

Add-Paragraph 'Preprocessing dan pengendalian kualitas data.' 'Normal' 0 0 6 0 -1 'Preprocessing dan pengendalian kualitas data.' | Out-Null
Add-Paragraph 'Teks dibersihkan secara konservatif dengan normalisasi spasi dan karakter kendali tanpa menghapus negasi, angka, tanda baca bermakna, atau informasi semantik. Nilai title kosong dapat diganti string kosong apabila text tersedia, sedangkan baris tanpa isi review yang dapat digunakan dikeluarkan. Duplikasi diperiksa melalui identitas review apabila tersedia dan melalui kombinasi parent_asin, asin, timestamp, title, text, serta rating. Pemeriksaan hash teks dilakukan lintas split setelah alokasi produk untuk mendeteksi salinan yang dapat menyebabkan kebocoran.' | Out-Null
Add-Paragraph 'Fitur terstruktur dihitung sebelum training, tetapi parameter transformasinya hanya dipelajari dari training. Review_length adalah jumlah karakter isi review, word_count adalah jumlah token berbasis pemisahan spasi setelah normalisasi, dan title_length adalah jumlah karakter judul. Fitur panjang ditransformasi dengan ln(1+x) bila distribusinya sangat menceng, lalu distandardisasi menggunakan rata-rata dan simpangan baku training. Verified_purchase dipetakan secara konsisten ke nilai biner; kategori tidak dikenal pada validation/testing ditangani dengan aturan eksplisit.' | Out-Null

Add-Paragraph 'Pembentukan target mentah.' 'Normal' 0 0 6 0 -1 'Pembentukan target mentah.' | Out-Null
Add-Paragraph 'Dataset menyediakan helpful_vote tetapi tidak menyediakan total_votes, sehingga helpfulness ratio tidak dapat dihitung secara valid. Target observasi awal ditetapkan sebagai transformasi logaritmik berikut.' | Out-Null
Add-Equation 'y_i = ln(1 + v_i)' | Out-Null
Add-Paragraph 'Pada persamaan tersebut, v_i adalah helpful_vote ulasan ke-i. Transformasi logaritmik mengurangi pengaruh nilai ekstrem tanpa mengubah urutan monotonik. Helpful_vote dan seluruh turunannya tidak pernah dimasukkan sebagai fitur. Ulasan dengan vote nol dipertahankan karena nol dapat menunjukkan belum adanya paparan yang cukup.' | Out-Null

Add-Paragraph 'Pengukuran dan koreksi pengaruh usia.' 'Normal' 0 0 6 0 -1 'Pengukuran dan koreksi pengaruh usia.' | Out-Null
Add-Paragraph 'Usia ulasan dihitung dalam hari dari satu waktu referensi snapshot yang konsisten. T_ref diambil dari tanggal snapshot resmi; apabila tanggal tersebut tidak tersedia, maksimum timestamp valid pada snapshot digunakan dan keputusan ini dicatat. Timestamp yang melebihi T_ref dianggap tidak valid.' | Out-Null
Add-Equation 'review_age_days_i = (T_ref - timestamp_i) / 86.400.000' | Out-Null
Add-Paragraph 'Hubungan usia dan vote terlebih dahulu dideskripsikan melalui distribusi vote, proporsi nol, median, mean, kuantil, serta korelasi Spearman antara ln(1+age) dan helpful_vote. Ringkasan disajikan secara keseluruhan dan per kelompok usia yang batasnya dipelajari dari training. Istilah pengaruh dalam penelitian ini merujuk pada asosiasi setelah pengendalian produk dan kovariat yang tersedia, bukan efek kausal.' | Out-Null
Add-Paragraph 'Model count awal adalah Negative Binomial karena helpful_vote diperkirakan overdispersed. Poisson digunakan hanya jika pemeriksaan dispersi mendukung. Bentuk model adalah sebagai berikut.' | Out-Null
Add-Equation 'ln E[v_i] = alpha_p(i) + f(ln(1 + age_i)) + beta^T x_i' | Out-Null
Add-Paragraph 'Alpha_p(i) adalah efek produk, f(.) adalah fungsi usia linear atau spline, dan x_i memuat kovariat nonteks seperti rating, verified_purchase, serta panjang ulasan. Kompleksitas spline, regularisasi, dan bentuk model dipilih menggunakan training/validation. Hasil dilaporkan sebagai kurva usia beserta interval kepercayaan 95%, perubahan vote yang diharapkan, serta tambahan deviance explained atau pseudo-R2 dibandingkan model tanpa usia [12].' | Out-Null
Add-Paragraph 'Target terkoreksi usia hanya mengurangi komponen paparan usia yang telah dipusatkan pada distribusi training; efek produk dan kovariat lain tidak dikurangkan. Prediksi komponen usia untuk baris training dibuat melalui K-fold out-of-fold berdasarkan kelompok produk. Model usia untuk validation dan testing hanya dilatih pada training. Rumus targetnya adalah:' | Out-Null
Add-Equation 'y_i(adj) = ln(1 + v_i) - f_hat(ln(1 + age_i))' | Out-Null
Add-Paragraph 'Target terkoreksi dapat bernilai negatif dan tetap digunakan untuk menentukan arah preferensi pasangan. Untuk NDCG, nilai tersebut dipetakan ke tingkat relevansi nonnegatif 0-4 menggunakan batas kuantil yang hanya dihitung dari training. Hasil berbasis target mentah dan target terkoreksi dilaporkan dalam tabel terpisah dan tidak dibandingkan sebagai angka yang identik.' | Out-Null

Add-Paragraph 'Product-disjoint split dan pencegahan kebocoran.' 'Normal' 0 0 6 0 -1 'Product-disjoint split dan pencegahan kebocoran.' | Out-Null
Add-Paragraph 'Urutan operasi dijaga agar tidak terjadi kebocoran: deduplikasi global dan validasi identitas dilakukan sebelum split; alokasi dilakukan pada parent_asin; fit scaler, encoder kategorikal, kuantil, model usia, dan aturan pasangan dilakukan pada training; pemilihan hyperparameter dilakukan pada validation; dan testing digunakan satu kali. Daftar produk, identitas baris, serta checksum setiap split disimpan. Pemeriksaan assert memastikan irisan parent_asin antarsplit kosong dan salinan teks lintas split telah ditangani.' | Out-Null

Add-Paragraph 'Ekstraksi embedding BLaIR.' 'Normal' 0 0 6 0 -1 'Ekstraksi embedding BLaIR.' | Out-Null
Add-Paragraph 'Masukan encoder dibentuk dari title dan text dengan pemisah tokenizer checkpoint hyp1231/blair-roberta-base. Tokenisasi, special token, panjang maksimum, padding, dan truncation mengikuti konfigurasi checkpoint dan dicatat. Jika teks melebihi panjang maksimum, strategi truncation mempertahankan judul dan bagian awal isi secara deterministik. Representasi token [CLS] pada lapisan terakhir digunakan sebagai embedding dan normalisasi L2 diuji sesuai dokumentasi checkpoint [14]. Encoder dibekukan pada eksperimen utama; embedding dihitung tanpa gradien, disimpan, lalu diverifikasi keterkaitannya dengan identitas baris.' | Out-Null

Add-Paragraph 'Feature fusion dan arsitektur MLP.' 'Normal' 0 0 6 0 -1 'Feature fusion dan arsitektur MLP.' | Out-Null
Add-Paragraph 'Embedding e_i digabungkan dengan vektor fitur terstruktur z_i menjadi x_i = [e_i; z_i]. Fitur model utama hanya mencakup informasi yang tersedia saat inferensi: embedding teks, rating, verified_purchase, review_length, word_count, dan title_length. Review_age, helpful_vote, target, parent_asin, serta asin tidak menjadi input prediktif.' | Out-Null
Add-Caption 'Tabel 3.5 Konfigurasi awal model MLP ranking' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Komponen','Konfigurasi awal'),
    @('Input','Embedding BLaIR + fitur terstruktur tertransformasi'),
    @('Hidden layer 1','Dense 256 neuron + ReLU'),
    @('Regularisasi','Dropout 0,2'),
    @('Hidden layer 2','Dense 64 neuron + ReLU'),
    @('Output','Satu skor ranking tanpa aktivasi'),
    @('Optimizer','Adam; learning rate dan weight decay ditentukan pada validation'),
    @('Loss','Pairwise logistic loss bergaya RankNet'),
    @('Kontrol training','Mini-batch pasangan, early stopping NDCG@10 validation, gradient clipping bila diperlukan')
) @(145,275) | Out-Null
Add-Paragraph 'Pasangan (i,j) hanya dibentuk dari ulasan dalam parent_asin yang sama dan digunakan jika target i lebih tinggi daripada target j. Untuk skor s_i dan s_j, loss pasangan didefinisikan sebagai berikut [11].' | Out-Null
Add-Equation 'L_ij = ln(1 + exp(-(s_i - s_j)))' | Out-Null
Add-Paragraph 'Pasangan dengan target sama tidak menghasilkan preferensi. Jumlah pasangan per produk dibatasi, arah pasangan diacak secara seimbang, dan produk besar tidak boleh mendominasi mini-batch. Pada varian age-matched, pasangan diprioritaskan jika selisih usia berada di bawah batas yang dipilih pada validation. Pada varian pembobotan, pasangan lintas usia diberi bobot yang ditentukan pada validation dan proporsinya selalu dilaporkan.' | Out-Null

Add-Paragraph 'Rancangan eksperimen.' 'Normal' 0 0 6 0 -1 'Rancangan eksperimen.' | Out-Null
Add-Caption 'Tabel 3.6 Matriks eksperimen penelitian' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Kelompok','Varian','Tujuan'),
    @('Skala','100k; 250k; 500k; 750k; 1M review','Mengukur perubahan performa akibat penambahan data training.'),
    @('Baseline','TF-IDF + linear; TF-IDF + MLP; BLaIR + linear','Memisahkan manfaat representasi dan arsitektur.'),
    @('Model utama','BLaIR + MLP; BLaIR + fitur + MLP','Mengukur manfaat nonlinearitas dan feature fusion.'),
    @('Ablasi','Embedding saja; +rating; +verified; +seluruh fitur inferensi','Mengukur kontribusi fitur terstruktur.'),
    @('Kontrol usia','Target mentah; age-matched; target OOF terkoreksi; koreksi + bobot lintas usia','Mengukur dampak strategi pengendalian paparan.'),
    @('Oracle','Model tambahan dengan review_age','Mengukur upper bound informasi usia; bukan model produksi.')
) @(70,165,185) | Out-Null
Add-Paragraph 'Seluruh varian dalam satu perbandingan menggunakan split, sampel, target, dan protokol evaluasi yang setara. Minimal tiga seed digunakan untuk training model neural; nilai rata-rata dan simpangan baku antarseed dilaporkan. Model terbaik dipilih berdasarkan NDCG@10 macro pada validation. Fine-tuning penuh encoder tidak menjadi eksperimen utama dan hanya dapat ditambahkan sebagai analisis lanjutan jika sumber daya memungkinkan.' | Out-Null

Add-Paragraph 'Evaluasi model dan analisis statistik.' 'Normal' 0 0 6 0 -1 'Evaluasi model dan analisis statistik.' | Out-Null
Add-Caption 'Tabel 3.7 Metrik dan aturan evaluasi' 'Judul Tabel' | Out-Null
Add-Table @(
    @('Metrik','Penggunaan','Aturan utama'),
    @('NDCG@5','Kualitas lima posisi teratas','Dihitung per produk dengan IDCG > 0, lalu macro-average.'),
    @('NDCG@10','Metrik utama kualitas ranking','Cut-off menggunakan min(k,n); target mentah dan terkoreksi dilaporkan terpisah [13].'),
    @('Spearman','Kesesuaian urutan monotonik','Produk minimal tiga ulasan dan target tidak konstan.'),
    @('MAP','Presisi posisi relevan','Produk memiliki minimal satu relevan dan satu nonrelevan; threshold dibekukan dari training/validation.'),
    @('MAE/RMSE','Akurasi prediksi ln(1+vote)','Hanya untuk baseline regresi atau keluaran terkalibrasi, bukan skor ranking mentah.'),
    @('NB deviance','Kecocokan model count usia','Dibandingkan dengan model tanpa komponen usia.')
) @(80,135,205) | Out-Null
Add-Paragraph 'NDCG, Spearman, dan MAP dihitung untuk setiap produk, kemudian dirata-ratakan secara makro agar produk besar tidak mendominasi. Untuk target mentah, gain berasal dari ln(1+helpful_vote); untuk target terkoreksi, gain berasal dari tingkat relevansi 0-4 yang ditetapkan oleh kuantil training. Threshold biner MAP dipilih dari kandidat yang ditentukan sebelum testing, misalnya vote positif atau kuantil relevansi, dengan validation sebagai dasar pemilihan.' | Out-Null
Add-Paragraph 'Produk dengan kurang dari dua ulasan valid dikeluarkan dari metrik ranking. Produk dengan target konstan dikeluarkan dari Spearman dan analisis preferensi; produk tanpa relevan atau tanpa nonrelevan dikeluarkan dari MAP. Jumlah produk valid, jumlah ulasan, dan alasan eksklusi dilaporkan untuk setiap metrik. Performa juga disajikan menurut kelompok review baru, menengah, dan lama serta menurut ukuran kelompok produk.' | Out-Null
Add-Paragraph 'Ketidakpastian hasil diestimasi dengan bootstrap pada tingkat parent_asin sebanyak 1.000 replikasi sehingga struktur ulasan dalam produk tetap utuh. Perbandingan dua model menggunakan selisih metrik per produk dan interval kepercayaan 95%; klaim peningkatan hanya dibuat jika arah perbedaan konsisten, besar efek dilaporkan, dan tidak hanya bergantung pada satu seed. Analisis usia menyajikan interval kepercayaan kurva dan uji sensitivitas terhadap batas kelompok usia, bentuk spline, serta aturan pasangan.' | Out-Null

Add-Paragraph 'Reproduksibilitas dan kriteria penghentian.' 'Normal' 0 0 6 0 -1 'Reproduksibilitas dan kriteria penghentian.' | Out-Null
Add-Bullets @(
    'Menetapkan seed untuk split produk, sampling E1-E5, fold model usia, pembentukan pasangan, dan inisialisasi model.',
    'Menyimpan konfigurasi checkpoint, tokenizer, pooling, panjang token, scaler, threshold, kuantil, hyperparameter, waktu proses, penggunaan RAM/VRAM, dan kapasitas penyimpanan.',
    'Menyimpan model usia, prediksi out-of-fold, embedding, daftar produk tiap split, identitas sampel nested, checkpoint terbaik, dan hasil per produk.',
    'Menggunakan early stopping berdasarkan NDCG@10 validation dengan patience yang ditetapkan sebelum test; training dihentikan jika tidak ada perbaikan atau batas epoch tercapai.',
    'Menjalankan pemeriksaan otomatis bahwa fitur terlarang tidak masuk ke tensor model dan bahwa irisan parent_asin antarsplit kosong.'
)
Add-Paragraph 'Luaran akhir penelitian adalah model yang menghasilkan skor ranking untuk setiap ulasan dan dapat diterapkan pada produk baru tanpa memerlukan review_age pada inferensi. Hasil terhadap target mentah tetap dilaporkan sebagai pembanding, sedangkan hasil target terkoreksi usia menjadi dasar penilaian kualitas yang lebih sedikit dipengaruhi kesempatan paparan. Apabila tujuan bergeser menjadi prediksi jumlah vote kumulatif pada horizon tertentu, review_age atau horizon harus ditambahkan pada tahap kalibrasi dan dievaluasi sebagai tugas yang berbeda.' | Out-Null

# Refresh all automatic lists and page references in Word.
foreach ($toc in $doc.TablesOfContents) { $toc.Update() }

# Save as a new DOCX, never over the retained reference or the user's open file.
$doc.SaveAs2($output, 16)
$pageCount = $doc.ComputeStatistics(2)
$paragraphCount = $doc.Paragraphs.Count
$tableCount = $doc.Tables.Count
$inlineCount = $doc.InlineShapes.Count
$doc.Close(0)

if ($createdWord) { $word.Quit() }

Write-Output "OUTPUT=$output"
Write-Output "PAGES=$pageCount PARAGRAPHS=$paragraphCount TABLES=$tableCount INLINE_SHAPES=$inlineCount"
