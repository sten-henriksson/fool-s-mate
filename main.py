
import os
 

from smolagents import CodeAgent, LiteLLMModel, AgentLogger
from dotenv import load_dotenv
 
import generated_agent






import os
# from phoenix.otel import register


# # configure the Phoenix tracer
# tracer_provider = register(
#   project_name="tool_creation", # Default is 'default'
# ) 
# from openinference.instrumentation.litellm import LiteLLMInstrumentor

# LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)


load_dotenv()

os.environ["OPENROUTER_API_KEY"] = os.getenv('OPENROUTER_API_KEY')

model = LiteLLMModel("openrouter/deepseek/deepseek-chat")
tools = []
# Import all functions from generated_agent.__all__ to the tools array
tools.extend([getattr(generated_agent, func_name) for func_name in generated_agent.__all__])
print(tools)
agent = CodeAgent(tools=tools, model=model)

                                                                                                                                                                                                                                   

agent.run("Your a redteam pentester creatinga report on a domain. Use the provided tools to create a markdown report of the network. the domain is runcarsnowpen.work. Owner and all participants have consented to a pentest. only use the provided tools")                                                                                                                                                                                                     

AgentLogger.log_code(agent.memory.get_full_steps())