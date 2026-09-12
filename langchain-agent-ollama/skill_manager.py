from typing import Dict, List, Optional, Any
from skill_loader import SkillLoader
from langchain.tools import tool

class SkillManager:
    def __init__(self, skills_dir: str = "skills"):
        self.loader = SkillLoader(skills_dir)
        self.skills: Dict[str, dict] = {}
        self.tools: Dict[str, Any] = {}
        self.permissions: Dict[str, List[str]] = {}
        
    def initialize(self):
        """初始化skill管理器"""
        self.skills = self.loader.load_all_skills()
        self._build_tool_registry()
        self._load_permissions()
        print(f"[OK] 已加载 {len(self.skills)} 个skill")
    
    def _build_tool_registry(self):
        """构建工具注册表"""
        for skill_name, skill in self.skills.items():
            if 'tools' in skill:
                for tool_ref in skill['tools']:
                    # 解析工具引用，如 "mcp.web_search"
                    parts = tool_ref.split('.')
                    if len(parts) == 2:
                        source, tool_name = parts
                        # 这里可以注册工具引用
                        self.tools[f"{skill_name}.{tool_name}"] = {
                            'source': source,
                            'name': tool_name,
                            'skill': skill_name
                        }
    
    def _load_permissions(self):
        """加载权限配置"""
        for skill_name, skill in self.skills.items():
            if 'permissions' in skill:
                self.permissions[skill_name] = skill['permissions']
    
    def get_skill(self, skill_name: str) -> Optional[dict]:
        """获取skill信息"""
        return self.skills.get(skill_name)
    
    def get_skills_by_tag(self, tag: str) -> List[dict]:
        """根据标签获取skill"""
        if not tag:
            return list(self.skills.values())
        
        result = []
        for skill in self.skills.values():
            if 'tags' in skill and tag in skill['tags']:
                result.append(skill)
        return result
    
    def get_tools_for_skill(self, skill_name: str) -> List[str]:
        """获取skill使用的工具"""
        skill = self.get_skill(skill_name)
        if skill and 'tools' in skill:
            return skill['tools']
        return []
    
    def check_permission(self, skill_name: str, permission: str) -> bool:
        """检查权限"""
        if skill_name not in self.permissions:
            return True  # 默认允许
        
        required_permissions = self.permissions[skill_name]
        return permission in required_permissions
    
    def get_all_skill_names(self) -> List[str]:
        """获取所有skill名称"""
        return list(self.skills.keys())
    
    def get_skill_descriptions(self) -> Dict[str, str]:
        """获取所有skill描述"""
        descriptions = {}
        for skill_name, skill in self.skills.items():
            descriptions[skill_name] = skill.get('description', '无描述')
        return descriptions