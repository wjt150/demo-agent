---
name: web_search
description: 搜索最新信息（新闻、天气、实时数据、未知知识）
version: 1.0
author: project
tags: [search, web, info, news]
permissions:
  - network
  - external_api
parameters:
  - name: query
    type: string
    required: true
    description: 搜索关键词
tools:
  - mcp.web_search
  - mcp.fetch_page
execution:
  type: llm_driven
  steps:
    - 从用户输入中提取搜索关键词
    - 调用 web_search 工具进行搜索
    - 分析搜索结果
    - 如果需要详细信息，调用 fetch_page 获取网页内容
    - 整理并返回结果
  output_format: 返回搜索结果摘要，包含标题、摘要和链接
examples:
  - input: "搜索最新AI新闻"
    output: "调用web_search工具返回结果"
  - input: "帮我搜一下最新的科技动态"
    output: "调用web_search工具搜索并返回摘要"
---

## 功能说明
这个skill用于搜索最新信息，包括新闻、天气、实时数据等。

## 使用场景
- 用户询问最新信息
- 需要获取网页链接
- 不确定答案时
- 需要实时数据

## 工作流程
1. 调用web_search获取搜索结果
2. 如果需要详细信息，调用fetch_page
3. 整理并返回结果

## 注意事项
- 搜索结果可能包含过时信息
- 对于实时性要求高的信息，建议直接调用专门的工具
- 搜索结果需要验证可靠性