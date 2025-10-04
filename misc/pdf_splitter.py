#!/usr/bin/env python3
"""
PDF Splitter Script
Splits a PDF file into multiple parts with specified number of pages per part.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import pypdf
except ImportError:
    print("Error: pypdf is required. Install with: pip install pypdf")
    sys.exit(1)


def split_pdf(input_path, output_dir=None, pages_per_part=10):
    """
    Split a PDF file into multiple parts.

    Args:
        input_path (str): Path to the input PDF file
        output_dir (str, optional): Directory for output files. Defaults to None.
        pages_per_part (int, optional): Number of pages per part. Defaults to 10.
    """
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        return False

    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: Input file '{input_path}' is not a PDF.")
        return False

    # Set output directory
    if output_dir is None:
        output_dir = input_path.parent / input_path.stem
    else:
        output_dir = Path(output_dir)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Read the input PDF
        reader = pypdf.PdfReader(input_path)
        total_pages = len(reader.pages)

        print(f"Processing PDF: {input_path}")
        print(f"Total pages: {total_pages}")
        print(f"Pages per part: {pages_per_part}")
        print(f"Output directory: {output_dir}")

        # Calculate number of parts needed
        num_parts = (total_pages + pages_per_part - 1) // pages_per_part
        print(f"Will create {num_parts} part(s)")

        # Split the PDF
        for part_num in range(num_parts):
            start_page = part_num * pages_per_part
            end_page = min((part_num + 1) * pages_per_part, total_pages)

            # Create a new PDF writer for this part
            writer = pypdf.PdfWriter()

            # Add pages to this part
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Create output filename
            output_filename = f"{input_path.stem}_part_{part_num + 1}.pdf"
            output_path = output_dir / output_filename

            # Write the part to file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            print(f"Created: {output_path} (pages {start_page + 1}-{end_page})")

        print(f"\nSuccessfully split PDF into {num_parts} part(s)")
        return True

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Split a PDF file into multiple parts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf -o output_folder
  %(prog)s document.pdf -p 5
  %(prog)s document.pdf -o output_folder -p 15
        """
    )

    parser.add_argument(
        'input_pdf',
        help='Path to the PDF file to split'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory for split parts (default: same name as input PDF without extension)',
        default=None
    )

    parser.add_argument(
        '-p', '--pages',
        type=int,
        help='Number of pages per part (default: 10)',
        default=10
    )

    args = parser.parse_args()

    # Validate pages argument
    if args.pages <= 0:
        print("Error: Number of pages per part must be greater than 0.")
        sys.exit(1)

    # Split the PDF
    success = split_pdf(args.input_pdf, args.output, args.pages)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()