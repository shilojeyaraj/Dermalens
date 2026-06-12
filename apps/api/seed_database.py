#!/usr/bin/env python3
"""
Cloud Run job to seed Elasticsearch database
This runs as a separate Cloud Run job after backend deployment
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    load_dotenv()
except Exception:
    print("⚠️  Could not read .env; proceeding with existing environment variables.")

# Import the seeding function
from seed_elasticsearch_data import generate_sample_products, seed_elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main function to seed the database"""
    try:
        logger.info("🌱 Starting Elasticsearch database seeding...")

        # Generate sample products
        logger.info("📦 Generating sample products...")
        products = generate_sample_products(1000)
        logger.info(f"✅ Generated {len(products)} products")

        # Seed Elasticsearch
        logger.info("💾 Seeding Elasticsearch database...")
        result = seed_elasticsearch(products)

        if result:
            logger.info("🎉 Database seeding completed successfully!")
            logger.info(f"📊 Seeded {len(products)} products to Elasticsearch")
        else:
            logger.error("❌ Database seeding failed!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error during database seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
