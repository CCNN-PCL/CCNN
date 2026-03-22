import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import chat from '@/views/chat.vue';
import home from '@/views/home.vue';
// import Login from '../views/Login';
// import Register from '../views/Register';
// import Dashboard from '../views/Dashboard.vue';
import { authStore } from '@/store/auth'; // 导入authStore
const routes = [
  {
    path: '/',
    name: 'home',
    component: home  },
  {
    path: '/ctlogin',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/chat',
    name: 'chat',
    component: chat,
    meta: { requiresAuth: false }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 导航守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const isPublicRoute = to.path === '/ctlogin' || to.path === '/register';
  const userData = localStorage.getItem('user');
  // const isAuthenticated = userData && JSON.parse(userData).loggedIn;
  const isAuthenticated = authStore.isAuthenticated;

  const userObj = JSON.parse(userData);

  // 如果访问需要认证的页面但未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/ctlogin');
  }
  if (to.path === '/highApp' && (!isAuthenticated || userObj.level != '高')) {
    return next('/ctlogin');
  }
  // // 如果已登录但访问登录/注册页
  // if (isAuthenticated && isPublicRoute) {
  //   if (userObj.level == '高') {
  //   return next('/highApp');
  // } else if (userObj.level == '中') {
  //   return next('/midApp');
  // }
  // }
  next();
});

export default router;