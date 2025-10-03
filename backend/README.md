# Dermalens Skin Analysis Backend

A Python backend service that uses OpenCV and PyTorch to analyze skin conditions from uploaded images/videos and recommend skincare products.

## Features

- **Face Detection**: Uses OpenCV's Haar Cascade to detect faces in images and videos
- **Skin Condition Classification**: PyTorch-based CNN to classify various skin conditions:
  - Acne, blackheads, whiteheads
  - Hyperpigmentation, dark spots
  - Wrinkles, aging signs
  - Dry skin, oily skin, sensitive skin
  - Rosacea, eczema
- **Product Recommendations**: Mock Google Store API integration for skincare product suggestions
- **Routine Generation**: Automatically generates personalized morning and evening skincare routines
- **REST API**: FastAPI-based API for easy frontend integration

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- At least 4GB RAM (8GB+ recommended for training)

### Installation

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Test the setup**:
   ```bash
   python test_setup.py
   ```

### Training Data Structure

Organize your training images in the following structure:

```
training_data/
├── acne/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── hyperpigmentation/
│   ├── image1.jpg
│   └── ...
├── dry_skin/
│   └── ...
└── ... (other skin conditions)
```

**Supported image formats**: PNG, JPG, JPEG

## Usage

### Training the Model

1. **Add training images** to the appropriate folders in `training_data/`
2. **Run training**:
   ```bash
   python train_model.py
   ```

The training script will:
- Load and preprocess your images
- Split data into training/validation sets
- Train the CNN model with data augmentation
- Save the best model to `models/skin_classifier.pth`
- Generate training curves and confusion matrix

### Running the API Server

1. **Start the server**:
   ```bash
   python main.py
   ```

2. **API will be available at**: `http://localhost:8000`

3. **API Documentation**: `http://localhost:8000/docs` (Swagger UI)

### API Endpoints

#### `POST /analyze-skin`
Analyze skin conditions from uploaded image or video.

**Request**: Multipart form data with image/video file
**Response**:
```json
{
  "analysis_results": [...],
  "detected_conditions": ["acne", "hyperpigmentation"],
  "recommended_products": [...],
  "skincare_routine": {...},
  "analysis_timestamp": "2024-01-01T12:00:00"
}
```

#### `POST /search-products`
Search for products based on skin conditions.

**Request**: JSON with conditions list
**Response**: List of recommended products

#### `POST /generate-routine`
Generate personalized skincare routine.

**Request**: JSON with conditions and products
**Response**: Morning and evening routine with instructions

## Model Architecture

The skin condition classifier uses a custom CNN architecture:

```
Input (3, 224, 224) RGB image
├── Conv2d(3→32) + ReLU + MaxPool2d
├── Conv2d(32→64) + ReLU + MaxPool2d  
├── Conv2d(64→128) + ReLU + MaxPool2d
├── Conv2d(128→256) + ReLU + AdaptiveAvgPool2d
└── Classifier: Linear(256*4*4→512) + ReLU + Dropout + Linear(512→12)
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# Google Store API (optional)
GOOGLE_STORE_API_KEY=your_api_key_here

# Model settings
MODEL_PATH=models/skin_classifier.pth
CONFIDENCE_THRESHOLD=0.3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS settings
ALLOWED_ORIGINS=http://localhost:3000
```

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application
├── train_model.py         # Model training script
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── models/              # Trained models
├── training_data/       # Training images
├── temp_uploads/        # Temporary file storage
└── logs/               # Log files
```

### Adding New Skin Conditions

1. Add the condition to `SKIN_CONDITIONS` list in `main.py`
2. Create a folder in `training_data/` with the condition name
3. Add training images to the folder
4. Retrain the model with `python train_model.py`

### Customizing Product Recommendations

Edit the `product_database` dictionary in the `search_products()` function in `main.py` to add your own product recommendations.

## Troubleshooting

### Common Issues

1. **"No faces detected"**: Ensure the uploaded image/video contains clear, well-lit faces
2. **"No training data found"**: Check that images are in the correct folder structure
3. **CUDA out of memory**: Reduce batch size in `train_model.py` or use CPU-only training
4. **Import errors**: Run `pip install -r requirements.txt` to install dependencies

### Performance Tips

- Use GPU for training if available (CUDA-compatible GPU)
- Increase batch size for faster training (if you have enough RAM)
- Use data augmentation to improve model generalization
- Collect more diverse training data for better accuracy

## License

This project is part of the Dermalens skincare analysis application.
