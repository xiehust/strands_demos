from strands import tool
from strands.hooks import HookProvider,HookRegistry,AfterToolCallEvent,MessageAddedEvent,BeforeModelCallEvent
import os
import re
import traceback
import logging

# 配置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



skill_prompt_template="""
Execute a skill within the main conversation

<skills_instructions>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke skills using this tool with the skill name only (no arguments)
- When you invoke a skill, you will see <command-message>The \"{{name}}\" skill is loading</command-message>
- The skill's prompt will expand and provide detailed instructions on how to complete the task
- Examples:
  - `command: "pdf"` - invoke the pdf skill
  - `command: "xlsx"` - invoke the xlsx skill
  - `command: "ms-office-suite:pdf"` - invoke using fully qualified name

Important:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already running
- Do not use this tool for built-in CLI commands (like /help, /clear, etc.)
</skills_instructions>

<available_skills>
{skills}
<available_skills>
"""

template = \
"""
<skill>
<name>
{name}
</name>
<description>
{desc}
</description>
</skill>"""

ROOT=os.path.dirname(__file__)
SKILLS_ROOT = os.path.join(ROOT , "skills")




        

def init_skills() ->str:
    logger.info("🚀 开始初始化技能系统...")
    skills = []
    try:
        # list all sub folders in skills with contains SKILL.md
        skill_root_path = SKILLS_ROOT
        logger.info(f"📁 扫描技能目录: {skill_root_path}")
        sub_folders = os.listdir(skill_root_path)
        logger.info(f"📋 发现 {len(sub_folders)} 个子目录")
        
        for sub_folder in sub_folders:
            if not os.path.isdir(os.path.join(skill_root_path,sub_folder)):
                continue
            if sub_folder.startswith('.'):
                continue
            path = os.path.join(skill_root_path,sub_folder,"SKILL.md")
            logger.info(f"🔍 正在处理技能: {sub_folder}")
            
            # Read the skill file
            with open(path, 'r', encoding='utf-8') as f:
                skill_content = f.read()

            # Parse YAML frontmatter (basic parsing)
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', skill_content, re.DOTALL)

            if not frontmatter_match:
                logger.error(f"❌ 技能 '{sub_folder}' 格式无效，缺少YAML前置内容")
                continue

            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2)

            # Parse the name and description from YAML (simple parsing)
            name_match = re.search(r'name:\s*(.+)', yaml_content)
            desc_match = re.search(r'description:\s*(.+)', yaml_content)

            skill_name = name_match.group(1).strip() if name_match else sub_folder
            skill_desc = desc_match.group(1).strip() if desc_match else "No description available"
            
            skills.append(template.format(name=skill_name,desc=skill_desc))
            logger.info(f"✅ 成功加载技能: {skill_name} - {skill_desc}")
            
        logger.info(f"🎉 技能初始化完成！共加载 {len(skills)} 个技能")
        return "".join(skills) if skills else ""
            
    except Exception as e:
        logger.error(f"💥 技能初始化失败: {str(e)}")
        traceback.print_exc()
        return ""


