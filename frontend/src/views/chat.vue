<template>
  <div >
    <!-- 主界面 -->
    <div class="dashboard-container">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ 'sidebar-hidden': !sidebarVisible }">        
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
          <p style="margin: 0; color: #666; font-size: 20px;">当前登录用户</p>
          <h3 v-if="user.username" style="margin: 5px 0; color: #2196F3;">👤 {{ user.username }}<br>
            ⭐信任评分：{{ score }}</h3>
          <h3 v-else style="margin: 5px 0; color: #2196F3;">👤 未登录</h3>
        </div>
        <button class="btn-primary" style="width: 100%;" @click="handleLogout">
          退出登录
        </button>

      </div>
      <!-- 切换按钮（侧边栏显示时） -->
      <button class="toggle-btn toggle-btn-sidebar" @click="toggleSidebar">
          ◀
      </button>
      <!-- 主内容区域 -->
      <div class="main-content" :class="{ 'main-content-full': !sidebarVisible }">
        <!-- 切换按钮（侧边栏隐藏时） -->
        <button class="toggle-btn toggle-btn-chat" @click="toggleSidebar">
            ▶
        </button>
       
        <!-- 聊天区域 -->
        <div class="chat-container">
          <div class="messages-container" ref="messagesContainer">
            <div v-for="(message, index) in chatHistory" :key="index" class="message">
              <div v-if="message.role === 'user'" class="user-message">
                <div class="message-content">
                  <div class="message-timestamp">{{ message.timestamp }}</div>
                  <div class="message-text">{{ message.content }}</div>
                  <div v-if="message.images && message.images.length" class="message-images">
                    <div v-for="(img, imgIndex) in message.images" :key="imgIndex" class="message-image">
                      <img :src="img" alt="聊天图片">
                    </div>
                  </div>
                </div>
                <div class="message-avatar">👤</div>
              </div>
               <div v-else class="assistant-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                  <div class="message-timestamp">{{ message.timestamp }}</div>
                  <div class="message-text" v-html="message.content"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 聊天输入区域 -->
          <div class="chat-input-container">
            <div class="chat-input-wrapper">
              
              
              <div class="input-section">
                <div v-if="chatAttachments.length" class="attachments-preview">
                  <div v-for="(attachment, index) in chatAttachments" :key="index" class="attachment-item">
                    <div v-if="isImageFile(attachment)" class="attachment-image">
                      <img :src="attachment.preview" alt="附件预览">
                    </div>
                    <div v-else class="attachment-file">
                      📄 {{ attachment.file.name }}
                    </div>
                    <button class="remove-btn" @click="removeAttachment(index)">×</button>
                  </div>
                </div>
                
                <div class="input-wrapper">
                 <textarea
                    v-model="userInput"
                    placeholder="请输入健康问题..."
                    class="text-input auto-height"
                    rows="2"
                    @keydown.enter.prevent="sendMessage_by_erbsocket"
                  ></textarea>
                  <div class="upload-section">
                <div class="upload-btn" @click="triggerChatFileUpload" title="上传图片或文件">
                  📎
                </div>
                <input 
                  ref="chatFileInput"
                  type="file" 
                  multiple 
                  @change="handleChatFileUpload"
                  class="file-input"
                  style="display: none;" 

                />
              </div>
      
                  <button class="send-btn" @click="sendMessage_by_erbsocket" :disabled="!userInput || waiting">
                    发送
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 历史记录 -->
        <div v-if="showHistory" class="history-panel">
          <h3>📜 聊天历史记录</h3>
          <div v-for="(msg, index) in chatHistory" :key="index" class="history-message">
            <div v-if="msg.role === 'user'">
              <strong>👤 用户 ({{ msg.timestamp }}):</strong>
              <p>{{ msg.content }}</p>
              <div v-if="msg.images && msg.images.length" class="history-images">
                <div v-for="(img, imgIndex) in msg.images" :key="imgIndex" class="history-image">
                  <img :src="img" alt="历史图片">
                </div>
              </div>
            </div>
            <div v-else>
              <strong>🤖 智慧医疗 ({{ msg.timestamp }}):</strong>
              <p v-html="msg.content"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUpdated, onUnmounted, nextTick } from 'vue'
