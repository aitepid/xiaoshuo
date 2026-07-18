# 晨昏书局 Web / Capacitor 前端

本目录是小说平台的商用级 H5 前端，同时可通过 Capacitor 打包为 Android / iOS 原生容器。

## 本地启动

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
```

## Capacitor 同步

```bash
npm run cap:sync
```

## 打开原生工程

```bash
npm run cap:android
npm run cap:ios
```

## 原生适配

- 已处理 Safe Area 兼容
- 已配置 Splash Screen 与 Status Bar
- 已接入移动端底部 TabBar

## 运行时配置

- `VITE_API_BASE_URL`：后端 API 地址，生产环境建议指向 Nginx 的 `/api/v1`