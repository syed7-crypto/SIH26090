class Artisan {
  const Artisan({
    this.name = '',
    this.craftType = '',
    this.region = '',
    this.language = 'English',
  });

  factory Artisan.fromJson(Map<String, dynamic> json) => Artisan(
    name: json['name'] as String? ?? '',
    craftType: json['craftType'] as String? ?? '',
    region: json['region'] as String? ?? '',
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
    name: name ?? this.name,
    craftType: craftType ?? this.craftType,
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
