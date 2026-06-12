"""
Fivetran Connector for Skincare Product Data Pipeline
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import fivetran_sdk
import pandas as pd
import requests
from fivetran_sdk import Connector, ConnectorConfig, ConnectorState

logger = logging.getLogger(__name__)


class SkincareDataConnector(Connector):
    """
    Custom Fivetran connector for skincare product data
    Fetches data from multiple sources and loads into Google Cloud BigQuery
    """

    def __init__(self):
        super().__init__()
        self.connector_name = "skincare_products_connector"

        # Data sources
        self.data_sources = {
            "sephora": "https://www.sephora.com/api/catalog/products",
            "ulta": "https://www.ulta.com/api/v1/products",
            "dermstore": "https://www.dermstore.com/api/products",
            "skincare_ingredients_db": "https://api.skincaredb.com/ingredients",
            "product_reviews": "https://api.reviews.com/skincare",
        }

        # Google Cloud configuration
        self.gcp_project_id = "your-gcp-project-id"
        self.bigquery_dataset = "skincare_data"
        self.gcs_bucket = "skincare-data-bucket"

    def get_connector_config(self) -> ConnectorConfig:
        """Define the connector configuration"""
        return ConnectorConfig(
            name=self.connector_name,
            description="Skincare product data connector for AI-powered recommendations",
            version="1.0.0",
            supported_destinations=["bigquery", "cloud_sql", "cloud_storage"],
            supported_sync_modes=["incremental", "full_refresh"],
            schema_config={
                "products": {
                    "description": "Main skincare products table",
                    "columns": {
                        "id": "STRING",
                        "name": "STRING",
                        "brand": "STRING",
                        "description": "TEXT",
                        "ingredients": "TEXT",
                        "price": "FLOAT64",
                        "rating": "FLOAT64",
                        "review_count": "INT64",
                        "product_type": "STRING",
                        "skin_conditions": "ARRAY<STRING>",
                        "skin_types": "ARRAY<STRING>",
                        "url": "STRING",
                        "image_url": "STRING",
                        "allergen_free": "BOOLEAN",
                        "fragrance_free": "BOOLEAN",
                        "cruelty_free": "BOOLEAN",
                        "vegan": "BOOLEAN",
                        "spf_level": "INT64",
                        "created_at": "TIMESTAMP",
                        "updated_at": "TIMESTAMP",
                    },
                },
                "ingredients": {
                    "description": "Skincare ingredients database",
                    "columns": {
                        "ingredient_id": "STRING",
                        "name": "STRING",
                        "scientific_name": "STRING",
                        "category": "STRING",
                        "benefits": "ARRAY<STRING>",
                        "side_effects": "ARRAY<STRING>",
                        "concentration_range": "STRING",
                        "compatibility": "ARRAY<STRING>",
                        "safety_rating": "FLOAT64",
                        "created_at": "TIMESTAMP",
                    },
                },
                "reviews": {
                    "description": "Product reviews and ratings",
                    "columns": {
                        "review_id": "STRING",
                        "product_id": "STRING",
                        "user_id": "STRING",
                        "rating": "INT64",
                        "review_text": "TEXT",
                        "helpful_votes": "INT64",
                        "verified_purchase": "BOOLEAN",
                        "created_at": "TIMESTAMP",
                    },
                },
                "skin_conditions": {
                    "description": "Skin condition definitions and treatments",
                    "columns": {
                        "condition_id": "STRING",
                        "name": "STRING",
                        "description": "TEXT",
                        "severity_levels": "ARRAY<STRING>",
                        "common_causes": "ARRAY<STRING>",
                        "recommended_ingredients": "ARRAY<STRING>",
                        "avoid_ingredients": "ARRAY<STRING>",
                        "treatment_approaches": "ARRAY<STRING>",
                        "created_at": "TIMESTAMP",
                    },
                },
            },
        )

    def extract_data(self, state: ConnectorState) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data from various skincare data sources"""
        extracted_data = {"products": [], "ingredients": [], "reviews": [], "skin_conditions": []}

        try:
            # Extract products from multiple sources
            extracted_data["products"] = self._extract_products(state)

            # Extract ingredients data
            extracted_data["ingredients"] = self._extract_ingredients(state)

            # Extract reviews data
            extracted_data["reviews"] = self._extract_reviews(state)

            # Extract skin conditions data
            extracted_data["skin_conditions"] = self._extract_skin_conditions(state)

            logger.info(
                f"Extracted {sum(len(data) for data in extracted_data.values())} total records"
            )

        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise

        return extracted_data

    def _extract_products(self, state: ConnectorState) -> List[Dict[str, Any]]:
        """Extract product data from multiple sources"""
        products = []

        # Get last sync time for incremental updates
        last_sync = state.get("last_product_sync")
        if not last_sync:
            last_sync = datetime.now() - timedelta(days=30)  # Default to 30 days ago

        # Extract from Sephora API
        sephora_products = self._extract_from_sephora(last_sync)
        products.extend(sephora_products)

        # Extract from Ulta API
        ulta_products = self._extract_from_ulta(last_sync)
        products.extend(ulta_products)

        # Extract from Dermstore API
        dermstore_products = self._extract_from_dermstore(last_sync)
        products.extend(dermstore_products)

        # Deduplicate products
        products = self._deduplicate_products(products)

        return products

    def _extract_from_sephora(self, last_sync: datetime) -> List[Dict[str, Any]]:
        """Extract products from Sephora API"""
        products = []

        try:
            # This would be a real API call to Sephora
            # For demo purposes, we'll use mock data
            mock_products = [
                {
                    "id": "sephora_001",
                    "name": "CeraVe Foaming Facial Cleanser",
                    "brand": "CeraVe",
                    "description": "Gentle foaming cleanser for normal to oily skin",
                    "ingredients": "Ceramides, Hyaluronic Acid, Niacinamide",
                    "price": 16.99,
                    "rating": 4.5,
                    "review_count": 1250,
                    "product_type": "cleanser",
                    "skin_conditions": ["acne", "oily_skin"],
                    "skin_types": ["oily", "combination"],
                    "url": "https://www.sephora.com/product/cerave-foaming-facial-cleanser",
                    "image_url": "https://www.sephora.com/images/cerave-cleanser.jpg",
                    "allergen_free": True,
                    "fragrance_free": True,
                    "cruelty_free": False,
                    "vegan": False,
                    "spf_level": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ]

            products.extend(mock_products)
            logger.info(f"Extracted {len(mock_products)} products from Sephora")

        except Exception as e:
            logger.error(f"Error extracting from Sephora: {e}")

        return products

    def _extract_from_ulta(self, last_sync: datetime) -> List[Dict[str, Any]]:
        """Extract products from Ulta API"""
        products = []

        try:
            # Mock Ulta data
            mock_products = [
                {
                    "id": "ulta_001",
                    "name": "The Ordinary Niacinamide 10% + Zinc 1%",
                    "brand": "The Ordinary",
                    "description": "High-strength vitamin and mineral blemish formula",
                    "ingredients": "Niacinamide, Zinc PCA",
                    "price": 12.90,
                    "rating": 4.3,
                    "review_count": 890,
                    "product_type": "serum",
                    "skin_conditions": ["acne", "oily_skin", "blackheads"],
                    "skin_types": ["oily", "combination"],
                    "url": "https://www.ulta.com/product/ordinary-niacinamide",
                    "image_url": "https://www.ulta.com/images/ordinary-niacinamide.jpg",
                    "allergen_free": True,
                    "fragrance_free": True,
                    "cruelty_free": True,
                    "vegan": True,
                    "spf_level": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ]

            products.extend(mock_products)
            logger.info(f"Extracted {len(mock_products)} products from Ulta")

        except Exception as e:
            logger.error(f"Error extracting from Ulta: {e}")

        return products

    def _extract_from_dermstore(self, last_sync: datetime) -> List[Dict[str, Any]]:
        """Extract products from Dermstore API"""
        products = []

        try:
            # Mock Dermstore data
            mock_products = [
                {
                    "id": "dermstore_001",
                    "name": "Paula's Choice 2% BHA Liquid Exfoliant",
                    "brand": "Paula's Choice",
                    "description": "Gentle exfoliant for unclogging pores and smoothing skin",
                    "ingredients": "Salicylic Acid, Green Tea Extract",
                    "price": 32.00,
                    "rating": 4.7,
                    "review_count": 2100,
                    "product_type": "exfoliant",
                    "skin_conditions": ["acne", "blackheads", "large_pores"],
                    "skin_types": ["oily", "combination"],
                    "url": "https://www.dermstore.com/product/paulas-choice-bha",
                    "image_url": "https://www.dermstore.com/images/paulas-choice-bha.jpg",
                    "allergen_free": True,
                    "fragrance_free": True,
                    "cruelty_free": True,
                    "vegan": True,
                    "spf_level": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ]

            products.extend(mock_products)
            logger.info(f"Extracted {len(mock_products)} products from Dermstore")

        except Exception as e:
            logger.error(f"Error extracting from Dermstore: {e}")

        return products

    def _extract_ingredients(self, state: ConnectorState) -> List[Dict[str, Any]]:
        """Extract ingredients data from skincare ingredients database"""
        ingredients = []

        try:
            # Mock ingredients data
            mock_ingredients = [
                {
                    "ingredient_id": "ing_001",
                    "name": "Niacinamide",
                    "scientific_name": "Nicotinamide",
                    "category": "Vitamin B3",
                    "benefits": ["oil_control", "pore_minimizing", "skin_brightening"],
                    "side_effects": ["mild_irritation"],
                    "concentration_range": "2-10%",
                    "compatibility": ["hyaluronic_acid", "vitamin_c"],
                    "safety_rating": 4.8,
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "ingredient_id": "ing_002",
                    "name": "Salicylic Acid",
                    "scientific_name": "2-Hydroxybenzoic acid",
                    "category": "Beta Hydroxy Acid",
                    "benefits": ["acne_treatment", "exfoliation", "pore_clearing"],
                    "side_effects": ["dryness", "irritation"],
                    "concentration_range": "0.5-2%",
                    "compatibility": ["niacinamide", "retinol"],
                    "safety_rating": 4.2,
                    "created_at": datetime.now().isoformat(),
                },
            ]

            ingredients.extend(mock_ingredients)
            logger.info(f"Extracted {len(ingredients)} ingredients")

        except Exception as e:
            logger.error(f"Error extracting ingredients: {e}")

        return ingredients

    def _extract_reviews(self, state: ConnectorState) -> List[Dict[str, Any]]:
        """Extract product reviews data"""
        reviews = []

        try:
            # Mock reviews data
            mock_reviews = [
                {
                    "review_id": "rev_001",
                    "product_id": "sephora_001",
                    "user_id": "user_123",
                    "rating": 5,
                    "review_text": "This cleanser is amazing! My skin feels so clean and soft.",
                    "helpful_votes": 45,
                    "verified_purchase": True,
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "review_id": "rev_002",
                    "product_id": "ulta_001",
                    "user_id": "user_456",
                    "rating": 4,
                    "review_text": "Great serum, helps with my acne. Takes time to see results.",
                    "helpful_votes": 23,
                    "verified_purchase": True,
                    "created_at": datetime.now().isoformat(),
                },
            ]

            reviews.extend(mock_reviews)
            logger.info(f"Extracted {len(reviews)} reviews")

        except Exception as e:
            logger.error(f"Error extracting reviews: {e}")

        return reviews

    def _extract_skin_conditions(self, state: ConnectorState) -> List[Dict[str, Any]]:
        """Extract skin conditions data"""
        conditions = []

        try:
            # Mock skin conditions data
            mock_conditions = [
                {
                    "condition_id": "cond_001",
                    "name": "Acne",
                    "description": "Inflammatory skin condition characterized by pimples, blackheads, and whiteheads",
                    "severity_levels": ["mild", "moderate", "severe"],
                    "common_causes": [
                        "hormonal_changes",
                        "excess_oil",
                        "bacteria",
                        "clogged_pores",
                    ],
                    "recommended_ingredients": [
                        "salicylic_acid",
                        "benzoyl_peroxide",
                        "niacinamide",
                    ],
                    "avoid_ingredients": ["coconut_oil", "heavy_moisturizers"],
                    "treatment_approaches": ["gentle_cleansing", "exfoliation", "spot_treatment"],
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "condition_id": "cond_002",
                    "name": "Hyperpigmentation",
                    "description": "Dark spots caused by excess melanin production",
                    "severity_levels": ["mild", "moderate", "severe"],
                    "common_causes": ["sun_exposure", "hormonal_changes", "inflammation"],
                    "recommended_ingredients": ["vitamin_c", "azelaic_acid", "retinol"],
                    "avoid_ingredients": ["fragrance", "alcohol"],
                    "treatment_approaches": [
                        "sunscreen",
                        "brightening_serums",
                        "gentle_exfoliation",
                    ],
                    "created_at": datetime.now().isoformat(),
                },
            ]

            conditions.extend(mock_conditions)
            logger.info(f"Extracted {len(conditions)} skin conditions")

        except Exception as e:
            logger.error(f"Error extracting skin conditions: {e}")

        return conditions

    def _deduplicate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate products based on name and brand"""
        seen = set()
        unique_products = []

        for product in products:
            key = (product["name"].lower(), product["brand"].lower())
            if key not in seen:
                seen.add(key)
                unique_products.append(product)

        return unique_products

    def load_data(self, data: Dict[str, List[Dict[str, Any]]], destination: str) -> bool:
        """Load data to Google Cloud destination"""
        try:
            if destination == "bigquery":
                return self._load_to_bigquery(data)
            elif destination == "cloud_storage":
                return self._load_to_cloud_storage(data)
            elif destination == "cloud_sql":
                return self._load_to_cloud_sql(data)
            else:
                raise ValueError(f"Unsupported destination: {destination}")

        except Exception as e:
            logger.error(f"Error loading data to {destination}: {e}")
            return False

    def _load_to_bigquery(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Load data to Google Cloud BigQuery"""
        try:
            from google.cloud import bigquery

            client = bigquery.Client(project=self.gcp_project_id)

            for table_name, records in data.items():
                if not records:
                    continue

                # Create dataset if it doesn't exist
                dataset_id = f"{self.gcp_project_id}.{self.bigquery_dataset}"
                dataset = bigquery.Dataset(dataset_id)
                dataset.location = "US"
                dataset = client.create_dataset(dataset, exists_ok=True)

                # Create table
                table_id = f"{dataset_id}.{table_name}"
                table = bigquery.Table(table_id)
                table = client.create_table(table, exists_ok=True)

                # Load data
                errors = client.insert_rows_json(table, records)
                if errors:
                    logger.error(f"BigQuery insert errors: {errors}")
                    return False

                logger.info(f"Loaded {len(records)} records to {table_id}")

            return True

        except Exception as e:
            logger.error(f"Error loading to BigQuery: {e}")
            return False

    def _load_to_cloud_storage(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Load data to Google Cloud Storage"""
        try:
            from google.cloud import storage

            client = storage.Client(project=self.gcp_project_id)
            bucket = client.bucket(self.gcs_bucket)

            for table_name, records in data.items():
                if not records:
                    continue

                # Convert to JSON
                json_data = json.dumps(records, indent=2)

                # Upload to GCS
                blob_name = f"skincare_data/{table_name}/{datetime.now().strftime('%Y/%m/%d')}/{table_name}.json"
                blob = bucket.blob(blob_name)
                blob.upload_from_string(json_data, content_type="application/json")

                logger.info(
                    f"Uploaded {len(records)} records to gs://{self.gcs_bucket}/{blob_name}"
                )

            return True

        except Exception as e:
            logger.error(f"Error loading to Cloud Storage: {e}")
            return False

    def _load_to_cloud_sql(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Load data to Google Cloud SQL"""
        try:
            # This would implement Cloud SQL loading
            # For now, just log the action
            logger.info(
                f"Loading data to Cloud SQL: {sum(len(records) for records in data.values())} total records"
            )
            return True

        except Exception as e:
            logger.error(f"Error loading to Cloud SQL: {e}")
            return False


# Global connector instance
skincare_connector = SkincareDataConnector()
