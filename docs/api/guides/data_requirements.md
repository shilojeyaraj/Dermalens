# Data Requirements for Dermalens

## **Current Data Status**

### **✅ What We Have:**
1. **Training Data**: 1000+ skin condition images in `backend/training_data/`
2. **Mock Product Data**: Sample products in code
3. **User Profiles**: Supabase database schema
4. **Skin Conditions**: 12 condition types defined

### **❌ What We Need:**

## **1. Product Database (HIGH PRIORITY)**

### **Required Data Sources:**
- **Sephora API**: 10,000+ skincare products
- **Ulta API**: 8,000+ beauty products  
- **Dermstore API**: 5,000+ professional products
- **Amazon API**: 50,000+ product reviews
- **Beautylish API**: 3,000+ indie brands

### **Data Fields Needed:**
```json
{
  "product_id": "string",
  "name": "string",
  "brand": "string", 
  "description": "text",
  "ingredients": "text",
  "price": "float",
  "rating": "float",
  "review_count": "integer",
  "product_type": "string",
  "skin_conditions": ["array"],
  "skin_types": ["array"],
  "url": "string",
  "image_url": "string",
  "allergen_free": "boolean",
  "fragrance_free": "boolean",
  "cruelty_free": "boolean",
  "vegan": "boolean",
  "spf_level": "integer",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## **2. Ingredients Database (MEDIUM PRIORITY)**

### **Required Data:**
- **INCI Names**: 5,000+ cosmetic ingredients
- **Benefits**: What each ingredient does
- **Side Effects**: Potential reactions
- **Compatibility**: Which ingredients work together
- **Safety Ratings**: FDA/EWG safety scores
- **Concentration Ranges**: Effective dosages

### **Data Fields:**
```json
{
  "ingredient_id": "string",
  "name": "string",
  "scientific_name": "string",
  "category": "string",
  "benefits": ["array"],
  "side_effects": ["array"],
  "concentration_range": "string",
  "compatibility": ["array"],
  "safety_rating": "float",
  "created_at": "timestamp"
}
```

## **3. User Reviews & Ratings (MEDIUM PRIORITY)**

### **Required Data:**
- **Product Reviews**: 100,000+ user reviews
- **Rating Distribution**: 1-5 star ratings
- **Review Text**: Detailed feedback
- **User Demographics**: Age, skin type, concerns
- **Verified Purchases**: Authentic reviews only

## **4. Skin Condition Database (LOW PRIORITY)**

### **Required Data:**
- **Condition Definitions**: Medical descriptions
- **Severity Levels**: Mild, moderate, severe
- **Common Causes**: What triggers conditions
- **Treatment Approaches**: Recommended solutions
- **Prevention Tips**: How to avoid conditions

## **Data Acquisition Strategies**

### **1. Free APIs (Hackathon)**
```python
# Free APIs we can use
FREE_APIS = {
    "openfoodfacts": "https://world.openfoodfacts.org/api/v0/product/",
    "cosmetic_ingredients": "https://api.cosmetic-ingredients.com/",
    "skincare_reviews": "https://api.reviews.com/skincare"
}
```

### **2. Web Scraping (Legal)**
```python
# Scrape public product pages
SCRAPING_TARGETS = {
    "sephora": "https://www.sephora.com/shop/skincare",
    "ulta": "https://www.ulta.com/shop/skincare",
    "dermstore": "https://www.dermstore.com/skincare"
}
```

### **3. Mock Data Generation (Hackathon)**
```python
# Generate realistic mock data
MOCK_DATA_GENERATORS = {
    "products": "Generate 10,000+ realistic products",
    "reviews": "Generate 50,000+ user reviews", 
    "ingredients": "Generate 5,000+ ingredient profiles"
}
```

## **Immediate Action Plan**

### **Week 1: Basic Data Setup**
1. **Set up Elasticsearch** (2 hours)
2. **Create mock product database** (4 hours)
3. **Set up Fivetran connector** (3 hours)
4. **Test data pipeline** (2 hours)

### **Week 2: Data Enhancement**
1. **Add real product data** (8 hours)
2. **Implement web scraping** (6 hours)
3. **Add user reviews** (4 hours)
4. **Optimize search performance** (3 hours)

### **Week 3: Production Ready**
1. **Data validation** (4 hours)
2. **Performance optimization** (3 hours)
3. **Monitoring setup** (2 hours)
4. **Documentation** (2 hours)

## **Hackathon Demo Data**

### **Minimum Viable Dataset:**
- **Products**: 1,000+ skincare products
- **Ingredients**: 500+ common ingredients
- **Reviews**: 5,000+ user reviews
- **Conditions**: 12 skin conditions
- **Users**: 100+ test profiles

### **Demo Data Generator:**
```python
# backend/generate_demo_data.py
import random
import json
from datetime import datetime

def generate_demo_products(count=1000):
    """Generate realistic demo products"""
    brands = ["CeraVe", "The Ordinary", "Paula's Choice", "Neutrogena", "Olay"]
    types = ["cleanser", "serum", "moisturizer", "sunscreen", "exfoliant"]
    conditions = ["acne", "dry_skin", "oily_skin", "hyperpigmentation", "aging"]
    
    products = []
    for i in range(count):
        product = {
            "id": f"demo_{i:04d}",
            "name": f"Demo Product {i+1}",
            "brand": random.choice(brands),
            "product_type": random.choice(types),
            "price": round(random.uniform(5.99, 89.99), 2),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "review_count": random.randint(10, 5000),
            "skin_conditions": random.sample(conditions, random.randint(1, 3)),
            "skin_types": random.sample(["dry", "oily", "combination", "sensitive"], random.randint(1, 2)),
            "created_at": datetime.now().isoformat()
        }
        products.append(product)
    
    return products

# Generate and save demo data
demo_products = generate_demo_products(1000)
with open('demo_products.json', 'w') as f:
    json.dump(demo_products, f, indent=2)
```

## **Cost Estimation**

### **Free Tier (Hackathon):**
- **Elasticsearch**: Free (local) or $16/month (cloud)
- **Fivetran**: Free trial (14 days)
- **Google Cloud**: $300 free credits
- **Total**: $0-50/month

### **Production Scale:**
- **Elasticsearch**: $100-500/month
- **Fivetran**: $200-1000/month
- **Google Cloud**: $500-2000/month
- **Total**: $800-3500/month

## **Next Steps**

1. **Set up Elasticsearch** (follow setup guide)
2. **Create Fivetran account** (follow setup guide)
3. **Generate demo data** (run data generator)
4. **Test integration** (run test scripts)
5. **Deploy to production** (Google Cloud)
