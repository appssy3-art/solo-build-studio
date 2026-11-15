import os
import re
from huggingface_hub import HfApi, hf_hub_download

# Hugging Face auth
token_path = os.path.expanduser('~/.cache/huggingface/token')
token = open(token_path, encoding='utf-8').read().strip()
api = HfApi(token=token)
user = api.whoami()['name']

NEW_SECTION = """## 🔗 관련 링크 및 채널

- 🚀 **개발자 허브 (SOLO BUILD-H):** [전체 프로젝트 & 웹 앱 둘러보기](https://appssy3-art.github.io/solo-build-studio/)

- 📺 **유튜브 채널 (솔로빌드):** [개발 과정 및 쇼츠 영상 보기](https://www.youtube.com/@solobuild.studio)"""

def update_readme_text(content, model_title=""):
    if not content.strip():
        return f"# {model_title}\n\n{NEW_SECTION}\n"
    
    # Check if section exists
    has_section = bool(re.search(r'#+\s*🔗?\s*관련\s*링크\s*및\s*채널', content))
    
    if has_section:
        # Pattern matches the heading and everything until next heading or end of string
        pattern = r'(\n*#+\s*🔗?\s*관련\s*링크\s*및\s*채널.*?)($|(?=\n#+\s))'
        updated = re.sub(pattern, r'\n\n' + NEW_SECTION + r'\n\n', content, flags=re.DOTALL)
    else:
        updated = content.rstrip() + '\n\n\n' + NEW_SECTION + '\n'
        
    return updated.strip() + '\n'

def main():
    models = [m.id for m in api.list_models(author=user)]
    print(f"Total models to process: {len(models)}")
    
    success_count = 0
    skip_count = 0
    
    for idx, model_id in enumerate(models, start=1):
        model_name = model_id.split('/')[-1]
        print(f"[{idx}/{len(models)}] Processing {model_id}...")
        
        # 1. Fetch current README
        content = ""
        try:
            local_path = hf_hub_download(repo_id=model_id, filename="README.md", token=token)
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"  -> No existing README found ({e}). Creating new.")
            content = f"# {model_name}\n"
            
        # 2. Update content
        new_content = update_readme_text(content, model_name)
        
        if new_content == content:
            print("  -> Already up to date. Skipping.")
            skip_count += 1
            continue
            
        # 3. Upload to Hugging Face
        try:
            api.upload_file(
                path_or_fileobj=new_content.encode("utf-8"),
                path_in_repo="README.md",
                repo_id=model_id,
                commit_message="docs: update developer hub (SOLO BUILD-H) & youtube links"
            )
            print("  -> Successfully updated on Hugging Face!")
            success_count += 1
        except Exception as e:
            print(f"  -> ERROR uploading: {e}")
            
    print("\n=== SUMMARY ===")
    print(f"Updated: {success_count}")
    print(f"Skipped / Unchanged: {skip_count}")

    # Also sync local folders if present
    local_dirs = [
        r"E:\ai랩\hf_connectailab-rl-solo-build-H-MicroDuck-100k",
        r"E:\ai랩\hf_connectailab-rl-solo-build-H-RollerDuck-Skate"
    ]
    for d in local_dirs:
        readme_file = os.path.join(d, "README.md")
        if os.path.exists(readme_file):
            print(f"Syncing local file: {readme_file}")
            with open(readme_file, "r", encoding="utf-8") as f:
                cur = f.read()
            upd = update_readme_text(cur, os.path.basename(d))
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(upd)
            print("  -> Local file synced!")

if __name__ == "__main__":
    main()

