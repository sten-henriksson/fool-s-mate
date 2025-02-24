# gets list of tools
# seperate smol llm agent for each tool that uses .md as prompt 
# manager agent tells what is expected to be done with the tool



import os

from smolagents import CodeAgent, LiteLLMModel
from dotenv import load_dotenv
import yaml
from cli_tool import cli_agent
load_dotenv()

YAML_FILE = os.getenv('COMMANDS_YAML', 'prompts/prompts_pentest.yaml')
def read_yaml_commands(file_path):
    """Read a YAML file and extract command values"""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return {
                'sys_prompt': data.get('sys_prompt'),
            }
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}
command = read_yaml_commands(YAML_FILE)

os.environ["OPENROUTER_API_KEY"] = os.getenv('OPENROUTER_API_KEY')

from smolagents.gradio_ui import GradioUI

def create_agent():
    model = LiteLLMModel("openrouter/deepseek/deepseek-chat")
    return CodeAgent(tools=[cli_agent], model=model)

# Create agent
agent = create_agent()

# Create Gradio UI with logging
ui = GradioUI(agent)
ui.launch()

# print the content of prompts/approved_commands.yaml

commands = []
with open("prompts/approved_commands.yaml", 'r') as file:
    for line in file:
        commands.append(line.strip())

print(commands)
commands[0] = ""

prompt = command["sys_prompt"]
prompt = prompt + "\n approved commands:"+str(commands)

res = agent.run(prompt)
print(prompt)

print("res")
 
