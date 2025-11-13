#!/usr/bin/env python3
"""
Helper script to batch-convert PDF files to Markdown using PyMuPDF4LLM.

This script scans the 'pdfs' directory for PDF files and converts them to
markdown format, saving the output with the same base name (e.g., file.pdf -> file.md).
"""
import pymupdf
import pymupdf.layout
import pymupdf4llm
from pathlib import Path
import sys
import argparse
from PIL import Image, ImageEnhance

def parse_page_range(range_str, total_pages):
    """
    Parse a page range string into a list of page indices.
    
    Args:
        range_str: String like "1-5", "1,3,5-7", or "all"
        total_pages: Total number of pages in the document
    
    Returns:
        List of 0-indexed page numbers
    
    Examples:
        "1-5" -> [0, 1, 2, 3, 4]
        "1,3,5" -> [0, 2, 4]
        "all" -> [0, 1, 2, ..., total_pages-1]
    """
    if range_str.lower() == "all":
        return list(range(total_pages))
    
    pages = set()
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle range like "1-5"
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            # Convert to 0-indexed and add to set
            for i in range(start - 1, end):
                if 0 <= i < total_pages:
                    pages.add(i)
        else:
            # Handle single page like "3"
            page_num = int(part.strip()) - 1  # Convert to 0-indexed
            if 0 <= page_num < total_pages:
                pages.add(page_num)
    
    return sorted(list(pages))

