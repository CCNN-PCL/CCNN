# PowerShell脚本：构建并导出 triage-agent 镜像为 tar 包

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "构建 triage-agent 镜像" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 镜像名称和标签
$IMAGE_NAME = "triage-agent"
$IMAGE_TAG = "latest"
$FULL_IMAGE_NAME = "${IMAGE_NAME}:${IMAGE_TAG}"

# tar包文件名
$TAR_FILE = "${IMAGE_NAME}.tar"

# 检查Dockerfile是否存在
if (-not (Test-Path "Dockerfile")) {
    Write-Host "错误: 未找到 Dockerfile" -ForegroundColor Red
    exit 1
}

# 检查requirements.txt是否存在
if (-not (Test-Path "requirements.txt")) {
    Write-Host "错误: 未找到 requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "`n步骤 1: 构建 Docker 镜像..." -ForegroundColor Yellow
docker build -t $FULL_IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host "✓ 镜像构建成功" -ForegroundColor Green

# 显示镜像信息
Write-Host "`n镜像信息:" -ForegroundColor Yellow
docker images $FULL_IMAGE_NAME

Write-Host "`n步骤 2: 导出镜像为 tar 包..." -ForegroundColor Yellow
docker save -o $TAR_FILE $FULL_IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "镜像导出失败" -ForegroundColor Red
    exit 1
}

# 检查tar包是否生成
if (Test-Path $TAR_FILE) {
    $TAR_SIZE = (Get-Item $TAR_FILE).Length / 1MB
    Write-Host "✓ 镜像导出成功" -ForegroundColor Green
    Write-Host "文件: $TAR_FILE" -ForegroundColor Green
    Write-Host "大小: $([math]::Round($TAR_SIZE, 2)) MB" -ForegroundColor Green
    Write-Host "`n可以使用以下命令加载镜像:" -ForegroundColor Yellow
    Write-Host "docker load -i $TAR_FILE" -ForegroundColor Cyan
} else {
    Write-Host "错误: tar包未生成" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green


