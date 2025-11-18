#!/usr/bin/env python3
"""
Example usage of the Code Execution MCP Server

This demonstrates how an agent would interact with the MCP server
using the code execution pattern.
"""

import json


def example_1_progressive_discovery():
    """
    Example 1: Progressive Tool Discovery

    Instead of loading all tool definitions upfront, the agent
    discovers tools as needed.
    """
    print("=" * 60)
    print("Example 1: Progressive Tool Discovery")
    print("=" * 60)

    # Step 1: List categories (minimal tokens)
    print("\n[Agent] What tool categories are available?")
    print("[Tool Call] list_tool_categories()")
    print("""
[Result]
Available Tool Categories:

## filesystem
File and directory operations
Tools: 3

## data_processing
Data manipulation and analysis tools
Tools: 2

## skills
Manage and execute saved skills
Tools: 3
""")

    # Step 2: Search for relevant tools (only load what's needed)
    print("\n[Agent] I need to work with files. Search for file tools.")
    print("[Tool Call] search_tools(query='file', detail_level='summary')")
    print("""
[Result]
Found 3 tool(s) matching 'file':

## filesystem.read_file
Read content from a file

## filesystem.write_file
Write content to a file

## filesystem.list_directory
List contents of a directory
""")

    # Step 3: Get full details only for the tool needed
    print("\n[Agent] I need details on read_file.")
    print("[Tool Call] search_tools(query='read_file', detail_level='full')")
    print("""
[Result]
## filesystem.read_file
Read content from a file

**Parameters:**
  - `path`: str - Path to the file
  - `encoding`: str - File encoding (default: utf-8)

**Returns:** str - File content
""")

    print("\n✅ Token usage: ~500 tokens (vs 10,000+ for loading all tools)")


def example_2_context_efficient_processing():
    """
    Example 2: Context-Efficient Data Processing

    Large datasets are processed in the execution environment,
    not passed through the model context.
    """
    print("\n" + "=" * 60)
    print("Example 2: Context-Efficient Data Processing")
    print("=" * 60)

    print("\n[Scenario] Process a large JSON file with 10,000 records")
    print("[Agent] I'll write code to filter the data in the execution environment.")

    print("\n[Tool Call] execute_code(code='''")
    print("""
from tools.filesystem import read_file, write_file
import json

# Read large dataset (10,000 records, ~50,000 tokens if passed through context)
data = json.loads(read_file('large_dataset.json'))

# Filter in execution environment (data doesn't touch model context!)
active_users = [user for user in data if user['status'] == 'active']
premium_users = [user for user in active_users if user['tier'] == 'premium']

# Write filtered data
write_file('premium_users.json', json.dumps(premium_users, indent=2))

# Only return summary to model
print(f"Total users: {len(data)}")
print(f"Active users: {len(active_users)}")
print(f"Premium users: {len(premium_users)}")
print(f"Sample: {premium_users[:3]}")
''')
""")

    print("\n[Result]")
    print("""
✅ Code executed successfully

Output:
Total users: 10000
Active users: 3452
Premium users: 847
Sample: [
  {'id': 1, 'name': 'Alice', 'status': 'active', 'tier': 'premium'},
  {'id': 5, 'name': 'Bob', 'status': 'active', 'tier': 'premium'},
  {'id': 12, 'name': 'Carol', 'status': 'active', 'tier': 'premium'}
]
""")

    print("\n✅ Token usage: ~2,000 tokens")
    print("   (vs ~150,000 tokens if all data passed through context)")
    print("   Savings: 98.7%")


