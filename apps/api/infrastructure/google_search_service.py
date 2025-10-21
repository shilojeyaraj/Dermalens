"""
Google Custom Search API service for finding skincare products
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional, Any
import logging
from config import (
    GOOGLE_API_KEY,
    GOOGLE_SEARCH_ENGINE_ID,
    GOOGLE_SEARCH_ENABLED,
    GOOGLE_SEARCH_MAX_RESULTS,
    GOOGLE_SEARCH_SAFE_SEARCH,
    GOOGLE_SEARCH_COUNTRY,
    GOOGLE_SEARCH_LANGUAGE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSearchService:
    """Service for searching skincare products using Google Custom Search API"""
    
    def __init__(self):
        """Initialize the Google Custom Search service"""
        self.api_key = GOOGLE_API_KEY
        self.search_engine_id = GOOGLE_SEARCH_ENGINE_ID
        self.enabled = GOOGLE_SEARCH_ENABLED and self.api_key and self.search_engine_id
        self.service = None
        
        if self.enabled:
            try:
                self.service = build("customsearch", "v1", developerKey=self.api_key)
                logger.info("Google Custom Search API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Custom Search API: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Google Custom Search API is not enabled or missing credentials")
    
    def is_enabled(self) -> bool:
        """Check if Google Search is enabled and configured"""
        return self.enabled
    
    def search_products(
        self,
        query: str,
        skin_condition: Optional[str] = None,
        max_results: int = GOOGLE_SEARCH_MAX_RESULTS,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for skincare products using Google Custom Search
        
        Args:
            query: Search query string
            skin_condition: Specific skin condition to filter for
            max_results: Maximum number of results to return
            filters: Additional filters (price range, brand, etc.)
            
        Returns:
            Dictionary containing search results and metadata
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Google Custom Search API is not enabled",
                "products": []
            }
        
        try:
            # Build the search query
            search_query = self._build_search_query(query, skin_condition, filters)
            
            # Execute search
            results = self._execute_search(search_query, max_results)
            
            # Parse and format results
            products = self._parse_search_results(results)
            
            return {
                "success": True,
                "query": search_query,
                "products": products,
                "total_results": len(products),
                "metadata": {
                    "search_time": results.get("searchInformation", {}).get("searchTime", 0),
                    "total_available": results.get("searchInformation", {}).get("totalResults", "0")
                }
            }
            
        except HttpError as e:
            logger.error(f"Google Search API error: {str(e)}")
            return {
                "success": False,
                "error": f"Search API error: {str(e)}",
                "products": []
            }
        except Exception as e:
            logger.error(f"Unexpected error during product search: {str(e)}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "products": []
            }
    
    def search_products_for_conditions(
        self,
        conditions: List[str],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for products targeting multiple skin conditions
        
        Args:
            conditions: List of skin conditions to search for
            user_profile: User's skin profile for personalized filtering
            
        Returns:
            Dictionary containing aggregated search results
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Google Custom Search API is not enabled",
                "products_by_condition": {}
            }
        
        all_products = {}
        
        for condition in conditions:
            # Build condition-specific query
            query = f"skincare products for {condition}"
            
            # Add user profile filters if available
            filters = self._build_filters_from_profile(user_profile)
            
            # Search for this condition
            result = self.search_products(query, skin_condition=condition, filters=filters)
            
            if result["success"]:
                all_products[condition] = result["products"]
        
        # Deduplicate and rank products
        deduplicated_products = self._deduplicate_and_rank(all_products, user_profile)
        
        return {
            "success": True,
            "products_by_condition": all_products,
            "recommended_products": deduplicated_products,
            "total_products": len(deduplicated_products)
        }
    
    def _build_search_query(
        self,
        query: str,
        skin_condition: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build optimized search query"""
        search_parts = [query]
        
        if skin_condition:
            search_parts.append(f"for {skin_condition}")
        
        # Add filters to query
        if filters:
            if filters.get("brand"):
                search_parts.append(filters["brand"])
            if filters.get("product_type"):
                search_parts.append(filters["product_type"])
            if filters.get("ingredients_include"):
                search_parts.append(f"with {' '.join(filters['ingredients_include'])}")
            if filters.get("ingredients_exclude"):
                for ingredient in filters["ingredients_exclude"]:
                    search_parts.append(f"-{ingredient}")
        
        return " ".join(search_parts)
    
    def _execute_search(self, query: str, max_results: int = 10) -> Dict:
        """Execute Google Custom Search API call"""
        try:
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=min(max_results, 10),  # API max is 10 per request
                safe=GOOGLE_SEARCH_SAFE_SEARCH,
                gl=GOOGLE_SEARCH_COUNTRY,
                lr=f"lang_{GOOGLE_SEARCH_LANGUAGE}"
            ).execute()
            
            return result
            
        except HttpError as e:
            logger.error(f"Google Search API HTTP error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing search: {str(e)}")
            raise
    
    def _parse_search_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Parse Google Search results into product format"""
        products = []
        
        items = results.get("items", [])
        
        for idx, item in enumerate(items):
            product = {
                "name": item.get("title", "Unknown Product"),
                "description": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": item.get("displayLink", ""),
                "image": self._extract_image(item),
                "rank": idx + 1,
                "relevance_score": self._calculate_relevance(item)
            }
            
            # Extract additional metadata from page
            product.update(self._extract_product_metadata(item))
            
            products.append(product)
        
        return products
    
    def _extract_image(self, item: Dict) -> Optional[str]:
        """Extract product image URL from search result"""
        # Try pagemap first
        if "pagemap" in item:
            if "cse_image" in item["pagemap"]:
                return item["pagemap"]["cse_image"][0].get("src")
            if "metatags" in item["pagemap"]:
                for metatag in item["pagemap"]["metatags"]:
                    if "og:image" in metatag:
                        return metatag["og:image"]
        return None
    
    def _extract_product_metadata(self, item: Dict) -> Dict[str, Any]:
        """Extract additional product metadata from search result"""
        metadata = {}
        
        if "pagemap" in item:
            # Extract price information
            if "offer" in item["pagemap"]:
                offer = item["pagemap"]["offer"][0]
                metadata["price"] = offer.get("price")
                metadata["currency"] = offer.get("pricecurrency", "USD")
                metadata["availability"] = offer.get("availability", "unknown")
            
            # Extract product information
            if "product" in item["pagemap"]:
                product_info = item["pagemap"]["product"][0]
                metadata["brand"] = product_info.get("brand")
                metadata["rating"] = product_info.get("ratingvalue")
                metadata["review_count"] = product_info.get("reviewcount")
            
            # Extract metatags
            if "metatags" in item["pagemap"]:
                metatag = item["pagemap"]["metatags"][0]
                if not metadata.get("brand"):
                    metadata["brand"] = metatag.get("og:brand") or metatag.get("product:brand")
        
        return metadata
    
    def _calculate_relevance(self, item: Dict) -> float:
        """Calculate relevance score for search result"""
        score = 0.5  # Base score
        
        # Boost score if it's from known skincare retailers
        known_retailers = ["sephora", "ulta", "dermstore", "lookfantastic", "cultbeauty", "beautylish"]
        domain = item.get("displayLink", "").lower()
        if any(retailer in domain for retailer in known_retailers):
            score += 0.3
        
        # Boost if has product structured data
        if "pagemap" in item and "product" in item["pagemap"]:
            score += 0.2
        
        return min(score, 1.0)
    
    def _build_filters_from_profile(self, user_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build search filters from user profile"""
        filters = {}
        
        if not user_profile:
            return filters
        
        # Add allergy exclusions
        if "allergies" in user_profile and user_profile["allergies"]:
            filters["ingredients_exclude"] = user_profile["allergies"]
        
        # Add skin type preferences
        if "skin_type" in user_profile:
            filters["skin_type"] = user_profile["skin_type"]
        
        # Add sensitivity considerations
        if user_profile.get("sensitivity_level") == "high":
            filters["ingredients_include"] = ["fragrance-free", "gentle", "hypoallergenic"]
        
        return filters
    
    def _deduplicate_and_rank(
        self,
        products_by_condition: Dict[str, List[Dict]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Deduplicate products and rank by relevance"""
        seen_urls = set()
        unique_products = []
        
        # Flatten all products
        for condition, products in products_by_condition.items():
            for product in products:
                url = product.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    product["conditions_matched"] = [condition]
                    unique_products.append(product)
                elif url in seen_urls:
                    # Find existing product and add condition
                    for existing in unique_products:
                        if existing.get("url") == url:
                            existing["conditions_matched"].append(condition)
                            break
        
        # Rank products
        for product in unique_products:
            score = product.get("relevance_score", 0.5)
            
            # Boost for matching multiple conditions
            score += len(product.get("conditions_matched", [])) * 0.1
            
            # Boost for having ratings
            if product.get("rating"):
                score += 0.1
            
            # Boost for having price info
            if product.get("price"):
                score += 0.05
            
            product["final_score"] = min(score, 1.0)
        
        # Sort by final score
        unique_products.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        return unique_products


# Global service instance
google_search_service = GoogleSearchService()

