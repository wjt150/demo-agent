import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class SkillLoader:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_cache: Dict[str, dict] = {}
    
    def discover_skills(self) -> List[str]:
        """发现所有可用的skill"""
        skills = []
        if not self.skills_dir.exists():
            return skills
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skills.append(skill_dir.name)
        return skills
    
    def load_skill(self, skill_name: str) -> Optional[dict]:
        """加载单个skill"""
        if skill_name in self.skills_cache:
            return self.skills_cache[skill_name]
        
        skill_file = self.skills_dir / skill_name / "SKILL.md"
        if not skill_file.exists():
            return None
        
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    markdown_content = parts[2]
                    
                    skill_config = yaml.safe_load(yaml_content)
                    if skill_config is None:
                        skill_config = {}
                    
                    skill_config['content'] = markdown_content
                    skill_config['name'] = skill_name
                    
                    # 确保 execution 字段存在
                    if 'execution' not in skill_config:
                        skill_config['execution'] = {
                            'type': 'generic',
                            'steps': ['处理用户输入', '返回结果'],
                            'output_format': '返回处理结果'
                        }
                    
                    self.skills_cache[skill_name] = skill_config
                    return skill_config
            
            return None
        except Exception as e:
            print(f"加载skill {skill_name} 失败: {e}")
            return None
    
    def load_all_skills(self) -> Dict[str, dict]:
        """加载所有skill"""
        skills = {}
        for skill_name in self.discover_skills():
            skill = self.load_skill(skill_name)
            if skill:
                skills[skill_name] = skill
        return skills
    
    def reload_skill(self, skill_name: str) -> Optional[dict]:
        """重新加载单个skill"""
        if skill_name in self.skills_cache:
            del self.skills_cache[skill_name]
        return self.load_skill(skill_name)
    
    def get_skill_names(self) -> List[str]:
        """获取所有skill名称"""
        return self.discover_skills()