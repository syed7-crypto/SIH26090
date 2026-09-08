class ProductDraft {
  ProductDraft({
    required this.id,
    required this.createdAt,
    this.name = '',
    this.category = '',
    this.material = '',
    this.colour = '',
    this.craftType = '',
    this.dimensions = '',
    this.description = '',
    this.language = 'English',
    List<String> photoPaths = const [],
    this.photoReadiness,
    this.voiceTranscript = '',
    this.price,
    this.status = ProductStatus.draft,
  }) : photoPaths = List.unmodifiable(photoPaths.take(2));

  factory ProductDraft.empty(String id, {String language = 'English'}) =>
      ProductDraft(id: id, createdAt: DateTime.now(), language: language);

  factory ProductDraft.fromJson(Map<String, dynamic> json) => ProductDraft(
    id: json['id'] as String,
    createdAt: DateTime.parse(json['createdAt'] as String),
    name: json['name'] as String? ?? '',
    category: json['category'] as String? ?? '',
    material: json['material'] as String? ?? '',
    colour: json['colour'] as String? ?? '',
    craftType: json['craftType'] as String? ?? '',
    dimensions: json['dimensions'] as String? ?? '',
    description: json['description'] as String? ?? '',
    language: json['language'] as String? ?? 'English',
    photoPaths: (json['photoPaths'] as List? ?? const []).cast<String>(),
    photoReadiness: (json['photoReadiness'] as num?)?.toDouble(),
    voiceTranscript: json['voiceTranscript'] as String? ?? '',
    price: (json['price'] as num?)?.toDouble(),
    status: ProductStatus.values.byName(json['status'] as String? ?? 'draft'),
  );

  final String id;
  final DateTime createdAt;
  final String name;
  final String category;
  final String material;
  final String colour;
  final String craftType;
  final String dimensions;
  final String description;
  final String language;
  final List<String> photoPaths;
  final double? photoReadiness;
  final String voiceTranscript;
  final double? price;
  final ProductStatus status;

  ProductDraft copyWith({
    String? name,
    String? category,
    String? material,
    String? colour,
    String? craftType,
    String? dimensions,
    String? description,
    String? language,
    List<String>? photoPaths,
    double? photoReadiness,
    String? voiceTranscript,
    double? price,
    ProductStatus? status,
  }) => ProductDraft(
    id: id,
    createdAt: createdAt,
    name: name ?? this.name,
    category: category ?? this.category,
    material: material ?? this.material,
    colour: colour ?? this.colour,
    craftType: craftType ?? this.craftType,
    dimensions: dimensions ?? this.dimensions,
    description: description ?? this.description,
    language: language ?? this.language,
    photoPaths: photoPaths ?? this.photoPaths,
    photoReadiness: photoReadiness ?? this.photoReadiness,
    voiceTranscript: voiceTranscript ?? this.voiceTranscript,
    price: price ?? this.price,
    status: status ?? this.status,
  );

  int get readiness {
    double score = photoPaths.length == 2
        ? 20
        : photoPaths.isNotEmpty
        ? 10
        : 0;
    const fieldWeight = 80 / 6;
    if (name.trim().isNotEmpty) score += fieldWeight;
    if (category.trim().isNotEmpty) score += fieldWeight;
    if (material.trim().isNotEmpty) score += fieldWeight;
    if (description.trim().isNotEmpty) score += fieldWeight;
    if (dimensions.trim().isNotEmpty) score += fieldWeight;
    if (price != null && price! > 0) score += fieldWeight;
    return score.round();
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'createdAt': createdAt.toIso8601String(),
    'name': name,
    'category': category,
    'material': material,
    'colour': colour,
    'craftType': craftType,
    'dimensions': dimensions,
    'description': description,
    'language': language,
    'photoPaths': photoPaths,
    'photoReadiness': photoReadiness,
    'voiceTranscript': voiceTranscript,
    'price': price,
    'status': status.name,
  };
}

enum ProductStatus { draft, ready, published }
