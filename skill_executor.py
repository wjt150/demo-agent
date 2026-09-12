import datetime
import re
from typing import Any, Dict, Optional, List
from skill_manager import SkillManager
from skill_router import SkillRouter
from langchain.tools import tool
from langchain_ollama import ChatOllama

MODEL_NAME = "deepseek-r1:7b"

class SkillExecutor:
    def __init__(self, skill_manager: SkillManager, skill_router: SkillRouter):
        self.skill_manager = skill_manager
        self.skill_router = skill_router
        self.execution_history: Dict[str, list] = {}
        self.mcp_tools: Dict[str, Any] = {}
        self.valorant_rag = None
        self.llm = ChatOllama(model=MODEL_NAME, temperature=0.3)
    
    def register_tools(self, mcp_tools: list, valorant_rag=None):
        """注册外部工具（从main.py调用）"""
        self.mcp_tools = {tool.name: tool for tool in mcp_tools}
        self.valorant_rag = valorant_rag
    
    async def execute(self, user_input: str, context: Optional[Dict] = None) -> Any:
        """执行skill"""
        # 1. 路由到合适的skill
        skill_name, is_explicit = self.skill_router.route(user_input)
        
        if not skill_name:
            return None
        
        # 2. 检查权限
        if not self._check_permissions(skill_name):
            return f"权限不足：无法执行skill {skill_name}"
        
        # 3. 执行skill
        result = await self._execute_skill(skill_name, user_input, context)
        
        # 4. 记录执行历史
        self._record_execution(skill_name, user_input, result)
        
        return result
    
    def _check_permissions(self, skill_name: str) -> bool:
        """检查权限"""
        return True
    
    async def _execute_skill(self, skill_name: str, user_input: str, context: Optional[Dict]) -> Any:
        """统一的动态执行入口"""
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return f"未找到skill: {skill_name}"
        
        # 所有skill都通过LLM动态执行
        return await self._execute_with_llm(skill_name, user_input, skill)
    
    async def _execute_with_llm(self, skill_name: str, user_input: str, skill: dict) -> str:
        """LLM驱动的动态执行"""
        # 1. 构建执行提示词
        execution_prompt = self._build_execution_prompt(skill_name, user_input, skill)
        
        # 2. 调用LLM生成执行计划
        response = await self.llm.ainvoke(execution_prompt)
        
        # 3. 解析LLM输出，调用工具
        result = await self._parse_and_execute(response.content, skill, user_input)
        
        return result
    
    def _build_execution_prompt(self, skill_name: str, user_input: str, skill: dict) -> str:
        """构建执行提示词"""
        tools_info = self._get_tools_info(skill)
        execution = skill.get('execution', {})
        steps = execution.get('steps', ['处理用户输入', '返回结果'])
        output_format = execution.get('output_format', '返回处理结果')
        
        return f"""你是一个Skill执行器。根据以下信息执行skill：

## Skill信息
- 名称: {skill_name}
- 描述: {skill.get('description', '')}
- 用户输入: {user_input}

## 可用工具
{tools_info}

## 执行步骤
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(steps))}

## 输出要求
{output_format}

请严格按照步骤执行，调用相应工具完成任务。直接返回工具调用结果，不要添加额外解释。"""
    
    def _get_tools_info(self, skill: dict) -> str:
        """获取skill可用工具信息"""
        tools = skill.get('tools', [])
        if not tools:
            return "无可用工具"
        
        info_lines = []
        for tool_ref in tools:
            tool_name = tool_ref.split('.')[-1] if '.' in tool_ref else tool_ref
            desc = self._get_tool_description(tool_name)
            info_lines.append(f"- {tool_ref}: {desc}")
        
        return '\n'.join(info_lines) if info_lines else "无可用工具"
    
    def _get_tool_description(self, tool_name: str) -> str:
        """获取工具描述"""
        descriptions = {
            'web_search': '搜索最新信息（新闻、天气、实时数据）',
            'fetch_page': '获取网页详细内容',
            'get_weather': '查询城市天气',
            'valorant_rag': '查询Valorant游戏知识库'
        }
        return descriptions.get(tool_name, '未知工具')
    
    async def _parse_and_execute(self, llm_output: str, skill: dict, user_input: str) -> str:
        """解析LLM输出，调用对应工具"""
        tools = skill.get('tools', [])
        
        # 根据skill类型调用对应的工具
        for tool_ref in tools:
            tool_name = tool_ref.split('.')[-1] if '.' in tool_ref else tool_ref
            
            # MCP工具
            if tool_name in self.mcp_tools:
                try:
                    # 根据不同工具传不同参数
                    if tool_name == 'web_search':
                        query = self._extract_search_query(user_input)
                        result = await self.mcp_tools[tool_name].ainvoke({"query": query})
                        return f"搜索结果：\n{result}"
                    elif tool_name == 'get_weather':
                        city = self._extract_city(user_input)
                        days = self._extract_days(user_input)
                        result = await self.mcp_tools[tool_name].ainvoke({"city": city, "days": days})
                        return f"天气信息：\n{result}"
                    elif tool_name == 'fetch_page':
                        result = await self.mcp_tools[tool_name].ainvoke({"url": llm_output})
                        return f"网页内容：\n{result}"
                    else:
                        result = await self.mcp_tools[tool_name].ainvoke({"query": user_input})
                        return f"工具调用结果：\n{result}"
                except Exception as e:
                    return f"工具调用失败: {e}"
            
            # 自定义工具（如valorant_rag）
            if tool_name == 'valorant_rag' and self.valorant_rag:
                try:
                    result = self.valorant_rag.invoke(user_input)
                    return f"知识库查询结果：\n{result}"
                except Exception as e:
                    return f"知识库查询失败: {e}"
        
        # 如果没有匹配的工具，直接返回LLM输出
        return llm_output
    
    def _extract_search_query(self, user_input: str) -> str:
        """从用户输入中提取搜索关键词"""
        prefixes = ['搜索', '查找', '查询', '搜', '找', '帮我搜', '帮我找', '帮我查']
        query = user_input
        
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):]
                break
        
        return query.strip()
    
    def _extract_city(self, user_input: str) -> str:
        """从用户输入中提取城市名称"""
        city_patterns = [
            r'(\w+)(?:的|市|区)?(?:天气|气温|温度)',
            r'(?:查询|查|看)(\w+)(?:的|市|区)?(?:天气|气温|温度)',
            r'(\w+)(?:今天|明天|后天|未来\d+天)?(?:天气|气温|温度)'
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        
        return "北京"
    
    def _extract_days(self, user_input: str) -> int:
        """从用户输入中提取天数"""
        days_match = re.search(r'(\d+)\s*天', user_input)
        if days_match:
            return int(days_match.group(1))
        
        future_match = re.search(r'未来\s*(\d+)\s*天', user_input)
        if future_match:
            return int(future_match.group(1))
        
        return 1
    
    def _record_execution(self, skill_name: str, user_input: str, result: Any):
        """记录执行历史"""
        if skill_name not in self.execution_history:
            self.execution_history[skill_name] = []
        
        self.execution_history[skill_name].append({
            'input': user_input,
            'result': result,
            'timestamp': datetime.datetime.now()
        })
    
    def get_execution_history(self, skill_name: Optional[str] = None) -> Dict[str, list]:
        """获取执行历史"""
        if skill_name:
            return {skill_name: self.execution_history.get(skill_name, [])}
        return self.execution_history
    
    def clear_execution_history(self, skill_name: Optional[str] = None):
        """清除执行历史"""
        if skill_name:
            if skill_name in self.execution_history:
                self.execution_history[skill_name] = []
        else:
            self.execution_history = {}