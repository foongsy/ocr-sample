#!/usr/bin/env python3
"""
LLM-based OCR script using pydantic-ai and openrouter.

Processes images in a folder using vision-capable LLM to extract text
and save as markdown files. Uses Langfuse for monitoring and observability.
"""
import asyncio
import argparse
from pathlib import Path
from pydantic_ai import Agent, BinaryContent
from langfuse import get_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Langfuse client
langfuse = get_client()

# Verify connection and instrument agents
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
    Agent.instrument_all()
else:
    print("Warning: Langfuse authentication failed. Proceeding without instrumentation.")

# Create OCR agent
ocr_agent = Agent(
    'openrouter:google/gemini-2.5-flash-lite',
    instrument=True,
    system_prompt="""You are an expert OCR assistant. Extract all text from the provided image 
and format it as clean, well-structured markdown. Preserve the document structure, headings, 
lists, tables, and formatting as much as possible. Output only the markdown content without 
any additional commentary or explanation."""
)

# Create refinement agent
refine_agent = Agent(
    'openrouter:google/gemini-2.5-flash',
    instrument=True,
    system_prompt="""You are an expert text refinement specialist. Your task is to improve OCR-extracted text by:

1. Correcting OCR misrecognitions and errors
2. Fixing formatting issues, spacing, and line breaks
3. Improving markdown structure and consistency
4. Preserving the original document structure and meaning
5. Using the provided image as reference to verify accuracy

Output only the refined markdown content without any commentary."""
)


async def process_image_to_markdown(image_path: Path) -> str:
    """
    Process a single image file and extract text as markdown using LLM.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Extracted text formatted as markdown
    
    Raises:
        Exception if image processing fails
    """
    # Read image bytes
    image_data = image_path.read_bytes()
    
    # Determine media type from extension
    ext = image_path.suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
    }
    media_type = media_type_map.get(ext, 'image/png')
    
    # Process with OCR agent
    result = await ocr_agent.run(
        [
            "Extract all text from this image and format as markdown:",
            BinaryContent(data=image_data, media_type=media_type),
        ]
    )
    
    return result.output


async def refine_ocr_text(raw_text: str, image_path: Path) -> str:
    """
    Refine raw OCR text using both the text and original image as context.
    
    Args:
        raw_text: Raw OCR output to be refined
        image_path: Path to original image for visual reference
    
    Returns:
        Refined and corrected markdown text
    """
    image_data = image_path.read_bytes()
    ext = image_path.suffix.lower()
    media_type_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}
    media_type = media_type_map.get(ext, 'image/png')
    
    result = await refine_agent.run(
        [
            f"Here is raw OCR text that may contain errors. Please refine and correct it using the image as reference:\n\n{raw_text}",
            BinaryContent(data=image_data, media_type=media_type),
        ]
    )
    
    return result.output


async def process_folder(image_folder: str):
    """
    Process all images in a folder and save markdown outputs.
    
    Args:
        image_folder: Path to folder containing images
    """
    # Validate input folder
    input_path = Path(image_folder)
    if not input_path.exists():
        print(f"Error: Input folder '{image_folder}' does not exist")
        return False
    
    if not input_path.is_dir():
        print(f"Error: '{image_folder}' is not a directory")
        return False
    
    # Determine output directory: {parent_of_input}/llm_md/
    output_path = input_path.parent / "llm_md"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files (non-recursive)
    image_extensions = ['*.png', '*.jpg', '*.jpeg']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(ext))
    
    # Sort for consistent ordering
    image_files = sorted(image_files)
    
    if not image_files:
        print(f"No image files found in '{image_folder}'")
        return False
    
    print(f"Found {len(image_files)} image(s) to process")
    print(f"Input folder: {input_path}")
    print(f"Output folder: {output_path}")
    print("=" * 60)
    
    # Process each image
    success_count = 0
    error_count = 0
    
    for idx, image_file in enumerate(image_files, start=1):
        try:
            print(f"[{idx}/{len(image_files)}] Processing {image_file.name}... ", end="", flush=True)
            
            # Extract text as markdown
            raw_text = await process_image_to_markdown(image_file)
            
            # Refine the extracted text
            markdown_text = await refine_ocr_text(raw_text, image_file)
            
            # Save to output file
            output_file = output_path / f"{image_file.stem}.md"
            output_file.write_text(markdown_text, encoding='utf-8')
            
            print(f"✓ Saved to {output_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            error_count += 1
    
    # Print summary
    print("=" * 60)
    print(f"Processing complete:")
    print(f"  ✓ Success: {success_count}")
    if error_count > 0:
        print(f"  ✗ Errors: {error_count}")
    print(f"  Output location: {output_path}")
    
    return error_count == 0


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LLM-based OCR: Extract text from images using vision-capable LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process all images in a folder
  uv run llm_ocr.py AR2024_C/png_bw/
  
  # Process color images
  uv run llm_ocr.py AR2024_C/png/

Output will be saved to a 'llm_md' folder in the parent directory of the input folder.
For example: AR2024_C/png_bw/ → AR2024_C/llm_md/
        '''
    )
    
    parser.add_argument(
        'image_folder',
        help='Path to folder containing images to process (png, jpg, jpeg)'
    )
    
    args = parser.parse_args()
    
    # Process the folder
    success = await process_folder(args.image_folder)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

