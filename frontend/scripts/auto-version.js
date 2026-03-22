#!/usr/bin/env node

/**
 * 自动版本号生成脚本
 * 基于时间戳生成版本号，格式：YYYY.MM.DD.HHMM
 * 例如：2026.03.01.1415
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

// 生成基于时间戳的版本号
function generateTimestampVersion() {
  const now = new Date();
  
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  
  // 格式：YYYY.MM.DD.HHMM
  return `${year}.${month}.${day}.${hours}${minutes}`;
}

// 生成语义化版本号（基于提交次数）
function generateSemanticVersion(currentVersion) {
  try {
    const versionParts = currentVersion.split('.').map(Number);
    
    if (versionParts.length !== 3) {
      // 如果不是标准语义化版本，使用时间戳版本
      return generateTimestampVersion();
    }
    
    let [major, minor, patch] = versionParts;
    
    // 每次构建增加patch版本
    patch += 1;
    
    // 如果patch超过99，增加minor并重置patch
    if (patch > 99) {
      minor += 1;
      patch = 0;
    }
    
    // 如果minor超过99，增加major并重置minor
    if (minor > 99) {
      major += 1;
      minor = 0;
    }
    
    return `${major}.${minor}.${patch}`;
  } catch (error) {
    // 如果解析失败，使用时间戳版本
    return generateTimestampVersion();
  }
}

// 获取当前版本
function getCurrentVersion() {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    return packageData.version;
  } catch (error) {
    console.error(color('错误: 无法读取package.json', 'red'));
    return '0.0.0';
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
    return { success: true, oldVersion, newVersion };
  } catch (error) {
    console.error(color('❌ 更新版本号失败:', 'red'), error.message);
    return { success: false, error: error.message };
  }
}

// 显示帮助信息
function showHelp() {
  console.log(color('\n📦 自动版本号生成工具', 'cyan'));
  console.log(color('='.repeat(40), 'cyan'));
  console.log('用法: node scripts/auto-version.js [选项]');
  console.log('');
  console.log('选项:');
  console.log('  timestamp    使用时间戳版本 (YYYY.MM.DD.HHMM)');
  console.log('  semantic     使用语义化版本 (自动增加patch)');
  console.log('  show         显示当前版本');
  console.log('  help         显示帮助信息');
  console.log('');
  console.log('默认: 使用时间戳版本');
  console.log('');
  console.log('示例:');
  console.log('  node scripts/auto-version.js');
  console.log('  node scripts/auto-version.js timestamp');
  console.log('  node scripts/auto-version.js semantic');
  console.log('  node scripts/auto-version.js show');
  console.log('');
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'timestamp';
  
  switch (mode.toLowerCase()) {
    case 'show': {
      const currentVersion = getCurrentVersion();
      console.log(color(`当前版本: ${currentVersion}`, 'green'));
      break;
    }
      
    case 'timestamp': {
      const currentVersion = getCurrentVersion();
      const newVersion = generateTimestampVersion();
      
      console.log(color(`\n🔄 正在生成时间戳版本...`, 'blue'));
      console.log(`当前版本: ${color(currentVersion, 'yellow')}`);
      console.log(`新版本: ${color(newVersion, 'green')}`);
      console.log(color(`格式: 年.月.日.时分`, 'cyan'));
      
      const result = updateVersion(newVersion);
      if (result.success) {
        console.log(color(`\n📝 版本已自动更新，建议提交更改:`, 'cyan'));
        console.log(`  git add package.json`);
        console.log(`  git commit -m "chore: auto-bump version to ${newVersion}"`);
      }
      break;
    }
      
    case 'semantic': {
      const currentVersion = getCurrentVersion();
      const newVersion = generateSemanticVersion(currentVersion);
      
      console.log(color(`\n🔄 正在生成语义化版本...`, 'blue'));
      console.log(`当前版本: ${color(currentVersion, 'yellow')}`);
      console.log(`新版本: ${color(newVersion, 'green')}`);
      console.log(color(`规则: 自动增加patch版本号`, 'cyan'));
      
      const result = updateVersion(newVersion);
      if (result.success) {
        console.log(color(`\n📝 版本已自动更新，建议提交更改:`, 'cyan'));
        console.log(`  git add package.json`);
        console.log(`  git commit -m "chore: auto-bump version to ${newVersion}"`);
      }
      break;
    }
      
    case 'help':
    case '--help':
    case '-h':
      showHelp();
      break;
      
    default:
      console.error(color(`错误: 未知选项 "${mode}"`, 'red'));
      showHelp();
      process.exit(1);
  }
}

// 执行
if (require.main === module) {
  main();
}

// 导出函数供其他脚本使用
module.exports = {
  generateTimestampVersion,
  generateSemanticVersion,
  getCurrentVersion,
  updateVersion
};
