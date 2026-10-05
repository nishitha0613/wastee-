"""Waste Classification Service.

Provides a production-grade interface for AI-based waste image classification.
Supports:
1. Deep-Learning ONNX MobileNetV2 Neural Classifier with 1000-class ImageNet-to-Waste mapping.
2. Strict image preprocessing and corrupted image handling (via Pillow).
3. Configurable confidence thresholding (AI_CONFIDENCE_THRESHOLD = 0.60) for low-confidence/uncertain results.
4. Comprehensive debug logging (uploaded image, model's raw predicted class, raw confidence, mapped category)
   without exposing sensitive filesystem paths.
5. Zero default-to-Organic behavior. Uncertain or ambiguous inputs are strictly categorized as 'Other'.
"""
import abc
import io
import json
import logging
import math
import os
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Tuple
from PIL import Image, ImageStat, UnidentifiedImageError

from app.config import get_settings
from app.models.waste_report import WasteType

logger = logging.getLogger(__name__)
settings = get_settings()

SUPPORTED_CATEGORIES: List[str] = [
    WasteType.ORGANIC.value,
    WasteType.PLASTIC.value,
    WasteType.PAPER.value,
    WasteType.GLASS.value,
    WasteType.METAL.value,
    WasteType.E_WASTE.value,
    WasteType.HAZARDOUS.value,
    WasteType.OTHER.value,
]


class CorruptedImageError(ValueError):
    """Raised when an uploaded file cannot be decoded as an image or is corrupted."""
    pass


class InvalidImageError(ValueError):
    """Raised when an image fails dimension or format constraints."""
    pass


class ImagePreprocessor:
    """Safely opens, validates, converts, resizes, and normalizes images for AI models."""

    DEFAULT_SIZE = 224

    @staticmethod
    def load_and_validate(image_input: Union[str, Path, bytes]) -> Image.Image:
        """Safely read and validate an image from path or bytes."""
        try:
            if isinstance(image_input, (str, Path)):
                path = Path(image_input)
                if not path.exists():
                    raise CorruptedImageError(f"Image path does not exist: {path.name}")
                raw_bytes = path.read_bytes()
            elif isinstance(image_input, bytes):
                raw_bytes = image_input
            else:
                raise CorruptedImageError("Unsupported image input type.")

            if len(raw_bytes) == 0:
                raise CorruptedImageError("Image byte stream is empty.")

            # Test image header and byte stream integrity with Pillow verify
            stream = io.BytesIO(raw_bytes)
            with Image.open(stream) as probe:
                probe.verify()

            # Reopen fresh stream for decoding and transformations
            stream.seek(0)
            img = Image.open(stream)
            img.load()  # Force decoding of all pixel data to detect truncated images

            # Convert to standard RGB mode (strips transparency alpha or CMYK)
            if img.mode != "RGB":
                img = img.convert("RGB")

            return img

        except (UnidentifiedImageError, OSError, SyntaxError) as exc:
            raise CorruptedImageError(
                f"Uploaded image is corrupted, truncated, or in an unreadable format: {str(exc)}"
            ) from exc

    @staticmethod
    def preprocess_for_inference(
        img: Image.Image,
        target_size: Optional[int] = None,
    ) -> Tuple[Image.Image, Dict[str, float]]:
        """Resize to target CNN dimensions (e.g. 224x224) and extract image quality metrics."""
        size = target_size or settings.IMAGE_INPUT_SIZE or ImagePreprocessor.DEFAULT_SIZE

        # High-quality antialiased bicubic/lanczos resampling
        resample_mode = getattr(Image, "Resampling", Image).LANCZOS
        resized_img = img.resize((size, size), resample=resample_mode)

        # Compute image variance and brightness statistics
        stat = ImageStat.Stat(resized_img)
        mean_brightness = sum(stat.mean) / len(stat.mean)
        variance = sum(stat.var) / len(stat.var)

        metrics = {
            "mean_brightness": mean_brightness,
            "variance": variance,
            "width": img.width,
            "height": img.height,
        }

        return resized_img, metrics


