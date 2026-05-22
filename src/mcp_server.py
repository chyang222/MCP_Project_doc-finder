import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from src.tools.index_tool import index_documents
from src.tools.search_tool import search_documents

server = Server("doc-finder")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="index_documents",
            description=(
                "지정된 폴더의 문서(pptx, pdf, docx)를 스캔하여 DB에 인덱싱합니다. "
                "변경된 파일만 증분 처리합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "인덱싱할 폴더 경로 (비우면 config 기본값 사용)",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="search_documents",
            description=(
                "자연어 질의로 관련 문서와 페이지를 검색합니다. "
                "예: 'Graph Studio 온톨로지 설계 관련 자료'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 내용 (자연어)",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "반환할 결과 수 (기본값: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "index_documents":
        result = await index_documents(arguments.get("folder_path"))
        return [types.TextContent(type="text", text=result)]

    elif name == "search_documents":
        result = await search_documents(
            query=arguments["query"],
            top_k=arguments.get("top_k", 5),
        )
        return [types.TextContent(type="text", text=result)]

    else:
        return [types.TextContent(type="text", text=f"알 수 없는 도구: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
