import subprocess                                                                                                                                                                                                      
from typing import Optional                                                                                                                                                                                            
import yaml                                                                                                                                                                                                            
from pathlib import Path                                                                                                                                                                                               
from functools import lru_cache                                                                                                                                                                                        
from smolagents  import tool,LiteLLMModel
import os
from datetime import datetime

def is_docker_running() -> bool:
    try:
        subprocess.run(["docker", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
                                                                                                                                                                                                 
@lru_cache(maxsize=1)                                                                                                                                                                                                  
def load_approved_commands() -> set:                                                                                                                                                                                   
    """Load approved commands from YAML file"""                                                                                                                                                                        
    yaml_path = "prompts/approved_commands.yaml"                                                                                                                                                
        
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
        if not data:
            return set()
        # Handle both list and dictionary formats
        if isinstance(data, list):
            return set(data)
        elif isinstance(data, dict):
            commands = data.get("approved_commands", [])
            if isinstance(commands, str):
                return set([commands])
            return set(commands)
        return set()

import os

from smolagents import CodeAgent, DuckDuckGoSearchTool
from litellm import completion
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENROUTER_API_KEY"] = os.getenv('OPENROUTER_API_KEY')


@tool                                                                                                                                                                                                      
def execute_cli_command(command: str, use_docker: bool = False, docker_image: str = "kali-linux") -> str:                                                                                                                                                                          
    """
    Execute cli command either locally or in a Docker container

    Args:
        command: cli command to execute
        use_docker: whether to run in Docker container
        docker_image: Docker image to use (default: kali-linux)

    Returns:
        str: Command output
    """                                                                                                                                                                                                            
    approved_commands = load_approved_commands()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create log file with timestamp
    log_file = f"logs/cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                                                                                                                                                                                                                    
    # Get the base command without arguments                                                                                                                                                                           
    base_command = command.split()[0]                                                                                                                                                                                  
                                                                                                                                                                                                                    
    if base_command not in approved_commands:                                                                                                                                                                          
        raise ValueError(f"Command '{base_command}' is not in the approved list")                                                                                                                                      
                                                                                                                                                                                                                    
    try:
        if use_docker:
            if not is_docker_running():
                raise ValueError("Docker is not running")
                
            docker_command = f"docker run --rm {docker_image} {command}"
            result = subprocess.run(
                docker_command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        # Log command and output
        with open(log_file, "w") as f:
            f.write(f"Command: {command}\n")
            f.write("Output:\n")
            f.write(result.stdout)
            
        return result.stdout                                                                                                                                                                                           
    except subprocess.CalledProcessError as e:
        # Log command and error
        with open(log_file, "w") as f:
            f.write(f"Command: {command}\n")
            f.write("Error:\n")
            f.write(e.stderr)
            
        return f"Error: {e.stderr}"

import re
import requests
import subprocess
import select
import sys
from markdownify import markdownify
from requests.exceptions import RequestException
from smolagents import tool
def get_doc(cli: str) -> str:

    try:
        # Send a GET request to the URL
        response = requests.get(f"https://www.kali.org/tools/{cli}")
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

 

@tool                                                                                                                                                                                                      
def cli_agent(goal: str, clicommand: str, use_docker: bool = False, docker_image: str = "kali-linux") -> str:                                                                                                                                                                     
    """
    Execute cli command and return the output

    Args:
        goal: What to do with the cli command
        clicommand: the name of the cli command without arguments or options
        use_docker: whether to run in Docker container
        docker_image: Docker image to use (default: kali-linux)

    Returns:
        str: status and output of the command
    """   
    os.environ["OPENROUTER_API_KEY"] = os.getenv('OPENROUTER_API_KEY')
    model = LiteLLMModel("openrouter/deepseek/deepseek-chat")
    # Get base command without arguments for documentation path
    base_command = clicommand.split()[0]
    documentation = get_doc(base_command)
    
    # Use LiteLLM completion directly instead of passing a model
    agent = CodeAgent(tools=[execute_cli_command],model=model)
    value = agent.run(
        f"The goal: {goal}\n\n"
        f"the command: {clicommand}\n\n"
        f"use_docker: {use_docker}\n"
        f"docker_image: {docker_image}\n\n"
    )
    return str(value)


 
if __name__ == "__main__":
    # Test command execution
    print("Testing command execution:")
    try:
        result = execute_cli_command("ls -l", use_docker=False)
        print("Command output:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