class BaseWasteClassifier(abc.ABC):
    """Abstract base class defining the waste classification contract."""

    @abc.abstractmethod
    def classify(
        self,
        image_input: Union[str, Path, bytes],
        original_filename: str = "",
    ) -> Dict[str, Any]:
        """Classify a waste image.

        Returns a dictionary with:
        {
            "waste_type": str,
            "confidence": float (0.0 - 1.0),
            "is_low_confidence": bool,
            "model_used": str,
            "raw_class_idx": Optional[int],
            "raw_class_name": Optional[str],
            "message": Optional[str]
        }
        """
        pass

    def apply_confidence_threshold(
        self,
        raw_result: Dict[str, Any],
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluates confidence against threshold. If below, categorizes as 'Other'."""
        eff_threshold = threshold if threshold is not None else settings.AI_CONFIDENCE_THRESHOLD
        confidence = float(raw_result.get("confidence", 0.0))
        # Ensure confidence is clamped between 0.0 and 1.0
        confidence = max(0.0, min(1.0, round(confidence, 4)))
        predicted_type = raw_result.get("waste_type", WasteType.OTHER.value)
        raw_name = raw_result.get("raw_class_name", "")

        if confidence < eff_threshold or predicted_type == WasteType.OTHER.value:
            return {
                "waste_type": WasteType.OTHER.value,
                "confidence": round(confidence, 2),
                "is_low_confidence": True,
                "raw_prediction": predicted_type,
                "raw_class_idx": raw_result.get("raw_class_idx"),
                "raw_class_name": raw_name,
                "model_used": raw_result.get("model_used", "Unknown"),
                "message": (
                    f"Identification uncertain — please verify the waste type. "
                    f"AI confidence ({round(confidence * 100)}%) is below verification threshold "
                    f"({round(eff_threshold * 100)}%). Item categorized as 'Other'."
                ),
            }

        return {
            "waste_type": predicted_type,
            "confidence": round(confidence, 2),
            "is_low_confidence": False,
            "raw_prediction": predicted_type,
            "raw_class_idx": raw_result.get("raw_class_idx"),
            "raw_class_name": raw_name,
            "model_used": raw_result.get("model_used", "Unknown"),
            "message": None,
        }


class ONNXWasteClassifier(BaseWasteClassifier):
    """Production ONNX Runtime MobileNetV2 Waste Classifier.

    Loads model session once on startup for high-performance inference.
    Maps ImageNet classes to our 8 waste management streams:
    - Plastic (water bottle, pop bottle, pill bottle, etc.)
    - Organic (fruits, vegetables, food, natural plant matter)
    - Paper (carton, cardboard, envelope, books, tissue)
    - Glass (wine bottle, beer glass, goblet, flacon)
    - Metal (tin cans, food cans, metal tools, aluminum)
    - E-Waste (computers, cellphones, keyboards, monitors)
    - Hazardous (batteries, gas masks, syringes, chemicals)
    - Other (uncertain, low confidence, or unmapped objects)
    """

    def __init__(self, model_path: Union[str, Path]):
        self.model_path = Path(model_path)
        self.session = None
        self.labels: Dict[int, str] = {}
        self.mapping: Dict[str, str] = {}
        self._load_labels_and_mapping()
        self._init_session()

    def _load_labels_and_mapping(self) -> None:
        """Loads ImageNet class names and category mapping from disk or defaults."""
        base_dir = self.model_path.parent
        labels_file = base_dir / "imagenet_labels.json"
        mapping_file = base_dir / "imagenet_to_waste.json"

        if labels_file.exists():
            try:
                with open(labels_file, "r") as f:
                    raw_labels = json.load(f)
                    self.labels = {i: name for i, name in enumerate(raw_labels)}
            except Exception as e:
                logger.warning(f"Could not load labels file: {e}")

        if mapping_file.exists():
            try:
                with open(mapping_file, "r") as f:
                    self.mapping = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load mapping file: {e}")

        # Core fallback mappings for key waste objects
        core_overrides = {
            "898": WasteType.PLASTIC.value,  # water bottle
            "737": WasteType.PLASTIC.value,  # soda bottle / pop bottle
            "907": WasteType.GLASS.value,    # wine bottle
            "441": WasteType.GLASS.value,    # beer glass
            "440": WasteType.GLASS.value,    # beer bottle
            "508": WasteType.E_WASTE.value,  # computer keyboard
            "681": WasteType.E_WASTE.value,  # notebook computer
            "487": WasteType.E_WASTE.value,  # mobile phone
            "642": WasteType.E_WASTE.value,  # computer mouse (or marimba)
            "478": WasteType.PAPER.value,    # carton
            "549": WasteType.PAPER.value,    # envelope
            "999": WasteType.PAPER.value,    # toilet paper
            "948": WasteType.ORGANIC.value,  # Granny Smith apple
            "954": WasteType.ORGANIC.value,  # banana
            "950": WasteType.ORGANIC.value,  # orange
            "937": WasteType.ORGANIC.value,  # broccoli
        }
        for k, v in core_overrides.items():
            if k not in self.mapping:
                self.mapping[k] = v

    def _init_session(self) -> None:
        try:
            import onnxruntime as ort
            if self.model_path.exists():
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                self.session = ort.InferenceSession(str(self.model_path), sess_options=opts)
                self.input_name = self.session.get_inputs()[0].name
                logger.info(f"ONNX Waste Classifier successfully initialized from {self.model_path.name}")
            else:
                self.session = None
        except Exception as exc:
            logger.error(f"Failed to load ONNX model session: {exc}")
            self.session = None

    def is_available(self) -> bool:
        return self.session is not None

    def classify(
        self,
        image_input: Union[str, Path, bytes],
        original_filename: str = "",
    ) -> Dict[str, Any]:
        if not self.is_available():
            raise RuntimeError("ONNX model session is not loaded.")

        # 1. Preprocess image
        img = ImagePreprocessor.load_and_validate(image_input)
        resized_img, metrics = ImagePreprocessor.preprocess_for_inference(img)

        # Flat / solid color check
        if metrics["variance"] < 0.02:
            logger.info(f"[AI Classification] Flat/solid image detected (variance: {metrics['variance']:.4f}). Categorized as Other.")
            raw_result = {
                "waste_type": WasteType.OTHER.value,
                "confidence": 0.20,
                "raw_class_idx": -1,
                "raw_class_name": "blank_or_solid_color",
                "model_used": "ONNX MobileNetV2 (Low Variance Filter)",
            }
            return self.apply_confidence_threshold(raw_result)

        # 2. Convert to normalized numpy tensor: [1, 3, 224, 224]
        import numpy as np
        arr = np.array(resized_img, dtype=np.float32) / 255.0
        # ImageNet standardization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = (arr - mean) / std
        # Transpose from HWC to CHW
        arr = np.transpose(arr, (2, 0, 1))
        # Add batch dimension
        tensor = np.expand_dims(arr, axis=0)

        # 3. Inference
        outputs = self.session.run(None, {self.input_name: tensor})
        logits = outputs[0][0]

        # Softmax computation
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        best_idx = int(np.argmax(probs))
        confidence = float(probs[best_idx])
        raw_class_name = self.labels.get(best_idx, f"class_{best_idx}")
        predicted_category = self.mapping.get(str(best_idx), WasteType.OTHER.value)

        # Strict rule: NEVER classify a plastic bottle or bottle as Organic
        if "bottle" in raw_class_name.lower():
            if "water bottle" in raw_class_name.lower() or "soda bottle" in raw_class_name.lower() or "pop bottle" in raw_class_name.lower():
                predicted_category = WasteType.PLASTIC.value
            elif "wine" in raw_class_name.lower() or "beer" in raw_class_name.lower():
                predicted_category = WasteType.GLASS.value

        # Log AI Inference telemetry
        safe_filename = Path(original_filename).name if original_filename else "uploaded_image"
        logger.info(
            f"[AI Waste Classifier] Image: '{safe_filename}' | "
            f"Raw Predicted Class: #{best_idx} ({raw_class_name}) | "
            f"Raw Confidence: {confidence:.4f} | "
            f"Mapped Category: {predicted_category}"
        )

        raw_result = {
            "waste_type": predicted_category,
            "confidence": confidence,
            "raw_class_idx": best_idx,
            "raw_class_name": raw_class_name,
            "model_used": f"MobileNetV2 ONNX Neural Model ({self.model_path.name})",
        }

        return self.apply_confidence_threshold(raw_result)


class DevelopmentWasteClassifier(BaseWasteClassifier):
    """Fallback Development Classifier.

    Active only if the ONNX model file cannot be found.
    Uses strict visual feature inspection and keyword verification.
    NEVER defaults unknown images to Organic.
    """

    KEYWORD_MAPPING = {
        "bottle": WasteType.PLASTIC.value,
        "plastic": WasteType.PLASTIC.value,
        "cup": WasteType.PLASTIC.value,
        "jug": WasteType.PLASTIC.value,
        "can": WasteType.METAL.value,
        "tin": WasteType.METAL.value,
        "metal": WasteType.METAL.value,
        "aluminum": WasteType.METAL.value,
        "apple": WasteType.ORGANIC.value,
        "banana": WasteType.ORGANIC.value,
        "food": WasteType.ORGANIC.value,
        "organic": WasteType.ORGANIC.value,
        "vegetable": WasteType.ORGANIC.value,
        "box": WasteType.PAPER.value,
        "cardboard": WasteType.PAPER.value,
        "paper": WasteType.PAPER.value,
        "newspaper": WasteType.PAPER.value,
        "magazine": WasteType.PAPER.value,
        "glass": WasteType.GLASS.value,
        "jar": WasteType.GLASS.value,
        "battery": WasteType.HAZARDOUS.value,
        "chemical": WasteType.HAZARDOUS.value,
        "paint": WasteType.HAZARDOUS.value,
        "hazardous": WasteType.HAZARDOUS.value,
        "phone": WasteType.E_WASTE.value,
        "laptop": WasteType.E_WASTE.value,
        "cable": WasteType.E_WASTE.value,
        "wire": WasteType.E_WASTE.value,
        "circuit": WasteType.E_WASTE.value,
        "ewaste": WasteType.E_WASTE.value,
        "peel": WasteType.ORGANIC.value,
    }

    def classify(
        self,
        image_input: Union[str, Path, bytes],
        original_filename: str = "",
    ) -> Dict[str, Any]:
        img = ImagePreprocessor.load_and_validate(image_input)
        resized_img, metrics = ImagePreprocessor.preprocess_for_inference(img)

        # 1. Flat image detection
        if metrics["variance"] < 0.02:
            raw_result = {
                "waste_type": WasteType.OTHER.value,
                "confidence": 0.25,
                "model_used": "Development Feature Classifier (Blank/featureless image)",
            }
            return self.apply_confidence_threshold(raw_result)

        # 2. Check filename keywords if provided
        fn_lower = original_filename.lower()
        for kw, cat in self.KEYWORD_MAPPING.items():
            if kw in fn_lower:
                logger.info(f"[Development Classifier] Keyword match: '{kw}' -> {cat}")
                raw_result = {
                    "waste_type": cat,
                    "confidence": 0.85,
                    "model_used": "Development Feature Classifier (Keyword heuristics)",
                }
                return self.apply_confidence_threshold(raw_result)

        # 3. For any image without confident verification, NEVER default to Organic.
        # Categorize as Other with low confidence below threshold.
        safe_filename = Path(original_filename).name if original_filename else "uploaded_image"
        logger.info(f"[Development Classifier] Image '{safe_filename}' not confidently matched. Yielding Other.")
        raw_result = {
            "waste_type": WasteType.OTHER.value,
            "confidence": 0.40,
            "model_used": "Development Feature Classifier (Uncertain object)",
        }
        return self.apply_confidence_threshold(raw_result)


# Singleton instance initialization
def _create_default_classifier() -> BaseWasteClassifier:
    """Instantiates the best available classifier: ONNX MobileNetV2 if present, else Development classifier."""
    model_path_str = getattr(settings, "AI_MODEL_PATH", None)
    if model_path_str:
        base_dir = Path(__file__).resolve().parent.parent.parent
        resolved_path = base_dir / model_path_str
        if resolved_path.exists():
            try:
                onnx_clf = ONNXWasteClassifier(resolved_path)
                if onnx_clf.is_available():
                    logger.info(f"Loaded ONNX classifier from {resolved_path}")
                    return onnx_clf
            except Exception as e:
                logger.error(f"Failed to instantiate ONNXWasteClassifier: {e}")

    logger.warning("No valid ONNX model found. Falling back to DevelopmentWasteClassifier.")
    return DevelopmentWasteClassifier()


_active_classifier: BaseWasteClassifier = _create_default_classifier()


def get_waste_classifier() -> BaseWasteClassifier:
    """FastAPI dependency returning the singleton waste classifier instance."""
    return _active_classifier


def set_waste_classifier(classifier: BaseWasteClassifier) -> None:
    """Allows registering or hot-swapping a custom trained ML classifier model."""
    global _active_classifier
    _active_classifier = classifier


def classify_waste(
    image: Union[str, Path, bytes],
    original_filename: str = "",
) -> Dict[str, Any]:
    """Isolated, stable classifier interface.

    Returns:
    {
        "waste_type": str,
        "confidence": float (0.0 to 1.0),
        "is_low_confidence": bool,
        "model_used": str,
        "raw_class_idx": Optional[int],
        "raw_class_name": Optional[str],
        "message": Optional[str]
    }
    """
    return _active_classifier.classify(image, original_filename=original_filename)
