# setup_demo_env.ps1
# 演示模式真实环境配置脚本
# 在 cybertwin-agent-service 目录下执行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置演示模式环境" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 数据库配置（云MySQL）
Write-Host "[1/7] 配置数据库..." -ForegroundColor Yellow
$env:DATABASE_TYPE = "mysql"
$env:MYSQL_HOST = "192.168.208.66"
$env:MYSQL_PORT = "31717"
$env:MYSQL_DATABASE = "private_doctor_db"
$env:MYSQL_USER = "doctor_user"
$env:MYSQL_PASSWORD = "doctor_password"
Write-Host "  OK 数据库配置完成（云MySQL）" -ForegroundColor Green
Write-Host ""

# 大模型配置
Write-Host "[2/7] 配置大模型..." -ForegroundColor Yellow
$env:QWEN_BASE_URL = "http://192.168.64.60:32568/v1"
$env:QWEN_API_KEY = "custom"
$env:HUATUO_BASE_URL = "http://192.168.64.60:32508/v1"
$env:HUATUO_API_KEY = "custom"
$env:HUATUO2_BASE_URL = "http://172.22.11.169:30466/v1"
$env:HUATUO2_API_KEY = "custom"
Write-Host "  OK 大模型配置完成" -ForegroundColor Green
Write-Host ""

# EntryAgent配置（启用，使用标准A2A SDK）
Write-Host "[3/7] 配置EntryAgent..." -ForegroundColor Yellow
$env:USE_ENTRY_AGENT = "true"
$env:DATA_PROXY_APP_URL = "http://192.168.193.12:30090"
$env:DATA_PROXY_TIMEOUT = "120"
$env:DATA_PROXY_TOKEN = "test"
Write-Host "  OK EntryAgent配置完成（已启用）" -ForegroundColor Green
Write-Host ""

# MCP协议配置（启用）
Write-Host "[4/7] 配置MCP协议..." -ForegroundColor Yellow
$env:USE_MCP_PROTOCOL = "true"
$env:MCP_SERVER_BEIJING_URL = "http://192.168.193.12:30091"
$env:MCP_SERVER_SHANGHAI_URL = "http://192.168.193.12:30092"
$env:MCP_SERVER_TOKEN = "test"
$env:MCP_TRANSPORT_TYPE = "streamable-http"
$env:MCP_TIMEOUT = "60"
Write-Host "  OK MCP协议配置完成（已启用）" -ForegroundColor Green
Write-Host ""

# 微服务配置
Write-Host "[5/7] 配置微服务..." -ForegroundColor Yellow
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
Write-Host "[6/7] 配置演示模式..." -ForegroundColor Yellow
$env:DEMO_MODE_ENABLED = "true"
Write-Host "  OK 演示模式配置完成" -ForegroundColor Green
Write-Host ""

# Python路径（Cybertwin-Agent必需）
Write-Host "[7/7] 配置Python路径..." -ForegroundColor Yellow
$env:PYTHONPATH = (Get-Location).Parent.Parent.FullName
Write-Host "  OK Python路径配置完成: $env:PYTHONPATH" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "演示模式环境配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 现在可以启动服务了" -ForegroundColor Yellow
Write-Host ('  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001') -ForegroundColor Gray
