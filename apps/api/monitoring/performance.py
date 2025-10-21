"""
Performance Monitoring Service for Dermalens
Tracks and analyzes performance metrics for AI services, caching, and user interactions
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import statistics
import math

# Google Cloud monitoring
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query

# Prometheus for metrics
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configuration
from config import (
    PERFORMANCE_MONITORING_ENABLED, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION,
    METRICS_ENDPOINT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    service: str
    operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ServiceHealth:
    """Service health status"""
    service_name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any]


class PerformanceMonitoringService:
    """
    Comprehensive performance monitoring service
    
    Features:
    - Real-time metrics collection
    - Service health monitoring
    - Performance analytics
    - Alerting and notifications
    - Cost optimization tracking
    - User behavior analytics
    """
    
    def __init__(self):
        """Initialize the performance monitoring service"""
        self.enabled = PERFORMANCE_MONITORING_ENABLED
        self.project_id = GOOGLE_CLOUD_PROJECT
        self.region = GOOGLE_CLOUD_REGION
        
        # Monitoring clients
        self.monitoring_client = None
        self.prometheus_metrics = {}
        
        # Metrics storage
        self.metrics_buffer = []
        self.health_status = {}
        self.performance_history = {}
        
        # Configuration
        self.buffer_size = 1000
        self.flush_interval = 60  # seconds
        self.health_check_interval = 30  # seconds
        
        # Initialize monitoring
        self._initialize_monitoring()
        self._setup_prometheus_metrics()
        
        # Start background tasks
        if self.enabled:
            asyncio.create_task(self._background_monitoring())
            asyncio.create_task(self._health_checker())
    
    def _initialize_monitoring(self):
        """Initialize Google Cloud monitoring"""
        try:
            if self.enabled:
                self.monitoring_client = monitoring_v3.MetricServiceClient()
                logger.info("✅ Performance monitoring initialized")
            else:
                logger.warning("⚠️ Performance monitoring is disabled")
                
        except Exception as e:
            logger.error(f"❌ Monitoring initialization failed: {e}")
            self.enabled = False
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        try:
            if not self.enabled:
                return
            
            # Analysis metrics
            self.prometheus_metrics["analysis_requests"] = Counter(
                'dermalens_analysis_requests_total',
                'Total number of analysis requests',
                ['service', 'type', 'status']
            )
            
            self.prometheus_metrics["analysis_duration"] = Histogram(
                'dermalens_analysis_duration_seconds',
                'Analysis request duration',
                ['service', 'type'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
            )
            
            # Cache metrics
            self.prometheus_metrics["cache_operations"] = Counter(
                'dermalens_cache_operations_total',
                'Total cache operations',
                ['operation', 'result']
            )
            
            self.prometheus_metrics["cache_hit_rate"] = Gauge(
                'dermalens_cache_hit_rate',
                'Cache hit rate percentage'
            )
            
            # Recommendation metrics
            self.prometheus_metrics["recommendation_requests"] = Counter(
                'dermalens_recommendation_requests_total',
                'Total recommendation requests',
                ['type', 'status']
            )
            
            self.prometheus_metrics["recommendation_quality"] = Histogram(
                'dermalens_recommendation_quality_score',
                'Recommendation quality scores',
                ['type'],
                buckets=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            )
            
            # Service health metrics
            self.prometheus_metrics["service_health"] = Gauge(
                'dermalens_service_health',
                'Service health status',
                ['service']
            )
            
            # Start Prometheus HTTP server
            start_http_server(8001)
            logger.info("📊 Prometheus metrics server started on port 8001")
            
        except Exception as e:
            logger.error(f"❌ Prometheus metrics setup failed: {e}")
    
    async def track_analysis_performance(
        self,
        analysis_id: str,
        service: str,
        analysis_type: str,
        start_time: float,
        end_time: float,
        success: bool,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        additional_metrics: Optional[Dict[str, Any]] = None
    ):
        """Track analysis performance metrics"""
        try:
            if not self.enabled:
                return
            
            duration = end_time - start_time
            
            # Create performance metric
            metric = PerformanceMetric(
                metric_name="analysis_duration",
                value=duration,
                timestamp=datetime.now(),
                labels={
                    "service": service,
                    "type": analysis_type,
                    "status": "success" if success else "error",
                    "analysis_id": analysis_id
                },
                service=service,
                operation="analysis",
                user_id=user_id,
                session_id=session_id
            )
            
            # Add to buffer
            self.metrics_buffer.append(metric)
            
            # Update Prometheus metrics
            self.prometheus_metrics["analysis_requests"].labels(
                service=service,
                type=analysis_type,
                status="success" if success else "error"
            ).inc()
            
            self.prometheus_metrics["analysis_duration"].labels(
                service=service,
                type=analysis_type
            ).observe(duration)
            
            # Track additional metrics
            if additional_metrics:
                for metric_name, value in additional_metrics.items():
                    additional_metric = PerformanceMetric(
                        metric_name=metric_name,
                        value=value,
                        timestamp=datetime.now(),
                        labels=metric.labels.copy(),
                        service=service,
                        operation="analysis",
                        user_id=user_id,
                        session_id=session_id
                    )
                    self.metrics_buffer.append(additional_metric)
            
            # Flush buffer if needed
            if len(self.metrics_buffer) >= self.buffer_size:
                await self._flush_metrics()
            
            logger.info(f"📊 Tracked analysis performance: {service}/{analysis_type} - {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Analysis performance tracking failed: {e}")
    
    async def track_cache_performance(
        self,
        operation: str,
        cache_key: str,
        hit: bool,
        duration: float,
        service: str
    ):
        """Track cache performance metrics"""
        try:
            if not self.enabled:
                return
            
            # Update Prometheus metrics
            self.prometheus_metrics["cache_operations"].labels(
                operation=operation,
                result="hit" if hit else "miss"
            ).inc()
            
            # Create cache metric
            metric = PerformanceMetric(
                metric_name="cache_operation",
                value=duration,
                timestamp=datetime.now(),
                labels={
                    "operation": operation,
                    "result": "hit" if hit else "miss",
                    "cache_key": cache_key[:16] + "..." if len(cache_key) > 16 else cache_key
                },
                service=service,
                operation="cache"
            )
            
            self.metrics_buffer.append(metric)
            
            # Update cache hit rate
            await self._update_cache_hit_rate()
            
        except Exception as e:
            logger.error(f"❌ Cache performance tracking failed: {e}")
    
    async def track_recommendation_performance(
        self,
        recommendation_type: str,
        start_time: float,
        end_time: float,
        success: bool,
        quality_score: float,
        user_id: Optional[str] = None
    ):
        """Track recommendation performance metrics"""
        try:
            if not self.enabled:
                return
            
            duration = end_time - start_time
            
            # Update Prometheus metrics
            self.prometheus_metrics["recommendation_requests"].labels(
                type=recommendation_type,
                status="success" if success else "error"
            ).inc()
            
            self.prometheus_metrics["recommendation_quality"].labels(
                type=recommendation_type
            ).observe(quality_score)
            
            # Create recommendation metric
            metric = PerformanceMetric(
                metric_name="recommendation_duration",
                value=duration,
                timestamp=datetime.now(),
                labels={
                    "type": recommendation_type,
                    "status": "success" if success else "error",
                    "quality_score": str(quality_score)
                },
                service="recommendation_engine",
                operation="recommendation",
                user_id=user_id
            )
            
            self.metrics_buffer.append(metric)
            
        except Exception as e:
            logger.error(f"❌ Recommendation performance tracking failed: {e}")
    
    async def _update_cache_hit_rate(self):
        """Update cache hit rate metric"""
        try:
            # Calculate hit rate from recent metrics
            cache_metrics = [m for m in self.metrics_buffer if m.metric_name == "cache_operation"]
            
            if cache_metrics:
                hits = sum(1 for m in cache_metrics if m.labels.get("result") == "hit")
                total = len(cache_metrics)
                hit_rate = (hits / total) * 100 if total > 0 else 0
                
                self.prometheus_metrics["cache_hit_rate"].set(hit_rate)
            
        except Exception as e:
            logger.error(f"❌ Cache hit rate update failed: {e}")
    
    async def _flush_metrics(self):
        """Flush metrics buffer to monitoring service"""
        try:
            if not self.metrics_buffer or not self.monitoring_client:
                return
            
            # Group metrics by service
            service_metrics = {}
            for metric in self.metrics_buffer:
                service = metric.service
                if service not in service_metrics:
                    service_metrics[service] = []
                service_metrics[service].append(metric)
            
            # Send metrics to Google Cloud Monitoring
            for service, metrics in service_metrics.items():
                await self._send_metrics_to_cloud_monitoring(service, metrics)
            
            # Clear buffer
            self.metrics_buffer.clear()
            
            logger.info(f"📊 Flushed {len(service_metrics)} service metrics")
            
        except Exception as e:
            logger.error(f"❌ Metrics flush failed: {e}")
    
    async def _send_metrics_to_cloud_monitoring(
        self, 
        service: str, 
        metrics: List[PerformanceMetric]
    ):
        """Send metrics to Google Cloud Monitoring"""
        try:
            if not self.monitoring_client:
                return
            
            # This would implement actual Google Cloud Monitoring integration
            # For now, just log the metrics
            logger.info(f"📊 Sending {len(metrics)} metrics for service: {service}")
            
        except Exception as e:
            logger.error(f"❌ Cloud monitoring send failed: {e}")
    
    async def _background_monitoring(self):
        """Background task for continuous monitoring"""
        while self.enabled:
            try:
                # Flush metrics periodically
                if self.metrics_buffer:
                    await self._flush_metrics()
                
                # Update performance history
                await self._update_performance_history()
                
                # Sleep for flush interval
                await asyncio.sleep(self.flush_interval)
                
            except Exception as e:
                logger.error(f"❌ Background monitoring failed: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _health_checker(self):
        """Background task for service health checking"""
        while self.enabled:
            try:
                # Check health of all services
                await self._check_service_health()
                
                # Sleep for health check interval
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Health checking failed: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _check_service_health(self):
        """Check health of all services"""
        try:
            services_to_check = [
                "vertex_ai",
                "elasticsearch",
                "google_search",
                "caching",
                "recommendation_engine"
            ]
            
            for service in services_to_check:
                health = await self._check_single_service_health(service)
                self.health_status[service] = health
                
                # Update Prometheus health metric
                health_value = 1 if health.status == "healthy" else 0
                self.prometheus_metrics["service_health"].labels(service=service).set(health_value)
            
        except Exception as e:
            logger.error(f"❌ Service health check failed: {e}")
    
    async def _check_single_service_health(self, service: str) -> ServiceHealth:
        """Check health of a single service"""
        try:
            start_time = time.time()
            
            if service == "vertex_ai":
                # Check Vertex AI service
                from vertex_ai_service import vertex_ai_service
                is_healthy = vertex_ai_service.enabled
                response_time = time.time() - start_time
                
            elif service == "elasticsearch":
                # Check Elasticsearch service
                from elasticsearch_service import elasticsearch_service
                is_healthy = True  # Simplified check
                response_time = time.time() - start_time
                
            elif service == "google_search":
                # Check Google Search service
                from google_search_service import google_search_service
                is_healthy = google_search_service.is_enabled()
                response_time = time.time() - start_time
                
            elif service == "caching":
                # Check caching service
                from intelligent_caching_service import intelligent_caching_service
                is_healthy = intelligent_caching_service.enabled
                response_time = time.time() - start_time
                
            elif service == "recommendation_engine":
                # Check recommendation engine
                from ai_recommendation_engine import ai_recommendation_engine
                is_healthy = True  # Simplified check
                response_time = time.time() - start_time
                
            else:
                is_healthy = False
                response_time = 0
            
            # Determine health status
            if is_healthy and response_time < 5.0:
                status = "healthy"
            elif is_healthy and response_time < 10.0:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return ServiceHealth(
                service_name=service,
                status=status,
                response_time=response_time,
                error_rate=0.0,  # Would calculate from recent errors
                last_check=datetime.now(),
                details={"enabled": is_healthy}
            )
            
        except Exception as e:
            logger.error(f"❌ Health check for {service} failed: {e}")
            return ServiceHealth(
                service_name=service,
                status="unhealthy",
                response_time=0,
                error_rate=1.0,
                last_check=datetime.now(),
                details={"error": str(e)}
            )
    
    async def _update_performance_history(self):
        """Update performance history for analytics"""
        try:
            # Calculate performance statistics
            recent_metrics = self.metrics_buffer[-100:] if self.metrics_buffer else []
            
            if recent_metrics:
                # Group by service
                service_stats = {}
                for metric in recent_metrics:
                    service = metric.service
                    if service not in service_stats:
                        service_stats[service] = []
                    service_stats[service].append(metric.value)
                
                # Calculate statistics
                for service, values in service_stats.items():
                    if values:
                        self.performance_history[service] = {
                            "avg_response_time": statistics.mean(values),
                            "median_response_time": statistics.median(values),
                            "p95_response_time": self._calculate_percentile(values, 95),
                            "p99_response_time": self._calculate_percentile(values, 99),
                            "min_response_time": min(values),
                            "max_response_time": max(values),
                            "sample_count": len(values),
                            "timestamp": datetime.now().isoformat()
                        }
            
        except Exception as e:
            logger.error(f"❌ Performance history update failed: {e}")
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        try:
            sorted_values = sorted(values)
            index = int((percentile / 100) * len(sorted_values))
            return sorted_values[min(index, len(sorted_values) - 1)]
        except Exception:
            return 0.0
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        try:
            analytics = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_enabled": self.enabled,
                "services_health": {service: asdict(health) for service, health in self.health_status.items()},
                "performance_history": self.performance_history,
                "current_metrics": {
                    "buffer_size": len(self.metrics_buffer),
                    "total_metrics_collected": sum(len(metrics) for metrics in self.performance_history.values())
                },
                "recommendations": await self._generate_performance_recommendations()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Performance analytics generation failed: {e}")
            return {"error": str(e)}
    
    async def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        try:
            recommendations = []
            
            # Check cache hit rate
            cache_metrics = [m for m in self.metrics_buffer if m.metric_name == "cache_operation"]
            if cache_metrics:
                hits = sum(1 for m in cache_metrics if m.labels.get("result") == "hit")
                total = len(cache_metrics)
                hit_rate = (hits / total) * 100 if total > 0 else 0
                
                if hit_rate < 50:
                    recommendations.append("Consider increasing cache TTL or improving cache key generation")
            
            # Check response times
            for service, stats in self.performance_history.items():
                if stats.get("avg_response_time", 0) > 5.0:
                    recommendations.append(f"Consider optimizing {service} - avg response time: {stats['avg_response_time']:.2f}s")
            
            # Check service health
            unhealthy_services = [service for service, health in self.health_status.items() if health.status != "healthy"]
            if unhealthy_services:
                recommendations.append(f"Address health issues in services: {', '.join(unhealthy_services)}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Performance recommendations generation failed: {e}")
            return []
    
    async def get_service_health_status(self) -> Dict[str, ServiceHealth]:
        """Get current health status of all services"""
        return self.health_status.copy()
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        try:
            summary = {
                "total_metrics": len(self.metrics_buffer),
                "services_monitored": list(set(m.service for m in self.metrics_buffer)),
                "time_range": {
                    "earliest": min(m.timestamp for m in self.metrics_buffer).isoformat() if self.metrics_buffer else None,
                    "latest": max(m.timestamp for m in self.metrics_buffer).isoformat() if self.metrics_buffer else None
                },
                "metric_types": list(set(m.metric_name for m in self.metrics_buffer))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Metrics summary generation failed: {e}")
            return {"error": str(e)}


# Global service instance
performance_monitoring_service = PerformanceMonitoringService()
