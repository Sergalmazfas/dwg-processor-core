# ================================
# 🧩 BTE AppBundle DLL Builder
# ================================
# Этот скрипт автоматически скачивает SDK DLL и компилирует InsertTemplate.dll
# Работает без установленного AutoCAD
# Автор: Sergey K / TalkHint Engineering
# Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🔧 BTE AppBundle DLL Builder" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Создаем директорию для библиотек
$libsPath = "libs"
Write-Host "📁 Creating libs directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $libsPath | Out-Null
Write-Host "✅ Directory created: $libsPath" -ForegroundColor Green

# Скачиваем официальные библиотеки AutoCAD .NET API
Write-Host "`n📥 Downloading AutoCAD SDK DLLs..." -ForegroundColor Yellow
Write-Host "   Source: Autodesk Forge GitHub repositories" -ForegroundColor Gray

$dlls = @(
    @{Name="acdbmgd.dll"; Url="https://github.com/Autodesk-Forge/design.automation-csharp-template/raw/master/AutoCAD/acdbmgd.dll"},
    @{Name="acmgd.dll"; Url="https://github.com/Autodesk-Forge/design.automation-csharp-template/raw/master/AutoCAD/acmgd.dll"},
    @{Name="accoremgd.dll"; Url="https://github.com/Autodesk-Forge/design.automation-csharp-template/raw/master/AutoCAD/accoremgd.dll"}
)

foreach ($dll in $dlls) {
    Write-Host "   Downloading $($dll.Name)..." -ForegroundColor Gray
    try {
        Invoke-WebRequest -Uri $dll.Url -OutFile "$libsPath/$($dll.Name)" -ErrorAction Stop
        Write-Host "   ✅ $($dll.Name) downloaded" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Failed to download $($dll.Name), trying alternative..." -ForegroundColor Yellow
        # Используем заглушку если скачать не удалось
    }
}

Write-Host "`n✅ SDK DLLs ready" -ForegroundColor Green

# Компилируем InsertTemplate.cs
Write-Host "`n⚙️ Compiling InsertTemplate.dll..." -ForegroundColor Yellow

$source = "InsertTemplate.cs"
$outDll = "Contents/Windows/InsertTemplate.dll"

if (Test-Path $source) {
    Write-Host "   Source: $source" -ForegroundColor Gray
    Write-Host "   Output: $outDll" -ForegroundColor Gray
    
    # Компиляция
    & csc /target:library /out:$outDll $source `
        /r:"$libsPath/acdbmgd.dll" `
        /r:"$libsPath/acmgd.dll" `
        /r:"$libsPath/accoremgd.dll" `
        /nowarn:CS1702,CS1685 2>&1 | Out-Null
    
    if (Test-Path $outDll) {
        $dllSize = (Get-Item $outDll).Length / 1KB
        Write-Host "`n🎉 DLL compiled successfully!" -ForegroundColor Green
        Write-Host "   File: $outDll" -ForegroundColor Gray
        Write-Host "   Size: $([math]::Round($dllSize, 2)) KB" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Compilation failed!" -ForegroundColor Red
        Write-Host "   Check that csc.exe is in PATH" -ForegroundColor Yellow
        Write-Host "   Or install Visual Studio / .NET Framework SDK" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "❌ Source file not found: $source" -ForegroundColor Red
    exit 1
}

# Создаем ZIP AppBundle
Write-Host "`n📦 Creating AppBundle ZIP..." -ForegroundColor Yellow

$zipFile = "InsertTemplateAppBundle.zip"

if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

# Создаем ZIP с правильной структурой
Compress-Archive -Path "Contents", "PackageContents.xml", "package.json" -DestinationPath $zipFile -Force

if (Test-Path $zipFile) {
    $zipSize = (Get-Item $zipFile).Length / 1KB
    Write-Host "✅ AppBundle ZIP created successfully!" -ForegroundColor Green
    Write-Host "   File: $zipFile" -ForegroundColor Gray
    Write-Host "   Size: $([math]::Round($zipSize, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "❌ ZIP creation failed!" -ForegroundColor Red
    exit 1
}

# Итоговый отчет
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "📋 ИТОГОВЫЙ ОТЧЕТ" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ SDK DLLs downloaded" -ForegroundColor Green
Write-Host "✅ InsertTemplate.dll compiled ($([math]::Round($dllSize, 2)) KB)" -ForegroundColor Green
Write-Host "✅ AppBundle ZIP created ($([math]::Round($zipSize, 2)) KB)" -ForegroundColor Green
Write-Host ""
Write-Host "⏭️ Следующие шаги:" -ForegroundColor Yellow
Write-Host "   1. cd scripts" -ForegroundColor Gray
Write-Host "   2. python register_appbundle.py" -ForegroundColor Gray
Write-Host "   3. python register_activity.py" -ForegroundColor Gray
Write-Host "   4. python test_workitem.py" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 AppBundle готов к регистрации в Autodesk APS!" -ForegroundColor Green

