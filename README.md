# lean-mcp

A lightweight, minimal MCP (Model Context Protocol) server starter template. Built with Python and FastMCP for quick deployment and easy customization.

## Overview

lean-mcp is a lean, no-frills foundation for building MCP servers. It provides essential tooling infrastructure with streamable HTTP transport, ready to be adapted for your specific use case.

## Features

- **Streamable HTTP Transport** - RESTful API with session management
- **Filesystem Operations** - Complete file and directory management
- **Clean Architecture** - SOLID principles with DRY error handling
- **Type Safety** - Full type hints and validation with Pydantic
- **Pathlib-based** - Cross-platform file operations

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read file contents | `file_path: str` |
| `write_file` | Write content to file | `file_path: str`, `content: str` |
| `list_directory` | List directory contents | `directory_path: str` (optional) |
| `delete_file` | Delete a file | `file_path: str` |
| `create_directory` | Create a directory | `directory_path: str` |
| `file_info` | Get file/directory metadata | `file_path: str` |

## Requirements

- Python 3.12+
- uv package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/vdrnxs/lean-mcp.git
cd lean-mcp

# Install dependencies
uv sync
```

## Usage

### Start Server

```bash
uv run server.py
```

The server will start on `http://0.0.0.0:8080/mcp`

### Test Server

```bash
uv run test_server.py
```

Expected output:
```
=== Listing available tools ===
  - read_file
  - write_file
  - list_directory
  - delete_file
  - create_directory
  - file_info

=== Test 1: Read file ===
Content preview:
[project]
name = "lean-mcp"
version = "0.1.0"
...

=== Test 2: List directory ===
Directory contents:
[
  {
    "name": "server.py",
    "type": "file",
    "size": 5234
  },
  ...
]
```

## API Endpoints

### Base URL
```
http://localhost:8080/mcp
```

### Protocol
The server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification using streamable-http transport.

## Development

### Project Structure

```
lean-mcp/
├── server.py          # Main server implementation
├── test_server.py     # Client test suite
├── pyproject.toml     # Project dependencies
└── README.md          # Documentation
```

### Adding New Tools

Define tools using the `@mcp.tool()` decorator:

```python
@mcp.tool()
def your_function(param: type) -> return_type:
    """Tool description.

    Args:
        param: Parameter description.

    Returns:
        Return value description.
    """
    return result
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port |

## Dependencies

- `fastmcp>=2.6.1` - MCP server framework
- `pydantic<2.12` - Data validation

## License

See LICENSE file for details.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
