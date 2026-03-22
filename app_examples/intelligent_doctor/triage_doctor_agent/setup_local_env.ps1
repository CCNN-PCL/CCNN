# setup_local_env.ps1
# 本地测试环境配置脚本
# 在 cybertwin-agent-service 目录下执行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置本地测试环境" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 大模型配置（使用默认值，可选）
Write-Host "[1/6] 配置大模型..." -ForegroundColor Yellow
$env:QWEN_BASE_URL = "http://192.168.64.60:32568/v1"
$env:HUATUO_BASE_URL = "http://192.168.64.60:32508/v1"
$env:HUATUO2_BASE_URL = "http://172.22.11.169:30466/v1"
Write-Host "  OK 大模型配置完成" -ForegroundColor Green
Write-Host ""

# EntryAgent配置（禁用，使用HTTP降级）
Write-Host "[2/6] 配置EntryAgent..." -ForegroundColor Yellow
$env:USE_ENTRY_AGENT = "false"
$env:DATA_PROXY_APP_URL = "http://localhost:9000"
$env:DATA_PROXY_TIMEOUT = "30"
Write-Host "  OK EntryAgent配置完成（已禁用）" -ForegroundColor Green
Write-Host ""

# MCP协议配置（禁用）
Write-Host "[3/6] 配置MCP协议..." -ForegroundColor Yellow
$env:USE_MCP_PROTOCOL = "false"
Write-Host "  OK MCP协议配置完成（已禁用）" -ForegroundColor Green
Write-Host ""

# 微服务配置
Write-Host "[4/6] 配置微服务..." -ForegroundColor Yellow
$env:SERVICE_PORT = "8001"
$env:INTERNAL_MEDICINE_BEIJING_URL = "http://localhost:8002"
$env:INTERNAL_MEDICINE_SHANGHAI_URL = "http://localhost:8003"
$env:SURGICAL_BEIJING_URL = "http://localhost:8004"
$env:SURGICAL_SHANGHAI_URL = "http://localhost:8005"
$env:INTERNAL_MEDICINE_BEIJING_API_KEY = "test_api_key"
$env:INTERNAL_MEDICINE_SHANGHAI_API_KEY = "test_api_key"
$env:SURGICAL_BEIJING_API_KEY = "test_api_key"
$env:SURGICAL_SHANGHAI_API_KEY = "test_api_key"
Write-Host "  OK 微服务配置完成" -ForegroundColor Green
Write-Host ""

# 演示模式配置
Write-Host "[5/6] 配置演示模式..." -ForegroundColor Yellow
$env:DEMO_MODE_ENABLED = "true"
Write-Host "  OK 演示模式配置完成" -ForegroundColor Green
Write-Host ""

# Python路径（Cybertwin-Agent必需）
Write-Host "[6/6] 配置Python路径..." -ForegroundColor Yellow
$env:PYTHONPATH = (Get-Location).Parent.Parent.FullName
Write-Host "  OK Python路径配置完成: $env:PYTHONPATH" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "本地测试环境配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 现在可以启动服务了" -ForegroundColor Yellow
Write-Host ('  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001') -ForegroundColor Gray
