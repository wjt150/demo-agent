import re
from typing import Dict, List, Optional, Tuple
from skill_manager import SkillManager
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

class SkillRouter:
    def __init__(self, skill_manager: SkillManager, llm: ChatOllama):
        self.skill_manager = skill_manager
        self.llm = llm
        self.routing_prompt = self._create_routing_prompt()
    
    def _create_routing_prompt(self) -> PromptTemplate:
        """创建路由提示词"""
        skills_info = self._get_skills_info()
        
        return PromptTemplate.from_template(f"""
你是一个Skill路由器。根据用户输入，选择最合适的skill。

可用的skills：
{skills_info}

用户输入：{{user_input}}

请返回最合适的skill名称（只返回名称，不要其他内容）。
如果不需要任何skill，返回"none"。
""")
    
    def _get_skills_info(self) -> str:
        """获取所有skill信息"""
        info_lines = []
        for skill_name, skill in self.skill_manager.skills.items():
            desc = skill.get('description', '无描述')
            tags = ', '.join(skill.get('tags', []))
            info_lines.append(f"- {skill_name}: {desc} (标签: {tags})")
        return '\n'.join(info_lines)
    
    def route(self, user_input: str) -> Tuple[Optional[str], bool]:
        """
        路由用户输入到合适的skill
        返回: (skill_name, is_explicit)
        """
        # 1. 检查显式指定
        explicit_skill = self._check_explicit_specification(user_input)
        if explicit_skill:
            return explicit_skill, True
        
        # 2. LLM自动选择
        auto_skill = self._auto_route(user_input)
        return auto_skill, False
    
    def _check_explicit_specification(self, user_input: str) -> Optional[str]:
        """检查显式指定的skill"""
        # 支持格式：@skill_name 或 /skill_name
        patterns = [
            r'@(\w+)',
            r'/(\w+)',
            r'使用(\w+)skill',
            r'调用(\w+)工具',
            r'用(\w+)查询',
            r'通过(\w+)获取'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                skill_name = match.group(1)
                if self.skill_manager.get_skill(skill_name):
                    return skill_name
        return None
    
    def _auto_route(self, user_input: str) -> Optional[str]:
        """LLM自动路由"""
        try:
            response = self.llm.invoke(
                self.routing_prompt.format(user_input=user_input)
            )
            skill_name = response.content.strip()
            
            if skill_name == "none" or not self.skill_manager.get_skill(skill_name):
                return None
            
            return skill_name
        except Exception as e:
            print(f"LLM路由失败: {e}")
            return None
    
    def get_available_skills_for_input(self, user_input: str) -> List[str]:
        """获取用户输入可用的skill列表"""
        available = []
        
        # 检查显式指定
        explicit_skill = self._check_explicit_specification(user_input)
        if explicit_skill:
            available.append(explicit_skill)
        
        # 根据关键词匹配（扩展版）
        keywords_map = {
            'web_search': ['搜索', '查找', '查询', '搜', '找', '最新', '新闻', '信息', '资料'],
            'weather': ['天气', '气温', '温度', '下雨', '晴天', '阴天', '气候', '预报'],
            'valorant_rag': ['valorant', '英雄', '技能', '地图', '游戏', '攻略', '角色'],
            'custom_example': ['自定义', '示例', '模板', 'demo', '学习', '测试'],
            'demo_skill': ['演示', '展示', '功能', '展示', '示范']
        }
        
        for skill_name, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword in user_input.lower():
                    if skill_name not in available:
                        available.append(skill_name)
                    break
        
        return available