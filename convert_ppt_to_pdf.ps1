param (
    [string]$PptxPath,
    [string]$PdfPath
)

$PptxPath = [System.IO.Path]::GetFullPath($PptxPath)
$PdfPath = [System.IO.Path]::GetFullPath($PdfPath)

Write-Output "Converting $PptxPath to $PdfPath..."
$ppt = New-Object -ComObject PowerPoint.Application
try {
    # Open presentation (ReadOnly, Untitled, WithWindow=$false)
    $pres = $ppt.Presentations.Open($PptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    # 32 = ppSaveAsPDF
    $pres.SaveAs($PdfPath, 32)
    $pres.Close()
    Write-Output "PowerPoint to PDF conversion completed successfully!"
} catch {
    Write-Output ("Error during conversion: " + $_.Exception.ToString())
} finally {
    $ppt.Quit()
}
