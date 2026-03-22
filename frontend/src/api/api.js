// import axios from 'axios';

// // 创建配置好的 axios 实例
// const api = axios.create({
//   baseURL:  process.env.CYBERTWIN, // API 基础地址
//   timeout: 10000, // 请求超时时间
// });

// // 请求拦截器
// api.interceptors.request.use(
//   (config) => {
//     // 从 localStorage 获取 token
//     const token = localStorage.getItem('access_token');
//     // 如果 token 存在，将其添加到请求头中 [6,7](@ref)
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     // 请求错误处理
//     return Promise.reject(error);
//   }
// );

// // 响应拦截器
// api.interceptors.response.use(
//   (response) => {
//     // 对响应数据做点什么，直接返回 data 部分 [4,7](@ref)
//     return response.data;
//   },
//   (error) => {
//     // 对响应错误做点什么 [1,7,9](@ref)
//     if (error.response) {
//       const { status } = error.response;
      
//       switch (status) {
//         case 401:
//           // 未授权，清除本地 token 并跳转到登录页 [9,10](@ref)
//           localStorage.removeItem('access_token');
//           window.location.href = '/login';
//           break;
//         case 403:
//           console.error('无权限访问');
//           break;
//         case 404:
//           console.error('请求资源不存在');
//           break;
//         case 500:
//           console.error('服务器内部错误');
//           break;
//         default:
//           console.error(`请求错误: ${status}`);
//       }
//     } else if (error.request) {
//       // 请求已发出但没有响应
//       console.error('网络错误，请检查网络连接');
//     } else {
//       // 其他错误
//       console.error('请求配置错误', error.message);
//     }
    
//     return Promise.reject(error);
//   }
// );

// export default api;