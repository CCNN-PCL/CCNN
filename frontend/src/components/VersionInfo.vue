<template>
  <div class="version-info" v-if="showVersion">
    <div class="version-badge">
      <span class="version-label">v{{ version }}</span>
      <span class="build-time" v-if="buildTime">
        • {{ formattedBuildTime }}
      </span>
    </div>
    <div class="version-details" v-if="showDetails">
      <p><strong>应用名称:</strong> {{ appName }}</p>
      <p><strong>版本:</strong> {{ version }}</p>
      <p><strong>构建时间:</strong> {{ buildTime }}</p>
      <p><strong>构建时间戳:</strong> {{ buildTimestamp }}</p>
    </div>
  </div>
</template>

<script>
// 导入自动生成的版本信息
import { versionInfo } from '../version.js';

export default {
  name: 'VersionInfo',
  props: {
    showDetails: {
      type: Boolean,
      default: false
    },
    showAlways: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      version: versionInfo.version || 'unknown',
      appName: versionInfo.name || 'unknown',
      buildTime: versionInfo.buildTime || null,
      buildTimestamp: versionInfo.buildTimestamp || null,
      showVersion: true
    };
  },
  computed: {
    formattedBuildTime() {
      if (!this.buildTime) return '';
      
      try {
        const date = new Date(this.buildTime);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch (error) {
        return this.buildTime;
      }
    }
  },
  mounted() {
    // 如果不是始终显示，则在开发环境下隐藏
    if (!this.showAlways && process.env.NODE_ENV === 'development') {
      this.showVersion = false;
    }
    
    // 将版本信息挂载到全局，方便调试
    if (process.env.NODE_ENV === 'development') {
      window.__APP_VERSION__ = versionInfo;
      console.log('📦 App Version Info:', versionInfo);
    }
  }
};
</script>

<style scoped>
.version-info {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background-color: #f0f0f0;
  border-radius: 12px;
  color: #666;
  border: 1px solid #ddd;
}

.version-label {
  font-weight: bold;
  color: #333;
}

.build-time {
  margin-left: 4px;
  color: #888;
  font-size: 11px;
}

.version-details {
  margin-top: 8px;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #eee;
}

.version-details p {
  margin: 4px 0;
  font-size: 11px;
  color: #555;
}

.version-details strong {
  color: #333;
  margin-right: 4px;
}
</style>
