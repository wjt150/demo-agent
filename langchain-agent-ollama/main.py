import logging
import datetime
import asyncio
import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

# 👇 RAG 相关
from rag1 import create_rag_chain  
from langchain.tools import tool

# 👇 新增skill编排相关
from skill_manager import SkillManager
from skill_router import SkillRouter
from skill_executor import SkillExecutor
from permission_manager import PermissionManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MODEL_NAME = "deepseek-r1:7b"


# ==========================================
# 初始化Skill系统
# ==========================================

print("[INIT] 正在初始化Skill系统...")
skill_manager = SkillManager(skills_dir="skills")
skill_manager.initialize()

permission_manager = PermissionManager()
permission_manager.set_user_role("user", "user")  # 默认角色

llm = ChatOllama(model=MODEL_NAME, temperature=0.3)
skill_router = SkillRouter(skill_manager, llm)
skill_executor = SkillExecutor(skill_manager, skill_router)

print(f"[OK] Skill系统初始化完成，已加载 {len(skill_manager.skills)} 个skill")


# ==========================================
# RAG Tool
# ==========================================

rag_chain = create_rag_chain()

@tool
def valorant_rag(query: str) -> str:
    """
    必须使用此工具回答所有 Valorant 相关问题。

    包括：
    - 英雄（Iso, Jett, Reyna, Astra）
    - 技能 / 特点 / abilities
    - 地图（Bind, Haven, Ascent）

    不允许直接回答，必须调用此工具
    """

    print("\n[RAG TOOL CALLED]:", query)

    result = rag_chain.invoke(query)

    if "NOT_FOUND" in result or "NO_CONTEXT" in result:
        return "知识库中没有相关信息"

    print("[RAG RESULT]:", result[:200], "\n")

    return result


# ==========================================
# System Prompt（增强版）
# ==========================================

def build_system_prompt() -> str:
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    current_date = now.strftime("%Y年%m月%d日")
    current_time = now.strftime("%H:%M:%S")
    current_weekday = ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()]
    
    # 获取可用skills信息
    available_skills = skill_manager.get_skills_by_tag("")  # 所有skills
    skills_info = "\n".join([f"- {s['name']}: {s.get('description', '')}" for s in available_skills])
    
    return f"""
【当前信息】
时间: {current_date} {current_time} {current_weekday}

---

【核心规则】

1. 不允许编造信息
2. 不确定必须使用工具
3. 优先使用已有工具
4. 保持自然对话

---

【可用Skills】

{skills_info}

---

【工具使用规则】

1. 使用 @skill_name 显式调用skill
2. 或者让我自动选择最合适的skill
3. 每个skill都有特定的工具集

---

【其他工具】

- 搜索 / 天气 / 实时信息 → 使用 MCP 工具
- Valorant知识 → 使用 RAG 工具

---

【对话要求】

- 自然表达
- 不机械
- 有逻辑
"""


# ==========================================
# Router（增强版）
# ==========================================

def is_valorant_query(q: str):
    q = q.lower()
    return any(x in q for x in [
        "valorant", "iso", "jett", "reyna", "astra",
        "技能", "英雄", "地图"
    ])


# ==========================================
# 帮助文本
# ==========================================

HELP_TEXT = """
╔══════════════════════════════════════════════════════════════╗
║                      可用命令                                ║
╠══════════════════════════════════════════════════════════════╣
║  exit / quit  - 退出程序                                     ║
║  clear        - 清屏                                         ║
║  help         - 显示此帮助信息                                ║
║  skills       - 列出所有可用 skill                            ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║                      可用 Skills                             ║
╠══════════════════════════════════════════════════════════════╣
║  @weather 城市           - 查询天气                          ║
║  @web_search 关键词      - 搜索信息                          ║
║  @valorant_rag 问题      - 查询 Valorant 知识库              ║
║  @custom_example 内容    - 自定义示例                        ║
║  @demonstration 内容     - 演示功能                          ║
╚══════════════════════════════════════════════════════════════╝

提示: 直接输入问题会自动选择最合适的 skill
"""


# ==========================================
# 主程序（增强版）
# ==========================================

async def main():
    print("[START] Agent + RAG + Skill系统启动")
    print("=" * 50)

    # MCP 工具
    client = MultiServerMCPClient({
        "mytools": {
            "command": "python",
            "args": ["mcpserver.py"],
            "transport": "stdio",
        }
    })

    mcp_tools = await client.get_tools()
    logger.info("MCP工具: %s", [t.name for t in mcp_tools])

    # 注册工具到skill executor
    skill_executor.register_tools(mcp_tools, valorant_rag)

    # 👇 加入 RAG Tool
    tools = mcp_tools + [valorant_rag]

    # LLM（统一模型）
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=build_system_prompt(),
        checkpointer=InMemorySaver()
    )

    config = {"configurable": {"thread_id": "user"}}

    print("\n[READY] 已就绪，输入 help 查看帮助，exit 退出")
    print("[TIP] 提示：使用 @skill_name 显式调用skill，或让我自动选择")
    print("=" * 50)

    while True:
        query = input("\n❓ 问题: ")

        # 命令处理
        if query.lower() in ["exit", "quit"]:
            print("再见！")
            break
        
        if query.lower() == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        
        if query.lower() == "help":
            print(HELP_TEXT)
            continue
        
        if query.lower() == "skills":
            print("\n[SKILLS] 可用 Skills 列表:")
            for name, skill in skill_manager.skills.items():
                desc = skill.get('description', '无描述')
                tools = skill.get('tools', [])
                print(f"  @{name}: {desc}")
                print(f"    工具: {', '.join(tools)}")
            print()
            continue
        
        # 检查显式skill调用
        if '@' in query or '/' in query:
            print("\n[DETECT] 检测到显式skill调用")
            skill_result = await skill_executor.execute(query)
            if skill_result:
                print("\n[ANSWER] 回答:")
                print(skill_result)
                print("\n" + "="*50 + "\n")
                continue
        
        # Router（关键！）
        if is_valorant_query(query):
            print("\n[RAG] 直接走 RAG（强制）")
            result = valorant_rag.invoke(query)
        else:
            # 尝试skill自动路由
            print("\n[AUTO] 尝试skill自动路由...")
            skill_result = await skill_executor.execute(query)
            
            if skill_result:
                result = skill_result
            else:
                # 回退到原有Agent逻辑
                result = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": query}]},
                    config=config
                )
                
                try:
                    result = result["messages"][-1].content
                except Exception:
                    result = str(result)

        print("\n[ANSWER] 回答:")
        print(result)
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())