---
name: valorant_rag
description: 查询Valorant游戏知识库，包括英雄技能、地图信息等
version: 1.0
author: project
tags: [rag, knowledge, valorant, game]
permissions:
  - knowledge_base
parameters:
  - name: query
    type: string
    required: true
    description: 查询内容
tools:
  - custom.valorant_rag
execution:
  type: llm_driven
  steps:
    - 解析用户问题
    - 提取游戏相关关键词
    - 调用 valorant_rag 工具查询知识库
    - 整理查询结果
    - 返回答案
  output_format: 返回游戏知识答案
examples:
  - input: "Jett的技能是什么？"
    output: "调用valorant_rag工具查询Jett技能信息"
  - input: "Valorant有哪些英雄？"
    output: "调用valorant_rag工具查询英雄列表"
---

## 功能说明
这个skill用于查询Valorant游戏知识库，包括英雄技能、地图信息等。

## 使用场景
- 用户询问Valorant相关问题
- 需要游戏攻略
- 查询英雄技能信息

## 工作流程
1. 解析用户查询内容
2. 调用valorant_rag工具查询知识库
3. 整理并返回查询结果

## 注意事项
- 知识库内容可能不完整
- 对于最新游戏更新，可能需要等待知识库更新
- 支持中英文查询