import axios from 'axios';
import { socketService } from '@/services/socketService'
import { computed } from 'vue'
import useDeviceDetect from '@/plugins/deviceDetect';
export default {
  name: 'App',
  
  setup() {
    // 登录状态
    const loggedIn = ref(false)
    const user = ref({})
    
    // 登录表单
    const activeTab = ref('login')
    const loginUsername = ref('')
    const loginPassword = ref('')
    const registerUsername = ref('')
    const registerPassword = ref('')
    const confirmPassword = ref('')
    const errorMessage = ref('')
    const doctorAvatar = ref("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjAiIGhlaWdodD0iMTIwIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IiNBMDg0RjEiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMSAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHptMC0xMmE0IDQgMCAwIDAgLTQgNCA0IDQgMCAwIDAgNCA0IDQgNCAwIDAgMCA0LTQgNCA0IDAgMCAwLTQtNG0wIDJhMiAyIDAgMCAxIDIgMiAyIDIgMCAwIDEtMiAyIDIgMiAwIDAgMS0yLTIgMiAyIDAgMCAxIDItMm0wIDZjLTEuMSAwLTIgLjktMiAydjJoNHYtMmMwLTEuMS0uOS0yLTItMnoiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjEwIiByPSIxIiBmaWxsPSIjRkZGRkZGIi8+PHBhdGggZmlsbD0iI0ZGRkZGRiIgZD0iTTExIDEyaDJ2NGgtMnoiLz48L3N2Zz4=")
    
    // 医疗上传
    const selectedHospital = ref('')
    const imageType = ref('')
    const examinationDate = ref(new Date().toISOString().split('T')[0]);
    const description = ref('')
    const uploadedImage = ref(null)
    const uploadedFile = ref(null)
    const hasImages = ref(false)
    const hasMedicalRecords = ref(false)
    const fileInput = ref(null)
    const dragOver = ref(false)
    // 计算属性保持响应式
    // const userName = computed(() => authStore.user?.username || '未登录')
    // const score = computed(() => authStore.level)
    const score = ref({})

    // 聊天
    const userInput = ref('')
    const userInput_copy = ref('')
    const chatHistory = ref([])
    const showHistory = ref(false)
    const messagesContainer = ref(null)
    const chatFileInput = ref(null)
    const chatAttachments = ref([])
    const waiting = ref(false)   // 是否正在等待回答

    
  

    // 侧边栏状态
    const sidebarVisible = ref(true);
    
    // 切换侧边栏显示/隐藏
    const toggleSidebar = () => {
        sidebarVisible.value = !sidebarVisible.value;
    };


    
    const handleLogout = () => {
      loggedIn.value = false
      user.value = {}
      localStorage.removeItem('authState')
      // window.location.href = process.env.LOUGUT_URL
      window.location.href = '/logout'

    }
    

    
 
    const triggerChatFileUpload = () => {
      if (chatFileInput.value) {
        chatFileInput.value.click()
      }
    }
    
    const handleChatFileUpload = (event) => {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        // 检查文件大小限制 (20MB)
        const maxSize = 20 * 1024 * 1024
        if (file.size > maxSize) {
          alert(`文件 ${file.name} 大小超过限制（最大20MB）`)
          continue
        }
        
        // 检查文件类型
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
        if (!allowedTypes.includes(file.type)) {
          alert(`不支持的文件类型 ${file.type}。请选择 JPG、JPEG、PNG 或 PDF 文件`)
          continue
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          chatAttachments.value.push({
            file: file,
            preview: e.target.result,
            type: file.type
          })
        }
        reader.readAsDataURL(file)
      }
      
      // 清空input，允许重复选择相同文件
      event.target.value = ''
    }
    
    const isImageFile = (attachment) => {
      return attachment.type.startsWith('image/')
    }
    
    const removeAttachment = (index) => {
      chatAttachments.value.splice(index, 1)
    }
    
    // 聊天方法
    const sendMessage = async () => {
      if (!userInput.value.trim()) return
      const timestamp = new Date().toLocaleString('zh-CN')
      // 处理附件
      const imageUrls = []
      for (const attachment of chatAttachments.value) {
        if (isImageFile(attachment)) {
          imageUrls.push(attachment.preview)
        }
      }       
        // 添加用户消息
      const userMessage = {
        role: 'user',
        content: userInput.value,
        timestamp: timestamp,
        images: imageUrls
      }
      chatHistory.value.push(userMessage)
      try {
        // 准备发送的数据[2,5](@ref)
        const messageData = {
          user_id: user.value.username, // 替换为实际用户名
          user_input: userInput.value.trim()
          //timestamp: timestamp,
          // attachments: chatAttachments.value
          //imageUrls: imageUrls
        };
        console.log(messageData)
        userInput.value = ''
        chatAttachments.value = []
        // 发送POST请求到后端5000端口[1,3](@ref)
        axios.post(
          // `${process.env.USER_AGENT}/api/v1/chat/send`,
          '/api/v1/chat/send',
          messageData,
          {timeout: 120000})
        .then(result => {
          const response = result.data.response
          console.log('成功接收响应:', result.data)
          const aiResponse = {
            role: 'assistant',
            content: response,
            timestamp: new Date().toLocaleString('zh-CN')
          }
          chatHistory.value.push(aiResponse)
          saveMessages()

          if((result.data.metadata?.redirect ?? 0) == 1){
            window.open(process.env.MEDICAL_APP + result.data.metadata.redirect_url, '_blank')
          }

        })
        .catch(error => {
          console.error('请求错误:', error)
          if (error.response) {
            alert(`请求失败: ${error.response.status} - ${error.response.data.detail}`)
          } else {
            alert('网络错误，请稍后重试')
          }
        })
        .finally(() => {
          console.log("")
        })
            
      } catch (error) {
        // 错误处理[1,5](@ref)
        console.error('发送消息失败:', error);
      } 
      
    }

    const sendMessage_by_erbsocket = () => {
      if (!userInput.value.trim() || !user.value?.username) return
      const timestamp = new Date().toLocaleString('zh-CN')
      // 处理附件
      const imageUrls = []
      for (const attachment of chatAttachments.value) {
        if (isImageFile(attachment)) {
          imageUrls.push(attachment.preview)
        }
      }       
        // 添加用户消息
      const userMessage = {
        role: 'user',
        content: userInput.value,
        timestamp: timestamp,
        images: imageUrls
      }
      userInput_copy.value = userInput.value
      chatHistory.value.push(userMessage)
      
      // 准备发送的数据[2,5](@ref)
      const messageData = {
        user_id: user.value.userid,//之前时username
        username: user.value.username, // 替换为实际用户名username
        user_input: userInput.value.trim(),
        timestamp: timestamp,
        imageUrls: imageUrls
      };
      // 清空输入框和附件
      userInput.value = ''
      chatAttachments.value = []
      scrollToBottom()
      axios.post(
            // `${process.env.USER_AGENT}/api/v1/chat/send`,
            '/api/v1/chat/send',
            messageData).then()
      // 通过WebSocket发送消息
      const success = socketService.sendMessage(messageData)
  
      if (!success) {
        const errorMessage = {
          role: 'system',
          content: '发送失败：WebSocket未连接',
          timestamp: new Date().toLocaleString('zh-CN'),
          isError: true
        }
        chatHistory.value.push(errorMessage)
        scrollToBottom()
      }

    }  

    const initSocket = () => {
      socketService.connect()
      // 注册事件监听
      socketService.on('connected', () => {
        // connected.value = true
        console.log('Connected to server')
      })
      
      socketService.on('disconnected', () => {
        // connected.value = false
        console.log('Disconnected from server')
      })
      
      socketService.on('server_response', (data) => {
        console.log('📨 收到服务器响应:', data)

        // 根据不同的响应类型处理
        if (data.status === 'ok' || data.event === 'acknowledge') {
          console.log('✅ 服务器确认收到请求:', data.response)
          // 可以在这里显示处理中的状态
          const responseData = data.data || data
          const aiResponse = {
            role: 'assistant',
            content: responseData.response,
            agent_name: responseData.agent_name || 'AI助手',
            timestamp: new Date().toLocaleString('zh-CN'),
            metadata: responseData.metadata || {}
          }
          
          // 添加到聊天历史
          chatHistory.value.push(aiResponse)
          saveMessages()
          console.log('🤖 AI回复已添加到聊天历史:', aiResponse)

          if(data.metadata.redirect == 1){
            const params = new URLSearchParams({
              // user_id: user.value.userid,
              // username: user.value.username,
              user_input: userInput_copy.value.trim()
            });
            console.log("=======用户输入=========", user.value.username,userInput_copy.value)
              setTimeout(() => {window.open(`${process.env.MEDICAL_FRONTEND}/?${params.toString()}`, '_blank');}, 1500)
              // setTimeout(() => {window.open(`/medical_frontend/?${params.toString()}`, '_blank');}, 2000)

          }
          
          // 滚动到底部
          scrollToBottom()
          
        } 
        else if (data.response || data.event === 'chat_response') {
        }
      })
      
      socketService.on('error', (data) => {
        console.error('服务器错误:', data)       
        const errorMessage = {
          role: 'system',
          content: `错误: ${data.message || '请求失败'}`,
          timestamp: new Date().toLocaleString('zh-CN'),
          isError: true
        }
        
        chatHistory.value.push(errorMessage)
        scrollToBottom()
      })
    }

    const saveMessages = () => {
      localStorage.setItem(`chat_history_${user.value.username}`, JSON.stringify(chatHistory.value))
    }
    //让聊天区域立刻滚到最底部，确保用户总能看到最新一条消息。
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    // 其他方法
    const toggleHistory = () => {
      showHistory.value = !showHistory.value
    }
    
    const clearChat = () => {
      if (confirm('确定要清空所有聊天记录吗？')) {
        localStorage.removeItem(`chat_history_${user.value.username}`)
        chatHistory.value = []
      }
    }
    
    const checkConsistency = () => {
      alert('数据一致性检查功能')
    }
    
    const exportChat = () => {
      alert('导出聊天记录功能')
    }
    

    onMounted(() => {
        // 检查本地存储中是否有登录状态
        /* 1. 先删掉旧记录 */
        // 前端
        console.log("评分",score.value)
        fetch(
          // process.env.API_ME, {
          '/api/me',{
          method: 'GET',
          credentials: 'include'      // 关键
        }).then(r => r.json()).then(data => {
            console.log(data)
        if (data?.username){
          user.value = {                     // 整体赋值，保持响应式
            username: data.username,
            userid: data.userid || ''
            }
          } 
          score.value = data.trustscore
        });
        if (user.value) {
            localStorage.removeItem(`chat_history_${user.value.username}`)
        }
        const savedState = localStorage.getItem('authState')
        if (savedState) {
            const state = JSON.parse(savedState)
            loggedIn.value = state.loggedIn
            user.value = state.user
        }

        // 从本地存储加载聊天历史
        if (user.value) {
            const savedHistory = localStorage.getItem(`ier_agnet_chat_history_${user.value.username}`)
            if (savedHistory) {
            chatHistory.value = JSON.parse(savedHistory)
            }
        }
        // initSpeechRecognition()
        scrollToBottom()
        initSocket()
        startPolling()
    })
    // 请求数据的方法
    const { deviceInfo } = useDeviceDetect();

    const keep_auth = async () => {
      try {
        // 替换为你的实际API端点
        const response = await axios.post(
          // process.env.KEEP_AUTH, 
          '/api/keep-auth',
          {
          deviceInfo: deviceInfo.value
          }
        )
        score.value = response.data.trustscore
        if (score.value < 0.4) {
          handleLogout()
        }
      } catch (error) {
        console.error('请求失败:', error)
        // 可以添加用户提示，如使用Element Plus的ElMessage
      }
    }

    let pollTimer = null
    const POLL_INTERVAL = 10 * 60 * 100 // 1分钟，以毫秒为单位

    // 开始轮询
    const startPolling = () => {
      // 先清除可能存在的定时器
      stopPolling()
      // 立即请求一次，然后开始轮询
      keep_auth()
      pollTimer = setInterval(keep_auth, POLL_INTERVAL)
    }

    // 停止轮询
    const stopPolling = () => {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
    }
    onUpdated(() => {
      scrollToBottom()
    })

    onUnmounted(() => {
      socketService.disconnect()
      stopPolling()
    })

    // 暴露给模板
    return {
      // 状态
      loggedIn,
      user,
      activeTab,
      loginUsername,
      loginPassword,
      registerUsername,
      registerPassword,
      confirmPassword,
      errorMessage,
      doctorAvatar,
      selectedHospital,
      imageType,
      examinationDate,
      description,
      uploadedImage,
      uploadedFile,
      hasImages,
      hasMedicalRecords,
      fileInput,
      dragOver,
      userInput,
      chatHistory,
      showHistory,
      messagesContainer,
      chatFileInput,
      chatAttachments,  
      sidebarVisible,
      waiting,
      score,
      // 方法
      handleLogout,
      triggerChatFileUpload,
      handleChatFileUpload,
      isImageFile,
      removeAttachment,
      sendMessage,
      toggleHistory,
      clearChat,
      checkConsistency,
      exportChat,
      initSocket,
      // 您的所有状态和方法
      toggleSidebar,
      sendMessage_by_erbsocket,
      keep_auth,
      startPolling,
      stopPolling

    }
  }
}
</script>

