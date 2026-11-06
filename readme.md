# 扫地机器人智能客服系统

一个基于 LangChain、RAG 和 Agent 技术实现的扫地机器人智能客服项目。它可以处理常见的使用问题、故障排查、维护保养、选购建议等场景，并支持从知识库中检索相关资料，生成更准确的回答。同时，系统会在回答后展示引用来源，方便追溯知识依据。

---

## 项目概述

本项目的目标是将大模型能力、知识库检索和工具调用结合起来，构建一个专注于扫地机器人场景的智能客服系统。

支持的核心能力包括：

- 知识问答：回答扫地机器人相关问题
- 故障排查：给出常见故障的处理建议
- 维护保养：说明耗材、更换周期、日常维护方式
- 选购建议：根据场景给出推荐方案
- 报告生成：基于用户数据生成月度使用报告
- 引用溯源：回答中附带知识库引用，方便核对

---

## 功能特点

### 1. 智能 Agent

项目使用了自定义的 ReAct 风格 Agent，能够根据用户问题决定是否需要调用工具。它具备以下特点：

- 自动判断是否需要检索知识库
- 能根据问题选择合适的工具
- 支持多轮工具调用
- 可处理普通问答和报告生成场景
- 具备一定的工具调用约束和流程控制

相关代码：
- `agent/react_agent.py`
- `agent/tools/agent_tools.py`
- `agent/tools/middleware.py`

### 2. RAG 检索

系统通过向量数据库检索相关知识，再由大模型总结回答。

它会在 `data` 目录下的知识文件中查找相关内容，主要包括：

- 扫地机器人常见问题
- 扫拖一体机器人问题
- 故障排除相关知识
- 维护保养指南
- 选购指南

相关代码：
- `rag/vector_store.py`
- `rag/rag_service.py`

### 3. 引用展示功能

这是本项目比较实用的一点：在回答后，系统会展示引用来源。用户可以查看：

- 引用了哪些知识文件
- 检索到了哪些文本片段
- 答案对应的依据来源

在界面中，引用信息会以“查看引用”的形式展示，便于核对和追踪。相关实现位于：
- `app.py`
- `rag/rag_service.py`

它的实际效果是：

- 提高回答可信度
- 便于复查知识依据
- 让客服问答更像真实产品

### 4. 外部数据查询

项目中还内置了外部数据查询能力，例如：

- 获取当前用户 ID
- 获取当前月份
- 获取用户所在城市
- 查询天气
- 查询用户使用记录

这部分能力用于生成更具场景感的报告和回答。

### 5. 使用报告生成

系统支持生成用户月度使用报告，流程包括：

1. 先准备报告上下文
2. 获取用户 ID
3. 获取当前月份
4. 查询该用户对应的使用记录
5. 生成结构化报告

这个流程有明确的约束，确保报告生成逻辑更稳定。

---

## 技术栈

- Python
- Streamlit：前端交互界面
- LangChain：智能体与工具调用
- Chroma：向量数据库
- DashScope / Qwen：大模型与嵌入模型
- PyPDFLoader / TextLoader：知识文件读取
- PyYAML：配置文件管理
- CSV / TXT / PDF：知识库和外部数据来源

---

## 项目结构

```text
robot_cs_agent_self/
├── app.py                     # Streamlit 应用入口
├── readme.md                 # 项目说明
├── requirements.txt          # 依赖文件
├── agent/
│   ├── react_agent.py        # Agent 核心逻辑
│   └── tools/
│       ├── agent_tools.py    # 业务工具集合
│       └── middleware.py     # 中间件：日志、监控、提示词切换
├── rag/
│   ├── rag_service.py        # RAG 检索与总结
│   └── vector_store.py       # 向量库构建和检索
├── model/
│   ├── __init__.py
│   └── factory.py            # 模型创建工厂
├── utils/
│   ├── config_handler.py     # 配置加载
│   ├── file_handler.py        # 文件处理
│   ├── logger_handler.py      # 日志模块
│   ├── path_tool.py           # 路径工具
│   └── prompt_loader.py       # 提示词加载
├── config/
│   ├── agent.yml
│   ├── chroma.yml
│   ├── prompts.yml
│   └── rag.yml
├── prompts/
│   ├── main_prompt.txt
│   ├── rag_summarize.txt
│   └── report_prompt.txt
├── data/
│   ├── questions.txt
│   ├── 扫地机器人100问.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 维护保养200条.txt
│   ├── 故障排除200条.pdf
│   ├── 选购指南200条.pdf
│   └── external/
│       └── records.csv
├── chroma_db/               # 向量数据库持久化目录
├── logs/
│   └── app.log
└── __pycache__/
```

