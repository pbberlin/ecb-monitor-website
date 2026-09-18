import os
import re

target_opacity = "0.75"
target_opacity = "0.7"
target_opacity = "0.65"

for fn in os.listdir('.'):

    if fn.lower().endswith('.svg') and re.match(r'^0[1-6]-', fn):
        
        with open(fn, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # check, if attribute already exists
        if not re.search(r'<svg\b[^>]*?opacity=["\']', content, flags=re.IGNORECASE): 
            
            # first <svg Tag -   
            #    \b for matching exactly  "<svg
            new_content = re.sub(r'(<svg\b)', rf'\1 opacity="{target_opacity}"', content, count=1, flags=re.IGNORECASE)
            
            with open(fn, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
            print(f"transparency set for {fn}")
            
        else:
            
            # replace existing attribute
            new_content = re.sub(
                r'(<svg\b[^>]*?)opacity=(["\']).*?\2', 
                rf'\1opacity="{target_opacity}"', 
                content, 
                count=1, 
                flags=re.IGNORECASE
            )
            
            with open(fn, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
            print(f"transparency updated for {fn}")