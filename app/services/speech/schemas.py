"""Data models and schemas for Voice & Language Intelligence module."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any


@dataclass
class ProductDimensions:
    """Dimensions with unit of measurement."""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class ProductWeight:
    """Weight with unit of measurement."""
    value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class VoiceMetadata:
    """Voice input metadata and processing results."""
    language_code: Optional[str] = None
    original_transcript: Optional[str] = None
    translated_transcript: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ProductInfo:
    """Extracted product information from voice input."""
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    craft_type: Optional[str] = None
    description: Optional[str] = None
    dimensions: ProductDimensions = field(default_factory=ProductDimensions)
    weight: ProductWeight = field(default_factory=ProductWeight)
    usage: Optional[str] = None
    pattern: Optional[str] = None
    special_features: List[str] = field(default_factory=list)
    production_time: Optional[str] = None


@dataclass
class VoiceProcessingResult:
    """Complete voice processing pipeline result."""
    product_id: str
    product: ProductInfo
    voice: VoiceMetadata
    missing_fields: List[str] = field(default_factory=list)
    field_confidence: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format matching schema."""
        return {
            "product_id": self.product_id,
            "product": asdict(self.product),
            "voice": asdict(self.voice),
            "missing_fields": self.missing_fields,
            "field_confidence": self.field_confidence,
        }
