import os
from smolagents import CodeAgent, LiteLLMModel
from dotenv import load_dotenv
import yaml
from cli_tool import cli_agent

load_dotenv()

class KaliInfer:
    def __init__(self):
        self.YAML_FILE = os.getenv('COMMANDS_YAML', 'prompts/prompts_pentest.yaml')
        self.command = self.read_yaml_commands(self.YAML_FILE)
        
        os.environ["OPENROUTER_API_KEY"] = os.getenv('OPENROUTER_API_KEY')
        self.model = LiteLLMModel("openrouter/deepseek/deepseek-chat")
        self.agent = CodeAgent(tools=[cli_agent], model=self.model)
        
        self.commands = self.load_approved_commands()

    def read_yaml_commands(self, file_path):
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

    def load_approved_commands(self):
        """Load approved commands from YAML file"""
        commands = []
        with open("prompts/approved_commands.yaml", 'r') as file:
            for line in file:
                commands.append(line.strip())
        commands[0] = ""  # Remove first empty line
        return commands

    def run_agent_with_prompt_addition(self, additional_prompt: str):
        """Run the agent with additional prompt text"""
        base_prompt = self.command["sys_prompt"]
        full_prompt = f"{base_prompt}\n approved commands: {self.commands}\n{additional_prompt}"
        
        print(f"Running with prompt: {full_prompt}")
        result = self.agent.run(full_prompt)
        print("Result:", result)
        return result

# Create a single instance of KaliInfer
kali_infer = KaliInfer()
 
