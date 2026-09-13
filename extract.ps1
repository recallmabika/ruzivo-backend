$word = New-Object -ComObject Word.Application
$word.Visible = $false

$files = @(
    @{ In = "C:\Users\recal\Desktop\Level 2.2 Project\CHAPTER-1_RuzivoAI.docx"; Out = "C:\Users\recal\Desktop\Level 2.2 Project\ruzivo\chapter1.txt" },
    @{ In = "C:\Users\recal\Desktop\Level 2.2 Project\Chapter-2_RuzivoAI.docx"; Out = "C:\Users\recal\Desktop\Level 2.2 Project\ruzivo\chapter2.txt" },
    @{ In = "C:\Users\recal\Desktop\Level 2.2 Project\Chapter-3_RuzivoAI.docx"; Out = "C:\Users\recal\Desktop\Level 2.2 Project\ruzivo\chapter3.txt" }
)

foreach ($f in $files) {
    $doc = $word.Documents.Open($f.In)
    $doc.Content.Text | Out-File -FilePath $f.Out -Encoding UTF8
    $doc.Close()
    Write-Host "Extracted: $($f.Out)"
}

$word.Quit()
