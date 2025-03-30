#!/usr/bin/env python3
"""
Claude Pokémon MCP Client

This script demonstrates how to use Claude with the Pokémon MCP tools.
It creates a simple chat interface where you can interact with Claude
and the Pokémon MCP servers.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ClaudePokemonClient:
    def __init__(self):
        """Initialize the Claude Pokémon MCP client."""
        # Check for API key
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables.")
            print("Please create a .env file with your API key or set it in your environment.")
            sys.exit(1)
            
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=self.api_key)
        
        # Store conversation history
        self.messages = []
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to a Pokémon MCP server.
        
        Args:
            server_script_path: Path to the server script
        """
        if not server_script_path.endswith('.py'):
            raise ValueError("Server script must be a Python file (.py)")

        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
        return tools
    
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available MCP tools.
        
        Args:
            query: User's query
            
        Returns:
            Claude's response
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": query
        })
        
        # Get available tools from the MCP server
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        
        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=self.messages,
            tools=available_tools
        )
        
        # Process response and handle tool calls
        final_text = []
        assistant_message_content = []
        
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                print(f"\n[Calling tool {tool_name} with args {tool_args}]")
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                
                assistant_message_content.append(content)
                
                # Add assistant's message with tool call to history
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                
                # Add tool result as user message
                self.messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })
                
                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=self.messages,
                    tools=available_tools
                )
                
                # Reset for next iteration
                assistant_message_content = []
                for content in response.content:
                    if content.type == 'text':
                        final_text.append(content.text)
                        assistant_message_content.append(content)
        
        # Add final assistant message to history
        if assistant_message_content:
            self.messages.append({
                "role": "assistant",
                "content": assistant_message_content
            })
        
        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop with Claude and Pokémon MCP tools."""
        print("\nClaude Pokémon MCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nYou: ").strip()
                
                if query.lower() in ('quit', 'exit'):
                    break
                
                response = await self.process_query(query)
                print("\nClaude:", response)
                
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()

async def main():
    """Main function to run the Claude Pokémon MCP client."""
    if len(sys.argv) < 2:
        print("Usage: python claude_pokemon_client.py <path_to_server_script>")
        print("Example: python claude_pokemon_client.py pokemon_mcp/integration/pokemon_mcp_integration.py")
        sys.exit(1)
    
    client = ClaudePokemonClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
