# Skills 使用指南

## 可用 Skills 列表

| Skill | 功能 | 标签 |
|-------|------|------|
| `web_search` | 搜索最新信息 | search, web, info |
| `weather` | 查询天气预报 | weather, temperature |
| `valorant_rag` | 查询 Valorant 知识库 | rag, knowledge, game |
| `custom_example` | 自定义示例 skill | custom, example |
| `demo_skill` | 演示 skill 功能 | demo, example |

---

## 使用方式

### 显式调用

使用 `@skill_name` 前缀显式调用指定 skill：

```
@web_search 最新AI新闻
@weather 北京天气
@valorant_rag Jett的技能是什么
@custom_example 示例查询
@demonstration 演示查询
```

### 自动路由

直接输入问题，系统会自动选择最合适的 skill：

```
搜索最新科技动态        → 自动选择 web_search
今天广州天气怎么样       → 自动选择 weather
Valorant有哪些英雄      → 自动选择 valorant_rag
```

---

## 各 Skill 详细说明

### 1. web_search - 网页搜索

**功能**: 搜索最新信息，包括新闻、天气、实时数据等

**调用方式**:
```
@web_search 搜索关键词
```

**示例**:
```
@web_search 最新AI新闻
@web_search 今天的科技动态
@web_search 北京今天有什么活动
```

**可用工具**:
- `mcp.web_search` - 搜索引擎
- `mcp.fetch_page` - 获取网页内容

---

### 2. weather - 天气查询

**功能**: 查询城市天气信息和未来预报

**调用方式**:
```
@weather 城市名称
@weather 城市名称 天数
```

**参数**:
- `city` (必填): 城市名称
- `days` (可选): 预报天数，默认 1 天

**示例**:
```
@weather 北京
@weather 广州天气
@weather 上海未来三天
```

**可用工具**:
- `mcp.get_weather` - 天气 API

---

### 3. valorant_rag - Valorant 知识库

**功能**: 查询 Valorant 游戏知识库，包括英雄技能、地图信息等

**调用方式**:
```
@valorant_rag 问题
```

**示例**:
```
@valorant_rag Jett的技能是什么
@valorant_rag 有哪些英雄
@valorant_rag Bind地图特点
```

**可用工具**:
- `custom.valorant_rag` - 知识库查询

---

### 4. custom_example - 自定义示例

**功能**: 演示如何创建自定义 skill

**调用方式**:
```
@custom_example 查询内容
```

**示例**:
```
@custom_example 这是一个示例查询
```

**可用工具**:
- `mcp.web_search` - 搜索引擎

---

### 5. demo_skill - 演示 Skill

**功能**: 展示 skill 系统功能

**调用方式**:
```
@demonstration 查询内容
```

**示例**:
```
@demonstration 演示查询
```

**可用工具**:
- `mcp.web_search` - 搜索引擎

---

## 命令列表

| 命令 | 功能 |
|------|------|
| `exit` / `quit` | 退出程序 |
| `clear` | 清屏 |
| `help` | 显示帮助信息 |

---

## 添加新 Skill

### 方法

1. 在 `skills/` 目录下创建新文件夹
2. 创建 `SKILL.md` 文件，包含 YAML frontmatter
3. 重启程序即可自动加载

### SKILL.md 模板

```yaml
---
name: skill名称
description: skill描述
version: 1.0
author: 作者
tags: [标签1, 标签2]
permissions:
  - 权限1
parameters:
  - name: 参数名
    type: string
    required: true
    description: 参数描述
tools:
  - mcp.tool_name
execution:
  type: llm_driven
  steps:
    - 步骤1
    - 步骤2
  output_format: 输出格式
---

# Skill 标题

功能说明和使用场景
```

---

## 故障排除

### Skill 无法执行

1. 检查 SKILL.md 格式是否正确
2. 确认 YAML frontmatter 语法正确
3. 检查工具名称是否拼写正确

### 工具调用失败

1. 确认 MCP 服务已启动
2. 检查网络连接
3. 查看错误信息排查问题

### 路由不准确

1. 使用显式调用 `@skill_name` 确保正确路由
2. 检查 skill 的 tags 和 description 是否准确
