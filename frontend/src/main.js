import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import deviceDetect from './plugins/deviceDetect';

// 创建应用实例
const app = createApp(App);

// 使用路由插件
app.use(router);
app.use(deviceDetect);

// 挂载应用
app.mount('#app');