---

## 环境要求

- Python 3.10+
- 可用的 DashScope API Key
- 至少 2GB 可用磁盘空间
- 稳定的网络环境

---

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

Windows PowerShell：

```powershell
$env:DASHSCOPE_API_KEY="你的key"
```

Linux / macOS：

```bash
export DASHSCOPE_API_KEY="你的key"
```

### 3. 初始化知识库

```bash
python rag/vector_store.py
```

这一步会扫描 `data` 目录中的知识文件，进行文本分块、向量化和入库。只有初始化完成后，知识检索功能才能正常使用。

### 4. 启动项目

```bash
streamlit run app.py
```

启动后打开浏览器访问：

```text
http://localhost:8501
```

---

## 使用示例

### 普通问答

```text
拖地时地面出现水痕怎么解决？
```

### 故障排查

```text
机器人找不到充电座怎么办
```

### 维护保养

```text
扫地机器人需要多久更换滤网？
```

### 生成月度报告

```text
生成本月我的使用报告
```

### 场景型提问

```text
南方回南天用机器人拖地要注意什么
```

---

## 引用功能说明

本项目支持在回答中展示引用来源，用户可以在界面中查看：

- 具体引用了哪些知识文件
- 这些文件中检索到的片段内容
- 答案对应的依据来源

前端展示入口：
- `app.py`

后端引用实现：
- `rag/rag_service.py`

这样做的好处是：

- 提高回答可信度
- 让用户能查看知识依据
- 更适合做展示型 AI 应用

---

## 关键模块说明

### `app.py`

应用入口，负责：

- 启动 Streamlit 页面
- 展示聊天界面
- 调用 Agent
- 渲染回答内容和引用信息

### `agent/react_agent.py`

这是智能体的核心实现，负责：

- 接收用户问题
- 选择是否调用工具
- 执行工具调用
- 获取回答和引用来源
- 管理多轮推理

### `rag/rag_service.py`

实现知识检索和总结逻辑：

- 检索相关文档
- 提取内容
- 组装上下文
- 调用模型生成回答
- 返回引用来源

### `rag/vector_store.py`

负责文档加载和向量库管理：

- 读取知识文件
- 分块处理
- 生成 embedding
- 存入 Chroma

### `agent/tools/agent_tools.py`

封装各种工具：

- `rag_summarize`：知识库检索
- `get_weather`：查询天气
- `get_user_location`：获取用户城市
- `get_user_id`：获取用户 ID
- `get_current_month`：获取当前月份
- `fetch_external_data`：获取用户历史记录
- `fill_context_for_report`：报告前置上下文准备

---

## 项目亮点

- 有清晰的 Agent 调度逻辑
- 有完整的 RAG 检索链路
- 有真正的引用来源展示
- 支持多种客服场景
- 适合做 AI 智能客服学习项目
- 代码结构比较清晰，便于二次开发

---

## 后续扩展方向

如果继续扩展，可以加入这些能力：

- 用户登录和个人中心
- 历史对话记录
- 更大规模知识库管理
- 语音问答
- 实时设备数据接入
- 更细化的故障诊断流程

---

## 总结

这个项目是一个典型的“AI + 知识库 + Agent”项目，适合用来学习和展示大模型应用的实际工程能力。它不仅能回答问题，还能通过知识检索与引用机制，让回答更可靠、更可追溯。

如果你希望进一步拓展，这个项目非常适合作为 AI 客服类应用的基础模板。
