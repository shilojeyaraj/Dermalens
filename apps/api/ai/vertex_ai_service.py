"""
Enhanced Vertex AI Service for Dermalens
Implements advanced AI capabilities including streaming, ensemble models, and intelligent caching
"""
import asyncio
import base64
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple
import numpy as np
from PIL import Image
import io

# Google Cloud AI Platform imports
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from google.cloud.aiplatform.gapic.schema import predict, streaming_predict
from google.cloud import storage
from google.cloud import bigquery

# Redis for caching
import redis.asyncio as redis

# Configuration
from config import (
    GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION, VERTEX_AI_ENABLED, 
    VERTEX_AI_ENDPOINT, VERTEX_AI_CACHE_ENABLED, VERTEX_AI_STREAMING_ENABLED,
    ENSEMBLE_ENABLED, MODEL_ENSEMBLE_WEIGHTS, PERFORMANCE_MONITORING_ENABLED,
    METRICS_ENDPOINT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VertexAISkinAnalysisService:
    """
    Enhanced Vertex AI service for comprehensive skin analysis
    
    Features:
    - Multi-model ensemble analysis
    - Real-time streaming analysis
    - Intelligent caching system
    - Performance monitoring
    - Fallback to basic Gemini API
    """
    
    def __init__(self):
        """Initialize the enhanced Vertex AI service"""
        self.project_id = GOOGLE_CLOUD_PROJECT
        self.region = GOOGLE_CLOUD_REGION
        self.enabled = VERTEX_AI_ENABLED
        self.cache_enabled = VERTEX_AI_CACHE_ENABLED
        self.streaming_enabled = VERTEX_AI_STREAMING_ENABLED
        self.ensemble_enabled = ENSEMBLE_ENABLED
        self.monitoring_enabled = PERFORMANCE_MONITORING_ENABLED
        
        # Initialize clients
        self.prediction_client = None
        self.streaming_client = None
        self.cache_client = None
        self.storage_client = None
        self.bigquery_client = None
        self.monitoring_client = None
        
        # Model endpoints
        self.endpoints = {
            "skin_analysis": VERTEX_AI_ENDPOINT,
            "condition_classifier": f"projects/{self.project_id}/locations/{self.region}/endpoints/condition-classifier",
            "severity_analyzer": f"projects/{self.project_id}/locations/{self.region}/endpoints/severity-analyzer",
            "skin_type_detector": f"projects/{self.project_id}/locations/{self.region}/endpoints/skin-type-detector",
            "recommendation_engine": f"projects/{self.project_id}/locations/{self.region}/endpoints/recommendation-engine"
        }
        
        # Ensemble weights
        self.ensemble_weights = MODEL_ENSEMBLE_WEIGHTS
        
        # Initialize services
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all required Google Cloud clients"""
        try:
            if self.enabled:
                # Initialize AI Platform clients
                self.prediction_client = aiplatform.gapic.PredictionServiceClient()
                if self.streaming_enabled:
                    self.streaming_client = aiplatform.gapic.PredictionServiceClient()
                
                # Initialize caching
                if self.cache_enabled:
                    self.cache_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                
                # Initialize storage and BigQuery
                self.storage_client = storage.Client(project=self.project_id)
                self.bigquery_client = bigquery.Client(project=self.project_id)
                
                # Initialize monitoring
                if self.monitoring_enabled:
                    self.monitoring_client = aiplatform.gapic.ModelServiceClient()
                
                logger.info("✅ Vertex AI service initialized successfully")
            else:
                logger.warning("⚠️ Vertex AI is disabled, using fallback services")
                
        except Exception as e:
            logger.error(f"❌ Error initializing Vertex AI service: {e}")
            self.enabled = False
    
    async def analyze_skin_image(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Enhanced skin analysis with multiple AI capabilities
        
        Args:
            image_data: Raw image bytes
            user_profile: User's skin profile and preferences
            analysis_type: Type of analysis (comprehensive, quick, detailed)
            
        Returns:
            Comprehensive analysis results
        """
        start_time = time.time()
        analysis_id = self._generate_analysis_id(image_data, user_profile)
        
        try:
            # Check cache first
            if self.cache_enabled:
                cached_result = await self._get_from_cache(analysis_id)
                if cached_result:
                    logger.info(f"📋 Using cached analysis for {analysis_id}")
                    return cached_result
            
            # Perform analysis based on type
            if analysis_type == "streaming" and self.streaming_enabled:
                result = await self._streaming_analysis(image_data, user_profile)
            elif self.ensemble_enabled:
                result = await self._ensemble_analysis(image_data, user_profile)
            else:
                result = await self._single_model_analysis(image_data, user_profile)
            
            # Add metadata
            result.update({
                "analysis_id": analysis_id,
                "analysis_type": analysis_type,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "model_version": "2.0.0-vertex-ai"
            })
            
            # Cache result
            if self.cache_enabled:
                await self._store_in_cache(analysis_id, result)
            
            # Track performance
            if self.monitoring_enabled:
                await self._track_performance(analysis_id, start_time, time.time(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in skin analysis: {e}")
            # Fallback to basic analysis
            return await self._fallback_analysis(image_data, user_profile)
    
    async def _streaming_analysis(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Real-time streaming analysis for immediate feedback
        
        This is a SINGLE-AGENT approach where one streaming client handles all analysis
        """
        logger.info("🔄 Starting streaming analysis...")
        
        try:
            # Prepare streaming request
            instances = [{
                "image": {"b64": base64.b64encode(image_data).decode()},
                "user_profile": user_profile or {},
                "streaming": True
            }]
            
            # Stream predictions
            streaming_results = []
            async for prediction in self._stream_predictions(instances):
                streaming_results.append(prediction)
                logger.info(f"📊 Streamed result: {prediction.get('condition', 'unknown')}")
            
            # Combine streaming results
            return self._combine_streaming_results(streaming_results)
            
        except Exception as e:
            logger.error(f"❌ Streaming analysis failed: {e}")
            raise
    
    async def _ensemble_analysis(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Multi-model ensemble analysis for maximum accuracy
        
        This is a MULTI-AGENT approach where different models work in parallel
        """
        logger.info("🤖 Starting ensemble analysis...")
        
        try:
            # Prepare base request
            base_request = {
                "image": {"b64": base64.b64encode(image_data).decode()},
                "user_profile": user_profile or {}
            }
            
            # Create tasks for parallel execution
            tasks = []
            
            # Task 1: Condition Classification Agent
            condition_task = self._analyze_with_model(
                "condition_classifier", 
                base_request.copy(),
                "conditions"
            )
            tasks.append(("condition_classifier", condition_task))
            
            # Task 2: Severity Analysis Agent
            severity_task = self._analyze_with_model(
                "severity_analyzer", 
                base_request.copy(),
                "severity"
            )
            tasks.append(("severity_analyzer", severity_task))
            
            # Task 3: Skin Type Detection Agent
            skin_type_task = self._analyze_with_model(
                "skin_type_detector", 
                base_request.copy(),
                "skin_type"
            )
            tasks.append(("skin_type_detector", skin_type_task))
            
            # Execute all tasks in parallel
            logger.info("🚀 Executing ensemble models in parallel...")
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results
            ensemble_results = {}
            for i, (model_name, result) in enumerate(zip([name for name, _ in tasks], results)):
                if isinstance(result, Exception):
                    logger.error(f"❌ Model {model_name} failed: {result}")
                    continue
                
                ensemble_results[model_name] = result
                logger.info(f"✅ {model_name} completed successfully")
            
            # Combine ensemble results with weighted voting
            final_result = self._combine_ensemble_results(ensemble_results)
            
            logger.info("🎯 Ensemble analysis completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Ensemble analysis failed: {e}")
            raise
    
    async def _single_model_analysis(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Single model analysis (fallback approach)
        
        This is a SINGLE-AGENT approach using one model
        """
        logger.info("🔍 Starting single model analysis...")
        
        try:
            # Prepare request
            instances = [{
                "image": {"b64": base64.b64encode(image_data).decode()},
                "user_profile": user_profile or {}
            }]
            
            # Make prediction
            response = self.prediction_client.predict(
                endpoint=self.endpoints["skin_analysis"],
                instances=instances
            )
            
            # Process response
            result = self._process_prediction_response(response)
            
            logger.info("✅ Single model analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Single model analysis failed: {e}")
            raise
    
    async def _analyze_with_model(
        self, 
        model_name: str, 
        request_data: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze with a specific model (used in ensemble approach)
        
        This represents a SINGLE AGENT that specializes in one type of analysis
        """
        try:
            endpoint = self.endpoints.get(model_name)
            if not endpoint:
                raise ValueError(f"Endpoint not found for model: {model_name}")
            
            # Add analysis type to request
            request_data["analysis_type"] = analysis_type
            
            # Make prediction
            response = self.prediction_client.predict(
                endpoint=endpoint,
                instances=[request_data]
            )
            
            # Process response
            result = self._process_prediction_response(response)
            result["model_name"] = model_name
            result["analysis_type"] = analysis_type
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Model {model_name} analysis failed: {e}")
            raise
    
    async def _stream_predictions(self, instances: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream predictions in real-time
        
        This is a SINGLE-AGENT streaming approach
        """
        try:
            # This would be implemented with actual streaming API
            # For now, we'll simulate streaming with async generation
            async for chunk in self._simulate_streaming(instances):
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Streaming predictions failed: {e}")
            raise
    
    async def _simulate_streaming(self, instances: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Simulate streaming predictions (replace with actual streaming API)
        """
        # Simulate progressive analysis results
        conditions = ["acne", "hyperpigmentation", "wrinkles", "dry_skin"]
        confidences = [0.85, 0.72, 0.68, 0.45]
        
        for i, (condition, confidence) in enumerate(zip(conditions, confidences)):
            await asyncio.sleep(0.5)  # Simulate processing time
            
            yield {
                "condition": condition,
                "confidence": confidence,
                "severity": "moderate" if confidence > 0.7 else "mild",
                "timestamp": datetime.now().isoformat(),
                "progress": (i + 1) / len(conditions)
            }
    
    def _combine_streaming_results(self, streaming_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine streaming results into final analysis"""
        conditions = []
        max_confidence = 0
        overall_health_score = 0
        
        for result in streaming_results:
            if "condition" in result:
                conditions.append({
                    "condition": result["condition"],
                    "confidence": result["confidence"],
                    "severity": result.get("severity", "mild")
                })
                max_confidence = max(max_confidence, result["confidence"])
                overall_health_score += result["confidence"] * 20
        
        return {
            "success": True,
            "analysis_results": [{
                "face_id": 0,
                "conditions": conditions,
                "skin_type": {"primary": "combination", "confidence": max_confidence},
                "health_score": min(100, max(0, 100 - overall_health_score))
            }],
            "detected_conditions": [c["condition"] for c in conditions],
            "faces_detected": 1,
            "overall_health_score": min(100, max(0, 100 - overall_health_score)),
            "streaming_enabled": True
        }
    
    def _combine_ensemble_results(self, ensemble_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine results from multiple models using weighted voting
        
        This is where MULTI-AGENT coordination happens
        """
        logger.info("🔄 Combining ensemble results...")
        
        # Initialize combined result
        combined = {
            "success": True,
            "analysis_results": [],
            "detected_conditions": [],
            "faces_detected": 1,
            "ensemble_analysis": True,
            "model_contributions": {}
        }
        
        # Process each model's results
        all_conditions = []
        skin_types = []
        health_scores = []
        
        for model_name, result in ensemble_results.items():
            if not result.get("success", False):
                continue
            
            weight = self.ensemble_weights.get(model_name, 0.33)
            
            # Extract conditions
            if "conditions" in result:
                for condition in result["conditions"]:
                    condition["weight"] = weight
                    all_conditions.append(condition)
            
            # Extract skin type
            if "skin_type" in result:
                skin_types.append({
                    "type": result["skin_type"],
                    "weight": weight
                })
            
            # Extract health score
            if "health_score" in result:
                health_scores.append(result["health_score"] * weight)
            
            # Track model contribution
            combined["model_contributions"][model_name] = {
                "weight": weight,
                "confidence": result.get("confidence", 0.5)
            }
        
        # Weighted voting for conditions
        condition_votes = {}
        for condition in all_conditions:
            key = condition["condition"]
            if key not in condition_votes:
                condition_votes[key] = {"confidence": 0, "severity": "mild", "weight": 0}
            
            weight = condition["weight"]
            condition_votes[key]["confidence"] += condition["confidence"] * weight
            condition_votes[key]["weight"] += weight
            
            if condition["severity"] == "severe":
                condition_votes[key]["severity"] = "severe"
            elif condition["severity"] == "moderate" and condition_votes[key]["severity"] != "severe":
                condition_votes[key]["severity"] = "moderate"
        
        # Normalize confidences
        final_conditions = []
        for condition, data in condition_votes.items():
            if data["weight"] > 0:
                final_conditions.append({
                    "condition": condition,
                    "confidence": data["confidence"] / data["weight"],
                    "severity": data["severity"]
                })
        
        # Weighted voting for skin type
        skin_type_votes = {}
        for st in skin_types:
            key = st["type"]
            if key not in skin_type_votes:
                skin_type_votes[key] = 0
            skin_type_votes[key] += st["weight"]
        
        final_skin_type = max(skin_type_votes.items(), key=lambda x: x[1])[0] if skin_type_votes else "normal"
        
        # Calculate final health score
        final_health_score = sum(health_scores) if health_scores else 75
        
        # Build final result
        combined["analysis_results"] = [{
            "face_id": 0,
            "conditions": final_conditions,
            "skin_type": {"primary": final_skin_type, "confidence": max(skin_type_votes.values()) if skin_type_votes else 0.5},
            "health_score": min(100, max(0, int(final_health_score)))
        }]
        
        combined["detected_conditions"] = [c["condition"] for c in final_conditions]
        combined["overall_health_score"] = min(100, max(0, int(final_health_score)))
        
        logger.info(f"✅ Combined {len(ensemble_results)} model results")
        return combined
    
    def _process_prediction_response(self, response) -> Dict[str, Any]:
        """Process Vertex AI prediction response"""
        try:
            # Extract predictions from response
            predictions = response.predictions[0] if response.predictions else {}
            
            # Process based on response structure
            result = {
                "success": True,
                "conditions": predictions.get("conditions", []),
                "skin_type": predictions.get("skin_type", "normal"),
                "health_score": predictions.get("health_score", 75),
                "confidence": predictions.get("confidence", 0.5)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing prediction response: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fallback_analysis(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fallback analysis when Vertex AI is not available"""
        logger.warning("⚠️ Using fallback analysis (basic Gemini)")
        
        # Import and use existing Gemini service as fallback
        try:
            from gemini_analysis_service import get_gemini_service
            from config import GEMINI_API_KEY
            
            gemini_service = get_gemini_service(GEMINI_API_KEY)
            return gemini_service.analyze_skin_image(
                image_data=image_data,
                user_profile=user_profile,
                user_skin_profile=user_profile
            )
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis failed: {e}")
            return {
                "success": False,
                "error": f"All analysis methods failed: {str(e)}",
                "fallback_used": True
            }
    
    # Caching methods
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get analysis result from cache"""
        try:
            if not self.cache_client:
                return None
            
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache retrieval failed: {e}")
            return None
    
    async def _store_in_cache(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Store analysis result in cache"""
        try:
            if not self.cache_client:
                return
            
            await self.cache_client.setex(
                cache_key, 
                ttl, 
                json.dumps(result, default=str)
            )
            logger.info(f"💾 Cached analysis result: {cache_key}")
            
        except Exception as e:
            logger.error(f"❌ Cache storage failed: {e}")
    
    def _generate_analysis_id(self, image_data: bytes, user_profile: Optional[Dict[str, Any]]) -> str:
        """Generate unique analysis ID for caching"""
        # Create hash of image and user profile
        content = image_data + json.dumps(user_profile or {}, sort_keys=True).encode()
        return hashlib.md5(content).hexdigest()
    
    # Performance monitoring
    async def _track_performance(
        self, 
        analysis_id: str, 
        start_time: float, 
        end_time: float, 
        result: Dict[str, Any]
    ):
        """Track performance metrics"""
        try:
            if not self.monitoring_enabled:
                return
            
            metrics = {
                "analysis_id": analysis_id,
                "duration": end_time - start_time,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "conditions_detected": len(result.get("detected_conditions", [])),
                "health_score": result.get("overall_health_score", 0),
                "model_version": "2.0.0-vertex-ai"
            }
            
            # Store metrics (implement actual metrics storage)
            logger.info(f"📊 Performance metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"❌ Performance tracking failed: {e}")
    
    async def get_ai_recommendations(
        self, 
        skin_analysis: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI-powered product recommendations using Vertex AI
        
        This uses a SINGLE-AGENT approach for recommendations
        """
        try:
            if not self.enabled:
                return {"success": False, "error": "Vertex AI not enabled"}
            
            # Prepare recommendation request
            instances = [{
                "skin_conditions": skin_analysis.get("detected_conditions", []),
                "skin_type": skin_analysis.get("skin_type", {}).get("primary", "normal"),
                "health_score": skin_analysis.get("overall_health_score", 75),
                "user_preferences": user_profile,
                "budget_range": user_profile.get("budget", [0, 200]),
                "allergies": user_profile.get("allergies", [])
            }]
            
            # Get recommendations from Vertex AI
            response = self.prediction_client.predict(
                endpoint=self.endpoints["recommendation_engine"],
                instances=instances
            )
            
            # Process recommendations
            recommendations = self._process_recommendations(response)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "ai_powered": True,
                "model_used": "vertex-ai-recommendation-engine"
            }
            
        except Exception as e:
            logger.error(f"❌ AI recommendations failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_recommendations(self, response) -> List[Dict[str, Any]]:
        """Process recommendation response from Vertex AI"""
        try:
            # Extract recommendations from response
            predictions = response.predictions[0] if response.predictions else {}
            recommendations = predictions.get("recommendations", [])
            
            # Format recommendations
            formatted_recommendations = []
            for rec in recommendations:
                formatted_recommendations.append({
                    "name": rec.get("name", "Recommended Product"),
                    "brand": rec.get("brand", "Unknown Brand"),
                    "price": rec.get("price", 0),
                    "rating": rec.get("rating", 4.0),
                    "description": rec.get("description", ""),
                    "reason": rec.get("reason", "AI recommended"),
                    "confidence": rec.get("confidence", 0.8),
                    "url": rec.get("url", ""),
                    "image": rec.get("image", "")
                })
            
            return formatted_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error processing recommendations: {e}")
            return []


# Global service instance
vertex_ai_service = VertexAISkinAnalysisService()


# Documentation for Multi-Agent vs Single-Agent Implementation
"""
MULTI-AGENT vs SINGLE-AGENT IMPLEMENTATION DIFFERENCES

## SINGLE-AGENT APPROACH:
- One service handles all analysis tasks
- Sequential or simple parallel processing
- Easier to implement and debug
- Lower complexity
- Single point of failure
- Example: Basic Gemini API calls

## MULTI-AGENT APPROACH:
- Multiple specialized agents work together
- Each agent has specific expertise
- Complex coordination required
- Higher accuracy through specialization
- Fault tolerance (if one agent fails, others continue)
- Example: Ensemble analysis with different models

## CODE IMPLEMENTATION DIFFERENCES:

### Single-Agent (Simple):
```python
async def analyze_skin(image_data):
    # One model does everything
    result = await single_model.predict(image_data)
    return result
```

### Multi-Agent (Ensemble):
```python
async def analyze_skin_ensemble(image_data):
    # Multiple specialized agents
    condition_agent = ConditionClassifierAgent()
    severity_agent = SeverityAnalyzerAgent()
    skin_type_agent = SkinTypeDetectorAgent()
    
    # Parallel execution
    tasks = [
        condition_agent.analyze(image_data),
        severity_agent.analyze(image_data),
        skin_type_agent.analyze(image_data)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Coordination and combination
    final_result = coordinate_agents(results)
    return final_result
```

## BENEFITS OF MULTI-AGENT APPROACH:
1. **Specialization**: Each agent is optimized for specific tasks
2. **Fault Tolerance**: If one agent fails, others continue
3. **Scalability**: Agents can be scaled independently
4. **Accuracy**: Ensemble voting improves accuracy
5. **Flexibility**: Easy to add/remove agents

## BENEFITS OF SINGLE-AGENT APPROACH:
1. **Simplicity**: Easier to implement and maintain
2. **Performance**: Lower latency for simple tasks
3. **Resource Efficiency**: Less overhead
4. **Debugging**: Easier to trace issues
5. **Cost**: Lower computational requirements

## WHEN TO USE EACH:

### Use Multi-Agent when:
- High accuracy is critical
- Complex analysis required
- Fault tolerance needed
- Different models have different strengths
- Processing time is not critical

### Use Single-Agent when:
- Simple analysis is sufficient
- Low latency is critical
- Limited computational resources
- Easy maintenance is priority
- Cost is a major concern

## IMPLEMENTATION IN DERMALENS:

The current implementation supports both approaches:

1. **Single-Agent**: `_single_model_analysis()` - One model does everything
2. **Multi-Agent**: `_ensemble_analysis()` - Multiple specialized models
3. **Streaming**: `_streaming_analysis()` - Real-time single-agent streaming

Users can choose the approach based on their needs:
- Development/Testing: Single-agent (faster, simpler)
- Production: Multi-agent (more accurate, fault-tolerant)
- Real-time: Streaming (immediate feedback)
"""