def export_pages_to_images(pdf_path, page_range, output_dir=None, dpi=150):
    """
    Export specific pages from a PDF as PNG images.
    
    Args:
        pdf_path: Path to the PDF file
        page_range: Page range string like "1-5", "1,3,5-7", or "all"
        output_dir: Optional output directory. If None, uses PDF basename
        dpi: Resolution for exported images (default 150)
    
    Returns:
        True if successful, False otherwise
    
    Examples:
        export_pages_to_images("test.pdf", "1-5")
        export_pages_to_images("test.pdf", "all", output_dir="images")
        export_pages_to_images("test.pdf", "1,3,5", dpi=300)
    """
    try:
        pdf_path = Path(pdf_path)
        print(f"Opening PDF: {pdf_path}")
        
        # Open the PDF document
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        print(f"  Total pages: {total_pages}")
        
        # Parse the page range
        try:
            page_indices = parse_page_range(page_range, total_pages)
        except Exception as e:
            print(f"  ✗ Error parsing page range '{page_range}': {str(e)}")
            doc.close()
            return False
        
        if not page_indices:
            print(f"  ✗ No valid pages in range '{page_range}'")
            doc.close()
            return False
        
        print(f"  Pages to export: {len(page_indices)}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = pdf_path.stem  # Use PDF basename without extension
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"  Output directory: {output_path}")
        
        # Calculate zoom factor for desired DPI
        zoom = dpi / 72  # 72 is the default DPI
        mat = pymupdf.Matrix(zoom, zoom)
        
        # Export each page
        for idx, page_num in enumerate(page_indices, start=1):
            page = doc[page_num]
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Create output filename with 4-digit padding
            output_file = output_path / f"page_{page_num + 1:04d}.png"
            
            # Save as PNG
            pix.save(output_file)
            
            print(f"  ✓ [{idx}/{len(page_indices)}] Saved page {page_num + 1} -> {output_file}")
        
        doc.close()
        print(f"\n✓ Successfully exported {len(page_indices)} page(s) to '{output_path}'")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def export_pages_to_markdown(pdf_path, page_range, output_dir=None):
    """
    Export specific pages from a PDF as individual markdown files.
    
    Args:
        pdf_path: Path to the PDF file
        page_range: Page range string like "1-5", "1,3,5-7", or "all"
        output_dir: Optional output directory. If None, uses PDF basename
    
    Returns:
        True if successful, False otherwise
    
    Examples:
        export_pages_to_markdown("test.pdf", "1-5")
        export_pages_to_markdown("test.pdf", "all", output_dir="markdown")
    """
    try:
        pdf_path = Path(pdf_path)
        print(f"Opening PDF: {pdf_path}")
        
        # Open the PDF document
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        print(f"  Total pages: {total_pages}")
        
        # Parse the page range
        try:
            page_indices = parse_page_range(page_range, total_pages)
        except Exception as e:
            print(f"  ✗ Error parsing page range '{page_range}': {str(e)}")
            doc.close()
            return False
        
        if not page_indices:
            print(f"  ✗ No valid pages in range '{page_range}'")
            doc.close()
            return False
        
        print(f"  Pages to export: {len(page_indices)}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = pdf_path.stem  # Use PDF basename without extension
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"  Output directory: {output_path}")
        
        doc.close()
        
        # Export each page as markdown
        for idx, page_num in enumerate(page_indices, start=1):
            # Extract markdown for this specific page only
            md_text = pymupdf4llm.to_markdown(str(pdf_path), pages=[page_num])
            
            # Create output filename with 4-digit padding
            output_file = output_path / f"page_{page_num + 1:04d}.md"
            
            # Write markdown to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_text)
            
            print(f"  ✓ [{idx}/{len(page_indices)}] Saved page {page_num + 1} -> {output_file}")
        
        print(f"\n✓ Successfully exported {len(page_indices)} page(s) to '{output_path}'")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def process_images_to_bw(input_dir, contrast_factor=1.25):
    """
    Convert color PNG images to grayscale with enhanced contrast for VLM optimization.
    
    Args:
        input_dir: Directory containing color PNG images (e.g., "AR2024_C/png/")
        contrast_factor: Contrast enhancement multiplier (default 1.25 for moderate increase)
    
    Returns:
        Tuple of (success: bool, processed_count: int)
    
    Examples:
        process_images_to_bw("AR2024_C/png/")
        process_images_to_bw("AR2024_C/png/", contrast_factor=1.3)
    """
    try:
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"  ✗ Error: Input directory '{input_dir}' does not exist")
            return False, 0
        
        # Create output directory (replace last part with _bw suffix)
        output_dir = str(input_path).replace('/png', '/png_bw')
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all PNG files
        png_files = sorted(list(input_path.glob("*.png")))
        
        if not png_files:
            print(f"  ✗ No PNG files found in '{input_dir}'")
            return False, 0
        
        print(f"  Processing {len(png_files)} image(s) to grayscale...")
        
        processed_count = 0
        for idx, png_file in enumerate(png_files, start=1):
            # Open image
            img = Image.open(png_file)
            
            # Convert to grayscale
            gray_img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray_img)
            enhanced_img = enhancer.enhance(contrast_factor)
            
            # Save to output directory
            output_file = output_path / png_file.name
            enhanced_img.save(output_file)
            
            print(f"  ✓ [{idx}/{len(png_files)}] Processed {png_file.name} -> {output_file}")
            processed_count += 1
        
        print(f"\n✓ Successfully processed {processed_count} image(s) to '{output_path}'")
        return True, processed_count
        
    except Exception as e:
        print(f"  ✗ Error processing images: {str(e)}")
        return False, 0

