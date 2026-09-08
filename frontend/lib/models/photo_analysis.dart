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
    required this.photoReadiness,
  });

  factory PhotoMediaAnalysis.fromJson(Map<String, dynamic> json) {
    final imagesJson = json['images'];
    final availableJson = json['available_types'];
    final missingJson = json['missing_types'];
    if (imagesJson is! List || availableJson is! List || missingJson is! List) {
      throw const FormatException('The media analysis response is invalid.');
    }

    final parsedImages = imagesJson
        .map((item) => PhotoImageAnalysis.fromJson(item))
        .toList();
    final readinessJson = json['photo_readiness'];
    return PhotoMediaAnalysis(
      images: parsedImages,
      availableTypes: availableJson.cast<String>(),
      missingTypes: missingJson.cast<String>(),
      mediaReadinessScore: _number(json['media_readiness_score']),
      recommendedPrimaryPath: json['recommended_primary_path'] as String?,
      photoReadiness: readinessJson is Map<String, dynamic>
          ? PhotoReadiness.fromJson(readinessJson)
          : PhotoReadiness.fromLegacy(parsedImages),
    );
  }

  final List<PhotoImageAnalysis> images;
  final List<String> availableTypes;
  final List<String> missingTypes;
  final double mediaReadinessScore;
  final String? recommendedPrimaryPath;
  final PhotoReadiness photoReadiness;
}

class PhotoReadiness {
  const PhotoReadiness({
    required this.score,
    required this.totalUploaded,
    required this.accepted,
    required this.enhanced,
    required this.removed,
    required this.needsRetake,
    required this.issues,
  });

  factory PhotoReadiness.fromJson(Map<String, dynamic> json) {
    return PhotoReadiness(
      score: _number(json['score']),
      totalUploaded: _integer(json['total_uploaded']),
      accepted: _integer(json['accepted']),
      enhanced: _integer(json['enhanced']),
      removed: _integer(json['removed']),
      needsRetake: _integer(json['needs_retake']),
      issues: _stringList(json['issues']),
    );
  }

  factory PhotoReadiness.fromLegacy(List<PhotoImageAnalysis> images) {
    final accepted = images.where((image) => image.status != 'removed' && image.status != 'needs_retake').length;
    return PhotoReadiness(
      score: images.isEmpty
          ? 0
          : images.map((image) => image.qualityScore).reduce((a, b) => a + b) / images.length,
      totalUploaded: images.length,
      accepted: accepted,
      enhanced: 0,
      removed: images.where((image) => image.status == 'removed').length,
      needsRetake: images.where((image) => image.status == 'needs_retake').length,
      issues: const [],
    );
  }

  final double score;
  final int totalUploaded;
  final int accepted;
  final int enhanced;
  final int removed;
  final int needsRetake;
  final List<String> issues;
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
    required this.originalPath,
    required this.finalPath,
    required this.status,
    required this.qualityScoreBefore,
    required this.qualityScoreAfter,
    required this.actions,
    required this.issuesBefore,
    required this.reason,
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
      originalPath: value['original_path'] as String? ?? value['storage_path'] as String,
      finalPath: value['final_path'] as String?,
      status: value['status'] as String? ?? 'kept',
      qualityScoreBefore: _number(value['quality_score_before'] ?? value['quality_score']),
      qualityScoreAfter: _number(value['quality_score_after'] ?? value['quality_score']),
      actions: _stringList(value['actions']),
      issuesBefore: _stringList(value['issues_before']),
      reason: value['reason'] as String? ?? 'Photo analyzed',
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
  final String originalPath;
  final String? finalPath;
  final String status;
  final double qualityScoreBefore;
  final double qualityScoreAfter;
  final List<String> actions;
  final List<String> issuesBefore;
  final String reason;
}

double _number(dynamic value) {
  if (value is num) return value.toDouble();
  throw const FormatException('A numeric analysis value is invalid.');
}

int _integer(dynamic value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  throw const FormatException('An integer analysis value is invalid.');
}

List<String> _stringList(dynamic value) {
  if (value == null) return const [];
  if (value is List && value.every((item) => item is String)) {
    return value.cast<String>();
  }
  throw const FormatException('A text list in the analysis is invalid.');
}
