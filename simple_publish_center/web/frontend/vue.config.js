const { defineConfig } = require('@vue/cli-service')
const AutoImport = require('unplugin-auto-import/webpack')
const Components = require('unplugin-vue-components/webpack')
const { ElementPlusResolver } = require('unplugin-vue-components/resolvers')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 3000,
    open: true,
    proxy: {
      // 代理API请求到后端服务
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    }
  },

  // 构建配置
  configureWebpack: {
    plugins: [
      // Element Plus按需引入
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    // 优化打包大小
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 250000,
        cacheGroups: {
          elementPlus: {
            name: 'chunk-elementPlus',
            test: /[\\/]node_modules[\\/]element-plus[\\/]/,
            priority: 30
          },
          monaco: {
            name: 'chunk-monaco',
            test: /[\\/]node_modules[\\/]monaco-editor[\\/]/,
            priority: 20
          },
          antv: {
            name: 'chunk-antv',
            test: /[\\/]node_modules[\\/]@antv[\\/]/,
            priority: 20
          },
          vendors: {
            name: 'chunk-vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10
          }
        }
      }
    }
  },

  // 生产环境配置
  productionSourceMap: false,
  
  // 样式配置
  css: {
    loaderOptions: {
      less: {
        lessOptions: {
          javascriptEnabled: true
        }
      }
    }
  }
}) 