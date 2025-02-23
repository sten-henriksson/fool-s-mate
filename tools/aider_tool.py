import yaml
import sys
import subprocess
import os
from pathlib import Path
from smolagents import tool
def read_yaml_commands():
    """Read a YAML file and extract command values"""
    try:
        with open("prompts.yaml", 'r') as file:
            data = yaml.safe_load(file)
            return {
                'coder_prompt': data.get('coder_prompt'),

            }
    except FileNotFoundError:
        print(f"Error: File {"prompts.yaml"} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}
 
@tool
def execute_aider_command(message: str, file_name: str) -> str:
    """
    Executes an aider command to modify a specified file with a given message.

    Args:
        message: The message/instruction to pass to the coder agent
        file_name: the name of the file. example.py format

    Returns:
        str: The output from the aider command or an error message if it fails
    """
    file_name = "./generated_agent/"+file_name
    path = Path(file_name)
    if not path.exists():
        path.touch()
        print(f"Created new file: {file_name}")
    
    # Build and run aider command
    command = f"aider --env-file ./.env --no-auto-commits  --architect   --no-check-update --no-stream --yes-always --no-detect-urls  --model openrouter/deepseek/deepseek-chat  --message '{message+"\n \n"+read_yaml_commands()["coder_prompt"]}' {file_name}"
    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr}"

if __name__ == "__main__":
    print(execute_aider_command("create a interface for ls", "ls.py"))

