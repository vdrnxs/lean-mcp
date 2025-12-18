import asyncio
import logging
import os

from fastmcp import FastMCP 

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("MCP Server on Cloud Run")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Use this to add two numbers together.
    
    Args:
        a: The first number.
        b: The second number.
    
    Returns:
        The sum of the two numbers.
    """
    logger.info(f">>> Tool: 'add' called with numbers '{a}' and '{b}'")
    return a + b

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read and return the contents of a file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The contents of the file as a string.
    """
    logger.info(f">>> Tool: 'read_file' called with path '{file_path}'")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f">>> Successfully read {len(content)} characters from '{file_path}'")
        return content
    except FileNotFoundError:
        error_msg = f"Error: File not found - '{file_path}'"
        logger.error(f">>> {error_msg}")
        return error_msg
    except PermissionError:
        error_msg = f"Error: Permission denied - '{file_path}'"
        logger.error(f">>> {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        logger.error(f">>> {error_msg}")
        return error_msg

if __name__ == "__main__":
    logger.info(f" MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="streamable-http", 
            host="0.0.0.0", 
            port=os.getenv("PORT", 8080),
        )
    )