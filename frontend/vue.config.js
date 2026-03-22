const { defineConfig } = require('@vue/cli-service')
const Dotenv = require('dotenv-webpack')
// 让 Node 侧也能读到 .env.*

module.exports = defineConfig({
  lintOnSave:false,
  transpileDependencies: true,
  // 业务代码变量
  configureWebpack: {
    plugins: [
      new Dotenv({
        path: `./.env.${process.env.NODE_ENV}`,
        safe: false,
        systemvars: true
      })
    ]
  },
  // devServer 使用同一变量
  // devServer: {
  //   proxy: {
  //     '/api': {
  //       target: process.env.CYBERTWIN,
  //       changeOrigin: true,
  //       secure: false,
  //       pathRewrite: { '^/api': '' }
  //     }
  //   }
  // }
    devServer: {
      // port: 8089,      // 想用的端口
      https: false,    // 是否启用 https
    },
})