print("execute from HOME DIR")

import os
import shutil

STATIC_DIR = 'static'
UNUSED_DIR = 'tmp-unused'

# Add folders where your code lives
SEARCH_DIRS = ['.'] 

IGNORE_DIRS = {UNUSED_DIR, '.git', 'venv', '.venv', '__pycache__', 'node_modules', 'cytoscape-fcose'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.cpt', '.mp4'}

def get_all_images():
    images = []
    for root, _, files in os.walk(STATIC_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                images.append(os.path.join(root, file))
    return images

def get_all_code_files():
    code_files = []
    for search_dir in SEARCH_DIRS:
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if file.endswith(('.html', '.py', '.js', '.css', '.ts', '.md')):
                    code_files.append(os.path.join(root, file))
    return code_files

def find_unused_images():
    images = get_all_images()
    code_files = get_all_code_files()
    
    code_contents = []
    for cf in code_files:
        # FIX 1: errors='ignore' ensures we NEVER skip an HTML file due to a weird character
        try:
            with open(cf, 'r', encoding='utf-8', errors='ignore') as f:
                # Store the file content fully lowercased for case-insensitive searching
                code_contents.append(f.read().lower())
        except Exception as e:
            print(f"Warning: Could not read {cf} - {e}")

    unused_images = []
    
    for image_path in images:
        # FIX 2: Lowercase the filename for the search
        filename = os.path.basename(image_path).lower()
        is_used = False
        
        for content in code_contents:
            if filename in content:
                is_used = True
                break
                
        if not is_used:
            unused_images.append(image_path)

    return unused_images

def move_unused_images(orphans):
    moved_count = 0
    for image_path in orphans:
        dest_path = os.path.join(UNUSED_DIR, image_path)
        dest_dir = os.path.dirname(dest_path)
        
        os.makedirs(dest_dir, exist_ok=True)
        
        try:
            shutil.move(image_path, dest_path)
            moved_count += 1
        except Exception as e:
            print(f"Error moving {image_path}: {e}")
            
    return moved_count

if __name__ == "__main__":
    print("Scanning for unused images...")
    orphans = find_unused_images()
    
    if not orphans:
        print("No unused images found!")
    else:
        print(f"Found {len(orphans)} potentially unused images:")
        for orphan in orphans:
            print(f" - {orphan}")
            
        print(f"\nMoving {len(orphans)} files to '{UNUSED_DIR}/' directory...")
        success_count = move_unused_images(orphans)
        
        print(f"Successfully moved {success_count} files.")