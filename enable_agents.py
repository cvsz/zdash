import os
import json
import yaml

input_dir = "/home/zeazdev/zdash/.agent/agents"
output_dir = "/home/zeazdev/zdash/.agents/agents"

os.makedirs(output_dir, exist_ok=True)

count = 0
for filename in os.listdir(input_dir):
    if not filename.endswith(".md"):
        continue
    
    filepath = os.path.join(input_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse YAML frontmatter
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            frontmatter = content[3:end_idx].strip()
            instructions = content[end_idx+3:].strip()
            try:
                metadata = yaml.safe_load(frontmatter)
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                continue
            
            name = metadata.get("name", filename.replace(".md", ""))
            description = metadata.get("description", "")
            
            # Write agent.json
            agent_dir = os.path.join(output_dir, name)
            os.makedirs(agent_dir, exist_ok=True)
            
            agent_json = {
                "name": name,
                "description": description,
                "instructions": instructions
            }
            
            with open(os.path.join(agent_dir, "agent.json"), "w", encoding="utf-8") as out_f:
                json.dump(agent_json, out_f, indent=2)
                
            count += 1
            print(f"Enabled agent: {name}")

print(f"Successfully enabled {count} agents.")
