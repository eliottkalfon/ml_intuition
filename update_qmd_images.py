#!/usr/bin/env python3
"""
Update QMD files to use conditional image formatting for epub.
This replaces image references with format-conditional blocks.
"""

import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
QMD_FILES = list(BASE_DIR.glob("**/*.qmd"))

# Pattern to match markdown image syntax
# Captures: alt text, image path, optional attributes
IMAGE_PATTERN = re.compile(
    r'!\[([^\]]*)\]\((/?)images/([^)]+\.(?:png|jpg|jpeg|gif))\)(\{[^}]*\})?'
)


def convert_image_path_to_jpeg(path: str) -> str:
    """Convert an image path to its JPEG equivalent."""
    # Replace extension with .jpg
    return re.sub(r'\.(png|jpeg|gif)$', '.jpg', path, flags=re.IGNORECASE)


def create_conditional_block(alt_text: str, leading_slash: str, image_path: str, attributes: str) -> str:
    """Create a conditional block for epub/non-epub formats."""
    attributes = attributes or ""
    jpeg_path = convert_image_path_to_jpeg(image_path)
    
    # For epub, use the epub_images folder with jpg
    # For other formats, keep the original
    block = f"""::: {{.content-visible when-format="epub"}}
![{alt_text}]({leading_slash}epub_images/{jpeg_path}){attributes}
:::

::: {{.content-hidden when-format="epub"}}
![{alt_text}]({leading_slash}images/{image_path}){attributes}
:::"""
    return block


def process_file(filepath: Path) -> int:
    """Process a single QMD file and return count of replacements."""
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    
    replacements = 0
    
    # Find all image references and replace them
    def replace_image(match):
        nonlocal replacements
        alt_text = match.group(1)
        leading_slash = match.group(2)
        image_path = match.group(3)
        attributes = match.group(4)
        
        replacements += 1
        return create_conditional_block(alt_text, leading_slash, image_path, attributes)
    
    content = IMAGE_PATTERN.sub(replace_image, content)
    
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        print(f"  Updated {filepath.relative_to(BASE_DIR)}: {replacements} image(s)")
    
    return replacements


def main():
    print("Updating QMD files with conditional image formatting")
    print("=" * 60)
    
    total_replacements = 0
    updated_files = 0
    
    for qmd_file in sorted(QMD_FILES):
        # Skip files in docs, print-build directories
        rel_path = qmd_file.relative_to(BASE_DIR)
        if str(rel_path).startswith(('docs/', 'print-build/')):
            continue
        
        replacements = process_file(qmd_file)
        if replacements > 0:
            total_replacements += replacements
            updated_files += 1
    
    print("=" * 60)
    print(f"Summary: Updated {updated_files} files with {total_replacements} image references")


if __name__ == "__main__":
    main()
