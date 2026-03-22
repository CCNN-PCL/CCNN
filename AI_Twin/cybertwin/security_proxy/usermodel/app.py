# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn
import os

# Import the existing trust evaluation classes and functions
from trust_eval import ZeroTrustModel, UserTrust, UserTrustEval, user_trust_eval, trust_eval

# Configure logging
logging.basicConfig(
    filename='./TrustEval.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

# FastAPI app instance
app = FastAPI(
    title="Trust Evaluation API",
    description="A FastAPI web application for user trust evaluation using machine learning models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class TrustEvaluationRequest(BaseModel):
    subject_type: str
    common_device: bool
    time: int
    location: str
    bio: float
    pswd: int
    access_network_score: float
    network_risk: float

class TrustEvaluationResponse(BaseModel):
    trust_score: float
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Global configuration
user_trust_model_config = {
    'model_path': './UserTrustEval.pth',
    'input_size': 7,
    'output_size': 1,
    'active_time_table_path': './Tables/time_active.json',
    'active_location_table_path': './Tables/location_time_active.json'
}

# Check if required files exist
def check_required_files():
    """Check if all required model and data files exist"""
    required_files = [
        user_trust_model_config['model_path'],
        user_trust_model_config['active_time_table_path'],
        user_trust_model_config['active_location_table_path']
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logging.error(f"Missing required files: {missing_files}")
        return False
    return True

# Check files on startup
if not check_required_files():
    logging.warning("Some required files are missing. The application may not work correctly.")

# Global model instance for caching
model_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    global model_instance
    try:
        if check_required_files():
            # Pre-load the model to avoid loading delays during requests
            model_instance = UserTrustEval(user_trust_model_config)
            logging.info("Model loaded successfully on startup")
        else:
            logging.error("Cannot load model due to missing files")
    except Exception as e:
        logging.error(f"Error loading model on startup: {str(e)}")

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse('static/index.html')

@app.get("/api", response_model=HealthResponse)
async def api_root():
    """API root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        message="Trust Evaluation API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is operational"
    )

@app.post("/evaluate", response_model=TrustEvaluationResponse)
async def evaluate_trust(request: TrustEvaluationRequest):
    """
    Evaluate user trust score based on provided attributes
    
    Args:
        request: TrustEvaluationRequest containing user attributes
        
    Returns:
        TrustEvaluationResponse with trust score and status
    """
    try:
        # Validate subject type
        if request.subject_type not in ['user', 'app']:
            raise HTTPException(
                status_code=400,
                detail="Invalid subject_type. Must be 'user' or 'app'"
            )
        
        # Convert request to the format expected by the original function
        input_data = {
            'subject_type': request.subject_type,
            'common_device': request.common_device,
            'time': request.time,
            'location': request.location,
            'bio': request.bio,
            'pswd': request.pswd,
            'access_network_score': request.access_network_score,
            'network_risk': request.network_risk,
        }
        
        # Evaluate trust score
        if request.subject_type == 'user':
            if model_instance is None:
                raise HTTPException(
                    status_code=503,
                    detail="Model not loaded. Please check if all required files are present."
                )
            trust_score = trust_eval(input_data)
        else:
            # For app type, return a placeholder or implement app-specific logic
            trust_score = 0.5  # Placeholder for app evaluation
        
        return TrustEvaluationResponse(
            trust_score=trust_score,
            status="success",
            message=f"Trust evaluation completed for {request.subject_type}"
        )
        
    except Exception as e:
        logging.error(f"Error in trust evaluation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating trust: {str(e)}"
        )

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded model"""
    try:
        return {
            "model_path": user_trust_model_config['model_path'],
            "input_size": user_trust_model_config['input_size'],
            "output_size": user_trust_model_config['output_size'],
            "status": "loaded"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting model info: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
