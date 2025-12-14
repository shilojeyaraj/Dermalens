"""
Enhanced Skin Analysis Service
Advanced AI-powered skin analysis with comprehensive logging and error handling
"""
import asyncio
import logging
import json
import base64
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from PIL import Image
import cv2
import sys
import os

# Import services
from ai.vertex_ai_service import vertex_ai_service
from infrastructure.elasticsearch_service import elasticsearch_service
from infrastructure.caching import intelligent_caching_service

# Configuration
try:
    from config import VERTEX_AI_ENABLED, ENSEMBLE_ENABLED
except ImportError:
    # Fallback values if settings module is not available
    VERTEX_AI_ENABLED = True
    ENSEMBLE_ENABLED = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSkinAnalysisService:
    """
    Enhanced skin analysis service with advanced AI capabilities
    
    Features:
    - Multi-modal analysis (visual + text)
    - Real-time processing
    - Comprehensive logging
    - Error handling and fallbacks
    - Detailed analysis reports
    """
    
    def __init__(self):
        """Initialize the enhanced skin analysis service"""
        self.vertex_ai = vertex_ai_service
        self.elasticsearch = elasticsearch_service
        self.caching = intelligent_caching_service
        
        # Service capabilities
        self.vertex_ai_enabled = VERTEX_AI_ENABLED
        self.ensemble_enabled = ENSEMBLE_ENABLED
        
        # Analysis parameters
        self.confidence_threshold = 0.3
        self.max_faces = 5
        self.image_quality_threshold = 0.7
        
        logger.info("🔬 Enhanced Skin Analysis Service initialized")
        logger.info(f"   - Vertex AI: {'✅' if self.vertex_ai_enabled else '❌'}")
        logger.info(f"   - Ensemble: {'✅' if self.ensemble_enabled else '❌'}")
        logger.info(f"   - Confidence threshold: {self.confidence_threshold}")
        logger.info(f"   - Max faces: {self.max_faces}")
    
    async def analyze_skin_image(
        self,
        image_data: bytes,
        user_profile: Optional[Dict[str, Any]] = None,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze skin image with enhanced AI capabilities
        
        Args:
            image_data: Raw image bytes
            user_profile: User's skin profile (optional)
            analysis_type: Type of analysis (comprehensive, quick, detailed)
            
        Returns:
            Complete analysis results with detailed logging
        """
        logger.info("🔍 Starting enhanced skin analysis")
        logger.info(f"   - Analysis type: {analysis_type}")
        logger.info(f"   - Image size: {len(image_data)} bytes")
        logger.info(f"   - User profile: {'✅' if user_profile else '❌'}")
        
        try:
            # Step 1: Validate and preprocess image
            logger.info("📸 Step 1: Validating and preprocessing image")
            image_validation = await self._validate_and_preprocess_image(image_data)
            if not image_validation["success"]:
                logger.error(f"❌ Image validation failed: {image_validation['error']}")
                return image_validation
            
            processed_image = image_validation["data"]
            logger.info(f"✅ Image processed successfully")
            logger.info(f"   - Dimensions: {processed_image['width']}x{processed_image['height']}")
            logger.info(f"   - Quality score: {processed_image['quality_score']:.2f}")
            
            # Step 2: Detect faces and extract regions
            logger.info("👤 Step 2: Detecting faces and extracting regions")
            face_analysis = await self._detect_and_extract_faces(processed_image)
            if not face_analysis["success"]:
                logger.error(f"❌ Face detection failed: {face_analysis['error']}")
                return face_analysis
            
            faces = face_analysis["data"]
            logger.info(f"✅ Face detection completed")
            logger.info(f"   - Faces detected: {len(faces)}")
            logger.info(f"   - Face regions: {[f['region'] for f in faces]}")
            
            # Step 3: Perform AI analysis
            logger.info("🤖 Step 3: Performing AI analysis")
            ai_results = await self._perform_ai_analysis(faces, user_profile, analysis_type)
            if not ai_results["success"]:
                logger.error(f"❌ AI analysis failed: {ai_results['error']}")
                return ai_results
            
            analysis_data = ai_results["data"]
            logger.info(f"✅ AI analysis completed")
            logger.info(f"   - Conditions detected: {len(analysis_data.get('detected_conditions', []))}")
            logger.info(f"   - Confidence scores: {[c.get('confidence', 0) for c in analysis_data.get('conditions', [])]}")
            
            # Step 4: Generate comprehensive report
            logger.info("📊 Step 4: Generating comprehensive report")
            report = await self._generate_comprehensive_report(
                analysis_data, 
                user_profile, 
                processed_image,
                faces
            )
            
            # Step 5: Cache results
            logger.info("💾 Step 5: Caching analysis results")
            await self._cache_analysis_results(report)
            
            logger.info("🎉 Enhanced skin analysis completed successfully")
            return {
                "success": True,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "processing_time": report.get("processing_time", 0),
                "data": report
            }
            
        except Exception as e:
            logger.error(f"💥 Enhanced skin analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_and_preprocess_image(self, image_data: bytes) -> Dict[str, Any]:
        """Validate and preprocess the input image"""
        try:
            logger.info("🔍 Validating image format and quality")
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"   - Original format: {image.format}")
            logger.info(f"   - Original size: {image.size}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                logger.info("   - Converted to RGB")
            
            # Calculate quality score
            quality_score = await self._calculate_image_quality(image)
            logger.info(f"   - Quality score: {quality_score:.2f}")
            
            if quality_score < self.image_quality_threshold:
                logger.warning(f"⚠️ Low image quality: {quality_score:.2f} < {self.image_quality_threshold}")
            
            # Resize if too large
            max_size = 2048
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"   - Resized to: {new_size}")
            
            return {
                "success": True,
                "data": {
                    "image": image,
                    "width": image.width,
                    "height": image.height,
                    "quality_score": quality_score,
                    "format": image.format,
                    "mode": image.mode
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Image validation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Image validation failed: {str(e)}"
            }
    
    async def _calculate_image_quality(self, image: Image.Image) -> float:
        """Calculate image quality score"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate sharpness (Laplacian variance)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = np.std(gray)
            
            # Normalize scores (0-1)
            sharpness_score = min(sharpness / 1000, 1.0)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            contrast_score = min(contrast / 100, 1.0)
            
            # Weighted quality score
            quality = (sharpness_score * 0.5 + brightness_score * 0.3 + contrast_score * 0.2)
            
            logger.info(f"   - Sharpness: {sharpness:.2f} (score: {sharpness_score:.2f})")
            logger.info(f"   - Brightness: {brightness:.2f} (score: {brightness_score:.2f})")
            logger.info(f"   - Contrast: {contrast:.2f} (score: {contrast_score:.2f})")
            
            return quality
            
        except Exception as e:
            logger.error(f"❌ Quality calculation failed: {str(e)}")
            return 0.5  # Default medium quality
    
    async def _detect_and_extract_faces(self, processed_image: Dict[str, Any]) -> Dict[str, Any]:
        """Detect faces and extract regions for analysis"""
        try:
            logger.info("👤 Detecting faces in image")
            
            image = processed_image["image"]
            
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            logger.info(f"   - Raw face detections: {len(faces)}")
            
            if len(faces) == 0:
                logger.warning("⚠️ No faces detected in image")
                return {
                    "success": False,
                    "error": "No faces detected in image. Please ensure the image contains a clear view of a face."
                }
            
            # Process and filter faces
            processed_faces = []
            for i, (x, y, w, h) in enumerate(faces[:self.max_faces]):
                # Add padding
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img_cv.shape[1], x + w + padding)
                y2 = min(img_cv.shape[0], y + h + padding)
                
                # Extract face region
                face_region = img_cv[y1:y2, x1:x2]
                
                # Calculate face quality
                face_quality = self._calculate_face_quality(face_region)
                
                if face_quality > 0.3:  # Minimum face quality threshold
                    processed_faces.append({
                        "face_id": i,
                        "region": (x1, y1, x2, y2),
                        "size": (w, h),
                        "quality": face_quality,
                        "image": face_region
                    })
                    logger.info(f"   - Face {i}: quality {face_quality:.2f}, size {w}x{h}")
                else:
                    logger.warning(f"   - Face {i}: quality too low ({face_quality:.2f}), skipping")
            
            if not processed_faces:
                logger.error("❌ No high-quality faces found")
                return {
                    "success": False,
                    "error": "No high-quality faces found. Please ensure the image has clear, well-lit faces."
                }
            
            logger.info(f"✅ Face detection completed: {len(processed_faces)} faces")
            return {
                "success": True,
                "data": processed_faces
            }
            
        except Exception as e:
            logger.error(f"❌ Face detection failed: {str(e)}")
            return {
                "success": False,
                "error": f"Face detection failed: {str(e)}"
            }
    
    def _calculate_face_quality(self, face_region: np.ndarray) -> float:
        """Calculate quality score for a face region"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = np.std(gray)
            
            # Normalize scores
            sharpness_score = min(sharpness / 1000, 1.0)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            contrast_score = min(contrast / 100, 1.0)
            
            # Weighted quality score
            quality = (sharpness_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
            
            return quality
            
        except Exception as e:
            logger.error(f"❌ Face quality calculation failed: {str(e)}")
            return 0.0
    
    async def _perform_ai_analysis(
        self, 
        faces: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform AI analysis on detected faces"""
        try:
            logger.info(f"🤖 Performing {analysis_type} AI analysis")
            
            if self.vertex_ai_enabled:
                logger.info("   - Using Vertex AI for analysis")
                return await self._vertex_ai_analysis(faces, user_profile, analysis_type)
            else:
                logger.info("   - Using fallback analysis")
                return await self._fallback_analysis(faces, user_profile, analysis_type)
                
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
    
    async def _vertex_ai_analysis(
        self, 
        faces: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform analysis using Vertex AI"""
        try:
            logger.info("🔬 Starting Vertex AI analysis")
            
            # Prepare analysis data
            analysis_data = {
                "faces": faces,
                "user_profile": user_profile,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call Vertex AI service
            result = await self.vertex_ai.analyze_skin_comprehensive(analysis_data)
            
            if result["success"]:
                logger.info("✅ Vertex AI analysis completed")
                logger.info(f"   - Conditions: {len(result.get('detected_conditions', []))}")
                logger.info(f"   - Confidence: {result.get('overall_confidence', 0):.2f}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Vertex AI analysis failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Vertex AI analysis error: {str(e)}")
            return {
                "success": False,
                "error": f"Vertex AI analysis failed: {str(e)}"
            }
    
    async def _fallback_analysis(
        self, 
        faces: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform fallback analysis when Vertex AI is not available"""
        try:
            logger.info("🔄 Performing fallback analysis")
            
            # Mock analysis results
            detected_conditions = []
            conditions = []
            
            for i, face in enumerate(faces):
                # Simulate condition detection
                face_conditions = [
                    {
                        "condition": "acne",
                        "confidence": 0.75 + (i * 0.05),
                        "severity": "moderate",
                        "location": "forehead"
                    },
                    {
                        "condition": "dry_skin",
                        "confidence": 0.65 + (i * 0.03),
                        "severity": "mild",
                        "location": "cheeks"
                    }
                ]
                
                conditions.extend(face_conditions)
                detected_conditions.extend([c["condition"] for c in face_conditions])
            
            # Remove duplicates
            detected_conditions = list(set(detected_conditions))
            
            logger.info(f"✅ Fallback analysis completed")
            logger.info(f"   - Conditions: {detected_conditions}")
            logger.info(f"   - Total conditions: {len(conditions)}")
            
            return {
                "success": True,
                "data": {
                    "detected_conditions": detected_conditions,
                    "conditions": conditions,
                    "faces_analyzed": len(faces),
                    "overall_confidence": 0.7,
                    "analysis_method": "fallback",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Fallback analysis failed: {str(e)}"
            }
    
    async def _generate_comprehensive_report(
        self,
        analysis_data: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]],
        processed_image: Dict[str, Any],
        faces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        try:
            logger.info("📊 Generating comprehensive report")
            
            # Calculate skin health score
            skin_health_score = self._calculate_skin_health_score(analysis_data)
            logger.info(f"   - Skin health score: {skin_health_score:.2f}")
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(analysis_data, user_profile)
            logger.info(f"   - Recommendations generated: {len(recommendations)}")
            
            # Create comprehensive report
            report = {
                "analysis_results": analysis_data.get("conditions", []),
                "detected_conditions": analysis_data.get("detected_conditions", []),
                "skin_health_score": skin_health_score,
                "faces_detected": len(faces),
                "image_quality": processed_image.get("quality_score", 0),
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "processing_time": 0,  # Will be calculated
                "user_profile": user_profile,
                "analysis_method": analysis_data.get("analysis_method", "unknown")
            }
            
            logger.info("✅ Comprehensive report generated")
            return report
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            return {
                "analysis_results": [],
                "detected_conditions": [],
                "skin_health_score": 0.0,
                "faces_detected": 0,
                "image_quality": 0.0,
                "recommendations": [],
                "analysis_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _calculate_skin_health_score(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate overall skin health score"""
        try:
            conditions = analysis_data.get("conditions", [])
            if not conditions:
                return 1.0  # No conditions = perfect skin
            
            # Calculate weighted score based on conditions
            total_confidence = 0
            condition_count = 0
            
            for condition in conditions:
                confidence = condition.get("confidence", 0)
                severity = condition.get("severity", "mild")
                
                # Weight by severity
                severity_weights = {"mild": 0.3, "moderate": 0.6, "severe": 0.9}
                weight = severity_weights.get(severity, 0.5)
                
                total_confidence += confidence * weight
                condition_count += 1
            
            if condition_count == 0:
                return 1.0
            
            # Calculate health score (inverse of problem score)
            avg_problem_score = total_confidence / condition_count
            health_score = max(0.0, 1.0 - avg_problem_score)
            
            return round(health_score, 2)
            
        except Exception as e:
            logger.error(f"❌ Health score calculation failed: {str(e)}")
            return 0.5  # Default medium score
    
    async def _generate_recommendations(
        self, 
        analysis_data: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        try:
            logger.info("💡 Generating personalized recommendations")
            
            detected_conditions = analysis_data.get("detected_conditions", [])
            recommendations = []
            
            # Generate recommendations based on conditions
            for condition in detected_conditions:
                if condition == "acne":
                    recommendations.append({
                        "type": "product",
                        "category": "cleanser",
                        "name": "Salicylic Acid Cleanser",
                        "brand": "CeraVe",
                        "reason": "Gentle exfoliation to treat acne",
                        "confidence": 0.8
                    })
                elif condition == "dry_skin":
                    recommendations.append({
                        "type": "product",
                        "category": "moisturizer",
                        "name": "Hyaluronic Acid Moisturizer",
                        "brand": "The Ordinary",
                        "reason": "Deep hydration for dry skin",
                        "confidence": 0.9
                    })
            
            # Add general recommendations
            recommendations.extend([
                {
                    "type": "lifestyle",
                    "category": "routine",
                    "name": "Daily Sunscreen",
                    "reason": "Protect skin from UV damage",
                    "confidence": 1.0
                },
                {
                    "type": "lifestyle",
                    "category": "routine",
                    "name": "Gentle Cleansing",
                    "reason": "Maintain skin barrier health",
                    "confidence": 0.9
                }
            ])
            
            logger.info(f"✅ Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation failed: {str(e)}")
            return []
    
    async def _cache_analysis_results(self, report: Dict[str, Any]) -> None:
        """Cache analysis results for future use"""
        try:
            logger.info("💾 Caching analysis results")
            
            # Create cache key
            cache_key = f"skin_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Cache the results
            await self.caching.set(cache_key, report, ttl=3600)  # 1 hour TTL
            
            logger.info(f"✅ Results cached with key: {cache_key}")
            
        except Exception as e:
            logger.error(f"❌ Caching failed: {str(e)}")


# Create global instance
enhanced_skin_analysis_service = EnhancedSkinAnalysisService()
