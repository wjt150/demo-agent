# Skill系统使用指南

## 概述

Skill系统为您的AI Agent提供了动态工具加载、可重用skill定义和混合模式调用的能力。

## 快速开始

### 1. 查看可用Skills

```python
from skill_manager import SkillManager

manager = SkillManager("skills")
manager.initialize()

# 获取所有skill
skills = manager.get_all_skill_names()
print(f"可用skills: {skills}")

# 获取skill描述
descriptions = manager.get_skill_descriptions()
for name, desc in descriptions.items():
    print(f"{name}: {desc}")
```

### 2. 显式调用Skill

在用户输入中使用以下格式显式调用skill：

- `@skill_name` - 使用@符号
- `/skill_name` - 使用/符号
- `使用skill_name查询` - 自然语言

示例：
```
@web_search 搜索AI新闻
/weather 查询北京天气
使用valorant_rag查询Jett技能
```

### 3. 自动路由

系统会自动分析用户输入，选择最合适的skill：

```python
from skill_router import SkillRouter
from skill_manager import SkillManager
from langchain_ollama import ChatOllama

manager = SkillManager("skills")
manager.initialize()

llm = ChatOllama(model="deepseek-r1:7b", temperature=0.3)
router = SkillRouter(manager, llm)

# 路由用户输入
skill_name, is_explicit = router.route("搜索最新AI新闻")
print(f"路由到: {skill_name}, 显式指定: {is_explicit}")
```

## 创建自定义Skill

### 1. 创建Skill目录

```bash
mkdir skills/my_skill
```

### 2. 创建SKILL.md文件

```yaml
---
name: my_skill
description: 我的自定义skill
version: 1.0
author: user
tags: [custom, my_skill]
permissions:
  - network
parameters:
  - name: query
    type: string
    required: true
    description: 查询内容
tools:
  - mcp.web_search
examples:
  - input: "示例输入"
    output: "示例输出"
---

## 功能说明
这里描述skill的功能。

## 使用场景
- 场景1
- 场景2

## 工作流程
1. 步骤1
2. 步骤2
```

### 3. 验证Skill

```python
from skill_manager import SkillManager

manager = SkillManager("skills")
manager.initialize()

if "my_skill" in manager.skills:
    print("Skill创建成功")
else:
    print("Skill创建失败")
```

## 权限管理

### 1. 配置文件

权限配置存储在`permissions.yaml`文件中：

```yaml
permissions:
  network:
    description: 网络访问权限
    tools: [web_search, fetch_page]
  
  weather:
    description: 天气服务权限
    tools: [get_weather]

roles:
  user:
    permissions: [network, weather]
  
  admin:
    permissions: [network, weather, file_system]

skill_permissions:
  web_search:
    required: [network]
  
  weather:
    required: [weather]
```

### 2. 设置用户角色

```python
from permission_manager import PermissionManager

manager = PermissionManager()
manager.set_user_role("user1", "user")
manager.set_user_role("admin1", "admin")
```

### 3. 检查权限

```python
# 检查用户是否有权限执行指定skill
has_perm = manager.check_permission("user1", "web_search")
print(f"权限检查: {has_perm}")

# 获取用户可用的skill列表
available = manager.get_available_skills("user1")
print(f"可用skills: {available}")
```

## 高级功能

### 1. 根据标签获取Skill

```python
# 获取所有搜索相关的skill
search_skills = manager.get_skills_by_tag("search")
print(f"搜索skills: {[s['name'] for s in search_skills]}")
```

### 2. 获取Skill使用的工具

```python
# 获取指定skill使用的工具
tools = manager.get_tools_for_skill("web_search")
print(f"web_search使用的工具: {tools}")
```

### 3. 执行历史记录

```python
from skill_executor import SkillExecutor

# 执行skill后会自动记录历史
executor = SkillExecutor(manager, router)
result = await executor.execute("搜索AI新闻")

# 查看执行历史
history = executor.get_execution_history()
print(f"执行历史: {history}")
```

## 示例代码

查看`example_skill_usage.py`文件获取完整的使用示例。

## 文件结构

```
skills/
├── search/
│   └── SKILL.md          # 网页搜索skill
├── weather/
│   └── SKILL.md          # 天气查询skill
├── rag/
│   └── SKILL.md          # RAG检索skill
└── custom_example/
    └── SKILL.md          # 自定义skill示例

skill_loader.py           # Skill加载器
skill_manager.py          # Skill管理器
skill_router.py           # Skill路由器
skill_executor.py         # Skill执行器
permission_manager.py     # 权限管理器
```

## 注意事项

1. Skill文件必须使用YAML + Markdown格式
2. YAML frontmatter必须包含`name`和`description`字段
3. 权限配置需要与skill的`permissions`字段匹配
4. 自定义skill需要放在`skills/`目录下
5. 系统会自动缓存已加载的skill，提高性能

## 故障排除

### 1. Skill未加载

检查：
- Skill目录是否存在
- SKILL.md文件格式是否正确
- YAML frontmatter是否包含必要字段

### 2. 权限错误

检查：
- 用户角色是否正确设置
- 权限配置文件是否正确
- skill所需的权限是否已定义

### 3. 路由失败

检查：
- LLM模型是否可用
- skill描述是否清晰
- 用户输入是否包含明确的skill调用指令