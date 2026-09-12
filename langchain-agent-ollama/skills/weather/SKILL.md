---
name: weather
description: 查询城市天气信息，包括当前天气和未来预报
version: 1.0
author: project
tags: [weather, temperature, forecast]
permissions:
  - network
  - external_api
parameters:
  - name: city
    type: string
    required: true
    description: 城市名称
  - name: days
    type: integer
    required: false
    description: 预报天数（默认1天）
tools:
  - mcp.get_weather
execution:
  type: llm_driven
  steps:
    - 从用户输入中提取城市名称
    - 提取天数参数（默认1天）
    - 调用 get_weather 工具查询天气
    - 整理天气信息
    - 返回天气预报
  output_format: 返回天气信息，包含日期、温度、天气状况
examples:
  - input: "今天广州天气怎么样？"
    output: "调用get_weather工具返回广州天气信息"
  - input: "查询北京未来三天的天气"
    output: "调用get_weather工具返回北京三天天气预报"
---

## 功能说明
这个skill用于查询城市天气信息，包括当前天气和未来预报。

## 使用场景
- 用户询问天气
- 需要出行建议
- 规划活动安排

## 工作流程
1. 解析用户输入的城市名称
2. 调用get_weather工具获取天气数据
3. 整理并返回天气信息

## 注意事项
- 天气数据可能有延迟
- 对于精确的天气信息，建议使用专业气象服务
- 支持中文城市名称