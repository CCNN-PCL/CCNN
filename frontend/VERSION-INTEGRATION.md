# 版本集成管理

## 概述

本项目已集成完整的版本管理系统，实现了：
1. **自动版本管理**：通过Makefile和npm脚本管理版本号
2. **构建时版本注入**：在构建过程中自动注入版本信息到应用中
3. **Docker镜像版本标签**：自动使用版本号作为Docker镜像标签
4. **前端版本展示**：在应用界面中显示版本信息

## 快速开始

### 查看当前版本
```bash
make version
# 或
make version-show
# 或
npm run version:show
```

### 构建项目（自动注入版本信息）
```bash
make build
```

### 构建Docker镜像（带版本标签）
```bash
make docker-image
# 这会构建两个标签：
#   - cybertwin-frontend:<version>
#   - cybertwin-frontend:latest
```

### 运行Docker容器
```bash
make docker-run
```

## 版本管理命令

### 更新修订版本 (patch)
用于bug修复：`0.1.0` → `0.1.1`
```bash
make version-patch
```

### 更新次版本 (minor)
用于新功能：`0.1.0` → `0.2.0`
```bash
make version-minor
```

### 更新主版本 (major)
用于重大变更：`0.1.0` → `1.0.0`
```bash
make version-major
```

### 设置特定版本
```bash
make version-set VERSION=1.2.3
```

## 版本信息注入

### 注入的文件
1. **src/version.js** - 供前端组件使用的版本信息
2. **dist/version.json** - 构建产物中的版本信息文件
3. **public/index.html** - HTML中的meta标签版本信息

### 版本信息内容
```javascript
{
  "version": "0.1.0",
  "name": "face_frontend",
  "buildTime": "2026-03-01T08:18:00.451Z",
  "buildTimestamp": 1772353080451
}
```

## 前端版本展示

### VersionInfo组件
在应用页脚显示版本信息，包含：
- 版本号 (如：v0.1.0)
- 构建时间

### 使用方式
```vue
<template>
  <VersionInfo :showAlways="true" :showDetails="false" />
</template>

<script>
import VersionInfo from './components/VersionInfo.vue';

export default {
  components: {
    VersionInfo
  }
}
</script>
```

### 组件属性
- `showAlways`: 是否始终显示（默认：false，开发环境隐藏）
- `showDetails`: 是否显示详细版本信息（默认：false）

## Docker镜像构建

### 镜像标签策略
- **版本标签**: `cybertwin-frontend:<version>` (如：`cybertwin-frontend:0.1.0`)
- **最新标签**: `cybertwin-frontend:latest`

### 构建命令
```bash
# 构建带版本标签的镜像
make docker-image

# 运行最新版本的镜像
make docker-run
```

## 工作流程示例

### 示例1：修复bug后发布新版本
```bash
# 1. 修复bug并提交代码
git commit -m "fix: 修复登录问题"

# 2. 更新patch版本
make version-patch
# 输出：版本号已更新: 0.1.0 → 0.1.1

# 3. 提交版本变更
git add package.json
git commit -m "chore: bump version to 0.1.1"

# 4. 构建Docker镜像
make docker-image
# 构建两个标签：cybertwin-frontend:0.1.1 和 cybertwin-frontend:latest

# 5. 推送镜像到仓库
docker push your-registry/cybertwin-frontend:0.1.1
docker push your-registry/cybertwin-frontend:latest
```

### 示例2：发布新功能版本
```bash
# 1. 开发新功能并提交
git commit -m "feat: 添加聊天历史功能"

# 2. 更新minor版本
make version-minor
# 输出：版本号已更新: 0.1.1 → 0.2.0

# 3. 提交版本变更
git add package.json
git commit -m "chore: bump version to 0.2.0"

# 4. 创建Git标签
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# 5. 构建和推送Docker镜像
make docker-image
docker push your-registry/cybertwin-frontend:0.2.0
docker push your-registry/cybertwin-frontend:latest
```

## 文件说明

### 核心文件
- `Makefile` - 包含版本管理和构建命令
- `package.json` - 包含版本号和npm脚本
- `scripts/update-version.js` - 版本更新脚本
- `scripts/inject-version.js` - 版本信息注入脚本

### 生成文件
- `src/version.js` - 自动生成的版本信息（构建时生成）
- `dist/version.json` - 构建产物中的版本信息
- `public/index.html` - 注入版本meta标签的HTML文件

### 组件文件
- `src/components/VersionInfo.vue` - 版本信息展示组件

## 环境变量

### Makefile变量
- `VERSION` - 当前版本号（自动从package.json读取）
- `APP_NAME` - 应用名称（默认：cybertwin-frontend）
- `IMAGE_NAME` - Docker镜像名称（格式：`<app-name>:<version>`）
- `IMAGE_NAME_LATEST` - 最新版Docker镜像名称（格式：`<app-name>:latest`）

### 自定义变量
可以在执行make命令时覆盖默认值：
```bash
make docker-image APP_NAME=my-app VERSION=1.0.0
```

## 调试信息

### 控制台输出
在开发环境中，版本信息会输出到浏览器控制台：
```javascript
console.log('📦 App Version Info:', window.__APP_VERSION__);
```

### 版本文件访问
构建后可以通过以下URL访问版本信息：
```
http://localhost:8080/version.json
```

## 注意事项

1. **版本注入时机**：版本信息在`prebuild`阶段注入，确保构建产物包含最新版本信息
2. **Git操作**：版本更新后需要手动提交package.json变更
3. **Docker标签**：每次构建都会同时创建版本标签和latest标签
4. **开发环境**：VersionInfo组件在开发环境下默认隐藏，可通过`showAlways=true`强制显示

## 故障排除

### 版本信息未显示
1. 检查是否执行了构建命令：`make build`
2. 检查`src/version.js`文件是否存在
3. 检查浏览器控制台是否有错误信息

### Docker构建失败
1. 检查Docker服务是否运行：`docker ps`
2. 检查是否有足够的磁盘空间
3. 检查网络连接是否可以拉取基础镜像

### 版本更新失败
1. 检查package.json文件格式是否正确
2. 检查是否有文件写入权限
3. 检查node.js版本是否兼容
