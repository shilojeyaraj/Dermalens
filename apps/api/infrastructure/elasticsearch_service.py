"""
Elasticsearch service for intelligent product search and recommendations
"""
from elasticsearch import Elasticsearch
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ElasticsearchProductService:
    """Elasticsearch service for skincare product search and recommendations"""
    
    def __init__(self, elasticsearch_url: str = None):
        from config import ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD, ELASTICSEARCH_SSL_VERIFY
        
        # Use environment variables if not provided
        if elasticsearch_url is None:
            elasticsearch_url = ELASTICSEARCH_URL
        
        # Configure Elasticsearch client with authentication
        if ELASTICSEARCH_API_KEY:
            # Use API key authentication
            self.es = Elasticsearch(
                [elasticsearch_url],
                api_key=ELASTICSEARCH_API_KEY,
                verify_certs=ELASTICSEARCH_SSL_VERIFY
            )
        elif ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
            # Use basic authentication
            self.es = Elasticsearch(
                [elasticsearch_url],
                basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
                verify_certs=ELASTICSEARCH_SSL_VERIFY
            )
        else:
            # No authentication (local development)
            self.es = Elasticsearch([elasticsearch_url])
        
        self.index_name = "skincare_products"
        self.ensure_index_exists()
    
    def ensure_index_exists(self):
        """Create the skincare products index if it doesn't exist"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "name": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "brand": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "ingredients": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "skin_conditions": {
                            "type": "keyword"
                        },
                        "skin_types": {
                            "type": "keyword"
                        },
                        "product_type": {
                            "type": "keyword"
                        },
                        "price": {
                            "type": "float"
                        },
                        "rating": {
                            "type": "float"
                        },
                        "review_count": {
                            "type": "integer"
                        },
                        "url": {
                            "type": "keyword"
                        },
                        "image_url": {
                            "type": "keyword"
                        },
                        "allergen_free": {
                            "type": "boolean"
                        },
                        "fragrance_free": {
                            "type": "boolean"
                        },
                        "cruelty_free": {
                            "type": "boolean"
                        },
                        "vegan": {
                            "type": "boolean"
                        },
                        "spf_level": {
                            "type": "integer"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "updated_at": {
                            "type": "date"
                        }
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "skincare_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop", "snowball"]
                            }
                        }
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created Elasticsearch index: {self.index_name}")
    
    def index_product(self, product: Dict[str, Any]) -> str:
        """Index a single product in Elasticsearch"""
        try:
            # Add timestamp
            product["created_at"] = datetime.now().isoformat()
            product["updated_at"] = datetime.now().isoformat()
            
            # Generate ID if not provided
            product_id = product.get("id", f"{product['brand']}_{product['name']}".lower().replace(" ", "_"))
            
            response = self.es.index(
                index=self.index_name,
                id=product_id,
                body=product
            )
            
            logger.info(f"Indexed product: {product['name']}")
            return response["_id"]
            
        except Exception as e:
            logger.error(f"Error indexing product: {e}")
            raise
    
    def bulk_index_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index multiple products"""
        try:
            actions = []
            for product in products:
                product_id = product.get("id", f"{product['brand']}_{product['name']}".lower().replace(" ", "_"))
                product["created_at"] = datetime.now().isoformat()
                product["updated_at"] = datetime.now().isoformat()
                
                action = {
                    "_index": self.index_name,
                    "_id": product_id,
                    "_source": product
                }
                actions.append(action)
            
            response = self.es.bulk(body=actions)
            
            # Check for errors
            errors = [item for item in response["items"] if "error" in item]
            if errors:
                logger.error(f"Bulk indexing errors: {errors}")
            
            logger.info(f"Bulk indexed {len(products)} products")
            return response
            
        except Exception as e:
            logger.error(f"Error in bulk indexing: {e}")
            raise
    
    def search_products(
        self,
        query: str = "",
        skin_conditions: List[str] = None,
        skin_types: List[str] = None,
        product_types: List[str] = None,
        price_range: Dict[str, float] = None,
        min_rating: float = None,
        allergen_free: bool = None,
        fragrance_free: bool = None,
        size: int = 20,
        from_: int = 0
    ) -> Dict[str, Any]:
        """Search products with advanced filtering and scoring"""
        try:
            # Build the search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [],
                        "should": []
                    }
                },
                "size": size,
                "from": from_,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"rating": {"order": "desc"}},
                    {"review_count": {"order": "desc"}}
                ]
            }
            
            # Text search
            if query:
                search_body["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "brand^2", "description", "ingredients"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            
            # Filter by skin conditions
            if skin_conditions:
                search_body["query"]["bool"]["filter"].append({
                    "terms": {
                        "skin_conditions": skin_conditions
                    }
                })
            
            # Filter by skin types
            if skin_types:
                search_body["query"]["bool"]["filter"].append({
                    "terms": {
                        "skin_types": skin_types
                    }
                })
            
            # Filter by product types
            if product_types:
                search_body["query"]["bool"]["filter"].append({
                    "terms": {
                        "product_type": product_types
                    }
                })
            
            # Price range filter
            if price_range:
                price_filter = {"range": {"price": {}}}
                if "gte" in price_range:
                    price_filter["range"]["price"]["gte"] = price_range["gte"]
                if "lte" in price_range:
                    price_filter["range"]["price"]["lte"] = price_range["lte"]
                search_body["query"]["bool"]["filter"].append(price_filter)
            
            # Minimum rating filter
            if min_rating:
                search_body["query"]["bool"]["filter"].append({
                    "range": {
                        "rating": {"gte": min_rating}
                    }
                })
            
            # Boolean filters
            if allergen_free is not None:
                search_body["query"]["bool"]["filter"].append({
                    "term": {"allergen_free": allergen_free}
                })
            
            if fragrance_free is not None:
                search_body["query"]["bool"]["filter"].append({
                    "term": {"fragrance_free": fragrance_free}
                })
            
            # Boost certain criteria
            search_body["query"]["bool"]["should"].extend([
                {"term": {"cruelty_free": {"value": True, "boost": 1.2}}},
                {"term": {"vegan": {"value": True, "boost": 1.1}}},
                {"range": {"rating": {"gte": 4.0, "boost": 1.3}}},
                {"range": {"review_count": {"gte": 100, "boost": 1.1}}}
            ])
            
            # Execute search
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results
            products = []
            for hit in response["hits"]["hits"]:
                product = hit["_source"]
                product["_id"] = hit["_id"]
                product["_score"] = hit["_score"]
                products.append(product)
            
            return {
                "success": True,
                "products": products,
                "total": response["hits"]["total"]["value"],
                "took": response["took"],
                "max_score": response["hits"]["max_score"]
            }
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {
                "success": False,
                "error": str(e),
                "products": []
            }
    
    def get_recommendations(
        self,
        user_profile: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get personalized product recommendations based on user profile and analysis"""
        try:
            # Extract conditions from analysis
            detected_conditions = []
            for result in analysis_results:
                for condition_data in result["conditions"]:
                    if condition_data["confidence"] > 0.3:
                        detected_conditions.append(condition_data["condition"])
            
            # Get user preferences
            skin_type = user_profile.get("skin_type", "")
            allergies = user_profile.get("allergies", [])
            sensitivity_level = user_profile.get("sensitivity_level", "")
            
            # Build recommendation query
            search_body = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [],
                        "should": []
                    }
                },
                "size": limit,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"rating": {"order": "desc"}}
                ]
            }
            
            # Filter by detected conditions
            if detected_conditions:
                search_body["query"]["bool"]["filter"].append({
                    "terms": {
                        "skin_conditions": detected_conditions
                    }
                })
            
            # Filter by skin type
            if skin_type:
                search_body["query"]["bool"]["filter"].append({
                    "term": {
                        "skin_types": skin_type.lower()
                    }
                })
            
            # Exclude products with user allergies
            if allergies:
                for allergy in allergies:
                    search_body["query"]["bool"]["must_not"].append({
                        "match": {
                            "ingredients": allergy
                        }
                    })
            
            # Boost for sensitivity considerations
            if sensitivity_level == "high":
                search_body["query"]["bool"]["should"].extend([
                    {"term": {"fragrance_free": {"value": True, "boost": 2.0}}},
                    {"term": {"allergen_free": {"value": True, "boost": 1.5}}}
                ])
            
            # Execute search
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results
            recommendations = []
            for hit in response["hits"]["hits"]:
                product = hit["_source"]
                product["_id"] = hit["_id"]
                product["_score"] = hit["_score"]
                product["recommendation_reason"] = self._get_recommendation_reason(
                    product, detected_conditions, user_profile
                )
                recommendations.append(product)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total": response["hits"]["total"]["value"],
                "detected_conditions": detected_conditions
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def _get_recommendation_reason(
        self,
        product: Dict[str, Any],
        detected_conditions: List[str],
        user_profile: Dict[str, Any]
    ) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        # Check for condition matches
        product_conditions = product.get("skin_conditions", [])
        matching_conditions = set(detected_conditions) & set(product_conditions)
        if matching_conditions:
            reasons.append(f"Targets: {', '.join(matching_conditions)}")
        
        # Check for skin type match
        user_skin_type = user_profile.get("skin_type", "").lower()
        product_skin_types = [t.lower() for t in product.get("skin_types", [])]
        if user_skin_type in product_skin_types:
            reasons.append(f"Perfect for {user_skin_type} skin")
        
        # Check for special features
        if product.get("fragrance_free") and user_profile.get("sensitivity_level") == "high":
            reasons.append("Fragrance-free for sensitive skin")
        
        if product.get("cruelty_free"):
            reasons.append("Cruelty-free")
        
        if product.get("vegan"):
            reasons.append("Vegan")
        
        return "; ".join(reasons) if reasons else "Recommended based on your skin analysis"
    
    def get_similar_products(self, product_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get similar products using Elasticsearch's more_like_this query"""
        try:
            search_body = {
                "query": {
                    "more_like_this": {
                        "fields": ["name", "description", "ingredients", "skin_conditions"],
                        "like": [{"_index": self.index_name, "_id": product_id}],
                        "min_term_freq": 1,
                        "max_query_terms": 12,
                        "min_doc_freq": 1
                    }
                },
                "size": limit
            }
            
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            similar_products = []
            for hit in response["hits"]["hits"]:
                product = hit["_source"]
                product["_id"] = hit["_id"]
                product["_score"] = hit["_score"]
                similar_products.append(product)
            
            return {
                "success": True,
                "similar_products": similar_products
            }
            
        except Exception as e:
            logger.error(f"Error getting similar products: {e}")
            return {
                "success": False,
                "error": str(e),
                "similar_products": []
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics about the product database"""
        try:
            # Get total count
            count_response = self.es.count(index=self.index_name)
            total_products = count_response["count"]
            
            # Get aggregation data
            agg_body = {
                "size": 0,
                "aggs": {
                    "by_brand": {
                        "terms": {"field": "brand.keyword", "size": 10}
                    },
                    "by_type": {
                        "terms": {"field": "product_type", "size": 10}
                    },
                    "avg_rating": {
                        "avg": {"field": "rating"}
                    },
                    "price_stats": {
                        "stats": {"field": "price"}
                    }
                }
            }
            
            agg_response = self.es.search(
                index=self.index_name,
                body=agg_body
            )
            
            return {
                "success": True,
                "total_products": total_products,
                "brands": agg_response["aggregations"]["by_brand"]["buckets"],
                "product_types": agg_response["aggregations"]["by_type"]["buckets"],
                "average_rating": agg_response["aggregations"]["avg_rating"]["value"],
                "price_stats": agg_response["aggregations"]["price_stats"]
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global service instance
elasticsearch_service = ElasticsearchProductService()
