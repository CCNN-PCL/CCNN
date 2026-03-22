#!/usr/bin/env node

/**
 * 版本信息注入脚本
 * 在构建时将版本信息注入到应用中
 */

const fs = require('fs');
const path = require('path');

// 获取版本信息
function getVersionInfo() {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    return {
      version: packageData.version,
      name: packageData.name,
      buildTime: new Date().toISOString(),
      buildTimestamp: Date.now()
    };
  } catch (error) {
    console.error('Error reading package.json:', error.message);
    return {
      version: 'unknown',
      name: 'unknown',
      buildTime: new Date().toISOString(),
      buildTimestamp: Date.now()
    };
  }
}

// 创建版本信息文件
function createVersionFile() {
  const versionInfo = getVersionInfo();
  const versionJson = JSON.stringify(versionInfo, null, 2);
  
  // 创建dist目录下的版本文件
  const distDir = path.join(__dirname, '..', 'dist');
  if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
  }
  
  const versionFilePath = path.join(distDir, 'version.json');
  fs.writeFileSync(versionFilePath, versionJson, 'utf8');
  
  console.log(`✅ Version info written to: ${versionFilePath}`);
  console.log(`📦 Version: ${versionInfo.version}`);
  console.log(`🕐 Build time: ${versionInfo.buildTime}`);
  
  return versionInfo;
}

// 创建版本信息JS文件，供前端使用
function createVersionJsFile() {
  const versionInfo = getVersionInfo();
  
  // 创建src目录下的版本信息文件
  const srcDir = path.join(__dirname, '..', 'src');
  const versionJsContent = `// Auto-generated version info
// DO NOT EDIT - Generated during build process

export const versionInfo = ${JSON.stringify(versionInfo, null, 2)};

export const VERSION = '${versionInfo.version}';
export const APP_NAME = '${versionInfo.name}';
export const BUILD_TIME = '${versionInfo.buildTime}';
export const BUILD_TIMESTAMP = ${versionInfo.buildTimestamp};

export default {
  version: VERSION,
  name: APP_NAME,
  buildTime: BUILD_TIME,
  buildTimestamp: BUILD_TIMESTAMP,
  ...versionInfo
};
`;

  const versionJsPath = path.join(srcDir, 'version.js');
  fs.writeFileSync(versionJsPath, versionJsContent, 'utf8');
  
  console.log(`✅ Version JS file created: ${versionJsPath}`);
  
  return versionInfo;
}

// 更新index.html，注入版本信息
function updateIndexHtml() {
  try {
    const indexPath = path.join(__dirname, '..', 'public', 'index.html');
    let htmlContent = fs.readFileSync(indexPath, 'utf8');
    
    const versionInfo = getVersionInfo();
    
    // 在head中添加版本meta标签
    const versionMeta = `\n    <!-- Version Information -->
    <meta name="version" content="${versionInfo.version}">
    <meta name="build-time" content="${versionInfo.buildTime}">`;
    
    // 在</head>前插入版本信息
    if (htmlContent.includes('</head>')) {
      htmlContent = htmlContent.replace('</head>', `${versionMeta}\n  </head>`);
      
      // 写入更新后的文件
      fs.writeFileSync(indexPath, htmlContent, 'utf8');
      console.log(`✅ Version info injected into index.html`);
    } else {
      console.log('⚠️  Could not find </head> tag in index.html');
    }
  } catch (error) {
    console.error('Error updating index.html:', error.message);
  }
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'all';
  
  console.log('🔧 Injecting version information...');
  
  switch (command) {
    case 'json':
      createVersionFile();
      break;
    case 'js':
      createVersionJsFile();
      break;
    case 'html':
      updateIndexHtml();
      break;
    case 'all':
    default:
      createVersionFile();
      createVersionJsFile();
      updateIndexHtml();
      break;
  }
  
  console.log('✅ Version injection completed');
}

// 执行
if (require.main === module) {
  main();
}
