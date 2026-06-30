import os
import sys

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    print("--- Starting Deployment Package Check ---")
    errors = []

    # 1. Required files
    required_files = [
        "Dockerfile",
        ".dockerignore",
        "requirements.txt",
        "README.md",
        "model.joblib",
        "model_metadata.json",
        "predict.py",
        "features.py",
        "backend/app.py",
        "frontend/package.json"
    ]

    for f in required_files:
        if not os.path.exists(f):
            errors.append(f"Missing required file/folder: {f}")

    # 2. Check README.md for Hugging Face Frontmatter
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            if "sdk: docker" not in content or "app_port: 7860" not in content:
                errors.append("README.md is missing 'sdk: docker' or 'app_port: 7860' YAML frontmatter.")

    # 3. Check Dockerfile
    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r", encoding="utf-8") as f:
            content = f.read()
            if "EXPOSE 7860" not in content:
                errors.append("Dockerfile does not contain 'EXPOSE 7860'.")
            if "7860" not in content:
                errors.append("Dockerfile does not seem to bind uvicorn to port 7860.")

    # 4. Check requirements.txt
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            if "opencv-python-headless" not in content:
                errors.append("requirements.txt must use 'opencv-python-headless' instead of 'opencv-python'.")

    # 5. Check for forbidden large files (we won't fail strictly on zip if it's outside the build context, but good to warn)
    forbidden_dirs = [
        "dataset/Data",
        "node_modules",
        "venv",
        ".venv"
    ]
    for d in forbidden_dirs:
        if os.path.exists(d) and os.path.isdir(d):
            print(f"[WARNING] Large directory exists locally: {d} (Ensure it is in .dockerignore!)")

    if os.path.exists(".dockerignore"):
        with open(".dockerignore", "r", encoding="utf-8") as f:
            content = f.read()
            if "dataset" not in content:
                errors.append(".dockerignore must ignore 'dataset' folder.")
            if "node_modules" not in content:
                errors.append(".dockerignore must ignore 'node_modules' folder.")

    if errors:
        print("\n[FAIL] Deployment check failed with the following errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n[PASS] Deployment package checks passed! Ready for Hugging Face Spaces.")

if __name__ == "__main__":
    main()
