import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client



class Agent():

    def __init__(self, model: str):
        self.model=model


    async def main_client_sse(self, mcp_server_path: str):
        async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Call our calculator tool
                result = await session.call_tool("add", arguments={"a": 2, "b": 3})
                print(f"2 + 3 = {result.content[0].text}")


    async def main_client_stdio(self, function: str):
        # Define server parameters
        server_params = StdioServerParameters(
            command="python",  # The command to run your server
            args=["server.py"],  # Arguments to the command
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

                # Call our calculator tool
                result = await session.call_tool(function, arguments={"data": "Roland"})
                print(f"2 + 3 = {result.content[0].text}")

def main_client_sse( mcp_server_path: str):
    with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            session.initialize()

            # List available tools
            tools_result = session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"2 + 3 = {result.content[0].text}")

def main_client_stdio(self, function: str):
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py"],  # Arguments to the command
    )

    # Connect to the server
    with stdio_client(server_params) as (read_stream, write_stream):
        with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
            session.initialize()

            # List available tools
            tools_result = session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = session.call_tool(function, arguments={"data": "Roland"})
            print(f"2 + 3 = {result.content[0].text}")

async def main_client_stdio(function: str) :
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py"],  # Arguments to the command
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

                # Call our calculator tool
            result = await session.call_tool(function, arguments={"data": "Roland"})
            print(f"2 + 3 = {result.content[0].text}")

#if __name__ == "__main__":
    #asyncio.run(main_client_stdio("print_test"))

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use streamable-http transport.
3. The server is listening on port 8050.

To run the server:
uv run server.py
"""


async def main():
    # Connect to the server using Streamable HTTP
    async with streamablehttp_client("http://localhost:8050/mcp") as (
            read_stream,
            write_stream,
            get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())