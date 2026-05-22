# doc-finder-mcp

OneDrive/로컬 폴더의 문서(pptx, pdf, docx)를 인덱싱하고, 자연어로 관련 파일과 페이지를 찾아주는 MCP 서버입니다.

## 구조

```
doc-finder-mcp/
├── src/
│   ├── mcp_server.py          # MCP 서버 진입점
│   ├── indexer/
│   │   ├── extractor.py       # 파일별 텍스트/슬라이드/이미지 추출
│   │   └── embedder.py        # 임베딩 생성 (ko-sroberta-multitask, 로컬)
│   ├── db/
│   │   ├── sqlite_db.py       # 파일 메타 & 청크 정보 (SQLite)
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
| `index_documents` | 폴더 스캔 → 변경 파일만 추출/임베딩/저장 (증분 업데이트) |
| `search_documents` | 자연어 질의 → 관련 파일명 + 페이지 반환 |

## 주요 기능

- **지원 형식**: `.pptx` / `.pdf` / `.docx`
- **증분 인덱싱**: `last_modified` 기준으로 변경된 파일만 재처리
- **이미지 슬라이드 분석**: 텍스트 없이 이미지만 있는 PPT 슬라이드를 Claude Vision(`claude-haiku-4-5`)으로 자동 설명
- **한국어 임베딩**: `jhgan/ko-sroberta-multitask` (API 키 불필요, 로컬 실행)
- **벡터 검색**: ChromaDB 코사인 유사도 기반 시맨틱 검색

## 설치

```bash
pip install -r requirements.txt
cp .env.example .env
# .env 에서 DOC_FINDER_FOLDER 경로 설정
```

## 환경변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `DOC_FINDER_FOLDER` | 권장 | 인덱싱할 문서 폴더 경로 (기본값: `~/Documents`) |
| `ANTHROPIC_API_KEY` | 선택 | PPT 이미지 슬라이드 분석용 (Claude Code 환경에서는 자동 제공) |

## Claude Code 연동 (.claude/settings.json)

```json
{
  "mcpServers": {
    "doc-finder": {
      "command": "python",
      "args": ["/path/to/doc-finder-mcp/src/mcp_server.py"],
      "env": {
        "DOC_FINDER_FOLDER": "/path/to/your/documents"
      }
    }
  }
}
```

> `ANTHROPIC_API_KEY`는 Claude Code가 자동으로 주입하므로 별도 설정 불필요합니다.

## 사용 예시

```
"Graph Studio 온톨로지 설계 관련 자료 찾아줘"
→ [GraphStudio_Guide.pptx] 슬라이드 12 (유사도: 87.3%)
   경로: /Documents/GraphStudio_Guide.pptx
   내용 미리보기: 온톨로지 설계 시 노드 타입과 엣지 타입을...
```
