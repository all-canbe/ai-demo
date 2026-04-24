# 智能文档处理系统 - 前端

基于 React + TypeScript + Vite 构建的智能文档处理系统前端。

## 技术栈

- React 18
- TypeScript 5
- Vite 5
- Redux Toolkit
- React Router 6
- Tailwind CSS
- Framer Motion
- React Dropzone
- i18next (国际化)
- Axios

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── app/               # Redux store 配置
│   ├── api/               # API 接口
│   ├── components/        # 组件
│   │   ├── common/        # 通用组件
│   │   ├── layout/        # 布局组件
│   │   ├── document/      # 文档相关组件
│   │   └── chat/          # 聊天相关组件
│   ├── features/          # Redux slices
│   ├── hooks/             # 自定义 hooks
│   ├── i18n/              # 国际化配置
│   ├── pages/             # 页面组件
│   ├── routes/            # 路由配置
│   ├── types/             # TypeScript 类型定义
│   ├── App.tsx            # 应用入口组件
│   ├── main.tsx           # 应用入口
│   └── index.css          # 全局样式
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

### 代码检查

```bash
npm run lint
```

## 功能特性

- 用户认证（登录/注册）
- 文档上传和管理
- 多格式文档支持（PDF、Word、图片、TXT、MD、HTML）
- AI 智能聊天对话
- 引用来源展示
- 国际化支持（中文/英文）
- 响应式设计

## 环境变量

复制 `.env.example` 为 `.env` 并配置：

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MSW=false
```
