<template>
  <div class="device-info">
    <div class="device-card">
      <div class="device-icon">
        <i :class="deviceIcon"></i>
      </div>
      
      <div class="device-details">
        <h2>{{ deviceData.deviceType }}</h2>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="label">操作系统:</span>
            <span class="value">{{ deviceData.os }} {{ deviceData.osVersion }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">浏览器:</span>
            <span class="value">{{ deviceData.browser }} {{ deviceData.browserVersion }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">设备型号:</span>
            <span class="value">{{ deviceData.deviceModel }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">设备类型:</span>
            <span class="value">
              <span v-if="deviceData.isPhone">手机</span>
              <span v-else-if="deviceData.isTablet">平板</span>
              <span v-else>桌面设备</span>
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="user-agent">
      <h3>User Agent</h3>
      <p>{{ deviceData.userAgent }}</p>
    </div>
    
    <div class="simulate-device">
      <h3>模拟设备</h3>
      <div class="simulate-buttons">
        <button @click="simulateDevice('iPhone')">iPhone</button>
        <button @click="simulateDevice('iPad')">iPad</button>
        <button @click="simulateDevice('Android')">Android</button>
        <button @click="simulateDevice('Desktop')">桌面设备</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeviceInfo',
  data() {
    return {
      deviceData: this.$detectDevice()
    };
  },
  computed: {
    deviceIcon() {
      if (this.deviceData.isPhone) return 'fas fa-mobile-alt';
      if (this.deviceData.isTablet) return 'fas fa-tablet-alt';
      return 'fas fa-desktop';
    }
  },
  methods: {
    simulateDevice(type) {
      let userAgent = '';
      
      switch(type) {
        case 'iPhone':
          userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1';
          break;
        case 'iPad':
          userAgent = 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1';
          break;
        case 'Android':
          userAgent = 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36';
          break;
        default:
          userAgent = navigator.userAgent;
      }
      
      const md = new MobileDetect(userAgent);
      this.deviceData = {
        userAgent,
        isMobile: md.mobile() !== null,
        isTablet: md.tablet() !== null,
        isPhone: md.phone() !== null,
        os: md.os(),
        osVersion: md.version(md.os()),
        browser: md.userAgent(),
        browserVersion: md.versionStr(md.userAgent()),
        deviceType: md.mobile() || md.tablet() || 'Desktop',
        deviceModel: md.mobile() || md.tablet() || 'Desktop Computer'
      };
    }
  }
};
</script>

<style scoped>
.device-info {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.device-card {
  display: flex;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 30px;
}

.device-icon {
  width: 30%;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.device-icon i {
  font-size: 5rem;
  color: white;
}

.device-details {
  width: 70%;
  padding: 30px;
}

.device-details h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.8rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-weight: 600;
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.value {
  color: #333;
  font-size: 1.1rem;
}

.user-agent {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.user-agent h3 {
  color: #333;
  margin-bottom: 10px;
}

.user-agent p {
  background: white;
  padding: 15px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.9rem;
  overflow-x: auto;
}

.simulate-device {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.simulate-device h3 {
  color: #333;
  margin-bottom: 15px;
}

.simulate-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

button {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(38, 117, 252, 0.4);
}

button:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .device-card {
    flex-direction: column;
  }
  
  .device-icon, .device-details {
    width: 100%;
  }
  
  .device-icon {
    padding: 20px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>