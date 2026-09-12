---
name: demo_skill
description: 演示skill，展示skill系统功能
version: 1.0
author: demo
tags: [demo, example]
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
    - 接收用户输入
    - 分析查询内容
    - 调用 web_search 工具获取信息
    - 整理并返回结果
  output_format: 返回演示结果
examples:
  - input: "演示查询"
    output: "演示结果"
---

## 功能说明
这是一个演示skill，用于展示skill系统的功能。

## 使用场景
- 学习skill系统
- 测试skill功能
- 演示skill用法

## 工作流程
1. 接收用户输入
2. 分析查询内容
3. 调用相应工具
4. 返回处理结果