def example_3_control_flow():
    """
    Example 3: Complex Control Flow

    Use native Python control structures instead of
    chaining tool calls through the model.
    """
    print("\n" + "=" * 60)
    print("Example 3: Complex Control Flow")
    print("=" * 60)

    print("\n[Scenario] Poll a file until deployment completes")
    print("[Agent] I'll use a while loop with sleep in the execution environment.")

    print("\n[Tool Call] execute_code(code='''")
    print("""
import time
from tools.filesystem import read_file

print("Monitoring deployment status...")

max_attempts = 10
for attempt in range(1, max_attempts + 1):
    try:
        status = read_file('deployment_status.txt').strip()

        print(f"Attempt {attempt}: Status is '{status}'")

        if status == 'completed':
            print("✅ Deployment completed successfully!")
            break
        elif status == 'failed':
            print("❌ Deployment failed!")
            break
        elif attempt < max_attempts:
            print(f"Waiting 5 seconds before next check...")
            time.sleep(5)
    except Exception as e:
        print(f"Error checking status: {e}")
        break
else:
    print(f"⏱️ Timeout after {max_attempts} attempts")
''')
""")

    print("\n[Result]")
    print("""
✅ Code executed successfully

Output:
Monitoring deployment status...
Attempt 1: Status is 'in_progress'
Waiting 5 seconds before next check...
Attempt 2: Status is 'in_progress'
Waiting 5 seconds before next check...
Attempt 3: Status is 'in_progress'
Waiting 5 seconds before next check...
Attempt 4: Status is 'completed'
✅ Deployment completed successfully!
""")

    print("\n✅ Single execution with loop (30 seconds)")
    print("   vs 4 separate tool calls with agent loop (much slower)")


def example_4_privacy_preserving():
    """
    Example 4: Privacy-Preserving Operations

    Sensitive data flows through the execution environment
    without entering the model's context.
    """
    print("\n" + "=" * 60)
    print("Example 4: Privacy-Preserving Operations")
    print("=" * 60)

    print("\n[Scenario] Import customer PII data to CRM")
    print("[Agent] I'll process the PII in the execution environment.")
    print("        The model never sees the actual emails and phone numbers.")

    print("\n[Tool Call] execute_code(code='''")
    print("""
from tools.filesystem import read_file
import json

# Read customer data with PII
customers = json.loads(read_file('customers.json'))

# Process each customer (PII stays in execution environment)
updated_count = 0
for customer in customers:
    # In a real implementation, this would call a CRM API
    # The email and phone number never enter the model context
    success = update_crm(
        customer_id=customer['id'],
        email=customer['email'],      # PII - not logged
        phone=customer['phone'],      # PII - not logged
        name=customer['name']         # PII - not logged
    )

    if success:
        updated_count += 1

# Only return summary statistics
print(f"Processed {len(customers)} customers")
print(f"Successfully updated {updated_count} records")
print(f"Success rate: {updated_count / len(customers) * 100:.1f}%")
''')
""")

    print("\n[Result]")
    print("""
✅ Code executed successfully

Output:
Processed 1000 customers
Successfully updated 998 records
Success rate: 99.8%
""")

    print("\n✅ 1000 customers with PII processed")
    print("   Model only sees aggregate statistics")
    print("   PII never entered model context")


def example_5_skill_building():
    """
    Example 5: Building and Reusing Skills

    Agents can save useful code as skills for future reuse.
    """
    print("\n" + "=" * 60)
    print("Example 5: Building and Reusing Skills")
    print("=" * 60)

    print("\n[Scenario] Agent develops a useful data export function")
    print("\n--- First Time: Develop and Save ---")

    print("\n[Agent] Let me create a function to export filtered data.")
    print("\n[Tool Call] execute_code(code='''")
    print("""
def export_filtered_json(input_file, filter_key, filter_value, output_file):
    '''Export filtered JSON data to a file'''
    from tools.filesystem import read_file, write_file
    import json

    # Read data
    data = json.loads(read_file(input_file))

    # Filter
    filtered = [item for item in data if item.get(filter_key) == filter_value]

    # Export
    write_file(output_file, json.dumps(filtered, indent=2))

    return {
        'total': len(data),
        'filtered': len(filtered),
        'output': output_file
    }

# Test it
result = export_filtered_json('users.json', 'status', 'active', 'active_users.json')
print(f"Exported {result['filtered']}/{result['total']} items to {result['output']}")
''')
""")

    print("\n[Result]")
    print("""
✅ Code executed successfully
Output:
Exported 3452/10000 items to active_users.json
""")

    print("\n[Agent] This works great! Let me save it as a skill for future use.")
    print("\n[Tool Call] save_skill(")
    print("    name='export_filtered_json',")
    print("    code='''def export_filtered_json(...)...''',")
    print("    description='Export filtered JSON data'")
    print(")")

    print("\n[Result]")
    print("""
✅ Skill 'export_filtered_json' saved successfully

Location: ./agent_skills/export_filtered_json.py
Description: Export filtered JSON data

You can now use this skill in future executions by importing it:
```python
from tools.skills import load_skill
export_filtered_json = load_skill('export_filtered_json')
```
""")

    print("\n--- Later: Reuse the Skill ---")
    print("\n[Agent] I need to export premium users now.")
    print("\n[Tool Call] execute_code(code='''")
    print("""
from tools.skills import load_skill

# Load the saved skill
export_filtered_json = load_skill('export_filtered_json')

# Use it with different parameters
result = export_filtered_json('users.json', 'tier', 'premium', 'premium_users.json')
print(f"Exported {result['filtered']} premium users")
''')
""")

    print("\n[Result]")
    print("""
✅ Code executed successfully
Output:
Exported 847 premium users
""")

    print("\n✅ Skill reused without rewriting code")
    print("   Agent builds a library of reusable functions")


