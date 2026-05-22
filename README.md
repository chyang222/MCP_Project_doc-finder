# doc-finder-mcp

OneDrive/로컬 폴더의 문서(pptx, pdf, docx)를 인덱싱하고, 자연어로 관련 파일과 페이지를 찾아주는 MCP 서버입니다.

## 구조

```
doc-finder-mcp/
├── src/
│   ├── mcp_server.py          # MCP 서버 진입점
│   ├── indexer/
│   │   ├── extractor.py       # 파일별 텍스트/슬라이드 추출
│   │   └── embedder.py        # 임베딩 생성 (OpenAI)
│   ├── db/
│   │   ├── sqlite_db.py       # 파일 메타 & 청크 정보 (RDB)
│   │   └── vector_db.py       # 벡터 검색 (ChromaDB)
│   └── tools/
│       ├── index_tool.py      # MCP Tool: 증분 인덱싱
│       └── search_tool.py     # MCP Tool: 문서 검색
├── config.py
├── requirements.txt
└── .env.example
```

## MCP Tools

| Tool | 설명 |
|------|------|
| `index_documents` | 폴더 스캔 → 변경 파일만 추출/임베딩/저장 |
| `search_documents` | 자연어 질의 → 관련 파일명 + 페이지 반환 |

## 설치

```bash
pip install -r requirements.txt
cp .env.example .env
# .env 편집 후
```

## Claude Code 연동 (.claude/settings.json)

```json
{
  "mcpServers": {
    "doc-finder": {
      "command": "python",
      "args": ["/path/to/doc-finder-mcp/src/mcp_server.py"],
      "env": {
        "DOC_FINDER_FOLDER": "/path/to/your/documents",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## 사용 예시

```
"Graph Studio 온톨로지 설계 관련 자료 찾아줘"
→ [GraphStudio_Guide.pptx] 슬라이드 12 (유사도: 87.3%)
   경로: /Documents/GraphStudio_Guide.pptx
   내용 미리보기: 온톨로지 설계 시 노드 타입과 엣지 타입을...
```
