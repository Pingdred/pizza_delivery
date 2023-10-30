import types

from cat.mad_hatter.decorators import hook
from cat.log import log

from langchain.schema import AgentAction

def tool_agent(self, agent_input, allowed_tools):
    if len(allowed_tools) == 0:
        return {
            "intermediate_steps": [],
            "output": None
        }
    

     # tools currently recalled in working memory
    recalled_tools = self.cat.working_memory["procedural_memories"]
    # Get the tools names only
    tools_names = recalled_tools[0][0].metadata["name"]
    tools_names = self.cat.mad_hatter.execute_hook("agent_allowed_tools", tools_names)
    # Get tools with that name from mad_hatter
    tool = [i for i in self.cat.mad_hatter.tools if i.name in tools_names]
    tool = tool[0]
    
    log.critical(f"Used Tool: {tool.name}")
    tool_output = tool.func(None, tool.cat)

    return {
            "input": agent_input["input"], 
            "episodic_memory": agent_input["episodic_memory"],
            "declarative_memory": agent_input["declarative_memory"], 
            "chat_history": agent_input["chat_history"], 
            "output": tool_output, 
            "intermediate_steps":[(AgentAction(tool=tool.name, tool_input="None", log=""), tool_output)]
        }


@hook
def after_cat_bootstrap(cat) -> None:
    log.critical("REPLACE TOOL AGENT")
    funcType = types.MethodType
    cat.agent_manager.execute_tool_agent = funcType(tool_agent, cat.agent_manager) 
    