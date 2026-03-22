# CyberTwin Frontend


## 功能特性

### 核心功能
- 🔐 **用户认证与授权** - 基于cybertwin的安全认证系统
- 📱 **设备信息展示** - 实时检测和展示设备信息
- 🎭 **人脸识别功能** - 集成摄像头进行人脸识别
- 💬 **实时通信** - 基于 Socket.io 的实时聊天功能

### 页面功能
- **首页** - 项目介绍和功能展示
- **登录/注册** - 用户身份验证
- **聊天界面** - 实时消息交流


## 技术栈

### 前端框架
- **Vue 3** - 渐进式 JavaScript 框架
- **Vue Router** - 官方路由管理器
- **Vite** - 下一代前端构建工具

### UI 和样式
- **FontAwesome** - 图标库
- **CSS3** - 现代化样式设计

### 网络和通信
- **Axios** - HTTP 客户端
- **Socket.io** - 实时双向通信


### 工具库
- **mobile-detect** - 移动设备检测
- **markdown-it** - Markdown 解析器

## 快速开始

### 环境要求

- **Node.js** v22.16.0
- **npm** 10.9.2

### 安装依赖

```bash

# 安装依赖
npm install
```

### 开发环境运行

```bash
npm run serve
```


### 生产环境构建

```bash
npm run build
```

构建产物将生成在 `dist` 目录中。


## 项目结构

```
cybertwin-frontend/
├── public/                    # 静态资源
│   └── favicon.ico          # 网站图标
├── src/                      # 源代码
│   ├── api/                 # API 接口
│   │   ├── api.js          # Axios 实例配置
│   │   ├── auth.js         # 认证相关 API
│   ├── assets/              # 资源文件
│   │   └── logo.png       # 项目 Logo
│   ├── components/          # 可复用组件
│   │   ├── DeviceInfo.vue  # 设备信息组件
│   │   ├── FaceCamera.vue  # 人脸识别组件
│   │   └── TypeWriter.vue # 打字机效果组件
│   ├── plugins/             # Vue 插件
│   │   └── deviceDetect.js # 设备检测插件
│   ├── router/              # 路由配置
│   │   └── index.js       # 路由定义
│   ├── services/            # 业务服务
│   │   └── socketService.js # Socket 服务
│   ├── store/               # 状态管理
│   │   └── auth.js        # 认证状态
│   ├── views/               # 页面组件
│   │   ├── Chat.vue       # 聊天页面
│   │   ├── Dashboard.vue   # 仪表盘
│   │   ├── Home.vue       # 首页
│   │   ├── Login.vue      # 登录页
│   │   └── Register.vue   # 注册页
│   ├── App.vue             # 根组件
│   ├── main.js             # 应用入口
│   └── style.css           # 全局样式
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
├── .gitignore             # Git 忽略配置
├── babel.config.js        # Babel 配置
├── index.html             # HTML 模板
├── jsconfig.json          # JS 配置
├── LICENSE                # MIT 许可证
├── package.json           # 项目配置
├── README.md             # 项目文档
└── vite.config.js        # Vite 配置
```

## 配置说明

### 环境变量

项目使用环境变量进行配置，请在 `.env.development` 和 `.env.production` 中配置：



## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t cybertwin-frontend .

# 运行容器
docker run -p 80:80 cybertwin-frontend
```

### Nginx 部署

1. 构建项目：`npm run build`
2. 将 `dist` 目录内容复制到 Nginx 服务器
3. 配置 Nginx 指向 `index.html`


