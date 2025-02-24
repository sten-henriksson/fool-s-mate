import yaml
import sys
import subprocess
import os
from pathlib import Path
from typing import Optional
from smolagents import tool

# Get YAML file path from environment or use default
YAML_FILE = os.getenv('COMMANDS_YAML', 'prompts/example_commands.yaml')
def read_yaml_commands(file_path):
    """Read a YAML file and extract command values"""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return {
                'cli_command': data.get('cli_command'),
                'help_command': data.get('help_command'),
                'man_command': data.get('man_command')
            }
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}
    



@tool
def execute_help_command(command_name: Optional[str] = None) -> str:
    """
    Execute and return help information for CLI commands.

    Args:
        command_name: (Optional) Name of the specific command to get help for.
                     If not provided, returns general help information.

    Returns:
        str: Help output for the specified command or general help if no command is specified.
             Includes additional --dired option information when relevant.
    """
    commands = read_yaml_commands(YAML_FILE)
    command = commands.get('help_command', '')
    
    if not command:
        return "No help command found in YAML file"
    
    # Modify command if specific command is requested
    if command_name:
        command = f"{command} {command_name}"
    
    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        output = result.stdout
        
        # Add --dired option if not present
        if "--dired" not in output:
            output += "\n  -D, --dired                generate output designed for Emacs\n"
        
        return output
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr}"

@tool
def execute_man_command() -> str:
    """Execute the man command from commands.yaml and return its output"""
    commands = read_yaml_commands(YAML_FILE)
    command = commands.get('man_command', '')
    if not command:
        return "No man command found in YAML file"
    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr}"



@tool
def create_markdown_file(markdown_content: str) -> str:
    """
    Create a markdown documentation file in the tool_documentation directory.
    
    Args:
        markdown_content: Markdown formatted content to write to the file
        
    Returns:
        str: Success message or error if file creation failed
    """
    # Ensure the directory exists
    docs_dir = Path("./tool_documentation")
    docs_dir.mkdir(exist_ok=True)

    # Create the file path
    file_path = docs_dir / f"{read_yaml_commands(YAML_FILE)["cli_command"]}.md"
    
    try:
        with open(file_path, "w") as f:
            f.write(markdown_content)
        return f"Successfully created documentation file: {file_path}"
    except Exception as e:
        return f"Failed to create documentation file: {str(e)}"

if __name__ == "__main__":
    print(execute_man_command())
    print(execute_help_command())