def load_skill(command:str) -> str:
    logger.info(f"🎯 开始加载技能: {command}")
    try:
        skill_root_path = SKILLS_ROOT
        path = os.path.join(skill_root_path,command,"SKILL.md")
        logger.info(f"📄 读取技能文件: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            skill_content = f.read()
        # Parse YAML frontmatter (basic parsing)
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', skill_content, re.DOTALL)

        if not frontmatter_match:
            logger.error(f"❌ 技能 '{command}' 格式无效，缺少YAML前置内容")
            return [ {
                "text": f"<command-message>The \"{command}\" skill launching failed</command-message>\n<command-name>{command}</command-name>"
            }]
        markdown_content = frontmatter_match.group(2)
        logger.info(f"✅ 技能 '{command}' 加载成功，内容长度: {len(markdown_content)} 字符")
        return [{
                    "text": f"<command-message>The \"{command}\" skill is running</command-message>\n<command-name>{command}</command-name>"
                },
                {
                     "text": f"Base directory for this skill: {os.path.join(skill_root_path,command)}\n\n{markdown_content}"
                }]
    except Exception as e:
        logger.error(f"💥 技能 '{command}' 加载失败: {str(e)}")
        return [ {
            "text": f"<command-message>The \"{command}\" skill launching failed</command-message>\n<command-name>{command}</command-name>"
          }]
        
def generate_skill_tool():
    logger.info("🔧 开始生成技能工具...")
    skills_desc = init_skills()
    if not skills_desc:
        logger.warning("⚠️ 没有找到可用的技能，跳过工具生成")
        return None
    
    logger.info("🛠️ 创建动态技能函数...")
    def dynamic_func(command: str) -> str:
       logger.info(f"🚀 执行技能命令: {command}")
       return f"Launching skill: {command}"
    
    # 设置函数属性
    function_name = "Skill"
    dynamic_func.__name__ = function_name
    dynamic_func.__qualname__ = function_name
    dynamic_func.__doc__ = skill_prompt_template.format(skills=skills_desc)
    # 应用工具装饰器
    decorated_func = tool(dynamic_func)
    globals()[function_name] = decorated_func
    logger.info(f"✅ 技能工具 '{function_name}' 生成完成")
    return decorated_func


class SkillToolInterceptor(HookProvider):
    def __init__(self):
        super().__init__()
        self.tooluse_ids = {}
        logger.info("🎣 技能工具拦截器初始化完成")
    
    def register_hooks(self, registry: HookRegistry) -> None:
        logger.info("📌 注册技能工具钩子...")
        registry.add_callback(AfterToolCallEvent,self.add_skill_content)
        registry.add_callback(MessageAddedEvent,self.add_skill_message)
        registry.add_callback(BeforeModelCallEvent,self.add_message_cache)
        logger.info("✅ 所有钩子注册完成")
    
    # load skill content
    def add_skill_content(self, event: AfterToolCallEvent) -> None:
        logger.info(f"🔧 工具调用事件: {event.tool_use['name']}")
        # print(f"\n#Tool use:{event.tool_use['name']}\n")
        if event.tool_use['name'] == 'Skill':
            command = event.tool_use['input']['command']
            logger.info(f"🎯 处理技能命令: {command}")
            self.tooluse_ids[event.tool_use['toolUseId']] = load_skill(command)
            # logger.info(f"📝 技能内容已缓存，工具ID: {event.tool_use['toolUseId']}")
        # elif event.tool_use['name'] == 'AskUserQuestion':
        #     print(f"AskUserQuestion tool_use:{event.tool_use}")
            
     # add skill block in the followed content block of tool result
    def add_skill_message(self, event: MessageAddedEvent) -> None:
        if event.message['role'] == 'user':
            # logger.info("👤 处理用户消息事件...")
            for block in event.message['content']:
                if 'toolResult' in block:
                    tooluse_id = block['toolResult']['toolUseId']
                    skill_content = self.tooluse_ids.get(tooluse_id)
                    # print(f"MessageAddedEvent skill_content:{skill_content}")
                    if skill_content:
                        event.message['content'] += skill_content
                        self.tooluse_ids.pop(tooluse_id)
                        logger.info(f"✅ 技能内容已添加到消息，工具ID: {tooluse_id}")
                        break

            
    def add_message_cache(self, event:BeforeModelCallEvent) -> None:
        # logger.info("💾 处理模型调用前缓存事件...")
        # print("==========BeforeModelCallEvent=========\n")
        for message in event.agent.messages:
            content = message['content']
            if any(['cachePoint' in block for block in content]):
                content = content[:-1]
                message['content'] = content
        
        #add prompt cache to last message
        if event.agent.messages:
            event.agent.messages[-1]['content'] += [{
                "cachePoint": {
                    "type": "default"
                }
            }]
            # logger.info("✅ 缓存点已添加到最后一条消息")