# Hugging Face Spaces Deployment Guide

This project is prepared for a Hugging Face Docker Space. The Docker image builds the React frontend, copies the compiled `frontend/dist` into the Python runtime image, and serves both the FastAPI API and frontend from one process on port `7860`.

## Required Files

Keep these files in the repository you push to GitHub or Hugging Face:

- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- `README.md`
- `model.joblib`
- `model_metadata.json`
- `predict.py`
- `features.py`
- `backend/`
- `frontend/`
- `APPROACH.md`
- `DATASET_SOURCES.md`

Do not upload datasets, `node_modules`, virtual environments, local manual tests, submission zips, or `.env` files.

## Local Docker Test

```bash
docker build -t salescode-recapture-detector .
docker run --rm -p 7860:7860 salescode-recapture-detector
```

Then open:

```text
http://127.0.0.1:7860/health
http://127.0.0.1:7860/
```

Expected health response includes `"status": "ok"` and `"model_loaded": true`.

## GitHub Push Steps

For a new GitHub repository:

```bash
git init
git status
git add .
git status
git commit -m "Initial commit: SalesCode recapture detector"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

For an existing GitHub repository:

```bash
git status
git add .
git commit -m "Prepare SalesCode recapture detector for GitHub and Hugging Face"
git push
```

## Hugging Face Space Setup

1. Create a new Space at [Hugging Face Spaces](https://huggingface.co/spaces).
2. Choose the Docker SDK.
3. Use port `7860`; the README frontmatter sets `app_port: 7860`.
4. Push the repository files to the Space repo.
5. Wait for the Docker build to finish.
6. Open the app and test one real sample and one screen sample.
7. Test the health route at `https://huggingface.co/spaces/<USER>/<SPACE>/health` or from the running Space URL.

## Logs

Use the Space "Logs" panel to inspect build and runtime output. Useful things to check:

- `npm install` and `npm run build` complete in the frontend stage.
- `pip install -r requirements.txt` completes in the Python stage.
- Uvicorn starts on `0.0.0.0:7860`.
- `GET /health` returns status `ok`.

## Common Build Errors

- **Docker context too large:** confirm `.dockerignore` excludes `dataset`, `manual_test`, `submission`, `node_modules`, zips, caches, and virtual environments.
- **OpenCV import error:** keep `opencv-python-headless` in `requirements.txt`.
- **Port error:** confirm `EXPOSE 7860`, the Uvicorn command uses `--port 7860`, and README frontmatter has `app_port: 7860`.
- **Frontend missing:** confirm Docker built `frontend/dist` and copied it into `/app/frontend/dist`.
- **API 404 from UI:** frontend production calls should use relative `/api/...` paths.

## Notes

- Do not retrain or change the model threshold for deployment.
- Do not include the full ICL dataset or phone photo dataset in GitHub or Hugging Face.
- `python predict.py image.jpg` must continue to print only one float in normal mode.
