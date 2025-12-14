# Elasticsearch Setup Guide for Dermalens

## **Option 1: Local Development (Recommended for Hackathon)**

### **1. Install Elasticsearch**
```bash
# Using Docker (Easiest)
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  elasticsearch:8.11.0

# Or using Homebrew (macOS)
brew install elasticsearch
brew services start elasticsearch

# Or download from elastic.co
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0
./bin/elasticsearch
```

### **2. Verify Installation**
```bash
curl -X GET "localhost:9200/"
# Should return: {"name":"...","cluster_name":"...","version":{...}}
```

### **3. Configure for Production (Google Cloud)**
```bash
# Install Elasticsearch on Google Cloud VM
sudo apt-get update
sudo apt-get install openjdk-11-jdk
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0

# Configure elasticsearch.yml
echo "network.host: 0.0.0.0" >> config/elasticsearch.yml
echo "discovery.type: single-node" >> config/elasticsearch.yml
echo "xpack.security.enabled: false" >> config/elasticsearch.yml

# Start Elasticsearch
./bin/elasticsearch
```

## **Option 2: Elastic Cloud (Production Ready)**

### **1. Sign up for Elastic Cloud**
- Go to https://cloud.elastic.co/
- Create free trial account
- Deploy cluster in Google Cloud region

### **2. Get Connection Details**
- Copy Cloud ID and API Key
- Update your `.env` file:
```env
ELASTICSEARCH_URL=https://your-cluster.es.region.gcp.cloud.es.io:9243
ELASTICSEARCH_API_KEY=your-api-key
```

## **3. Initialize Product Data**

### **Run the Data Seeding Script**
```python
# backend/seed_elasticsearch.py
from elasticsearch_service import elasticsearch_service
import json

# Sample product data
sample_products = [
    {
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
        "spf_level": None
    },
    # Add more products...
]

# Seed the data
elasticsearch_service.bulk_index_products(sample_products)
```

## **4. Test Elasticsearch Integration**

### **Test Search Functionality**
```python
# Test basic search
result = elasticsearch_service.search_products(
    query="acne cleanser",
    skin_conditions=["acne"],
    skin_types=["oily"],
    size=5
)
print(f"Found {result['total']} products")
```

## **5. Environment Variables**

Add to your `.env` file:
```env
# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_SSL_VERIFY=false
```

## **6. Production Considerations**

### **Security**
- Enable authentication in production
- Use HTTPS/TLS
- Set up proper firewall rules
- Regular security updates

### **Performance**
- Allocate sufficient memory (4GB+ recommended)
- Use SSD storage
- Configure proper sharding
- Monitor cluster health

### **Monitoring**
- Set up Elasticsearch monitoring
- Use Kibana for visualization
- Monitor query performance
- Set up alerts for failures