def example_6_comparison():
    """
    Example 6: Side-by-Side Comparison

    Direct comparison of traditional vs code execution approach.
    """
    print("\n" + "=" * 60)
    print("Example 6: Traditional vs Code Execution Comparison")
    print("=" * 60)

    print("\n--- Traditional Approach (Inefficient) ---")
    print("\n[Tool Call 1] read_file('data.json')")
    print("[Result] <50,000 tokens of data loaded into context>")
    print("\n[Tool Call 2] filter_data(data, status='active')")
    print("[Result] <25,000 tokens of filtered data in context>")
    print("\n[Tool Call 3] aggregate_data(filtered, 'category', 'sum')")
    print("[Result] <5,000 tokens of aggregated data in context>")
    print("\n[Tool Call 4] write_file('report.json', aggregated)")
    print("[Result] Success")

    print("\n📊 Traditional Approach Stats:")
    print("   - Tool calls: 4")
    print("   - Context tokens: ~80,000")
    print("   - Time: ~40 seconds (4 calls × 10s)")
    print("   - Cost: ~$0.24 (80k tokens)")

    print("\n--- Code Execution Approach (Efficient) ---")
    print("\n[Tool Call] execute_code(code='''")
    print("""
from tools.filesystem import read_file, write_file
from tools.data_processing import aggregate_data
import json

# All processing in execution environment
data = json.loads(read_file('data.json'))
filtered = [item for item in data if item['status'] == 'active']
aggregated = aggregate_data(filtered, 'category', 'sum')
write_file('report.json', json.dumps(aggregated, indent=2))

# Only summary to context
print(f"Processed: {len(data)} → {len(filtered)} items")
print(f"Categories: {len(aggregated)}")
print(f"Result: {aggregated}")
''')
""")
    print("\n[Result]")
    print("""
✅ Code executed successfully
Output:
Processed: 10000 → 3452 items
Categories: 5
Result: {'electronics': 125000, 'clothing': 89000, ...}
""")

    print("\n📊 Code Execution Approach Stats:")
    print("   - Tool calls: 1")
    print("   - Context tokens: ~2,000")
    print("   - Time: ~10 seconds (1 call)")
    print("   - Cost: ~$0.006 (2k tokens)")

    print("\n🎯 Improvement:")
    print("   - Token reduction: 97.5% (80k → 2k)")
    print("   - Time reduction: 75% (40s → 10s)")
    print("   - Cost reduction: 97.5% ($0.24 → $0.006)")


def main():
    """Run all examples"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Code Execution MCP Server - Usage Examples".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)

    example_1_progressive_discovery()
    example_2_context_efficient_processing()
    example_3_control_flow()
    example_4_privacy_preserving()
    example_5_skill_building()
    example_6_comparison()

    print("\n" + "=" * 60)
    print("Summary: Benefits of Code Execution Pattern")
    print("=" * 60)
    print("""
✅ Reduced Context Usage
   - 95%+ reduction in token consumption
   - Only summaries enter model context
   - Large datasets processed outside context

✅ Improved Performance
   - Fewer round trips to model
   - Faster execution with native code
   - More efficient control flow

✅ Enhanced Capabilities
   - Complex logic with loops, conditionals
   - State persistence across executions
   - Reusable skill library

✅ Better Privacy
   - Sensitive data stays in execution environment
   - Model never sees PII
   - Deterministic security rules

✅ Cost Reduction
   - 90%+ cost savings on tokens
   - Faster = cheaper inference
   - More efficient = more scalable
""")

    print("=" * 60)
    print("🚀 This is the future of agent-tool interaction!")
    print("=" * 60)


if __name__ == "__main__":
    main()
