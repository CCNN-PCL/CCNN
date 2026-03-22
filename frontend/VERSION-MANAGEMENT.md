# 版本号管理

## 简介

这是一个纯净的版本号管理工具，只负责更新 `package.json` 中的版本号，不执行任何Git操作（提交、打标签等）。所有Git操作需要手动执行。

## 可用命令

### 查看当前版本
```bash
npm run version:show
# 或
node scripts/update-version.js show
```

### 更新修订版本 (patch)
用于bug修复：`1.0.0` → `1.0.1`
```bash
npm run version:patch
# 或
node scripts/update-version.js patch
```

### 更新次版本 (minor)
用于新功能：`1.0.0` → `1.1.0`
```bash
npm run version:minor
# 或
node scripts/update-version.js minor
```

### 更新主版本 (major)
用于重大变更：`1.0.0` → `2.0.0`
```bash
npm run version:major
# 或
node scripts/update-version.js major
```

### 设置特定版本
```bash
npm run version:set -- 1.2.3
# 或
node scripts/update-version.js set 1.2.3
```

### 显示帮助
```bash
node scripts/update-version.js help
```

## 使用示例

### 示例1：修复bug后更新版本
```bash
# 1. 查看当前版本
npm run version:show
# 输出: 当前版本: 1.0.0

# 2. 更新修订版本
npm run version:patch
# 输出: 版本号已更新: 1.0.0 → 1.0.1

# 3. 手动提交更改
git add package.json
git commit -m "chore: bump version to 1.0.1"

# 4. 手动创建标签（可选）
git tag -a v1.0.1 -m "Release version 1.0.1"
```

### 示例2：发布新功能
```bash
# 更新次版本
npm run version:minor
# 输出: 版本号已更新: 1.0.1 → 1.1.0

# 然后手动提交和打标签
git add package.json
git commit -m "chore: bump version to 1.1.0"
git tag -a v1.1.0 -m "Release version 1.1.0"
```

### 示例3：设置特定版本
```bash
# 设置版本为2.0.0
npm run version:set -- 2.0.0
# 或
node scripts/update-version.js set 2.0.0
```

## 版本号规范

遵循 [Semantic Versioning 2.0.0](https://semver.org/) 规范：

- **主版本号 (MAJOR)**: 不兼容的API修改
- **次版本号 (MINOR)**: 向下兼容的功能性新增  
- **修订号 (PATCH)**: 向下兼容的问题修正

格式：`MAJOR.MINOR.PATCH`

## 工作流程

1. **开发完成**后决定版本更新类型
2. **运行版本更新命令**更新package.json
3. **手动提交更改**到Git
4. **手动创建标签**（如果需要）
5. **手动推送标签**到远程仓库

## 手动Git操作参考

### 提交版本变更
```bash
git add package.json
git commit -m "chore: bump version to X.X.X"
```

### 创建Git标签
```bash
git tag -a vX.X.X -m "Release version X.X.X"
```

### 推送标签到远程
```bash
git push origin vX.X.X
# 或推送所有标签
git push --tags
```

### 查看所有标签
```bash
git tag -l
```

## 注意事项

1. 此工具**只更新package.json版本号**，不执行Git操作
2. 所有Git操作需要**手动执行**
3. 版本号更新后需要**手动提交**更改
4. 标签创建是**可选的**，但推荐为每个版本创建标签

## 文件说明

- `scripts/update-version.js` - 版本更新脚本
- `package.json` - 包含版本管理npm脚本
- `VERSION-MANAGEMENT.md` - 本文档

## 快速参考

```bash
# 查看版本
npm run version:show

# 更新版本（根据变更类型选择）
npm run version:patch    # bug修复
npm run version:minor    # 新功能
npm run version:major    # 重大变更

# 设置特定版本
npm run version:set -- 2.0.0
```
