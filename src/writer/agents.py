from abc import ABC, abstractmethod
import re
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json

class AgentOutput:
    """Represents the output from an agent's execution"""
    def __init__(self, response: str, reasoning: List[str], actions: List[Dict[str, Any]]):
        self.response = response
        self.reasoning = reasoning
        self.actions = actions

class Tool:
    """Represents a tool that can be used by agents"""
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func
        
    def run(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

class BaseAgent(ABC):
    """Base class for all agents"""
    def __init__(self, tools: Optional[List[Tool]] = None):
        self.tools = tools or []
        self.conversation_history = []
        
    @abstractmethod
    def run(self, prompt: str) -> AgentOutput:
        """Run the agent with the given prompt"""
        pass

    def add_tool(self, tool: Tool):
        """Add a tool to the agent's toolset"""
        self.tools.append(tool)

    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for prompt"""
        if not self.tools:
            return ""
        return "Available tools:\n" + "\n".join(
            f"- {tool.name}: {tool.description}" 
            for tool in self.tools
        )

class ReActAgent(BaseAgent):
    """
    ReAct (Reasoning + Acting) agent that follows a structured thought process:
    1. Reasoning about the current situation
    2. Planning actions based on reasoning
    3. Executing actions and observing results
    4. Repeating until task completion
    """
    
    def run(self, prompt: str) -> AgentOutput:
        thoughts = []
        actions = []
        
        # Add tools to system prompt if available
        system_prompt = f"""Follow these steps to answer the user's question:
1. Reason: Think about what needs to be done
2. Action: Decide what action to take based on reasoning
3. Observation: Consider the results
4. Response: Provide final answer based on observations

{self._format_tool_descriptions()}
"""
        # Initialize conversation with system prompt and user query
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Add to conversation history
        self.conversation_history.extend([
            {"role": "user", "content": prompt}
        ])
        
        response = None
        max_steps = 5  # Prevent infinite loops
        
        for _ in range(max_steps):
            # Get next action from AI
            action_response = self._get_llm_response(messages)
            
            # Extract reasoning and action
            reasoning = self._extract_reasoning(action_response)
            if reasoning:
                thoughts.append(reasoning)
            
            action = self._extract_action(action_response)
            if action:
                actions.append(action)
                # Execute tool if specified
                if action.get("tool"):
                    tool_result = self._execute_tool(action["tool"], action.get("args", {}))
                    messages.append({"role": "system", "content": f"Observation: {tool_result}"})
            
            # Check if final response is ready
            response = self._extract_response(action_response)
            if response:
                break
                
            messages.append({"role": "assistant", "content": action_response})
        
        if not response:
            response = "I was unable to reach a final conclusion."
            
        return AgentOutput(response, thoughts, actions)

    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM - implement with preferred LLM"""
        # Integrate with Writer AI API here
        pass

    def _extract_reasoning(self, text: str) -> Optional[str]:
        match = re.search(r"Reason:(.+?)(?=Action:|Response:|$)", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_action(self, text: str) -> Optional[Dict]:
        match = re.search(r"Action:(.+?)(?=Observation:|Response:|$)", text, re.DOTALL)
        if not match:
            return None
        action_text = match.group(1).strip()
        
        # Parse tool usage
        tool_match = re.match(r"Use tool '(\w+)' with args: (.+)", action_text)
        if tool_match:
            return {
                "tool": tool_match.group(1),
                "args": json.loads(tool_match.group(2))
            }
        return {"description": action_text}

    def _extract_response(self, text: str) -> Optional[str]:
        match = re.search(r"Response:(.+?)$", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Tool '{tool_name}' not found"
        return tool.run(**args)

class ChainOfThoughtAgent(BaseAgent):
    """
    Chain of Thought (CoT) agent that breaks down complex problems into steps
    and shows its reasoning process.
    """
    
    def run(self, prompt: str) -> AgentOutput:
        system_prompt = """Break down the problem into steps and show your reasoning process.
For each step:
1. State what you're thinking about
2. Show your reasoning
3. Draw intermediate conclusions
4. Move to the next logical step

{self._format_tool_descriptions()}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        self.conversation_history.extend([
            {"role": "user", "content": prompt}
        ])
        
        response = self._get_llm_response(messages)
        thoughts = self._extract_thoughts(response)
        final_answer = self._extract_final_answer(response)
        
        return AgentOutput(
            response=final_answer,
            reasoning=thoughts,
            actions=[]  # CoT agent doesn't use tools directly
        )

    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM - implement with preferred LLM"""
        pass

    def _extract_thoughts(self, text: str) -> List[str]:
        # Extract numbered steps/thoughts
        thoughts = re.findall(r"\d+\.\s+(.+?)(?=\d+\.|Final Answer:|$)", text, re.DOTALL)
        return [t.strip() for t in thoughts]

    def _extract_final_answer(self, text: str) -> str:
        match = re.search(r"Final Answer:(.+?)$", text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

class ToolUsingAgent(BaseAgent):
    """
    Tool-Using Agent that specializes in effectively utilizing available tools
    to solve problems.
    """
    
    def run(self, prompt: str) -> AgentOutput:
        if not self.tools:
            return AgentOutput(
                "No tools available to use.",
                ["Agent requires tools to function."],
                []
            )
            
        system_prompt = f"""You are a tool-using agent. Your goal is to solve problems by effectively using available tools.
Follow these steps:
1. Analyze what tools might be helpful
2. Plan a sequence of tool usage
3. Execute tools and analyze results
4. Provide final answer based on tool outputs

{self._format_tool_descriptions()}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        self.conversation_history.extend([
            {"role": "user", "content": prompt}
        ])
        
        thoughts = []
        actions = []
        current_response = None
        max_steps = 5
        
        for _ in range(max_steps):
            response = self._get_llm_response(messages)
            
            # Extract thought process
            thought = self._extract_thought(response)
            if thought:
                thoughts.append(thought)
            
            # Extract and execute tool action
            action = self._extract_tool_action(response)
            if action:
                actions.append(action)
                result = self._execute_tool(action["tool"], action.get("args", {}))
                messages.append({"role": "system", "content": f"Tool result: {result}"})
            
            # Check for final answer
            current_response = self._extract_final_answer(response)
            if current_response:
                break
                
            messages.append({"role": "assistant", "content": response})
            
        if not current_response:
            current_response = "Unable to reach a conclusion after maximum steps."
            
        return AgentOutput(current_response, thoughts, actions)

    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM - implement with preferred LLM"""
        pass

    def _extract_thought(self, text: str) -> Optional[str]:
        match = re.search(r"Thought:(.+?)(?=Tool Usage:|Final Answer:|$)", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_tool_action(self, text: str) -> Optional[Dict]:
        match = re.search(r"Tool Usage:(.+?)(?=Thought:|Final Answer:|$)", text, re.DOTALL)
        if not match:
            return None
            
        tool_text = match.group(1).strip()
        tool_match = re.match(r"Use '(\w+)' with parameters: (.+)", tool_text)
        if tool_match:
            return {
                "tool": tool_match.group(1),
                "args": json.loads(tool_match.group(2))
            }
        return None

    def _extract_final_answer(self, text: str) -> Optional[str]:
        match = re.search(r"Final Answer:(.+?)$", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Tool '{tool_name}' not found"
        return tool.run(**args)

class CustomAgent(BaseAgent):
    """
    Customizable agent that allows defining custom behavior and prompting strategies.
    """
    
    def __init__(
        self,
        system_prompt: str,
        tools: Optional[List[Tool]] = None,
        max_steps: int = 5,
        thought_pattern: Optional[str] = None,
        action_pattern: Optional[str] = None,
        response_pattern: Optional[str] = None
    ):
        super().__init__(tools)
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.thought_pattern = thought_pattern or r"Thought:(.+?)(?=Action:|Response:|$)"
        self.action_pattern = action_pattern or r"Action:(.+?)(?=Observation:|Response:|$)"
        self.response_pattern = response_pattern or r"Response:(.+?)$"
        
    def run(self, prompt: str) -> AgentOutput:
        full_prompt = f"{self.system_prompt}\n\n{self._format_tool_descriptions()}"
        
        messages = [
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": prompt}
        ]
        
        self.conversation_history.extend([
            {"role": "user", "content": prompt}
        ])
        
        thoughts = []
        actions = []
        current_response = None
        
        for _ in range(self.max_steps):
            response = self._get_llm_response(messages)
            
            # Extract components using custom patterns
            thought = self._extract_pattern(response, self.thought_pattern)
            if thought:
                thoughts.append(thought)
                
            action = self._extract_pattern(response, self.action_pattern)
            if action:
                parsed_action = self._parse_action(action)
                if parsed_action:
                    actions.append(parsed_action)
                    if parsed_action.get("tool"):
                        result = self._execute_tool(
                            parsed_action["tool"],
                            parsed_action.get("args", {})
                        )
                        messages.append(
                            {"role": "system", "content": f"Observation: {result}"}
                        )
            
            current_response = self._extract_pattern(response, self.response_pattern)
            if current_response:
                break
                
            messages.append({"role": "assistant", "content": response})
        
        if not current_response:
            current_response = "Maximum steps reached without conclusion."
            
        return AgentOutput(current_response, thoughts, actions)

    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM - implement with preferred LLM"""
        pass

    def _extract_pattern(self, text: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _parse_action(self, action_text: str) -> Optional[Dict]:
        """Parse action text into structured format - override for custom parsing"""
        tool_match = re.match(r"Use tool '(\w+)' with args: (.+)", action_text)
        if tool_match:
            return {
                "tool": tool_match.group(1),
                "args": json.loads(tool_match.group(2))
            }
        return {"description": action_text}

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Tool '{tool_name}' not found"
        return tool.run(**args)
