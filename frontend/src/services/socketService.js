// src/services/socketService.js
import { io } from 'socket.io-client'

class SocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.eventCallbacks = new Map()
    this.eventListeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  // connect() {
  //   if (this.socket) return

  //   const serverUrl = 'http://localhost:5050/api/v1/chat/ws/send'//import.meta.env.VITE_SOCKET_URL || 
    
  //   this.socket = io(serverUrl, {
  //     transports: ['websocket', 'polling']
  //   })

  //   // 连接事件处理
  //   this.socket.on('connect', () => {
  //     console.log('Socket connected')
  //     this.isConnected = true
  //     this.emitEvent('connected')
  //   })

  //   this.socket.on('disconnect', () => {
  //     console.log('Socket disconnected')
  //     this.isConnected = false
  //     this.emitEvent('disconnected')
  //   })

  //   this.socket.on('connect_error', (error) => {
  //     console.error('Socket connection error:', error)
  //     this.emitEvent('error', error)
  //   })

  //   // 注册服务器事件
  //   this.socket.on('server_response', (data) => {
  //     this.emitEvent('server_response', data)
  //   })

  //   this.socket.on('error', (data) => {
  //     this.emitEvent('error', data)
  //   })
  // }

  // disconnect() {
  //   if (this.socket) {
  //     this.socket.disconnect()
  //     this.socket = null
  //     this.isConnected = false
  //   }
  // }

  // // 发送消息到服务器
  // sendMessage(messageData) {
  //   if (!this.isConnected) {
  //     console.error('Socket not connected')
  //     return false
  //   }

  //   this.socket.emit('client_message', messageData)
  //   return true
  // }

  // // 事件监听管理
  // on(event, callback) {
  //   if (!this.eventCallbacks.has(event)) {
  //     this.eventCallbacks.set(event, [])
  //   }
  //   this.eventCallbacks.get(event).push(callback)
  // }

  // off(event, callback) {
  //   if (this.eventCallbacks.has(event)) {
  //     const callbacks = this.eventCallbacks.get(event)
  //     const index = callbacks.indexOf(callback)
  //     if (index > -1) {
  //       callbacks.splice(index, 1)
  //     }
  //   }
  // }

  // emitEvent(event, data) {
  //   if (this.eventCallbacks.has(event)) {
  //     this.eventCallbacks.get(event).forEach(callback => {
  //       callback(data)
  //     })
  //   }
  // }

  connect() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) return

    // const serverUrl = process.env.USER_AGENT_WEBSOCKET
    const serverUrl = '/api/v1/chat/ws/send'

    
    try {
      this.socket = new WebSocket(serverUrl)
      
      // WebSocket 事件处理
      this.socket.onopen = (event) => {
        console.log('✅ WebSocket 连接已建立')
        this.isConnected = true
        this.reconnectAttempts = 0
        this.emitEvent('connected', event)
      }

      this.socket.onclose = (event) => {
        console.log('🔌 WebSocket 连接已关闭', event.code, event.reason)
        this.isConnected = false
        this.emitEvent('disconnected', event)
        
        // 自动重连逻辑
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++
            console.log(`🔄 尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
            this.connect()
          }, 3000)
        }
      }

      this.socket.onerror = (error) => {
        console.error('❌ WebSocket 错误:', error)
        this.emitEvent('error', error)
      }

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('📨 收到服务器消息:', data)
          
          // 根据事件类型分发
          if (data.event) {
            this.emitEvent(data.event, data.data || data)
          } else if (data.status) {
            // 兼容旧格式
            this.emitEvent('server_response', data)
          }
        } catch (error) {
          console.error('❌ 消息解析错误:', error, event.data)
        }
      }
      
    } catch (error) {
      console.error('❌ WebSocket 创建失败:', error)
    }
  }

  sendMessage(messageData) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket 未连接，无法发送消息')
      this.emitEvent('error', { message: 'WebSocket 未连接' })
      return false
    }

    try {
      const dataToSend = {
        user_input: messageData.user_input || messageData.message || '',
        user_id: messageData.user_id || 'anonymous',
        user_info: messageData.user_info || {},
        context: messageData.context || {},
        timestamp: new Date().toISOString()
      }
      
      this.socket.send(JSON.stringify(dataToSend))
      console.log('📤 发送消息:', dataToSend)
      return true
    } catch (error) {
      console.error('❌ 发送消息失败:', error)
      this.emitEvent('error', error)
      return false
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close(1000, '用户主动断开')
      this.socket = null
      this.isConnected = false
    }
  }

  // 事件管理方法保持不变
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event)
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  emitEvent(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`事件处理错误 (${event}):`, error)
        }
      })
    }
  }

}

// 创建单例
export const socketService = new SocketService()



// // src/services/socketService.js
// import { io } from 'socket.io-client'

// class SocketService {
//   constructor() {
//     this.socket = null
//     this.isConnected = false
//     this.eventCallbacks = new Map()
//   }

//   connect() {
//     if (this.socket) return

//     const serverUrl = 'http://localhost:6001'//import.meta.env.VITE_SOCKET_URL || 
    
//     this.socket = io(serverUrl, {
//       transports: ['websocket', 'polling']
//     })

//     // 连接事件处理
//     this.socket.on('connect', () => {
//       console.log('Socket connected')
//       this.isConnected = true
//       this.emitEvent('connected')
//     })

//     this.socket.on('disconnect', () => {
//       console.log('Socket disconnected')
//       this.isConnected = false
//       this.emitEvent('disconnected')
//     })

//     this.socket.on('connect_error', (error) => {
//       console.error('Socket connection error:', error)
//       this.emitEvent('error', error)
//     })

//     // 注册服务器事件
//     this.socket.on('server_response', (data) => {
//       this.emitEvent('server_response', data)
//     })

//     this.socket.on('error', (data) => {
//       this.emitEvent('error', data)
//     })
//   }

//   disconnect() {
//     if (this.socket) {
//       this.socket.disconnect()
//       this.socket = null
//       this.isConnected = false
//     }
//   }

//   // 发送消息到服务器
//   sendMessage(messageData) {
//     if (!this.isConnected) {
//       console.error('Socket not connected')
//       return false
//     }

//     this.socket.emit('client_message', messageData)
//     return true
//   }

//   // 事件监听管理
//   on(event, callback) {
//     if (!this.eventCallbacks.has(event)) {
//       this.eventCallbacks.set(event, [])
//     }
//     this.eventCallbacks.get(event).push(callback)
//   }

//   off(event, callback) {
//     if (this.eventCallbacks.has(event)) {
//       const callbacks = this.eventCallbacks.get(event)
//       const index = callbacks.indexOf(callback)
//       if (index > -1) {
//         callbacks.splice(index, 1)
//       }
//     }
//   }

//   emitEvent(event, data) {
//     if (this.eventCallbacks.has(event)) {
//       this.eventCallbacks.get(event).forEach(callback => {
//         callback(data)
//       })
//     }
//   }
// }

// // 创建单例
// export const socketService = new SocketService()