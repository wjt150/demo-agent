---
name: custom_example
description: 自定义skill示例，演示如何创建新的skill
version: 1.0
author: user
tags: [custom, example, demo]
permissions:
  - network
parameters:
  - name: query
    type: string
    required: true
    description: 查询内容
tools:
  - mcp.web_search
execution:
  type: llm_driven
  steps:
    - 分析用户查询内容
    - 提取关键信息
    - 调用 web_search 工具搜索相关信息
    - 整理搜索结果
    - 返回处理结果
  output_format: 返回搜索结果摘要
examples:
  - input: "这是一个示例查询"
    output: "调用自定义skill处理"
---

## 功能说明
这是一个自定义skill示例，演示如何创建新的skill。

## 使用场景
- 学习如何创建skill
- 测试skill系统
- 自定义业务逻辑

## 工作流程
1. 接收用户查询
2. 处理查询
3. 返回结果