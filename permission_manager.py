import yaml
from typing import Dict, List, Optional
from pathlib import Path

class PermissionManager:
    def __init__(self, config_path: str = "permissions.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.user_roles: Dict[str, str] = {}
    
    def _load_config(self) -> dict:
        """加载权限配置"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                'permissions': {
                    'network': {
                        'description': '网络访问权限',
                        'tools': ['web_search', 'fetch_page']
                    },
                    'weather': {
                        'description': '天气服务权限',
                        'tools': ['get_weather']
                    },
                    'rag': {
                        'description': 'RAG检索权限',
                        'tools': ['valorant_rag']
                    },
                    'file_system': {
                        'description': '文件系统权限',
                        'tools': ['read', 'write', 'edit']
                    }
                },
                'roles': {
                    'user': {
                        'permissions': ['network', 'weather', 'rag']
                    },
                    'admin': {
                        'permissions': ['network', 'weather', 'rag', 'file_system']
                    },
                    'readonly': {
                        'permissions': ['rag']
                    }
                },
                'skill_permissions': {
                    'web_search': {
                        'required': ['network']
                    },
                    'weather': {
                        'required': ['weather']
                    },
                    'valorant_rag': {
                        'required': ['rag']
                    }
                }
            }
            
            # 保存默认配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
            
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载权限配置失败: {e}")
            return {'permissions': {}, 'roles': {}, 'skill_permissions': {}}
    
    def set_user_role(self, user_id: str, role: str):
        """设置用户角色"""
        self.user_roles[user_id] = role
    
    def check_permission(self, user_id: str, skill_name: str) -> bool:
        """检查用户是否有权限执行指定skill"""
        # 获取用户角色
        role = self.user_roles.get(user_id, 'user')
        
        # 获取角色权限
        role_permissions = self.config.get('roles', {}).get(role, {}).get('permissions', [])
        
        # 获取skill所需权限
        skill_permissions = self.config.get('skill_permissions', {}).get(skill_name, {}).get('required', [])
        
        # 检查是否拥有所有所需权限
        return all(perm in role_permissions for perm in skill_permissions)
    
    def get_available_skills(self, user_id: str) -> List[str]:
        """获取用户可用的skill列表"""
        role = self.user_roles.get(user_id, 'user')
        role_permissions = self.config.get('roles', {}).get(role, {}).get('permissions', [])
        
        available_skills = []
        for skill_name, skill_config in self.config.get('skill_permissions', {}).items():
            required = skill_config.get('required', [])
            if all(perm in role_permissions for perm in required):
                available_skills.append(skill_name)
        
        return available_skills
    
    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色权限"""
        return self.config.get('roles', {}).get(role, {}).get('permissions', [])
    
    def get_skill_requirements(self, skill_name: str) -> List[str]:
        """获取skill所需权限"""
        return self.config.get('skill_permissions', {}).get(skill_name, {}).get('required', [])
    
    def add_permission(self, permission_name: str, description: str, tools: List[str]):
        """添加新权限"""
        self.config['permissions'][permission_name] = {
            'description': description,
            'tools': tools
        }
        self._save_config()
    
    def add_role(self, role_name: str, permissions: List[str]):
        """添加新角色"""
        self.config['roles'][role_name] = {
            'permissions': permissions
        }
        self._save_config()
    
    def add_skill_permission(self, skill_name: str, required_permissions: List[str]):
        """添加skill权限要求"""
        self.config['skill_permissions'][skill_name] = {
            'required': required_permissions
        }
        self._save_config()
    
    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"保存权限配置失败: {e}")