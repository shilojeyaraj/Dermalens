#!/usr/bin/env python3
"""
Data seeding script for Elasticsearch
Populates the skincare products index with sample data
"""
import os
import sys
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables with tolerant encoding
try:
    load_dotenv()
except UnicodeDecodeError:
    try:
        load_dotenv(encoding="utf-16")
    except Exception:
        print("⚠️  Could not read .env with UTF-8/UTF-16; proceeding with existing environment variables.")

def _generate_realistic_url(brand, product_name, index):
    """Generate realistic product URLs based on brand and product"""
    # Clean brand name for URL
    brand_clean = brand.lower().replace("'", "").replace(" ", "-").replace("+", "plus")
    
    # Clean product name for URL
    product_clean = product_name.lower().replace(" ", "-").replace("'", "").replace("+", "plus")
    
    # Brand-specific URL patterns
    brand_urls = {
        "cerave": "https://www.cerave.com/products/",
        "the-ordinary": "https://theordinary.com/products/",
        "paulas-choice": "https://www.paulaschoice.com/products/",
        "neutrogena": "https://www.neutrogena.com/products/",
        "olay": "https://www.olay.com/products/",
        "la-roche-posay": "https://www.laroche-posay.us/products/",
        "avene": "https://www.aveneusa.com/products/",
        "vichy": "https://www.vichyusa.com/products/",
        "clinique": "https://www.clinique.com/products/",
        "estee-lauder": "https://www.esteelauder.com/products/",
        "lancome": "https://www.lancome-usa.com/products/",
        "dior": "https://www.dior.com/en_us/products/",
        "chanel": "https://www.chanel.com/us/products/",
        "sk-ii": "https://www.sk-ii.com/products/",
        "drunk-elephant": "https://www.drunkelephant.com/products/",
        "glossier": "https://www.glossier.com/products/",
        "fenty-beauty": "https://www.fentybeauty.com/products/",
        "rare-beauty": "https://www.rarebeauty.com/products/",
        "tatcha": "https://www.tatcha.com/products/",
        "dr-jart": "https://www.drjart.com/products/",
        "eltamd": "https://www.eltamd.com/products/",
        "kiehls": "https://www.kiehls.com/products/",
        "fresh": "https://www.fresh.com/products/",
        "origins": "https://www.origins.com/products/",
        "mac": "https://www.maccosmetics.com/products/",
        "nars": "https://www.narscosmetics.com/products/",
        "urban-decay": "https://www.urbandecay.com/products/",
        "too-faced": "https://www.toofaced.com/products/",
        "benefit": "https://www.benefitcosmetics.com/products/",
        "tarte": "https://www.tartecosmetics.com/products/",
        "it-cosmetics": "https://www.itcosmetics.com/products/",
        "bareminerals": "https://www.bareminerals.com/products/",
        "philosophy": "https://www.philosophy.com/products/",
        "murad": "https://www.murad.com/products/",
        "perricone-md": "https://www.perriconemd.com/products/",
        "sunday-riley": "https://www.sundayriley.com/products/",
        "herbivore": "https://www.herbivorebotanicals.com/products/",
        "biossance": "https://www.biossance.com/products/",
        "youth-to-the-people": "https://www.youthtothepeople.com/products/",
        "glow-recipe": "https://www.glowrecipe.com/products/",
        "krave-beauty": "https://www.kravebeauty.com/products/",
        "versed": "https://www.versed.com/products/",
        "the-inkey-list": "https://www.theinkeylist.com/products/",
        "good-molecules": "https://www.goodmolecules.com/products/",
        "the-chemistry-brand": "https://www.thechemistrybrand.com/products/",
        "first-aid-beauty": "https://www.firstaidbeauty.com/products/",
        "mario-badescu": "https://www.mariobadescu.com/products/",
        "kate-somerville": "https://www.katesomerville.com/products/",
        "ole-henriksen": "https://www.olehenriksen.com/products/"
    }
    
    # Get base URL for brand, fallback to generic
    base_url = brand_urls.get(brand_clean, "https://www.sephora.com/products/")
    
    # Create realistic product URL with specific product path
    # Add product-specific identifiers
    product_id = f"{index:04d}"
    product_slug = f"{product_clean}-{product_id}"
    
    # For some brands, add more specific paths
    if brand_clean in ["the-ordinary", "paulas-choice", "drunk-elephant"]:
        return f"{base_url}{product_slug}"
    elif brand_clean in ["cerave", "neutrogena", "olay"]:
        return f"{base_url}{product_slug}"
    else:
        # For other brands, create more specific product URLs
        return f"{base_url}{product_slug}"

