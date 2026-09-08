class Artisan {
  const Artisan({
    this.name = 'Artisan',
    this.craftType = 'Handicrafts',
    this.region = 'India',
    this.language = 'English',
  });

  factory Artisan.fromJson(Map<String, dynamic> json) => Artisan(
    name: (json['name'] as String?)?.trim().isNotEmpty == true
        ? (json['name'] as String).toUpperCase()
        : 'Artisan',
    craftType: (json['craftType'] as String?)?.trim().isNotEmpty == true
        ? (json['craftType'] as String).toUpperCase()
        : 'Handicrafts',
    region: (json['region'] as String?)?.trim().isNotEmpty == true
        ? json['region'] as String
        : 'India',
    language: json['language'] as String? ?? 'English',
  );

  final String name;
  final String craftType;
  final String region;
  final String language;

  Artisan copyWith({
    String? name,
    String? craftType,
    String? region,
    String? language,
  }) => Artisan(
    name: (name ?? this.name).toUpperCase(),
    craftType: (craftType ?? this.craftType).toUpperCase(),
    region: region ?? this.region,
    language: language ?? this.language,
  );

  Map<String, dynamic> toJson() => {
    'name': name,
    'craftType': craftType,
    'region': region,
    'language': language,
  };
}
