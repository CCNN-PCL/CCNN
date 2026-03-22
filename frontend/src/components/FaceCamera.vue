<template>
  <div class="camera-wrapper" v-show="!captured">
    <!-- 视频流显示 -->
    <video ref="video" autoplay muted playsinline class="camera-view" v-show="!captured"></video>
    <!-- 隐藏的画布用于捕获图像 -->、
    <canvas ref="canvas" class="d-none"></canvas>
    <!-- 遮罩层（仅在未捕获图像时显示） -->
    <div class="camera-overlay" v-if="!captured">
      <!-- 半透明遮罩（中间透明区域） -->
      <div class="mask"></div>
      <!-- 圆形扫描区域 -->
      <div class="scan-area">
        <!-- 扫描动画 -->
        <!-- <div class="scan-line"></div> -->
      </div>
      <!-- 引导文字 -->
      <div class="scan-guide">请将面部置于圆形区域内</div>
    </div>
    <div v-if="captured" class="preview-result">
      
      <button @click="retake" class="btn btn-sm btn-secondary retake-btn">
        <i class="fas fa-redo"></i> 重新拍摄
      </button>
    </div>
    
    <div v-else class="camera-controls">
      <button @click="capture" class="btn btn-primary capture-btn">
        <i class="fas fa-camera"></i> 拍摄照片
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'CameraComponent',
  emits: ['captured', 'preview', 'retake', 'error'],
  setup(props, { emit }) {
    const video = ref(null)
    const canvas = ref(null)
    const stream = ref(null)
    const captured = ref(false)
    const previewImage = ref(null)
    
    const startCamera = async () => {
      try {
        stopCamera()
        
        // 请求摄像头权限
        const mediaStream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 640 },
            height: { ideal: 380 },
            facingMode: 'user'
          } 
        })
        
        stream.value = mediaStream
        video.value.srcObject = mediaStream
      } catch (error) {
        emit('error', '无法访问摄像头: ' + error.message)
      }
    }
    
    const stopCamera = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
      }
    }
    
    const capture = () => {
      const videoEl = video.value
      const canvasEl = canvas.value
      const context = canvasEl.getContext('2d')
      
      canvasEl.width = videoEl.videoWidth
      canvasEl.height = videoEl.videoHeight
      context.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height)
      
      // 获取Base64编码（不含前缀）
      const base64Data = canvasEl.toDataURL('image/jpeg').split(',')[1]
      
      // 显示预览
      previewImage.value = `data:image/jpeg;base64,${base64Data}`
      captured.value = true
      
      // 发送事件
      emit('captured', base64Data)
      emit('preview', previewImage.value)
      
      // 关闭摄像头
      stopCamera()
    }
    
    const retake = () => {
      captured.value = false
      previewImage.value = null
      startCamera()
      emit('retake')
    }

    onMounted(() => {
      startCamera()
    })

    onUnmounted(() => {
      stopCamera()
    })

    return {
      video,
      canvas,
      captured,
      previewImage,
      capture,
      retake
    }
  }
}
</script>

<style scoped>
.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 遮罩层 - 中间透明圆形区域 */
.mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    ellipse 100px 150px at center, /* 匹配扫描区域尺寸 */
    transparent 0%,
    transparent 100%, 
    rgba(0, 0, 0, 0.8) 100%
  );
}
.mask::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* 创建椭圆形状的掩模 */
  -webkit-mask: radial-gradient(
    ellipse 100px 150px at center,
    transparent 0%,
    transparent 100%, 
    black 100%
  );
  mask: radial-gradient(
    ellipse 100px 150px at center,
    transparent 0%,
    transparent 100%, 
    black 100%
  );
  /* 只模糊外部区域 */
  backdrop-filter: blur(8px);
  pointer-events: none;
}
/* 扫描区域 */
.scan-area {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 300px;
  border-radius: 50%;
  border: 3px solid rgba(76, 201, 240, 0.8);
  box-shadow: 0 0 15px rgba(76, 201, 240, 0.5);
  overflow: hidden;
}

/* 扫描线动画 */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(
    to bottom,
    rgba(76, 201, 240, 0),
    rgba(76, 201, 240, 0.8),
    rgba(76, 201, 240, 0)
  );
  animation: scan 2.5s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(500px); }
}

/* 引导文字 */
.scan-guide {
  position: absolute;
  top: 0%;
  left: 0;
  right: 0;
  text-align: center;
  color: white;
  font-weight: 500;
  font-size: 1.1rem;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.7);
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  max-width: 300px;
  margin: 0 auto;
}
.camera-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.camera-view {
  width: 100%;
  height: auto;
  display: block;
}

.preview-result {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
}

.retake-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.camera-controls {
  position: absolute;
  bottom: 0px;
  left: 0;
  right: 0;
  text-align: center;
}

.capture-btn {
  padding: 10px 20px;
  font-size: 1.1rem;
}

.d-none {
  display: none;
}
</style>