def generate_sample_products(count=1000):
    """Generate realistic sample skincare products"""
    
    brands = [
        "CeraVe", "The Ordinary", "Paula's Choice", "Neutrogena", "Olay",
        "La Roche-Posay", "Avene", "Vichy", "Clinique", "Estée Lauder",
        "Lancôme", "Dior", "Chanel", "SK-II", "Drunk Elephant",
        "Glossier", "Fenty Beauty", "Rare Beauty", "Tatcha", "Dr. Jart+",
        "EltaMD", "Kiehl's", "Fresh", "Origins", "MAC", "NARS", "Urban Decay",
        "Too Faced", "Benefit", "Tarte", "IT Cosmetics", "BareMinerals",
        "Philosophy", "Murad", "Perricone MD", "Sunday Riley", "Herbivore",
        "Biossance", "Youth to the People", "Glow Recipe", "Krave Beauty",
        "Versed", "The Inkey List", "Good Molecules", "The Chemistry Brand",
        "First Aid Beauty", "Mario Badescu", "Kate Somerville", "Ole Henriksen"
    ]
    
    product_types = [
        "cleanser", "serum", "moisturizer", "sunscreen", "exfoliant",
        "toner", "essence", "mask", "oil", "treatment"
    ]
    
    skin_conditions = [
        "acne", "hyperpigmentation", "dark_spots", "wrinkles", "dry_skin",
        "oily_skin", "sensitive_skin", "normal_skin", "blackheads", "whiteheads",
        "rosacea", "eczema", "large_pores", "uneven_texture", "dull_skin"
    ]
    
    skin_types = ["dry", "oily", "combination", "normal", "sensitive"]
    
    ingredients = [
        "Niacinamide", "Hyaluronic Acid", "Salicylic Acid", "Retinol",
        "Vitamin C", "Ceramides", "Peptides", "AHA", "BHA", "Squalane",
        "Glycerin", "Aloe Vera", "Green Tea Extract", "Tea Tree Oil",
        "Jojoba Oil", "Argan Oil", "Rosehip Oil", "Snail Mucin",
        "Collagen", "Elastin", "Coenzyme Q10", "Alpha Arbutin"
    ]
    
    products = []
    
    for i in range(count):
        brand = random.choice(brands)
        product_type = random.choice(product_types)
        
        # Generate realistic product name
        if product_type == "cleanser":
            name_suffixes = ["Cleanser", "Facial Wash", "Gel Cleanser", "Foaming Cleanser"]
        elif product_type == "serum":
            name_suffixes = ["Serum", "Treatment", "Ampoule", "Concentrate"]
        elif product_type == "moisturizer":
            name_suffixes = ["Moisturizer", "Cream", "Lotion", "Gel"]
        elif product_type == "sunscreen":
            name_suffixes = ["Sunscreen", "SPF", "Sun Protection", "UV Defense"]
        else:
            name_suffixes = [product_type.title(), "Treatment", "Care"]
        
        name = f"{brand} {random.choice(name_suffixes)}"
        
        # Generate realistic price
        if brand in ["Chanel", "Dior", "Lancôme", "Estée Lauder", "SK-II"]:
            price = round(random.uniform(50, 150), 2)
        elif brand in ["Drunk Elephant", "Tatcha", "Dr. Jart+", "Glossier", "Sunday Riley", "Perricone MD"]:
            price = round(random.uniform(25, 120), 2)
        elif brand in ["The Ordinary", "The Inkey List", "Good Molecules", "Versed"]:
            price = round(random.uniform(5, 25), 2)
        else:
            price = round(random.uniform(8, 80), 2)
        
        # Generate rating and review count
        rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(10, 5000)
        
        # Generate skin conditions (1-4 per product)
        num_conditions = random.randint(1, 4)
        product_conditions = random.sample(skin_conditions, num_conditions)
        
        # Generate skin types (1-3 per product)
        num_types = random.randint(1, 3)
        product_skin_types = random.sample(skin_types, num_types)
        
        # Generate ingredients (3-8 per product)
        num_ingredients = random.randint(3, 8)
        product_ingredients = random.sample(ingredients, num_ingredients)
        
        # Generate boolean properties
        allergen_free = random.choice([True, False])
        fragrance_free = random.choice([True, False])
        cruelty_free = random.choice([True, False])
        vegan = random.choice([True, False])
        
        # Generate SPF level (only for sunscreens)
        spf_level = None
        if product_type == "sunscreen":
            spf_level = random.choice([15, 30, 50, 60])
        
        product = {
            "id": f"product_{i:04d}",
            "name": name,
            "brand": brand,
            "description": f"Professional {product_type} for {', '.join(product_skin_types)} skin. Targets {', '.join(product_conditions[:2])}.",
            "ingredients": ", ".join(product_ingredients),
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "product_type": product_type,
            "skin_conditions": product_conditions,
            "skin_types": product_skin_types,
            "url": _generate_realistic_url(brand, name, i),
            "image_url": f"https://picsum.photos/seed/skincare-{i}/600/600",
            "allergen_free": allergen_free,
            "fragrance_free": fragrance_free,
            "cruelty_free": cruelty_free,
            "vegan": vegan,
            "spf_level": spf_level,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        products.append(product)
    
    return products

def seed_elasticsearch():
    """Seed Elasticsearch with sample data"""
    try:
        # Ensure we can import the shared Elasticsearch service from project root
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from apps.api.infrastructure.elasticsearch_service import elasticsearch_service
        
        print("🌱 Seeding Elasticsearch with sample data...")
        
        # Generate sample products
        print("📦 Generating sample products...")
        products = generate_sample_products(1000)
        print(f"✅ Generated {len(products)} products")
        
        # Index products in batches
        batch_size = 100
        total_indexed = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            try:
                result = elasticsearch_service.bulk_index_products(batch)
                total_indexed += len(batch)
                print(f"📤 Indexed batch {i//batch_size + 1}/{(len(products)-1)//batch_size + 1} ({len(batch)} products)")
                
            except Exception as e:
                print(f"❌ Error indexing batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"🎉 Successfully indexed {total_indexed} products!")
        
        # Test search functionality
        print("\n🧪 Testing search functionality...")
        test_result = elasticsearch_service.search_products(
            query="acne cleanser",
            skin_conditions=["acne"],
            skin_types=["oily"],
            size=5
        )
        
        if test_result["success"]:
            print(f"✅ Search test successful! Found {len(test_result['products'])} products")
            for product in test_result["products"][:3]:
                print(f"  - {product['name']} by {product['brand']} (${product['price']})")
        else:
            print(f"❌ Search test failed: {test_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding Elasticsearch: {e}")
        return False

def main():
    """Main function"""
    print("🔬 Dermalens Elasticsearch Data Seeder")
    print("=" * 50)
    
    # Check if Elasticsearch is running
    try:
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from apps.api.infrastructure.elasticsearch_service import elasticsearch_service
        elasticsearch_service.es.ping()
        print("✅ Elasticsearch connection successful")
    except Exception as e:
        print(f"❌ Cannot connect to Elasticsearch: {e}")
        print("💡 Make sure Elasticsearch is running:")
        print("   docker run -d -p 9200:9200 elasticsearch:8.11.0")
        return
    
    # Seed data
    success = seed_elasticsearch()
    
    if success:
        print("\n🎉 Data seeding completed successfully!")
        print("🚀 Your Elasticsearch is ready for production!")
    else:
        print("\n❌ Data seeding failed!")
        print("🔧 Check your Elasticsearch configuration and try again")

if __name__ == "__main__":
    main()
