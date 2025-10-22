from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from strands import tool
import os

class Option(BaseModel):
    label: str = Field(
        ...,
        description="The display text for this option that the user will see and select. Should be concise (1-5 words) and clearly describe the choice."
    )
    description: str = Field(
        ...,
        description="Explanation of what this option means or what will happen if chosen. Useful for providing context about trade-offs or implications."
    )

class Question(BaseModel):
    question: str = Field(
        ...,
        description='The complete question to ask the user. Should be clear, specific, and end with a question mark.'
    )
    header: str = Field(
        ...,
        max_length=12,
        description='Very short label displayed as a chip/tag (max 12 chars).'
    )
    options: List[Option] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="The available choices for this question. Must have 2-4 options."
    )
    multiSelect: bool = Field(
        ...,
        description="Set to true to allow the user to select multiple options instead of just one."
    )

class AskUserInput(BaseModel):
    questions: List[Question] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Questions to ask the user (1-4 questions)"
    )
    answers: Optional[Dict[str, str]] = Field(
        default=None,
        description="User answers collected by the permission component"
    )
    
    
@tool(name="AskUserQuestion",
      inputSchema={"json":{
        "type":"object",
            "properties":{
               "questions":{
                  "type":"array",
                  "items":{
                     "type":"object",
                     "properties":{
                        "question":{
                           "type":"string",
                           "description":"The complete question to ask the user. Should be clear, specific, and end with a question mark. Example: \"Which library should we use for date formatting?\" If multiSelect is true, phrase it accordingly, e.g. \"Which features do you want to enable?\""
                        },
                        "header":{
                           "type":"string",
                           "description":"Very short label displayed as a chip/tag (max 12 chars). Examples: \"Auth method\", \"Library\", \"Approach\"."
                        },
                        "options":{
                           "type":"array",
                           "items":{
                              "type":"object",
                              "properties":{
                                 "label":{
                                    "type":"string",
                                    "description":"The display text for this option that the user will see and select. Should be concise (1-5 words) and clearly describe the choice."
                                 },
                                 "description":{
                                    "type":"string",
                                    "description":"Explanation of what this option means or what will happen if chosen. Useful for providing context about trade-offs or implications."
                                 }
                              },
                              "required":[
                                 "label",
                                 "description"
                              ],
                           },
                           "minItems":2,
                           "maxItems":4,
                           "description":"The available choices for this question. Must have 2-4 options. Each option should be a distinct, mutually exclusive choice (unless multiSelect is enabled). There should be no 'Other' option, that will be provided automatically."
                        },
                        "multiSelect":{
                           "type":"boolean",
                           "description":"default is false. Set to true to allow the user to select multiple options instead of just one. Use when choices are not mutually exclusive."
                        }
                     },
                     "required":[
                        "question",
                        "header",
                        "options",
                        "multiSelect"
                     ],
                  },
                  "minItems":1,
                  "maxItems":4,
                  "description":"Questions to ask the user (1-4 questions)"
               }
            },
            "required":[
               "questions"
            ]
    }}
    )
def ask_user(questions:List[Question]) ->dict:
    """Use this tool when you need to ask the user questions during execution. This allows you to:
1. Gather user preferences or requirements
2. Clarify ambiguous instructions
3. Get decisions on implementation choices as you work
4. Offer choices to the user about what direction to take.

Usage notes:
- Users will always be able to select \"Other\" to provide custom text input
- Use multiSelect: true to allow multiple answers to be selected for a question
"""

    print("\n" + "="*60)
    print(f"QUESTIONS FOR USER:{questions}")
    print("="*60)
    answers = {}
        
    for i, q in enumerate(questions):
        q = Question(**q)
        print(f"\n{'─'*60}")
        print(f"[{q.header}]")
        print(f"Q{i+1}: {q.question}")
        print(f"{'─'*60}")
        
        if q.multiSelect:
            print("(You can select multiple options)")
        else:
            print("(Select one option)")
        
        print("\nOptions:")
        for j, opt in enumerate(q.options, start=1):
            print(f"  {j}. {opt.label}")
            print(f"     {opt.description}")
        
        # Get user input
        while True:
            try:
                if q.multiSelect:
                    user_input = input(f"\nEnter your choice(s) [1-{len(q.options)}] (comma-separated, e.g., 1,3): ").strip()
                    
                    # Parse multiple selections
                    if not user_input:
                        print("❌ Please enter at least one selection.")
                        continue
                    
                    # Split by comma or space
                    selections = [s.strip() for s in user_input.replace(',', ' ').split()]
                    
                    try:
                        selected_indices = [int(s) for s in selections]
                    except ValueError:
                        print("❌ Please enter valid numbers.")
                        continue
                    
                    # Validate range
                    if not all(1 <= idx <= len(q.options) for idx in selected_indices):
                        print(f"❌ Please enter numbers between 1 and {len(q.options)}.")
                        continue
                    
                    # Remove duplicates and get labels
                    selected_indices = list(set(selected_indices))
                    selected_labels = [q.options[idx-1].label for idx in selected_indices]
                    answer = ", ".join(selected_labels)
                    
                    print(f"✓ Selected: {answer}")
                    
                else:
                    # Single select
                    user_input = input(f"\nEnter your choice [1-{len(q.options)}]: ").strip()
                    
                    if not user_input:
                        print("❌ Please enter a selection.")
                        continue
                    
                    try:
                        selected_idx = int(user_input)
                    except ValueError:
                        print("❌ Please enter a valid number.")
                        continue
                    
                    if not (1 <= selected_idx <= len(q.options)):
                        print(f"❌ Please enter a number between 1 and {len(q.options)}.")
                        continue
                    
                    answer = q.options[selected_idx - 1].label
                    print(f"✓ Selected: {answer}")
                
                # Store answer with sanitized key
                answer_key = q.header.lower().replace(" ", "_")
                answers[answer_key] = answer
                break
                
            except KeyboardInterrupt:
                print("\n\n❌ User cancelled input.")
                return {
                    "status": "success",
                    "content": [{"text":"User cancelled the question prompt"}] 
                }
    
    print("\n" + "="*60)
    print(f"✅ Collected {len(answers)} answer(s)")
    print("="*60 + "\n")
    
    return {
        "status": "success",
        "content": [{"json":answers}] 
    }
    

if __name__ == "__main__":
    test = {'questions': [{'question': '你想创建什么主题的演示文稿？', 'header': '演示主题', 'options': [{'label': '工作报告', 'description': '项目进展、团队总结、业绩汇报等'}, {'label': '学习教程', 'description': '知识讲解、步骤说明、学习资料'}, {'label': '产品介绍', 'description': '产品功能、特点、优势展示'}, {'label': '其他内容', 'description': '自定义内容'}], 'multiSelect': False}, {'question': '你希望演示文稿包含多少页？', 'header': '页数', 'options': [{'label': '简短版（3-5页）', 'description': '精简内容，快速呈现'}, {'label': '标准版（6-10页）', 'description': '适中内容，详细说明'}, {'label': '完整版（10页+）', 'description': '全面内容，深入讲解'}], 'multiSelect': False}]}
    inputtest = AskUserInput(**test)
    print(ask_user(test))