<style scoped>
/* 主题颜色 */
:root {
  --primary-color: #2196F3;
  --secondary-color: #64B5F6;
  --background-color: #F5F9FF;
  --transition-duration: 0.3s;
  --transition-timing: ease;
}

/* 整体背景 */
body {
  background-color: var(--background-color);
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 标题样式 */
h1 {
  color: var(--primary-color) !important;
  font-weight: 600 !important;
}

/* 按钮样式 */
.btn-primary {
  background-color:  #2196F3;
  color: white;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  border: none;
  transition: all 0.3s;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #64B5F6;
  transform: translateY(-2px);
}


.login-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  width: 450px;
  text-align: center;
}

.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  border: 3px solid #A084F1;
  box-shadow: 0 0 20px rgba(160, 132, 241, 0.3);
}

.login-title {
  color: white;
  font-size: 32px;
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  margin-bottom: 30px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 5px;
}

.tab {
  flex: 1;
  padding: 15px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.tab.active {
  background: rgba(160, 132, 241, 0.2);
  color: #E0D5FF;
}

.input-field {
  font-size: 28px;
  padding: 25px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(160, 132, 241, 0.3);
  border-radius: 12px;
  color: #FFFFFF;
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 20px;
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-size: 26px;
}

/* 主界面样式 */
.dashboard-container {
  display: flex;
  height: 80vh;
}

.sidebar {
  width: 300px;
  background-color: white;
  border-right: 1px solid #E0E0E0;
  padding: 20px;
  overflow: auto;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  transition: all 0.3s ease;
}
.sidebar::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */

}
.form-control {
  box-sizing: border-box;
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
  border: 1px solid #ddd; /* 确保边框一致 */
  font-family: inherit; /* 继承父元素的字体 */
  font-size: 14px; /* 统一字体大小 */
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.messages-container {
  /* flex: 1; */
  overflow-y: auto;
  padding: 20px;
}

.chat-input-container {
  border-top: none;
  padding: 10px 20px 20px;
  background-color: transparent; /* ✅ 与背景融合 */
  display: flex;
  justify-content: center;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.message-input {
  flex: 1;
  padding: 15px;
  border-radius: 20px;
  border: 1px solid #ddd;
}

.send-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0 20px;
  cursor: pointer;
}

.send-button:hover {
  background-color: var(--secondary-color);
}

.chat-message {
  margin-bottom: 15px;
}

.user-message, .assistant-message {
  display: flex;
  gap: 10px;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.user-message .message-avatar {
  background-color: #E3F2FD;
}

.assistant-message .message-avatar {
  background-color: #E8F5E9;
}

.message-content {
  max-width: 70%;
}

.user-message .message-content {
  background-color: #E3F2FD;
  border-radius: 18px 18px 5px 18px;
  padding: 10px 15px;
}

.assistant-message .message-content {
  background-color: #E8F5E9;
  border-radius: 18px 18px 18px 5px;
  padding: 10px 15px;
}

.message-timestamp {
  font-size: 0.8em;
  color: #666;
  margin-bottom: 5px;
  font-size: 13px;      /* 原12px → 13px */
    margin-bottom: 6px;   /* 与正文拉开一点 */
}

.message-text {
  color: #333;
      font-size: 18px;      /* 原≈14px → 17px */
    line-height: 1.65;    /* 宽松行距 */
    letter-spacing: 0.2px;
}

.chat-history {
  margin-top: 18px;
  padding: 20px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.divider {
  border-top: 1px solid #E0E0E0;
  margin: 20px 0;
}

.metric-card {
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* 添加上传区域样式 */
.upload-container {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #2196F3;
  background-color: #f5f9ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-text {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.upload-hint {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.browse-btn {
  background-color: transparent;
  color: #2196F3;
  border: 1px solid #2196F3;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.browse-btn:hover {
  background-color: #2196F3;
  color: white;
}
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-secondary {
  background-color: #f1f1f1;
  color: #333;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
}



.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  margin-bottom: 15px;
}

.user-message, .assistant-message {
  display: flex;
  gap: 10px;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e3f2fd;
}

.assistant-message .message-avatar {
  background-color: #e8f5e9;
}

.message-content {
  max-width: 70%;
  background-color: #f1f1f1;
  border-radius: 18px;
  padding: 10px 15px;
}

.user-message .message-content {
  background-color: #e3f2fd;
  border-radius: 18px 18px 5px 18px;
}

.assistant-message .message-content {
  background-color: #e8f5e9;
  border-radius: 18px 18px 18px 5px;
}

.message-timestamp {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}



.message-images {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.message-image img {
  max-width: 200px;
  border-radius: 8px;
}


.chat-input-wrapper {
  max-width: 70%;
  width: 100%;
  background-color: #ffffff;
  border-radius: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 10px 14px;
  border: 1px solid  #d0e3f0; /* ✅ 默认透明边框 */
  transition: border-color 0.3s ease;
}

.chat-input-wrapper:hover {
  border-color: #2196F3; /* ✅ 悬停时加边框 */
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-btn {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-bottom: 5px;
}

.upload-label {
  font-size: 12px;
  color: #666;
}

.input-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.attachments-preview {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.attachment-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

.attachment-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attachment-file {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f1f1f1;
}

.remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.text-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 18px;
  padding: 8px 12px;
  background: transparent;
}

.send-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  cursor: pointer;

  font-size: 17px;          
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 历史记录面板 */
.history-panel {
  overflow-y: auto;
  padding: 20px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.history-message {
  margin-bottom: 15px;
}

.history-images {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.history-image img {
  max-width: 150px;
  border-radius: 8px;
}
/* 切换按钮样式 */
.toggle-btn {
    transition: all 0.3s ease;
    /* transition: all var(--transition-duration) var(--transition-timing); */
    position: absolute;
    top: 110px;
    width: 24px;
    height: 48px;
    background-color: #2196F3;
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 200;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.text-input.auto-height {
  /* 基础外观 */
  font-size: 17px;
  line-height: 1.6;               /* 1 行 ≈ 25 px */
  padding: 12px 18px;
  /* border: 1px solid #d0e3f0; */
  border-radius: 20px;
  resize: none;                /* 禁止拖动 避免出现右下角的小拖把手柄*/
  outline: none;
  overflow-y: hidden;             /* 先隐藏滚动条 */
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  background: transparent;
  transition: border-color 0.3s ease;
}

/* 计算：4 行 + 上下 padding ≈ 4*25 + 24 = 124 px */
.text-input.auto-height {
  max-height: 124px !important;   /* 到 5 行出现滚动条 */
  overflow-y: auto !important;    /* 超过时自动滚动 */
}
.toggle-btn:hover {
    background-color: #1976D2;
    transform : scale(1.05);

}

.toggle-btn-sidebar {
    left: 340px;
    top: 45%;
    border-radius: 0 4px 4px 0;

}

.toggle-btn-chat {
    left: 0;
    top: 45%;
    border-radius: 0 4px 4px 0;
    display: none;
    transform: translateX(-10px);
    opacity: 0;

}

/* 侧边栏隐藏时的状态 */
.sidebar-hidden {
  /* transition: all 0.3s ease; */
    opacity: 0;
    width: 0;
    padding: 0;
    border: none;
    overflow: hidden;
}

.main-content-full {
    margin-left: 0;
    width: 100%;
}

.sidebar-hidden + .toggle-btn-sidebar {
    opacity: 0;
    visibility: hidden;
    transform: translateX(-10px);
}

.sidebar-hidden ~ .main-content .toggle-btn-chat {
    display: flex;
    opacity: 1;
    visibility: visible;
    transform: translateX(0);
}
.waiting-dots {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  height: 1em;
}
.waiting-dots span {
  width: 8px;
  height: 8px;
  background: #2196F3;
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}
.waiting-dots span:nth-child(2) { animation-delay: 0.2s; }
.waiting-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}
.bottom-hint {
  text-align: center;
  font-size: 13px;
  color: #999;
  margin-top: 8px;   /* 与输入框距离 */
  user-select: none;
}
.detail-wrapper {
  margin-top: 10px;
}
/* 展开详情：浅灰背景 + 灰色文字 */
.detail-box {
  color: #999 !important;        /* 灰色文字 */
  padding: 15px;
  border-radius: 10px;
  font-size: 17px;
  line-height: 1.6;
}
.expand-btn {
  background: none;
  border: none;
  color: #9e9e9e;          /* 默认浅灰 */
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s ease;
}

.expand-btn:hover {
  color: #616161;          /* 悬浮深灰 */
}
</style>
