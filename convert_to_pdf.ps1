param (
    [string]$DocxPath,
    [string]$PdfPath
)

$DocxPath = [System.IO.Path]::GetFullPath($DocxPath)
$PdfPath = [System.IO.Path]::GetFullPath($PdfPath)

Write-Output "Converting $DocxPath to $PdfPath..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($DocxPath)
    # 17 = wdFormatPDF
    $doc.SaveAs([ref]$PdfPath, [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Conversion completed successfully!"
} catch {
    Write-Output ("Error during conversion: " + $_.Exception.ToString())
} finally {
    $word.Quit()
}
