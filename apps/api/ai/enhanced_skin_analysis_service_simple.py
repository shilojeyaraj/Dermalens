"""
Enhanced Skin Analysis Service (Simple Version)
AI-powered skin analysis without OpenCV/numpy dependencies
"""
import asyncio
import logging
import json
import base64
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from PIL import Image, ImageStat, ImageFilter
import sys
import os

# Import services
from ai.vertex_ai_service import vertex_ai_service
from infrastructure.elasticsearch_service import elasticsearch_service
from infrastructure.caching import intelligent_caching_service

# Configuration
try:
    from settings import VERTEX_AI_ENABLED, ENSEMBLE_ENABLED
except ImportError:
    # Fallback values if settings module is not available
    VERTEX_AI_ENABLED = True
    ENSEMBLE_ENABLED = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSkinAnalysisService:
    """
    Enhanced skin analysis service with advanced AI capabilities (Simple Version)
    
    Features:
    - Multi-modal analysis (visual + text)
    - Real-time processing
    - Comprehensive logging
    - Error handling and fallbacks
    - Detailed analysis reports
    - No OpenCV/numpy dependencies
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
        self.min_brightness = 40.0  # 0-255 grayscale
        self.min_edge_density = 4.0  # heuristic for blur
        
        logger.info("🔬 Enhanced Skin Analysis Service (Simple) initialized")
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
        logger.info("🔍 Starting enhanced skin analysis (Simple)")
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
            
            # Step 2: Perform AI analysis (simplified)
            logger.info("🤖 Step 2: Performing AI analysis")
            ai_results = await self._perform_ai_analysis_simple(processed_image, user_profile, analysis_type)
            if not ai_results["success"]:
                logger.error(f"❌ AI analysis failed: {ai_results['error']}")
                return ai_results
            
            analysis_data = ai_results["data"]
            logger.info(f"✅ AI analysis completed")
            logger.info(f"   - Conditions detected: {len(analysis_data.get('detected_conditions', []))}")
            logger.info(f"   - Confidence scores: {[c.get('confidence', 0) for c in analysis_data.get('conditions', [])]}")
            
            # Step 3: Generate comprehensive report
            logger.info("📊 Step 3: Generating comprehensive report")
            report = await self._generate_comprehensive_report(
                analysis_data, 
                user_profile, 
                processed_image
            )
            
            # Step 4: Cache results
            logger.info("💾 Step 4: Caching analysis results")
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
            
            # Calculate quality score (enhanced heuristics)
            quality = await self._calculate_image_quality_simple(image)
            quality_score = quality.get("quality_score", 0.5)
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
            
            # Convert processed image back to bytes for AI analysis
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=95)
            processed_bytes = img_buffer.getvalue()
            
            return {
                "success": True,
                "data": {
                    "image": image,
                    "image_bytes": processed_bytes,
                    "width": image.width,
                    "height": image.height,
                    "quality_score": quality_score,
                    "brightness": quality.get("brightness"),
                    "edge_density": quality.get("edge_density"),
                    "low_light": quality.get("low_light", False),
                    "blurry": quality.get("blurry", False),
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
    
    async def _calculate_image_quality_simple(self, image: Image.Image) -> Dict[str, Any]:
        """Calculate image quality metrics (brightness, blur proxy) without OpenCV"""
        try:
            # Simple quality assessment based on image properties
            width, height = image.size
            
            # Size score (larger is better, up to a point)
            size_score = min(width * height / (1920 * 1080), 1.0)
            
            # Aspect ratio score (closer to square is better for face analysis)
            aspect_ratio = width / height
            aspect_score = 1.0 - abs(aspect_ratio - 1.0) * 0.5
            
            # Brightness (0-255)
            gray = image.convert('L')
            stat = ImageStat.Stat(gray)
            brightness = stat.mean[0]
            brightness_score = min(max((brightness - self.min_brightness) / (255 - self.min_brightness), 0.0), 1.0)
            low_light = brightness < self.min_brightness

            # Edge density as blur proxy
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            edge_density = edge_stat.var[0]  # variance of edge map
            edge_norm = min(edge_density / 20.0, 1.0)  # heuristic normalization
            blurry = edge_density < self.min_edge_density

            # Combined quality score
            quality = (size_score * 0.3 + aspect_score * 0.2 + brightness_score * 0.3 + edge_norm * 0.2)
            
            logger.info(f"   - Size score: {size_score:.2f}")
            logger.info(f"   - Aspect ratio: {aspect_ratio:.2f} (score: {aspect_score:.2f})")
            logger.info(f"   - Brightness: {brightness:.1f} (low_light={low_light})")
            logger.info(f"   - Edge density: {edge_density:.2f} (blurry={blurry})")
            
            return {
                "quality_score": float(min(max(quality, 0.0), 1.0)),
                "brightness": float(brightness),
                "edge_density": float(edge_density),
                "low_light": low_light,
                "blurry": blurry
            }
            
        except Exception as e:
            logger.error(f"❌ Quality calculation failed: {str(e)}")
            return {"quality_score": 0.5, "brightness": 128.0, "edge_density": 5.0, "low_light": False, "blurry": False}
    
    async def _perform_ai_analysis_simple(
        self, 
        processed_image: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform AI analysis (simplified version)"""
        try:
            logger.info(f"🤖 Performing {analysis_type} AI analysis (Simple)")
            
            if self.vertex_ai_enabled:
                logger.info("   - Using Vertex AI for analysis")
                return await self._vertex_ai_analysis_simple(processed_image, user_profile, analysis_type)
            else:
                logger.info("   - Using fallback analysis")
                return await self._fallback_analysis_simple(processed_image, user_profile, analysis_type)
                
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
    
    async def _vertex_ai_analysis_simple(
        self, 
        processed_image: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform analysis using Vertex AI (simplified)"""
        try:
            logger.info("🔬 Starting Vertex AI analysis (Simple)")
            
            # Prepare analysis data
            analysis_data = {
                "image": processed_image,
                "user_profile": user_profile,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call Vertex AI service with image bytes
            image_bytes = processed_image.get("image_bytes")
            if not image_bytes:
                raise ValueError("No image bytes available for analysis")
            
            logger.info(f"🔬 Calling Vertex AI with {len(image_bytes)} bytes")
            result = await self.vertex_ai.analyze_skin_comprehensive(image_bytes, user_profile)
            
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
    
    async def _fallback_analysis_simple(
        self, 
        processed_image: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform fallback analysis when Vertex AI is not available (simplified)"""
        try:
            logger.info("🔄 Performing fallback analysis (Simple)")
            
            # Mock analysis results
            detected_conditions = []
            conditions = []
            
            # Simulate condition detection based on image quality
            quality_score = processed_image.get("quality_score", 0.5)
            
            # Generate conditions based on quality and random factors
            if quality_score > 0.7:
                conditions.extend([
                    {
                        "condition": "acne",
                        "confidence": 0.75,
                        "severity": "moderate",
                        "location": "forehead",
                        "coordinates": {"x": 0.3, "y": 0.2, "radius": 0.05}
                    },
                    {
                        "condition": "dry_skin",
                        "confidence": 0.65,
                        "severity": "mild",
                        "location": "cheeks",
                        "coordinates": {"x": 0.2, "y": 0.4, "radius": 0.08}
                    }
                ])
            elif quality_score > 0.5:
                conditions.extend([
                    {
                        "condition": "dark_circles",
                        "confidence": 0.60,
                        "severity": "mild",
                        "location": "under_eyes",
                        "coordinates": {"x": 0.5, "y": 0.3, "radius": 0.06}
                    }
                ])
            else:
                conditions.extend([
                    {
                        "condition": "poor_lighting",
                        "confidence": 0.80,
                        "severity": "moderate",
                        "location": "overall",
                        "coordinates": {"x": 0.5, "y": 0.5, "radius": 0.1}
                    }
                ])
            
            detected_conditions = list(set([c["condition"] for c in conditions]))
            
            logger.info(f"✅ Fallback analysis completed")
            logger.info(f"   - Conditions: {detected_conditions}")
            logger.info(f"   - Total conditions: {len(conditions)}")
            
            return {
                "success": True,
                "data": {
                    "detected_conditions": detected_conditions,
                    "conditions": conditions,
                    "faces_analyzed": 1,  # Assume single face
                    "overall_confidence": 0.7,
                    "analysis_method": "fallback_simple",
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
        processed_image: Dict[str, Any]
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
                "faces_detected": 1,  # Simplified
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
                elif condition == "dark_circles":
                    recommendations.append({
                        "type": "product",
                        "category": "eye_cream",
                        "name": "Caffeine Eye Cream",
                        "brand": "The Ordinary",
                        "reason": "Reduce puffiness and dark circles",
                        "confidence": 0.85
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
