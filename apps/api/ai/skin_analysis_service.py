#!/usr/bin/env python3
"""
Skin Analysis Service
Handles PyTorch model integration and face detection for skin analysis
"""
import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)


class SkinAnalysisService:
    """Service for skin analysis using PyTorch models and computer vision"""

    def __init__(self, model_path: str = "models/skin_classifier.pth"):
        self.model_path = model_path
        self.model = None
        self.face_cascade = None
        self.skin_conditions = [
            "acne",
            "blackheads",
            "whiteheads",
            "dark_spots",
            "hyperpigmentation",
            "wrinkles",
            "dry_skin",
            "oily_skin",
            "sensitive_skin",
            "normal_skin",
            "rosacea",
            "eczema",
            "large_pores",
            "uneven_texture",
            "dull_skin",
        ]
        self.skin_types = ["dry", "oily", "combination", "normal", "sensitive"]
        self._load_model()
        self._load_face_cascade()

    def _load_model(self):
        """Load the PyTorch skin classification model"""
        try:
            if Path(self.model_path).exists():
                self.model = torch.load(self.model_path, map_location="cpu")
                self.model.eval()
                logger.info("Skin classification model loaded successfully")
            else:
                logger.warning(
                    f"Model file not found at {self.model_path}. Using mock predictions."
                )
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None

    def _load_face_cascade(self):
        """Load OpenCV Haar cascade for face detection"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            logger.info("Face cascade loaded successfully")
        except Exception as e:
            logger.error(f"Error loading face cascade: {e}")
            self.face_cascade = None

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in the image using OpenCV"""
        try:
            if self.face_cascade is None:
                return []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            face_data = []
            for i, (x, y, w, h) in enumerate(faces):
                face_data.append(
                    {
                        "face_id": i,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "confidence": 0.9,  # OpenCV doesn't provide confidence
                        "area": w * h,
                    }
                )

            return face_data

        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []

    def preprocess_image(
        self, image: np.ndarray, target_size: Tuple[int, int] = (224, 224)
    ) -> np.ndarray:
        """Preprocess image for model input"""
        try:
            # Resize image
            resized = cv2.resize(image, target_size)

            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

            # Normalize to [0, 1]
            normalized = rgb.astype(np.float32) / 255.0

            # Convert to tensor format (C, H, W)
            tensor = np.transpose(normalized, (2, 0, 1))

            return tensor

        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None

    def analyze_skin_conditions(self, image: np.ndarray, face_bbox: List[int]) -> Dict[str, Any]:
        """Analyze skin conditions for a specific face region"""
        try:
            x, y, w, h = face_bbox

            # Extract face region
            face_region = image[y : y + h, x : x + w]

            if face_region.size == 0:
                return {"error": "Invalid face region"}

            # Preprocess for model
            processed = self.preprocess_image(face_region)
            if processed is None:
                return {"error": "Failed to preprocess image"}

            if self.model is not None:
                # Use actual model prediction
                with torch.no_grad():
                    input_tensor = torch.FloatTensor(processed).unsqueeze(0)
                    predictions = self.model(input_tensor)
                    probabilities = torch.softmax(predictions, dim=1)

                # Get top predictions
                top_probs, top_indices = torch.topk(probabilities, 5)

                conditions = []
                for i in range(len(top_indices[0])):
                    idx = top_indices[0][i].item()
                    prob = top_probs[0][i].item()

                    if prob > 0.3:  # Threshold for relevance
                        condition = (
                            self.skin_conditions[idx]
                            if idx < len(self.skin_conditions)
                            else f"condition_{idx}"
                        )
                        conditions.append(
                            {
                                "condition": condition,
                                "confidence": float(prob),
                                "severity": self._get_severity(prob),
                            }
                        )
            else:
                # Mock predictions for development
                conditions = self._get_mock_predictions(face_region)

            return {
                "conditions": conditions,
                "skin_type": self._predict_skin_type(face_region),
                "health_score": self._calculate_health_score(conditions),
            }

        except Exception as e:
            logger.error(f"Error analyzing skin conditions: {e}")
            return {"error": str(e)}

    def _get_mock_predictions(self, face_region: np.ndarray) -> List[Dict[str, Any]]:
        """Generate mock predictions for development/testing"""
        # Simple heuristic-based mock predictions
        conditions = []

        # Analyze image properties for mock predictions
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)

        # Check for oiliness (brightness)
        brightness = np.mean(gray)
        if brightness > 120:
            conditions.append({"condition": "oily_skin", "confidence": 0.7, "severity": "moderate"})
        elif brightness < 80:
            conditions.append({"condition": "dry_skin", "confidence": 0.6, "severity": "mild"})

        # Check for texture (variance)
        texture_variance = np.var(gray)
        if texture_variance > 1000:
            conditions.append(
                {"condition": "uneven_texture", "confidence": 0.5, "severity": "mild"}
            )

        # Check for redness (BGR channels)
        b, g, r = cv2.split(face_region)
        redness = np.mean(r) - np.mean(g)
        if redness > 20:
            conditions.append({"condition": "rosacea", "confidence": 0.4, "severity": "mild"})

        # Add some random conditions for variety
        import random

        if random.random() > 0.7:
            conditions.append(
                {
                    "condition": "acne",
                    "confidence": random.uniform(0.3, 0.8),
                    "severity": random.choice(["mild", "moderate"]),
                }
            )

        return conditions[:3]  # Limit to 3 conditions

    def _predict_skin_type(self, face_region: np.ndarray) -> Dict[str, Any]:
        """Predict skin type based on image analysis"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            texture_variance = np.var(gray)

            # Simple heuristic for skin type
            if brightness > 120:
                skin_type = "oily"
                confidence = 0.7
            elif brightness < 80:
                skin_type = "dry"
                confidence = 0.6
            elif texture_variance > 1000:
                skin_type = "combination"
                confidence = 0.5
            else:
                skin_type = "normal"
                confidence = 0.8

            return {
                "primary": skin_type,
                "confidence": confidence,
                "health_score": min(100, max(0, 100 - (brightness - 100) * 0.5)),
            }

        except Exception as e:
            logger.error(f"Error predicting skin type: {e}")
            return {"primary": "normal", "confidence": 0.5, "health_score": 50}

    def _get_severity(self, confidence: float) -> str:
        """Convert confidence score to severity level"""
        if confidence > 0.8:
            return "severe"
        elif confidence > 0.6:
            return "moderate"
        elif confidence > 0.4:
            return "mild"
        else:
            return "minimal"

    def _calculate_health_score(self, conditions: List[Dict[str, Any]]) -> int:
        """Calculate overall skin health score"""
        if not conditions:
            return 85  # Good baseline if no issues detected

        # Start with base score
        score = 100

        # Deduct points based on conditions and severity
        for condition in conditions:
            confidence = condition.get("confidence", 0)
            severity = condition.get("severity", "mild")

            # Severity multipliers
            severity_multipliers = {"minimal": 0.1, "mild": 0.3, "moderate": 0.5, "severe": 0.8}

            deduction = confidence * severity_multipliers.get(severity, 0.3) * 20
            score -= deduction

        return max(0, min(100, int(score)))

    def analyze_skin_image(
        self, image_data: bytes, user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Main method to analyze skin from image data"""
        try:
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)

            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            # Detect faces
            faces = self.detect_faces(image_array)

            if not faces:
                return {
                    "success": False,
                    "error": "No faces detected in the image",
                    "faces_detected": 0,
                }

            # Analyze each face
            analysis_results = []
            all_conditions = set()

            for face in faces:
                face_analysis = self.analyze_skin_conditions(image_array, face["bbox"])

                if "error" not in face_analysis:
                    analysis_results.append(
                        {
                            "face_id": face["face_id"],
                            "bbox": face["bbox"],
                            "conditions": face_analysis["conditions"],
                            "skin_type": face_analysis["skin_type"],
                            "health_score": face_analysis["health_score"],
                        }
                    )

                    # Collect all conditions
                    for condition in face_analysis["conditions"]:
                        all_conditions.add(condition["condition"])

            # Calculate overall health score
            if analysis_results:
                overall_health = sum(result["health_score"] for result in analysis_results) / len(
                    analysis_results
                )
            else:
                overall_health = 50

            return {
                "success": True,
                "analysis_results": analysis_results,
                "detected_conditions": list(all_conditions),
                "faces_detected": len(faces),
                "overall_health_score": int(overall_health),
                "model_used": "pytorch-skin-classifier" if self.model else "mock-heuristic",
                "analysis_timestamp": "2024-01-15T10:30:00Z",
            }

        except Exception as e:
            logger.error(f"Error analyzing skin image: {e}")
            return {"success": False, "error": str(e), "faces_detected": 0}


# Create global instance
skin_analysis_service = SkinAnalysisService()
