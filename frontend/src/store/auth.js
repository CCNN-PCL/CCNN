import { reactive, readonly } from 'vue'

// 创建响应式状态
const state = reactive({
  isAuthenticated: false,
  user: null,
  level: 0 
})

// 从localStorage初始化状态
function initAuthState() {
  const userData = localStorage.getItem('user')
  if (userData) {
    const user = JSON.parse(userData)
    state.isAuthenticated = user.loggedIn
    state.user = user
    state.level = user.level || 0
  }
}

// 登录方法
function login(userData) {
  const user = {
    username: userData.username,
    token: userData.token,
    loggedIn: true,
    level: userData.level || 0
  }
  console.log(user)
  localStorage.setItem('user', JSON.stringify(user))
  state.isAuthenticated = true
  state.user = user
}

// 退出登录方法
function logout() {
  localStorage.removeItem('user')
  state.isAuthenticated = false
  state.user = null
  state.level = 0
}

// 导出只读状态和方法
export const authStore = readonly(state)
export const authActions = {
  initAuthState,
  login,
  logout
}