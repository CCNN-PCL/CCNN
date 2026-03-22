import { ref } from 'vue';
import { UAParser } from 'ua-parser-js';

export default function useDeviceInfo() {
  const deviceInfo = ref({});
   // 获取屏幕分辨率
  // 获取物理分辨率（实际像素）
  const physicalWidth = window.screen.width * window.devicePixelRatio;
  const physicalHeight = window.screen.height * window.devicePixelRatio;
  
  // 获取设备像素比
  const pixelRatio = window.devicePixelRatio || 1;
  const parser = new UAParser();
  const result = parser.getResult();
  // console.log(parser.getResult());
  // console.log(physicalHeight, physicalWidth, pixelRatio);
  deviceInfo.value = {
    os: result.os.name || 'Unknown',
    osVersion: result.os.version || 'Unknown',
    browser: result.browser.name || 'Unknown',
    browserVersion: result.browser.version || 'Unknown',
    device: result.device || 'Unknown',
    deviceType: result.device.type || 'desktop',
    cpu: result.cpu.architecture || 'Unknown',
    userAgent: result.ua,
    resolution: `${physicalWidth}×${physicalHeight}`,
  };

  return {
    deviceInfo
  };
}