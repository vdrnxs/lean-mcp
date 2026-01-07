import asyncio
import json
import logging
import os
from pathlib import Path

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("lean-mcp")

# DRY: Centralized error handling
def handle_file_operation(operation: str, path: str, func):
    """
    Generic error handler for file operations (DRY principle).

    Args:
        operation: Name of the operation being performed
        path: File path being operated on
        func: Function to execute

    Returns:
        Result of the function or error message
    """
    logger.info(f">>> Tool: '{operation}' called with path '{path}'")
    try:
        result = func()
        logger.info(f">>> Successfully completed '{operation}' on '{path}'")
        return result
    except FileNotFoundError:
        error_msg = f"Error: File not found - '{path}'"
        logger.error(f">>> {error_msg}")
        return error_msg
    except PermissionError:
        error_msg = f"Error: Permission denied - '{path}'"
        logger.error(f">>> {error_msg}")
        return error_msg
    except IsADirectoryError:
        error_msg = f"Error: Path is a directory, not a file - '{path}'"
        logger.error(f">>> {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Error in '{operation}': {str(e)}"
        logger.error(f">>> {error_msg}")
        return error_msg

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read and return the contents of a file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The contents of the file as a string.
    """
    def _read():
        path = Path(file_path)
        return path.read_text(encoding='utf-8')

    return handle_file_operation("read_file", file_path, _read)


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating it if it doesn't exist.

    Args:
        file_path: The path to the file to write.
        content: The content to write to the file.

    Returns:
        Success message or error description.
    """
    def _write():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return f"Successfully wrote {len(content)} characters to '{file_path}'"

    return handle_file_operation("write_file", file_path, _write)


@mcp.tool()
def list_directory(directory_path: str = ".") -> str:
    """List all files and directories in the specified path.

    Args:
        directory_path: The path to the directory to list. Defaults to current directory.

    Returns:
        JSON string containing list of files and directories with their types.
    """
    def _list():
        path = Path(directory_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")

        items = []
        for item in sorted(path.iterdir()):
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })

        return json.dumps(items, indent=2)

    return handle_file_operation("list_directory", directory_path, _list)


@mcp.tool()
def delete_file(file_path: str) -> str:
    """Delete a file.

    Args:
        file_path: The path to the file to delete.

    Returns:
        Success message or error description.
    """
    def _delete():
        path = Path(file_path)
        if path.is_dir():
            raise IsADirectoryError(f"Use delete_directory for directories")
        path.unlink()
        return f"Successfully deleted file '{file_path}'"

    return handle_file_operation("delete_file", file_path, _delete)


@mcp.tool()
def create_directory(directory_path: str) -> str:
    """Create a new directory, including parent directories if needed.

    Args:
        directory_path: The path to the directory to create.

    Returns:
        Success message or error description.
    """
    def _create():
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory '{directory_path}'"

    return handle_file_operation("create_directory", directory_path, _create)


@mcp.tool()
def file_info(file_path: str) -> str:
    """Get detailed information about a file or directory.

    Args:
        file_path: The path to the file or directory.

    Returns:
        JSON string containing file information (size, modified time, type, etc.).
    """
    def _info():
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {file_path}")

        stat = path.stat()
        info = {
            "name": path.name,
            "path": str(path.absolute()),
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_readable": os.access(path, os.R_OK),
            "is_writable": os.access(path, os.W_OK)
        }

        if path.is_file():
            info["extension"] = path.suffix

        return json.dumps(info, indent=2)

    return handle_file_operation("file_info", file_path, _info)

if __name__ == "__main__":
    import sys

    # Detectar si se ejecuta desde Claude Desktop (stdin no es terminal)
    if not sys.stdin.isatty():
        # Modo STDIO para Claude Desktop
        logger.info("Starting lean-mcp server with STDIO transport")
        asyncio.run(mcp.run_async(transport="stdio"))
    else:
        # Modo HTTP para desarrollo/web
        port = int(os.getenv("PORT", 8080))
        logger.info(f"Starting lean-mcp server on http://0.0.0.0:{port}")
        asyncio.run(
            mcp.run_async(
                transport="streamable-http",
                host="0.0.0.0",
                port=port,
            )
        )