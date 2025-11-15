# OCR Sample Project

A comparison toolkit for evaluating different OCR/text extraction approaches on PDF documents, featuring traditional PDF parsing vs. LLM-based vision OCR.

## Overview

This project demonstrates and compares two approaches for extracting text from PDF documents:

1. **Traditional PDF Parsing** - Using PyMuPDF4LLM for direct text/layout extraction
2. **LLM Vision OCR** - Using vision-capable language models (Google Gemini) to perform OCR on rendered PDF pages

## Features

### 📄 PDF Processing (`main.py`)

Comprehensive PDF processing utility with multiple modes:

- Convert entire PDFs to markdown using PyMuPDF4LLM
- Export specific page ranges as both markdown and PNG images
- Generate grayscale, contrast-enhanced images optimized for VLM processing
- Batch process multiple PDFs from a directory

**Example Usage:**
```bash
# Export pages 1-5 from a PDF (markdown + PNG + grayscale)
uv run main.py --export-pages document.pdf --range 1-5

# Export all pages at high resolution
uv run main.py --export-pages document.pdf --range all --dpi 300

# Extract markdown from entire PDF
uv run main.py document.pdf
```

### 🤖 LLM-Based OCR (`llm_ocr.py`)

Vision-based text extraction using pydantic-ai and OpenRouter:

- Two-stage pipeline: initial OCR + refinement pass
- Uses Google Gemini 2.5 Flash models
- Integrated with Langfuse for monitoring and observability
- Processes entire folders of images in batch

**Example Usage:**
```bash
# Process all images in a folder
uv run llm_ocr.py AR2024_C/png_bw/

# Output saved to: AR2024_C/llm_md/
```

### 📊 Comparison Dashboard (`compare_md.py`)

Interactive Streamlit app for side-by-side markdown comparison:

- Compare PyMuPDF4LLM vs LLM OCR outputs
- Navigate between pages with controls
- Toggle between rendered and raw markdown views
- Character count statistics

**Example Usage:**
```bash
uv run streamlit run compare_md.py
```

**Architecture:**

```mermaid
graph TB
    subgraph "User Interface"
        UI[Streamlit Web UI]
        INPUT[Folder Input: AR2024_C]
        NAV[Navigation Controls]
        SELECT[Page Selector Dropdown]
        MODE[View Mode Toggle]
        DISPLAY[Split View Display]
    end
    
    subgraph "File System"
        BASE[Base Folder: AR2024_C/]
        MD[md/ folder<br/>PyMuPDF4LLM output]
        LLM_MD[llm_md/ folder<br/>LLM OCR output]
        MD_FILES[page_0001.md<br/>page_0002.md<br/>...]
        LLM_FILES[page_0001.md<br/>page_0002.md<br/>...]
    end
    
    subgraph "Core Functions"
        LOAD[load_markdown_files<br/>Find common pages]
        READ[read_markdown_file<br/>Load content]
        COMPARE[display_markdown_comparison<br/>Render side-by-side]
    end
    
    subgraph "Session State"
        STATE[st.session_state.page_index<br/>Current page tracking]
    end
    
    UI --> INPUT
    INPUT --> BASE
    BASE --> MD
    BASE --> LLM_MD
    MD --> MD_FILES
    LLM_MD --> LLM_FILES
    
    BASE --> LOAD
    LOAD --> MD_FILES
    LOAD --> LLM_FILES
    LOAD --> |Common pages list| SELECT
    
    SELECT --> STATE
    NAV --> STATE
    STATE --> |Current page| READ
    
    READ --> MD_FILES
    READ --> LLM_FILES
    READ --> |Left content| COMPARE
    READ --> |Right content| COMPARE
    
    MODE --> COMPARE
    COMPARE --> DISPLAY
    DISPLAY --> |Rendered or Raw| UI
    
    style UI fill:#e1f5ff
    style DISPLAY fill:#e1f5ff
    style BASE fill:#fff4e6
    style MD fill:#f0f0f0
    style LLM_MD fill:#f0f0f0
    style STATE fill:#e8f5e9
```

### 🧪 Agent Demo (`agent.py`)

Example pydantic-ai agent implementation featuring:

- Multi-tool agent (calculator + lottery result extractor)
- Agent delegation pattern for vision tasks
- Structured output with Pydantic models

## Tech Stack

- **PyMuPDF / PyMuPDF4LLM** - Traditional PDF text extraction
- **pydantic-ai** - LLM agent framework with structured outputs
- **OpenRouter** - Access to Google Gemini vision models
- **Langfuse** - LLM observability and monitoring
- **Streamlit** - Interactive comparison dashboard
- **uv** - Fast Python package and project manager

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables (create `.env` file):
```env
OPENROUTER_API_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Typical Workflow

1. **Prepare PDF pages**:
   ```bash
   uv run main.py --export-pages AR2024_C.pdf --range 1-10
   ```
   Creates: `AR2024_C/md/`, `AR2024_C/png/`, `AR2024_C/png_bw/`

2. **Run LLM OCR**:
   ```bash
   uv run llm_ocr.py AR2024_C/png_bw/
   ```
   Creates: `AR2024_C/llm_md/`

3. **Compare results**:
   ```bash
   uv run streamlit run compare_md.py
   ```
   Opens interactive dashboard at `http://localhost:8501`

## Project Structure

```
.
├── main.py          # PDF processing utilities
├── llm_ocr.py       # LLM-based vision OCR
├── compare_md.py    # Streamlit comparison dashboard
├── agent.py         # pydantic-ai agent examples
├── pyproject.toml   # uv project configuration
└── AR2024_C.pdf     # Sample PDF for testing
```
