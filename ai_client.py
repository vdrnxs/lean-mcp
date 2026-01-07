"""
Simple AI Client for lean-mcp server
Connects GPT-4 to your filesystem MCP tools
"""
import asyncio
import json
import os
from openai import OpenAI
from fastmcp import Client

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
MCP_SERVER_URL = "http://localhost:8080/mcp"

client = OpenAI(api_key=OPENAI_API_KEY)

def build_openai_tool_schema(tool):
    """Convert MCP tool schema to OpenAI function calling format"""
    schema = dict(tool.inputSchema)
    schema["additionalProperties"] = False
    props = schema.get("properties", {})
    schema["required"] = list(props.keys())

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or f"Function {tool.name}",
            "parameters": schema,
            "strict": True,
        },
    }

async def main():
    print("Connecting to lean-mcp server...")

    async with Client(MCP_SERVER_URL) as mcp_session:
        # Discover available tools
        tools = await mcp_session.list_tools()
        openai_tools = [build_openai_tool_schema(tool) for tool in tools]

        print(f"\nConnected! Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}")

        # Conversation history
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful filesystem assistant. "
                    "You have access to file operations through MCP tools. "
                    "Help the user manage their files and directories."
                ),
            }
        ]

        print("\n=== AI Filesystem Assistant ===")
        print("Type 'quit' to exit\n")

        while True:
            # Get user input
            user_input = input("You: ").strip()

            if user_input.lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            # Call OpenAI
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=openai_tools,
            )

            msg = completion.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None)

            if tool_calls:
                # AI wants to use tools
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [tc.model_dump() for tc in tool_calls],
                })

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    print(f"\n[Executing: {tool_name}({args})]")

                    # Call MCP tool
                    result = await mcp_session.call_tool(tool_name, args)
                    result_text = result[0].text

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })

                # Get final response
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    tools=openai_tools,
                )
                final_msg = completion.choices[0].message
                print(f"\nAssistant: {final_msg.content}")
                messages.append({"role": "assistant", "content": final_msg.content})
            else:
                # Direct response without tools
                print(f"\nAssistant: {msg.content}")
                messages.append({"role": "assistant", "content": msg.content})

if __name__ == "__main__":
    asyncio.run(main())
