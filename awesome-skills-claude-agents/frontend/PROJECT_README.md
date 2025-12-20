# AI Agent Platform - Frontend

**科技风Agent平台前端项目**

## 🎨 设计特点

- **深色主题**: 专业科技感的深色UI (#101622背景)
- **现代字体**: Space Grotesk字体系列
- **Material Icons**: Google Material Symbols图标
- **响应式设计**: 桌面端优先设计
- **主题色**: 蓝色 (#2b6cee)

## 🚀 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **路由**: React Router v6
- **状态管理**: TanStack Query (待集成)
- **HTTP客户端**: Axios (待集成)

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/          # 通用组件
│   │   │   ├── Layout.tsx   # 主布局
│   │   │   ├── Sidebar.tsx  # 侧边栏导航
│   │   │   ├── Button.tsx   # 按钮组件
│   │   │   ├── Modal.tsx    # 模态框
│   │   │   ├── SearchBar.tsx # 搜索栏
│   │   │   ├── StatusBadge.tsx # 状态标签
│   │   │   └── LoadingSpinner.tsx # 加载指示器
│   │   ├── chat/            # 聊天组件 (在ChatPage内)
│   │   ├── agents/          # Agent管理组件 (在AgentsPage内)
│   │   ├── skills/          # Skill管理组件 (在SkillsPage内)
│   │   └── mcp/             # MCP管理组件 (在MCPPage内)
│   ├── pages/
│   │   ├── DashboardPage.tsx  # 仪表板页面
│   │   ├── ChatPage.tsx       # 聊天页面 (SSE流式)
│   │   ├── AgentsPage.tsx     # Agent管理页面
│   │   ├── SkillsPage.tsx     # Skill管理页面
│   │   └── MCPPage.tsx        # MCP服务器管理页面
│   ├── services/
│   │   ├── api.ts            # Axios客户端配置
│   │   ├── agents.ts         # Agent API服务
│   │   ├── skills.ts         # Skill API服务
│   │   ├── mcp.ts            # MCP API服务
│   │   └── chat.ts           # Chat SSE服务
│   ├── types/
│   │   └── index.ts          # TypeScript类型定义
│   ├── hooks/                # 自定义React Hooks
│   ├── utils/                # 工具函数
│   ├── App.tsx               # 根组件
│   ├── main.tsx              # 入口文件
│   └── index.css             # 全局样式
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

## 已完成功能

- [x] 项目基础架构搭建 (Vite + React + TypeScript)
- [x] Tailwind CSS 4.x 配置与深色主题
- [x] 通用组件库 (Layout, Sidebar, Button, Modal等)
- [x] Dashboard 仪表板页面
- [x] Chat 聊天页面 (SSE流式响应)
- [x] Agent 管理页面 (CRUD + 配置面板)
- [x] Skill 管理页面 (上传/AI生成)
- [x] MCP 服务器管理页面 (CRUD + 连接测试)
- [x] API服务层 (Axios + 类型定义)
- [x] 路由配置 (React Router v6)
- [x] 状态管理 (TanStack Query)


## 下一步计划

- [ ] 添加用户认证流程
- [ ] 实现真实的后端API对接
- [ ] 添加单元测试
- [ ] 性能优化 (代码分割等)
- [ ] 添加更多的交互动效 

## 🛠️ 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

## 🌐 本地访问

开发服务器运行后，访问: **http://localhost:5173/**


## 🎨 设计参考

UI设计位于项目根目录: `/ui_design/`
- agent对话主界面/
- agent定制管理/
- skill管理/
- mcp管理/

## 📄 相关文档

- [开发计划](../DEVELOPMENT_PLAN.md) - 详细的阶段开发计划
- [架构设计](../ARCHITECTURE.md) - 完整系统架构文档
- [Tailwind配置](./tailwind.config.js) - Tailwind定制配置


