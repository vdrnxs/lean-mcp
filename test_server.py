import asyncio

from fastmcp import Client

async def test_server():
    """Test the MCP server filesystem tools."""
    async with Client("http://localhost:8080/mcp") as client:
        print("=== Listing available tools ===")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}")

        print("\n=== Test 1: Read file ===")
        result = await client.call_tool("read_file", {"file_path": "pyproject.toml"})
        print(f"Content preview:\n{result[0].text[:200]}...")

        print("\n=== Test 2: List directory ===")
        result = await client.call_tool("list_directory", {"directory_path": "."})
        print(f"Directory contents:\n{result[0].text}")

        print("\n=== Test 3: Get file info ===")
        result = await client.call_tool("file_info", {"file_path": "server.py"})
        print(f"File info:\n{result[0].text}")

        print("\n=== Test 4: Write and read test file ===")
        result = await client.call_tool("write_file", {
            "file_path": "test_output.txt",
            "content": "Hello from MCP server!"
        })
        print(f"Write result: {result[0].text}")

        result = await client.call_tool("read_file", {"file_path": "test_output.txt"})
        print(f"Read result: {result[0].text}")

        print("\n=== Test 5: Delete test file ===")
        result = await client.call_tool("delete_file", {"file_path": "test_output.txt"})
        print(f"Delete result: {result[0].text}")

        print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(test_server())