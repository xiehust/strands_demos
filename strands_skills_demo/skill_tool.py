from strands import tool
from strands.hooks import HookProvider,HookRegistry,AfterToolCallEvent,MessageAddedEvent,BeforeModelCallEvent
import os
import re
import traceback



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
    skills = []
    try:
        # list all sub folders in skills with contains SKILL.md
        skill_root_path = SKILLS_ROOT
        sub_folders = os.listdir(skill_root_path)
        for sub_folder in sub_folders:
            if not os.path.isdir(os.path.join(skill_root_path,sub_folder)):
                continue
            if sub_folder.startswith('.'):
                continue
            path = os.path.join(skill_root_path,sub_folder,"SKILL.md")
            # Read the skill file
            with open(path, 'r', encoding='utf-8') as f:
                skill_content = f.read()

            # Parse YAML frontmatter (basic parsing)
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', skill_content, re.DOTALL)

            if not frontmatter_match:
                print(f"Error: Skill '{sub_folder}' has invalid format. Missing YAML frontmatter.")
                continue

            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2)

            # Parse the name and description from YAML (simple parsing)
            name_match = re.search(r'name:\s*(.+)', yaml_content)
            desc_match = re.search(r'description:\s*(.+)', yaml_content)

            skill_name = name_match.group(1).strip() if name_match else sub_folder
            skill_desc = desc_match.group(1).strip() if desc_match else "No description available"
            
            skills.append(template.format(name=skill_name,desc=skill_desc))
            
        return "".join(skills) if skills else ""
            
    except Exception as e:
        print(f"init skills/ failed, {str(e)}")
        traceback.print_exc()
        return ""


def load_skill(command:str) -> str:
    try:
        skill_root_path = SKILLS_ROOT
        path = os.path.join(skill_root_path,command,"SKILL.md")
        with open(path, 'r', encoding='utf-8') as f:
            skill_content = f.read()
        # Parse YAML frontmatter (basic parsing)
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', skill_content, re.DOTALL)

        if not frontmatter_match:
            print(f"Error: Skill '{path}' has invalid format. Missing YAML frontmatter.")
            return [ {
                "text": f"<command-message>The \"{command}\" skill launching faied</command-message>\n<command-name>{command}</command-name>"
            }]
        markdown_content = frontmatter_match.group(2)
        return [{
                    "text": f"<command-message>The \"{command}\" skill is running</command-message>\n<command-name>{command}</command-name>"
                },
                {
                     "text": f"Base directory for this skill: {os.path.join(skill_root_path,command)}\n\n{markdown_content}"
                }]
    except Exception as e:
        return [ {
            "text": f"<command-message>The \"{command}\" skill launching faied</command-message>\n<command-name>{command}</command-name>"
          }]
        
def generate_skill_tool():
    skills_desc = init_skills()
    if not skills_desc:
        return None
    
    def dynamic_func(command: str) -> str:
       return f"Launching skill: {command}"
    
    # 设置函数属性
    function_name = "Skill"
    dynamic_func.__name__ = function_name
    dynamic_func.__qualname__ = function_name
    dynamic_func.__doc__ = skill_prompt_template.format(skills=skills_desc)
    # 应用工具装饰器
    decorated_func = tool(dynamic_func)
    globals()[function_name] = decorated_func
    return decorated_func


class SkillToolInterceptor(HookProvider):
    def __init__(self):
        super().__init__()
        self.tooluse_ids = {}
    
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterToolCallEvent,self.add_skill_content)
        registry.add_callback(MessageAddedEvent,self.add_skill_message)
        registry.add_callback(BeforeModelCallEvent,self.add_message_cache)
    
    # load skill content
    def add_skill_content(self, event: AfterToolCallEvent) -> None:
        print(f"\n#Tool use:{event.tool_use['name']}\n")
        if event.tool_use['name'] == 'Skill':
            command = event.tool_use['input']['command']
            self.tooluse_ids[event.tool_use['toolUseId']] = load_skill(command)
        # elif event.tool_use['name'] == 'AskUserQuestion':
        #     print(f"AskUserQuestion tool_use:{event.tool_use}")
            
     # add skill block in the followed content block of tool result
    def add_skill_message(self, event: MessageAddedEvent) -> None:
        if event.message['role'] == 'user':
            for block in event.message['content']:
                if 'toolResult' in block:
                    tooluse_id = block['toolResult']['toolUseId']
                    skill_content = self.tooluse_ids.get(tooluse_id)
                    # print(f"MessageAddedEvent skill_content:{skill_content}")
                    if skill_content:
                        event.message['content'] += skill_content
                        self.tooluse_ids.pop(tooluse_id)
                        break

            
    def add_message_cache(self, event:BeforeModelCallEvent) -> None:
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