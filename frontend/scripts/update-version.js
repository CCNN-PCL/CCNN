#!/usr/bin/env node

/**
 * 纯净版版本更新脚本
 * 只更新package.json版本号，不执行任何Git操作
 */

const fs = require('fs');
const path = require('path');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function color(text, colorName) {
  return `${colors[colorName] || colors.reset}${text}${colors.reset}`;
}

// 显示帮助信息
function showHelp() {
  console.log(color('\n📦 版本号更新工具', 'cyan'));
  console.log(color('='.repeat(40), 'cyan'));
  console.log('用法: node scripts/update-version.js <命令> [版本号]');
  console.log('');
  console.log('命令:');
  console.log('  patch          更新修订版本 (1.0.0 → 1.0.1)');
  console.log('  minor          更新次版本 (1.0.0 → 1.1.0)');
  console.log('  major          更新主版本 (1.0.0 → 2.0.0)');
  console.log('  set <version>  设置特定版本号');
  console.log('  show           显示当前版本');
  console.log('  help           显示帮助信息');
  console.log('');
  console.log('示例:');
  console.log('  node scripts/update-version.js patch');
  console.log('  node scripts/update-version.js minor');
  console.log('  node scripts/update-version.js major');
  console.log('  node scripts/update-version.js set 1.2.3');
  console.log('  node scripts/update-version.js show');
  console.log('');
}

// 获取当前版本
function getCurrentVersion() {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    return packageData.version;
  } catch (error) {
    console.error(color('错误: 无法读取package.json', 'red'));
    process.exit(1);
  }
}

// 更新版本号
function updateVersion(newVersion) {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    const oldVersion = packageData.version;
    packageData.version = newVersion;
    
    fs.writeFileSync(packagePath, JSON.stringify(packageData, null, 2) + '\n', 'utf8');
    
    console.log(color(`✅ 版本号已更新: ${oldVersion} → ${newVersion}`, 'green'));
    return true;
  } catch (error) {
    console.error(color('❌ 更新版本号失败:', 'red'), error.message);
    return false;
  }
}

// 根据SemVer规则计算新版本
function calculateNewVersion(currentVersion, type) {
  const versionParts = currentVersion.split('.').map(Number);
  
  if (versionParts.length !== 3) {
    throw new Error(`无效的版本号格式: ${currentVersion}`);
  }
  
  let [major, minor, patch] = versionParts;
  
  switch (type) {
    case 'major':
      major += 1;
      minor = 0;
      patch = 0;
      break;
    case 'minor':
      minor += 1;
      patch = 0;
      break;
    case 'patch':
      patch += 1;
      break;
    default:
      throw new Error(`未知的版本更新类型: ${type}`);
  }
  
  return `${major}.${minor}.${patch}`;
}

// 验证版本号格式
function isValidVersion(version) {
  const semverRegex = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;
  return semverRegex.test(version);
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showHelp();
    return;
  }
  
  const command = args[0].toLowerCase();
  
  switch (command) {
    case 'show': {
      const currentVersion = getCurrentVersion();
      console.log(color(`当前版本: ${currentVersion}`, 'green'));
      break;
    }
      
    case 'patch':
    case 'minor':
    case 'major': {
      try {
        const currentVersion = getCurrentVersion();
        const newVersion = calculateNewVersion(currentVersion, command);
        
        console.log(color(`\n🔄 正在更新${command}版本...`, 'blue'));
        console.log(`当前版本: ${color(currentVersion, 'yellow')}`);
        console.log(`新版本: ${color(newVersion, 'green')}`);
        
        if (updateVersion(newVersion)) {
          console.log(color(`\n📝 请手动提交更改:`, 'cyan'));
          console.log(`  git add package.json`);
          console.log(`  git commit -m "chore: bump version to ${newVersion}"`);
          console.log(color(`\n🏷️ 如需创建标签:`, 'cyan'));
          console.log(`  git tag -a v${newVersion} -m "Release version ${newVersion}"`);
        }
      } catch (error) {
        console.error(color('❌ 错误:', 'red'), error.message);
      }
      break;
    }
      
    case 'set': {
      if (args.length < 2) {
        console.error(color('错误: 请指定要设置的版本号', 'red'));
        console.log('用法: node scripts/update-version.js set <版本号>');
        process.exit(1);
      }
      
      const newVersion = args[1];
      
      if (!isValidVersion(newVersion)) {
        console.error(color(`错误: 无效的版本号格式 "${newVersion}"`, 'red'));
        console.log(color('版本号应遵循SemVer规范，例如: 1.0.0, 2.1.3, 3.0.0-beta.1', 'yellow'));
        process.exit(1);
      }
      
      const currentVersion = getCurrentVersion();
      
      console.log(color(`\n🔄 正在设置版本号...`, 'blue'));
      console.log(`当前版本: ${color(currentVersion, 'yellow')}`);
      console.log(`新版本: ${color(newVersion, 'green')}`);
      
      if (updateVersion(newVersion)) {
        console.log(color(`\n📝 请手动提交更改:`, 'cyan'));
        console.log(`  git add package.json`);
        console.log(`  git commit -m "chore: set version to ${newVersion}"`);
      }
      break;
    }
      
    case 'help':
    case '--help':
    case '-h':
      showHelp();
      break;
      
    default:
      console.error(color(`错误: 未知命令 "${command}"`, 'red'));
      showHelp();
      process.exit(1);
  }
}

// 执行
if (require.main === module) {
  main();
}
