class VoiceAnalysisResult {
  const VoiceAnalysisResult({
    required this.productId,
    required this.product,
    required this.voice,
    required this.missingFields,
    required this.fieldConfidence,
  });

  factory VoiceAnalysisResult.fromJson(Map<String, dynamic> json) {
    if (json['product_id'] is! String ||
        json['product'] is! Map<String, dynamic> ||
        json['voice'] is! Map<String, dynamic> ||
        json['missing_fields'] is! List ||
        json['field_confidence'] is! Map<String, dynamic>) {
      throw const FormatException('The voice analysis response is invalid.');
    }

    return VoiceAnalysisResult(
      productId: json['product_id'] as String,
      product: VoiceProductInfo.fromJson(
        json['product'] as Map<String, dynamic>,
      ),
      voice: VoiceMetadata.fromJson(json['voice'] as Map<String, dynamic>),
      missingFields: (json['missing_fields'] as List).cast<String>(),
      fieldConfidence: (json['field_confidence'] as Map<String, dynamic>).map(
        (key, value) => MapEntry(key, _number(value)),
      ),
    );
  }

  final String productId;
  final VoiceProductInfo product;
  final VoiceMetadata voice;
  final List<String> missingFields;
  final Map<String, double> fieldConfidence;
}

class VoiceMetadata {
  const VoiceMetadata({
    required this.languageCode,
    required this.originalTranscript,
    required this.translatedTranscript,
    required this.confidence,
  });

  factory VoiceMetadata.fromJson(Map<String, dynamic> json) {
    return VoiceMetadata(
      languageCode: json['language_code'] as String?,
      originalTranscript: json['original_transcript'] as String?,
      translatedTranscript: json['translated_transcript'] as String?,
      confidence: _number(json['confidence']),
    );
  }

  final String? languageCode;
  final String? originalTranscript;
  final String? translatedTranscript;
  final double confidence;
}

class VoiceProductInfo {
  const VoiceProductInfo({
    this.name,
    this.category,
    this.subcategory,
    this.material,
    this.color,
    this.craftType,
    this.description,
    required this.dimensions,
    required this.weight,
    this.usage,
    this.pattern,
    required this.specialFeatures,
    this.productionTime,
  });

  factory VoiceProductInfo.fromJson(Map<String, dynamic> json) {
    final dimensions = json['dimensions'];
    final weight = json['weight'];
    return VoiceProductInfo(
      name: json['name'] as String?,
      category: json['category'] as String?,
      subcategory: json['subcategory'] as String?,
      material: json['material'] as String?,
      color: json['color'] as String?,
      craftType: json['craft_type'] as String?,
      description: json['description'] as String?,
      dimensions: dimensions is Map<String, dynamic>
          ? VoiceDimensions.fromJson(dimensions)
          : const VoiceDimensions(),
      weight: weight is Map<String, dynamic>
          ? VoiceWeight.fromJson(weight)
          : const VoiceWeight(),
      usage: json['usage'] as String?,
      pattern: json['pattern'] as String?,
      specialFeatures: json['special_features'] is List
          ? (json['special_features'] as List).cast<String>()
          : const [],
      productionTime: json['production_time'] as String?,
    );
  }

  final String? name;
  final String? category;
  final String? subcategory;
  final String? material;
  final String? color;
  final String? craftType;
  final String? description;
  final VoiceDimensions dimensions;
  final VoiceWeight weight;
  final String? usage;
  final String? pattern;
  final List<String> specialFeatures;
  final String? productionTime;
}

class VoiceDimensions {
  const VoiceDimensions({this.length, this.width, this.height, this.unit});

  factory VoiceDimensions.fromJson(Map<String, dynamic> json) {
    return VoiceDimensions(
      length: _nullableNumber(json['length']),
      width: _nullableNumber(json['width']),
      height: _nullableNumber(json['height']),
      unit: json['unit'] as String?,
    );
  }

  final double? length;
  final double? width;
  final double? height;
  final String? unit;
}

class VoiceWeight {
  const VoiceWeight({this.value, this.unit});

  factory VoiceWeight.fromJson(Map<String, dynamic> json) {
    return VoiceWeight(
      value: _nullableNumber(json['value']),
      unit: json['unit'] as String?,
    );
  }

  final double? value;
  final String? unit;
}

double _number(dynamic value) {
  if (value is num) return value.toDouble();
  throw const FormatException('A numeric voice value is invalid.');
}

double? _nullableNumber(dynamic value) => value == null ? null : _number(value);
