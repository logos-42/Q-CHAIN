@echo off
echo ========================================
echo     量子区块链 Q# 项目启动脚本
echo ========================================
echo.

echo 检查环境要求...
echo.

REM 检查 .NET SDK
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ .NET SDK 未安装或不在PATH中
    echo 请安装 .NET 8.0 SDK: https://dotnet.microsoft.com/download
    pause
    exit /b 1
) else (
    echo ✅ .NET SDK 已安装
)

REM 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装或不在PATH中
    echo 请安装 Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js 已安装
)

REM 检查 npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm 未安装
    pause
    exit /b 1
) else (
    echo ✅ npm 已安装
)

echo.
echo ========================================
echo     项目启动
echo ========================================
echo.

REM 创建解决方案文件（如果不存在）
if not exist "QuantumBlockchain.sln" (
    echo 创建解决方案文件...
    dotnet new sln -n QuantumBlockchain
    dotnet sln add WebApi/WebApi.csproj
    echo ✅ 解决方案文件已创建
) else (
    echo ✅ 解决方案文件已存在
)

REM 恢复 NuGet 包
echo 恢复 NuGet 包...
dotnet restore
if %errorlevel% neq 0 (
    echo ❌ NuGet 包恢复失败
    pause
    exit /b 1
)
echo ✅ NuGet 包恢复完成

REM 构建项目
echo 构建项目...
dotnet build
if %errorlevel% neq 0 (
    echo ❌ 项目构建失败
    pause
    exit /b 1
)
echo ✅ 项目构建完成

REM 安装前端依赖
echo 安装前端依赖...
cd Frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✅ 前端依赖安装完成

echo.
echo ========================================
echo     启动服务
echo ========================================
echo.

echo 选择启动模式:
echo 1. 仅后端 API (http://localhost:5000)
echo 2. 仅前端界面 (http://localhost:5173)
echo 3. 后端 + 前端 (推荐)
echo 4. 退出
echo.

set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" (
    echo 启动后端 API...
    start "量子区块链 API" cmd /k "cd WebApi && dotnet run"
    echo API 将在 http://localhost:5000 启动
    pause
    exit /b 0
)

if "%choice%"=="2" (
    echo 启动前端界面...
    start "量子区块链前端" cmd /k "cd Frontend && npm run dev"
    echo 前端将在 http://localhost:5173 启动
    pause
    exit /b 0
)

if "%choice%"=="3" (
    echo 启动后端 API...
    start "量子区块链 API" cmd /k "cd WebApi && dotnet run"
    
    timeout /t 3 /nobreak >nul
    
    echo 启动前端界面...
    start "量子区块链前端" cmd /k "cd Frontend && npm run dev"
    
    echo.
    echo ✅ 项目已启动!
    echo 🌐 API 服务: http://localhost:5000
    echo 🎨 前端界面: http://localhost:5173
    echo 📚 API 文档: http://localhost:5000/swagger
    echo.
    echo 按任意键退出所有服务...
    pause >nul
    exit /b 0
)

if "%choice%"=="4" (
    echo 退出...
    exit /b 0
)

echo ❌ 无效选择
pause