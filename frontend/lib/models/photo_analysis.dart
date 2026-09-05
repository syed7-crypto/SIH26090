class PhotoAnalysisResult {
  const PhotoAnalysisResult({required this.productId, required this.media});

  factory PhotoAnalysisResult.fromJson(Map<String, dynamic> json) {
    final mediaJson = json['media'];
    if (json['product_id'] is! String || mediaJson is! Map<String, dynamic>) {
      throw const FormatException('The photo analysis response is invalid.');
    }

    return PhotoAnalysisResult(
      productId: json['product_id'] as String,
      media: PhotoMediaAnalysis.fromJson(mediaJson),
    );
  }

  final String productId;
  final PhotoMediaAnalysis media;
}

class PhotoMediaAnalysis {
  const PhotoMediaAnalysis({
    required this.images,
    required this.availableTypes,
    required this.missingTypes,
    required this.mediaReadinessScore,
    required this.recommendedPrimaryPath,
  });

  factory PhotoMediaAnalysis.fromJson(Map<String, dynamic> json) {
    final imagesJson = json['images'];
    final availableJson = json['available_types'];
    final missingJson = json['missing_types'];
    if (imagesJson is! List || availableJson is! List || missingJson is! List) {
      throw const FormatException('The media analysis response is invalid.');
    }

    return PhotoMediaAnalysis(
      images: imagesJson
          .map((item) => PhotoImageAnalysis.fromJson(item))
          .toList(),
      availableTypes: availableJson.cast<String>(),
      missingTypes: missingJson.cast<String>(),
      mediaReadinessScore: _number(json['media_readiness_score']),
      recommendedPrimaryPath: json['recommended_primary_path'] as String?,
    );
  }

  final List<PhotoImageAnalysis> images;
  final List<String> availableTypes;
  final List<String> missingTypes;
  final double mediaReadinessScore;
  final String? recommendedPrimaryPath;
}

class PhotoImageAnalysis {
  const PhotoImageAnalysis({
    required this.imageId,
    required this.storagePath,
    required this.qualityScore,
    required this.blurScore,
    required this.brightnessScore,
    required this.photoType,
    required this.isDuplicate,
    required this.isRecommendedPrimary,
  });

  factory PhotoImageAnalysis.fromJson(dynamic value) {
    if (value is! Map<String, dynamic>) {
      throw const FormatException('An analyzed image is invalid.');
    }

    return PhotoImageAnalysis(
      imageId: value['image_id'] as String,
      storagePath: value['storage_path'] as String,
      qualityScore: _number(value['quality_score']),
      blurScore: _number(value['blur_score']),
      brightnessScore: _number(value['brightness_score']),
      photoType: value['photo_type'] as String,
      isDuplicate: value['is_duplicate'] as bool,
      isRecommendedPrimary: value['is_recommended_primary'] as bool,
    );
  }

  final String imageId;
  final String storagePath;
  final double qualityScore;
  final double blurScore;
  final double brightnessScore;
  final String photoType;
  final bool isDuplicate;
  final bool isRecommendedPrimary;
}

double _number(dynamic value) {
  if (value is num) return value.toDouble();
  throw const FormatException('A numeric analysis value is invalid.');
}
