#!/usr/bin/env python3
"""
Convert images to JPEG for epub optimization.
Usage: python convert_images_to_jpeg.py [quality]
Quality: 1-100 (default: 85)
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# Configuration
QUALITY = int(sys.argv[1]) if len(sys.argv) > 1 else 85
SOURCE_DIR = Path(__file__).parent / "images"
DEST_DIR = Path(__file__).parent / "epub_images"

# Supported input formats
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}


def convert_to_jpeg(source_path: Path, dest_path: Path, quality: int) -> None:
    """Convert an image to JPEG format."""
    try:
        with Image.open(source_path) as img:
            # Convert RGBA to RGB (JPEG doesn't support alpha)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPEG
            img.save(dest_path, 'JPEG', quality=quality, optimize=True)
            
            # Report size reduction
            source_size = source_path.stat().st_size
            dest_size = dest_path.stat().st_size
            reduction = (1 - dest_size / source_size) * 100
            print(f"  {source_path.name} -> {dest_path.name}: "
                  f"{source_size/1024:.1f}KB -> {dest_size/1024:.1f}KB "
                  f"({reduction:+.1f}%)")
    except Exception as e:
        print(f"  ERROR converting {source_path}: {e}")


def main():
    print(f"Converting images to JPEG (quality={QUALITY})")
    print(f"Source: {SOURCE_DIR}")
    print(f"Destination: {DEST_DIR}")
    print("-" * 60)
    
    total_source_size = 0
    total_dest_size = 0
    converted_count = 0
    
    # Process all subdirectories
    for subdir in sorted(SOURCE_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        
        dest_subdir = DEST_DIR / subdir.name
        dest_subdir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{subdir.name}/")
        
        for image_file in sorted(subdir.iterdir()):
            if image_file.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            
            # Output filename: change extension to .jpg
            dest_filename = image_file.stem + ".jpg"
            dest_path = dest_subdir / dest_filename
            
            convert_to_jpeg(image_file, dest_path, QUALITY)
            
            total_source_size += image_file.stat().st_size
            total_dest_size += dest_path.stat().st_size
            converted_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Converted: {converted_count} images")
    print(f"  Original total: {total_source_size/1024/1024:.2f} MB")
    print(f"  JPEG total: {total_dest_size/1024/1024:.2f} MB")
    print(f"  Reduction: {(1 - total_dest_size/total_source_size)*100:.1f}%")
    print(f"\nTo adjust quality, run: python convert_images_to_jpeg.py <quality>")
    print(f"Quality range: 1-100 (higher = better quality, larger file)")


if __name__ == "__main__":
    main()
