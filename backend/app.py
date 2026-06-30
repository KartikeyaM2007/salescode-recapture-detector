import os
import sys
import json
import joblib
import cv2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import tempfile

# Add parent dir to path so we can import predict / features
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from predict import fallback_heuristic
from features import extract_features

app = FastAPI(title="SalesCode Spot the Fake Photo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Failed to load model: {e}")

def get_health_payload():
    meta = {}
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

    phone_metrics = {}
    reports_path = os.path.join(BASE_DIR, "reports", "phone_metrics.json")
    if os.path.exists(reports_path):
        with open(reports_path, "r", encoding="utf-8") as f:
            phone_metrics = json.load(f)

    return {
        "status": "ok",
        "model_loaded": model is not None,
        "mode": "sample-trained" if model is not None else "heuristic fallback",
        "metadata": meta,
        "phone_metrics": phone_metrics
    }

@app.get("/health")
def root_health_check():
    return get_health_payload()

@app.get("/api/health")
def health_check():
    return get_health_payload()

def get_risk_level(score: float, threshold: float):
    if score >= threshold: return "likely recaptured/screen"
    if score >= 0.35: return "borderline / needs review"
    return "likely real"

@app.post("/api/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    logs = []
    def log_cb(msg):
        logs.append(msg)

    # Save to temp file
    temp_path = ""
    try:
        log_cb("Loading image...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            temp_path = tmp.name

        img = cv2.imread(temp_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image.")

        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from predict import run_prediction

        result = run_prediction(img, log_cb)

        feature_groups = {
            "Frequency & Texture": {
                "FFT HF Ratio": result["features"].get("fft_hf_ratio", 0),
                "Moiré Score": result["features"].get("moire_score", 0),
                "Banding": result["features"].get("banding_score", 0)
            },
            "Edge & Blur": {
                "Edge Density": result["features"].get("edge_density", 0),
                "Laplacian Sharpness": result["features"].get("laplacian_var", 0),
                "Sobel Mag": result["features"].get("sobel_mean", 0)
            },
            "Color & Lighting": {
                "Brightness": result["features"].get("brightness", 0),
                "Contrast": result["features"].get("contrast", 0),
                "Glare Ratio": result["features"].get("glare_ratio", 0)
            },
            "Screen & Print Cues": {
                "Bezel Score": result["features"].get("bezel_score", 0),
                "Paper Texture": result["features"].get("paper_texture", 0),
                "Perspective": result["features"].get("perspective_score", 0)
            },
            "Compression": {
                "Blockiness": result["features"].get("blockiness", 0),
                "Compression Diff": result["features"].get("compression_diff", 0)
            }
        }

        return {
            "score": result["final_score"],
            "raw_model_score": result.get("raw_model_score", 0),
            "rule_boost_total": result.get("rule_boost_total", 0),
            "individual_rule_boosts": result.get("individual_rule_boosts", {}),
            "threshold": result.get("threshold", 0.15),
            "model_type": result.get("model_type", "Unknown"),
            "label": "screen" if result["final_score"] >= result.get("threshold", 0.15) else "real",
            "risk_level": get_risk_level(result["final_score"], result.get("threshold", 0.15)),
            "feature_summary": result["features"],
            "feature_groups": feature_groups,
            "analysis_logs": logs,
            "model_status": result["model_status"],
            "model_type": result["model_type"],
            "threshold": result["threshold"]
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found.")

        requested_path = os.path.abspath(os.path.join(FRONTEND_DIST, full_path))
        dist_root = os.path.abspath(FRONTEND_DIST)
        if requested_path.startswith(dist_root) and os.path.isfile(requested_path):
            return FileResponse(requested_path)

        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
