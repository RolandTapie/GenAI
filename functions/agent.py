import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from functions.rag import extract_paragraphs,encode_chunks,retrieve_top_k,generate_answer_with_llm,test_llm_server,reformulation,send_prompt,send_mistral

import os
from dotenv import load_dotenv
# Charger les variables depuis le fichier .env
load_dotenv()
# Lire les variables d'environnement
pdf_path = os.getenv("business_file")
model_path = os.getenv("model_path")
mcp_server = os.getenv("mcp_serveur_path")
transport=os.getenv("mcp_transport")


class Agent():

    def __init__(self, model: str, mcp_serveur):
        self.model=model
        self.mcp_serveur=mcp_serveur
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self.tools=None

    async def __aenter__(self):
        await self.exit_stack.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.__aexit__(exc_type, exc_val, exc_tb)


    async def main_stdio (self):
        # Define server parameters
        print(self.mcp_serveur)
        server_params = StdioServerParameters(
            command="python",  # The command to run your server
            args=[self.mcp_serveur],  # Arguments to the command
        )

        # Connect to the server
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")



    async def main_sse(self):
        # Connect to the server using SSE
        async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")



    async def connect_to_server(self, server_path: str = mcp_server):
        """Connect to an MCP server.

       Args:
           server_script_path: Path to the server script.
       """
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
        )

        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialize the connection
        await self.session.initialize()

        # List available tools
        tools_result = await self.session.list_tools()
        print("\nConnected to server with tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")

        self.tools=tools_result.tools


    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        tools_result = await self.session.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]
        self.tools=tools

        return tools

    async def query_llm(self, message , tools, tool_choice):
        response = send_mistral("user",message)
        # response = await self.openai_client.chat.completions.create(
        #     model=self.model,
        #     messages=message,
        #     tools=tools,
        #     tool_choice=tool_choice,
        # )
        return response

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools.

        Args:
            query: The user query.

        Returns:
            The response from OpenAI.
        """
        # Get available tools
        tools = await self.get_mcp_tools()

        # Initial llm call
        messages=query
        response = await self.query_llm( messages,tools,"auto")

        # Get assistant's response
        print(response)
        assistant_message = response.choices[0].message

        # Initialize conversation with user query and assistant response
        messages = [
            {"role": "user", "content": query},
            assistant_message,
        ]

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                # Execute tool call
                result = await self.session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                )

                # Add tool response to conversation
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text,
                    }
                )

            # Get final response from OpenAI with tool results

            final_response = await self.query_llm(messages,tools,"none")

            return final_response.choices[0].message.content

        # No tool calls, just return the direct response
        return assistant_message.content

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    async with Agent("Mistral") as agent:
        await agent.connect_to_server()
        await agent.process_query("quelle est la capitale de la france?")


