# Fivetran Setup Guide for Dermalens

## **1. Create Fivetran Account**

### **Sign Up Process**
1. Go to https://fivetran.com/
2. Sign up for free trial (14 days)
3. Verify email and complete onboarding
4. Choose "Build Custom Connector" option

### **Get API Credentials**
1. Go to Settings → API Keys
2. Create new API key
3. Copy API Key and API Secret
4. Add to your `.env` file:
```env
FIVETRAN_API_KEY=your-api-key
FIVETRAN_API_SECRET=your-api-secret
```

## **2. Set Up Google Cloud Integration**

### **Create Google Cloud Project**
```bash
# Create new project
gcloud projects create dermalens-hackathon --name="Dermalens Hackathon"

# Set as default project
gcloud config set project dermalens-hackathon

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### **Create Service Account**
```bash
# Create service account
gcloud iam service-accounts create dermalens-connector \
    --display-name="Dermalens Fivetran Connector"

# Grant necessary permissions
gcloud projects add-iam-policy-binding dermalens-hackathon \
    --member="serviceAccount:dermalens-connector@dermalens-hackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding dermalens-hackathon \
    --member="serviceAccount:dermalens-connector@dermalens-hackathon.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create fivetran-key.json \
    --iam-account=dermalens-connector@dermalens-hackathon.iam.gserviceaccount.com
```

## **3. Deploy Custom Connector**

### **Install Fivetran SDK**
```bash
pip install fivetran-sdk
```

### **Deploy Connector**
```python
# backend/deploy_fivetran_connector.py
from fivetran_connector import skincare_connector
import os

# Set up credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'fivetran-key.json'
os.environ['GCP_PROJECT_ID'] = 'dermalens-hackathon'

# Deploy connector
connector_id = skincare_connector.deploy()
print(f"Connector deployed with ID: {connector_id}")
```

## **4. Configure Data Sources**

### **Set Up Mock Data Sources**
Since real APIs require authentication, we'll create mock data sources:

```python
# backend/mock_data_sources.py
import requests
import json
from datetime import datetime

class MockDataSources:
    """Mock data sources for hackathon demo"""
    
    @staticmethod
    def get_sephora_products():
        """Mock Sephora API response"""
        return [
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
                "updated_at": datetime.now().isoformat()
            },
            # Add more products...
        ]
    
    @staticmethod
    def get_ulta_products():
        """Mock Ulta API response"""
        return [
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
                "updated_at": datetime.now().isoformat()
            },
            # Add more products...
        ]
    
    @staticmethod
    def get_dermstore_products():
        """Mock Dermstore API response"""
        return [
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
                "updated_at": datetime.now().isoformat()
            },
            # Add more products...
        ]
```

## **5. Test Fivetran Integration**

### **Run Test Sync**
```python
# backend/test_fivetran.py
from fivetran_connector import skincare_connector
from mock_data_sources import MockDataSources

# Test data extraction
data = skincare_connector.extract_data({})
print(f"Extracted {sum(len(records) for records in data.values())} records")

# Test data loading
success = skincare_connector.load_data(data, "bigquery")
print(f"Data loading successful: {success}")
```

## **6. Environment Variables**

Add to your `.env` file:
```env
# Fivetran Configuration
FIVETRAN_API_KEY=your-api-key
FIVETRAN_API_SECRET=your-api-secret

# Google Cloud Configuration
GCP_PROJECT_ID=dermalens-hackathon
GOOGLE_APPLICATION_CREDENTIALS=./fivetran-key.json
BIGQUERY_DATASET=skincare_data
GCS_BUCKET=skincare-data-bucket
```

## **7. Production Considerations**

### **Real Data Sources**
For production, you'll need:
- API keys for Sephora, Ulta, Dermstore
- Rate limiting and error handling
- Data validation and cleaning
- Incremental sync strategies

### **Monitoring**
- Set up Fivetran monitoring
- Monitor sync status and errors
- Set up alerts for failures
- Track data quality metrics

### **Security**
- Use secure credential storage
- Implement proper access controls
- Regular security audits
- Data encryption in transit and at rest
