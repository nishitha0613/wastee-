# Waste Classification ML Model Repository

This directory holds trained deep learning model artifacts for the **Smart AI Assistant for Waste Disposal Guidance**.

## Expected Model Artifact Specifications

Place your trained model weight file here, e.g.:
`backend/app/models_ml/waste_classifier.onnx`

### 1. Model Architecture
- **Backbone**: MobileNetV3 / EfficientNet-B0 / ResNet-50 fine-tuned on the TrashNet / TACO / Waste-Classification dataset.
- **Format**: ONNX (`.onnx`) or TorchScript (`.pt`).
- **Input Tensor**:
  - Name: `input` (or default first input)
  - Shape: `[1, 3, 224, 224]` (Batch Size: 1, Channels: 3, Height: 224, Width: 224)
  - Type: Float32
  - Normalization: Normalized to `[0.0, 1.0]` and standardized with ImageNet stats:
    - Mean: `[0.485, 0.456, 0.406]`
    - Std: `[0.229, 0.224, 0.225]`
- **Output Tensor**:
  - Name: `output`
  - Shape: `[1, 8]` (Logits or Softmax probabilities over 8 categories)

### 2. Supported Categories Index Mapping
```json
{
  "0": "Organic",
  "1": "Plastic",
  "2": "Paper",
  "3": "Glass",
  "4": "Metal",
  "5": "E-Waste",
  "6": "Hazardous",
  "7": "Other"
}
```

### 3. Integration Workflow
1. Export your trained model from PyTorch/TensorFlow to `waste_classifier.onnx`.
2. Save it in this directory: `backend/app/models_ml/waste_classifier.onnx`.
3. Set `AI_MODEL_PATH=app/models_ml/waste_classifier.onnx` in `.env`.
4. The classifier service automatically detects the file on startup, loads it once into memory, and performs high-speed inference without restarting or rewriting any API endpoints.