def export_pages_combined(pdf_path, page_range, dpi=150):
    """
    Export pages from a PDF as both markdown and PNG images.
    
    Creates a directory structure:
    PDF_basename/
        md/
            page_0001.md
            page_0002.md
        png/
            page_0001.png
            page_0002.png
        png_bw/
            page_0001.png (grayscale, enhanced contrast)
            page_0002.png (grayscale, enhanced contrast)
    
    Args:
        pdf_path: Path to the PDF file
        page_range: Page range string like "1-5", "1,3,5-7", or "all"
        dpi: Resolution for exported images (default 150)
    
    Returns:
        True if successful, False otherwise
    
    Examples:
        export_pages_combined("test.pdf", "1-5")
        export_pages_combined("test.pdf", "all", dpi=300)
    """
    try:
        pdf_path = Path(pdf_path)
        base_dir = pdf_path.stem
        
        print(f"Exporting pages from: {pdf_path}")
        print(f"Base output directory: {base_dir}/")
        print(f"Page range: {page_range}\n")
        
        # Export markdown files
        print("=" * 60)
        print("MARKDOWN EXPORT")
        print("=" * 60)
        md_dir = f"{base_dir}/md"
        md_success = export_pages_to_markdown(pdf_path, page_range, output_dir=md_dir)
        
        print()
        
        # Export PNG files
        print("=" * 60)
        print("PNG EXPORT")
        print("=" * 60)
        png_dir = f"{base_dir}/png"
        png_success = export_pages_to_images(pdf_path, page_range, output_dir=png_dir, dpi=dpi)
        
        print()
        
        # Process images to grayscale with enhanced contrast
        print("=" * 60)
        print("GRAYSCALE PROCESSING (VLM Optimization)")
        print("=" * 60)
        bw_success, bw_count = process_images_to_bw(png_dir)
        
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if md_success and png_success and bw_success:
            print(f"✓ Successfully exported to:")
            print(f"  - Markdown files: {md_dir}/")
            print(f"  - PNG files (color): {png_dir}/")
            print(f"  - PNG files (grayscale): {base_dir}/png_bw/")
            return True
        else:
            print("✗ Some exports failed:")
            if not md_success:
                print(f"  - Markdown export failed")
            if not png_success:
                print(f"  - PNG export failed")
            if not bw_success:
                print(f"  - Grayscale processing failed")
            return False
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def extract_markdown_from_pdf(pdf_path, output_path=None):
    """
    Extract markdown from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Optional custom output path. If None, uses same name with .md extension
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Processing: {pdf_path}")
        
        # Convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # Determine output path
        if output_path is None:
            output_path = Path(pdf_path).with_suffix('.md')
        
        # Write markdown to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        
        print(f"  ✓ Saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def batch_extract(directory="pdfs"):
    """
    Batch extract markdown from all PDFs in a directory.
    
    Args:
        directory: Directory containing PDF files
    """
    pdf_dir = Path(directory)
    
    if not pdf_dir.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return
    
    # Find all PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)\n")
    
    # Process each PDF
    success_count = 0
    for pdf_file in pdf_files:
        if extract_markdown_from_pdf(pdf_file):
            success_count += 1
        print()
    
    # Summary
    print(f"Completed: {success_count}/{len(pdf_files)} files processed successfully")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='PDF processing utility: extract markdown and/or export pages as images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Export pages 1-5 from a PDF (both markdown and PNG)
  python main.py --export-pages document.pdf --range 1-5
  
  # Export all pages at high resolution
  python main.py --export-pages document.pdf --range all --dpi 300
  
  # Export specific pages
  python main.py --export-pages document.pdf --range 1,3,5-7
  
  # Legacy: batch extract markdown from directory
  python main.py pdfs/
        '''
    )
    
    parser.add_argument(
        '--export-pages',
        dest='export_pdf',
        metavar='PDF_FILE',
        help='Export pages from PDF as markdown and PNG images'
    )
    
    parser.add_argument(
        '--range',
        dest='page_range',
        metavar='RANGE',
        help='Page range (e.g., "1-5", "1,3,5-7", or "all"). Required with --export-pages'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        metavar='DPI',
        help='Resolution for PNG export (default: 150)'
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='PDF file or directory to process (legacy mode)'
    )
    
    args = parser.parse_args()
    
    # New mode: export pages with --export-pages
    if args.export_pdf:
        if not args.page_range:
            parser.error("--range is required when using --export-pages")
        
        pdf_path = Path(args.export_pdf)
        if not pdf_path.exists():
            print(f"Error: File '{pdf_path}' not found")
            sys.exit(1)
        
        if not pdf_path.is_file() or pdf_path.suffix.lower() != '.pdf':
            print(f"Error: '{pdf_path}' is not a valid PDF file")
            sys.exit(1)
        
        # Export pages as both markdown and PNG
        success = export_pages_combined(pdf_path, args.page_range, dpi=args.dpi)
        sys.exit(0 if success else 1)
    
    # Legacy mode: process file or directory
    elif args.path:
        path = Path(args.path)
        
        if path.is_file() and path.suffix.lower() == '.pdf':
            # Single file - full document markdown extraction
            extract_markdown_from_pdf(path)
        elif path.is_dir():
            # Directory - batch extraction
            batch_extract(str(path))
        else:
            print(f"Error: '{path}' is not a valid PDF file or directory")
            sys.exit(1)
    
    else:
        # No arguments - show help
        parser.print_help()

if __name__ == "__main__":
    main()

