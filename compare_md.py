#!/usr/bin/env python3
"""
Streamlit app for comparing markdown outputs from PyMuPDF4LLM and LLM OCR.

This app provides a side-by-side comparison interface with navigation controls
and the ability to toggle between rendered and raw markdown views.
"""
import streamlit as st
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="OCR Comparison",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def load_markdown_files(folder_path: Path) -> list[str]:
    """
    Load and return sorted list of common page names from both md folders.
    
    Args:
        folder_path: Base folder containing md/ and llm_md/ subdirectories
    
    Returns:
        Sorted list of page filenames (e.g., ['page_0001.md', 'page_0002.md'])
    """
    md_dir = folder_path / "md"
    llm_md_dir = folder_path / "llm_md"
    
    # Get list of files from both directories
    md_files = set()
    llm_md_files = set()
    
    if md_dir.exists():
        md_files = {f.name for f in md_dir.glob("*.md")}
    
    if llm_md_dir.exists():
        llm_md_files = {f.name for f in llm_md_dir.glob("*.md")}
    
    # Return intersection (common files) sorted
    common_files = sorted(md_files & llm_md_files)
    return common_files


def read_markdown_file(file_path: Path) -> str:
    """
    Read markdown file content, handling errors gracefully.
    
    Args:
        file_path: Path to the markdown file
    
    Returns:
        File content or error message
    """
    try:
        if not file_path.exists():
            return f"*File not found: {file_path.name}*"
        return file_path.read_text(encoding='utf-8')
    except Exception as e:
        return f"*Error reading file: {str(e)}*"


def display_markdown_comparison(left_content: str, right_content: str, render_mode: str):
    """
    Display two markdown contents side by side.
    
    Args:
        left_content: Content for left column (PyMuPDF4LLM)
        right_content: Content for right column (LLM OCR)
        render_mode: "Rendered" or "Raw Markdown"
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📘 PyMuPDF4LLM Output (main.py)")
        if render_mode == "Rendered":
            st.markdown(left_content)
        else:
            st.code(left_content, language="markdown", line_numbers=True)
    
    with col2:
        st.subheader("🤖 LLM OCR Output (llm_ocr.py)")
        if render_mode == "Rendered":
            st.markdown(right_content)
        else:
            st.code(right_content, language="markdown", line_numbers=True)


def main():
    """Main Streamlit app"""
    
    # Title and description
    st.title("📄 OCR Markdown Comparison Tool")
    st.markdown("""
    Compare markdown outputs from **PyMuPDF4LLM** (traditional PDF extraction) 
    and **LLM OCR** (vision-based extraction).
    """)
    
    st.divider()
    
    # Folder input
    folder_input = st.text_input(
        "Base Folder Path",
        value="AR2024_C",
        help="Enter the base folder containing md/ and llm_md/ subdirectories"
    )
    
    folder_path = Path(folder_input)
    
    # Validate folder exists
    if not folder_path.exists():
        st.error(f"❌ Folder not found: {folder_path}")
        st.stop()
    
    # Load available pages
    pages = load_markdown_files(folder_path)
    
    if not pages:
        st.warning("⚠️ No matching markdown files found in both md/ and llm_md/ folders")
        st.stop()
    
    # Initialize session state for current page index
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0
    
    # Ensure page_index is within valid bounds
    if st.session_state.page_index >= len(pages):
        st.session_state.page_index = len(pages) - 1
    if st.session_state.page_index < 0:
        st.session_state.page_index = 0
    
    # Navigation controls
    st.markdown("### 🧭 Navigation")
    
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
    
    with nav_col1:
        if st.button("⬅️ Previous", use_container_width=True):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()
    
    with nav_col2:
        # Dropdown selector
        selected_page = st.selectbox(
            "Select Page",
            options=pages,
            index=st.session_state.page_index,
            label_visibility="collapsed"
        )
        # Update index if dropdown changed
        new_index = pages.index(selected_page)
        if new_index != st.session_state.page_index:
            st.session_state.page_index = new_index
            st.rerun()
    
    with nav_col3:
        if st.button("Next ➡️", use_container_width=True):
            if st.session_state.page_index < len(pages) - 1:
                st.session_state.page_index += 1
                st.rerun()
    
    # Page counter
    st.caption(f"Page {st.session_state.page_index + 1} of {len(pages)}")
    
    # View mode toggle
    render_mode = st.radio(
        "View Mode",
        options=["Rendered", "Raw Markdown"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Load current page content
    current_page = pages[st.session_state.page_index]
    
    left_file = folder_path / "md" / current_page
    right_file = folder_path / "llm_md" / current_page
    
    left_content = read_markdown_file(left_file)
    right_content = read_markdown_file(right_file)
    
    # Display comparison
    display_markdown_comparison(left_content, right_content, render_mode)
    
    # Footer with stats
    st.divider()
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.caption(f"📊 Left: {len(left_content)} characters")
    with stats_col2:
        st.caption(f"📊 Right: {len(right_content)} characters")


if __name__ == "__main__":
    main()

