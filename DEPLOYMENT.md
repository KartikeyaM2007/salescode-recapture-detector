# Hugging Face Spaces Deployment Guide

This project is fully configured to be deployed as a Docker Space on Hugging Face. The configuration uses a multi-stage Dockerfile that builds the React frontend and serves it via the FastAPI backend, all on port 7860.

## Deployment Steps

1. **Create a New Space on Hugging Face:**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click "Create new Space".
   - **Name**: `SalesCode-Recapture-Detector` (or your choice).
   - **License**: Choose your preferred license.
   - **Select the Space SDK**: Choose **Docker**.
   - **Space Hardware**: Free tier (CPU basic) is sufficient for this lightweight model.
   - **Visibility**: Public or Private.

2. **Push Repository Files:**
   Clone your new Space repository and copy the required files from this project into it, or use the Hugging Face web UI to upload files.
   
   **Required Files:**
   - `Dockerfile`
   - `.dockerignore`
   - `requirements.txt`
   - `README.md` (MUST include the YAML frontmatter at the top)
   - `model.joblib`
   - `model_metadata.json`
   - `predict.py`
   - `features.py`
   - `backend/` directory
   - `frontend/` directory (The Dockerfile will build the frontend automatically)

   > **DO NOT UPLOAD:**
   > - The 8GB ICL dataset (`dataset/` folder)
   > - `node_modules/` or `venv/`
   > - Large `.zip` files

3. **Verify Configuration:**
   Ensure your `README.md` starts with:
   ```yaml
   ---
   title: SalesCode Recapture Detector
   emoji: 🛡️
   colorFrom: green
   colorTo: gray
   sdk: docker
   app_port: 7860
   ---
   ```

4. **Wait for Build:**
   Hugging Face will automatically detect the `Dockerfile` and begin building. You can click on the "Logs" button to watch the `npm install`, `npm run build`, and `pip install` steps.

5. **Test Your Space:**
   Once the status turns to "Running", the UI should appear in the Space frame.
   - Test by dragging a real photo and a screen photo to ensure the backend integration is successful.
   - You can also hit the health endpoint directly via your Space URL (e.g., `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/api/health`).

## Troubleshooting

- **Build Times Out or Fails on OOM:** Ensure you pushed `.dockerignore` so that massive datasets/caches aren't being sent to the Docker context.
- **Port Error:** Ensure `app_port: 7860` is in the `README.md` and `EXPOSE 7860` is in the `Dockerfile`.
- **OpenCV Errors:** We strictly use `opencv-python-headless` in `requirements.txt`. If you switch to `opencv-python`, the Docker slim image will fail missing `libGL.so.1`.
