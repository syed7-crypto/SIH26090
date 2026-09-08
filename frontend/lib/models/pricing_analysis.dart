import 'voice_analysis.dart';

class PricingRequest {
  const PricingRequest({
    required this.product,
    required this.artisanCosts,
    this.currency = 'INR',
    this.marketReferences,
  });

  final String currency;
  final ProductPricingInput product;
  final ArtisanCosts artisanCosts;
  final List<Map<String, dynamic>>? marketReferences;

  Map<String, dynamic> toJson() => {
    'currency': currency,
    'product': product.toJson(),
    'artisan_costs': artisanCosts.toJson(),
    if (marketReferences != null) 'market_references': marketReferences,
  };
}

class ProductPricingInput {
  const ProductPricingInput({
    this.name,
    this.category,
    this.subcategory,
    this.material,
    this.craftType,
    this.color,
    this.pattern,
    this.description,
    this.dimensions,
    this.usage,
    this.productionTime,
    this.specialFeatures,
  });

  factory ProductPricingInput.fromVoiceProduct(VoiceProductInfo product) {
    return ProductPricingInput(
      name: product.name,
      category: product.category,
      subcategory: product.subcategory,
      material: product.material,
      craftType: product.craftType,
      color: product.color,
      pattern: product.pattern,
      description: product.description,
      dimensions: _dimensions(product.dimensions),
      usage: product.usage,
      productionTime: product.productionTime,
      specialFeatures: product.specialFeatures.isEmpty
          ? null
          : List<String>.from(product.specialFeatures),
    );
  }

  final String? name;
  final String? category;
  final String? subcategory;
  final String? material;
  final String? craftType;
  final String? color;
  final String? pattern;
  final String? description;
  final String? dimensions;
  final String? usage;
  final String? productionTime;
  final List<String>? specialFeatures;

  Map<String, dynamic> toJson() => {
    if (_hasText(name)) 'name': name,
    if (_hasText(category)) 'category': category,
    if (_hasText(subcategory)) 'subcategory': subcategory,
    if (_hasText(material)) 'material': material,
    if (_hasText(craftType)) 'craft_type': craftType,
    if (_hasText(color)) 'color': color,
    if (_hasText(pattern)) 'pattern': pattern,
    if (_hasText(description)) 'description': description,
    if (_hasText(dimensions)) 'dimensions': dimensions,
    if (_hasText(usage)) 'usage': usage,
    if (_hasText(productionTime)) 'production_time': productionTime,
    if (specialFeatures != null && specialFeatures!.isNotEmpty)
      'special_features': specialFeatures,
  };
}

class ArtisanCosts {
  const ArtisanCosts({
    required this.material,
    required this.labourHours,
    required this.labourRatePerHour,
    required this.packaging,
    required this.other,
    required this.desiredMarginPercent,
    this.marginType = 'gross_margin',
  });

  final double material;
  final double labourHours;
  final double labourRatePerHour;
  final double packaging;
  final double other;
  final double desiredMarginPercent;
  final String marginType;

  Map<String, dynamic> toJson() => {
    'material': material,
    'labour_hours': labourHours,
    'labour_rate_per_hour': labourRatePerHour,
    'packaging': packaging,
    'other': other,
    'desired_margin_percent': desiredMarginPercent,
    'margin_type': marginType,
  };
}

sealed class PricingAnalysisResult {
  const PricingAnalysisResult({required this.productId});

  factory PricingAnalysisResult.fromJson(Map<String, dynamic> json) {
    if (json['product_id'] is! String || json['status'] is! String) {
      throw const FormatException('The pricing response is invalid.');
    }
    switch (json['status']) {
      case 'priced':
        return PricedPricingResult.fromJson(json);
      case 'needs_input':
        return NeedsInputPricingResult.fromJson(json);
      default:
        throw const FormatException('The pricing status is invalid.');
    }
  }

  final String productId;
}

class PricedPricingResult extends PricingAnalysisResult {
  const PricedPricingResult({
    required super.productId,
    required this.financialBreakdown,
    required this.pricing,
  });

  factory PricedPricingResult.fromJson(Map<String, dynamic> json) {
    final financialBreakdown = json['financial_breakdown'];
    final pricing = json['pricing'];
    if (financialBreakdown is! Map<String, dynamic> ||
        pricing is! Map<String, dynamic>) {
      throw const FormatException('The priced response is invalid.');
    }
    return PricedPricingResult(
      productId: json['product_id'] as String,
      financialBreakdown: FinancialBreakdown.fromJson(financialBreakdown),
      pricing: PricingDetails.fromJson(pricing),
    );
  }

  final FinancialBreakdown financialBreakdown;
  final PricingDetails pricing;
}

class NeedsInputPricingResult extends PricingAnalysisResult {
  const NeedsInputPricingResult({
    required super.productId,
    required this.missingInputs,
    required this.targetedQuestions,
  });

  factory NeedsInputPricingResult.fromJson(Map<String, dynamic> json) {
    final missing = json['missing_inputs'];
    final questions = json['targeted_questions'];
    if (missing is! List || questions is! List) {
      throw const FormatException('The pricing input response is invalid.');
    }
    return NeedsInputPricingResult(
      productId: json['product_id'] as String,
      missingInputs: missing.whereType<String>().toList(),
      targetedQuestions: questions
          .whereType<Map<String, dynamic>>()
          .map(TargetedQuestion.fromJson)
          .toList(),
    );
  }

  final List<String> missingInputs;
  final List<TargetedQuestion> targetedQuestions;
}

class FinancialBreakdown {
  const FinancialBreakdown({
    required this.breakEvenPrice,
    required this.artisanTakeHome,
    required this.reinvestmentFund,
    required this.profitMarginAmount,
  });

  factory FinancialBreakdown.fromJson(Map<String, dynamic> json) =>
      FinancialBreakdown(
        breakEvenPrice: _number(json['break_even_price']),
        artisanTakeHome: _number(json['artisan_take_home']),
        reinvestmentFund: _number(json['reinvestment_fund']),
        profitMarginAmount: _number(json['profit_margin_amount']),
      );

  final double breakEvenPrice;
  final double artisanTakeHome;
  final double reinvestmentFund;
  final double profitMarginAmount;
}

class PricingDetails {
  const PricingDetails({
    required this.costs,
    required this.labour,
    required this.desiredMarginPercent,
    required this.marginType,
    required this.currency,
    required this.marketReference,
    required this.marketMatchingBasis,
    required this.marketViability,
    required this.marketTrend,
    required this.productPositioning,
    required this.photoEvidence,
    required this.financialTerms,
    required this.suggestedPrice,
    required this.confidence,
    required this.explanation,
  });

  factory PricingDetails.fromJson(Map<String, dynamic> json) => PricingDetails(
    costs: PricingCosts.fromJson(_map(json['costs'], 'costs')),
    labour: LabourPricing.fromJson(_map(json['labour'], 'labour')),
    desiredMarginPercent: _number(json['desired_margin_percent']),
    marginType: json['margin_type'] as String,
    currency: json['currency'] as String,
    marketReference: MarketReference.fromJson(
      _map(json['market_reference'], 'market reference'),
    ),
    marketMatchingBasis: json['market_matching_basis'] as String,
    marketViability: MarketViability.fromJson(
      _map(json['market_viability'], 'market viability'),
    ),
    marketTrend: MarketTrend.fromJson(
      _map(json['market_trend'], 'market trend'),
    ),
    productPositioning: ProductPositioning.fromJson(
      _map(json['product_positioning'], 'product positioning'),
    ),
    photoEvidence: PhotoEvidence.fromJson(
      _map(json['photo_evidence'], 'photo evidence'),
    ),
    financialTerms: FinancialTerms.fromJson(
      _map(json['financial_terms'], 'financial terms'),
    ),
    suggestedPrice: SuggestedPrice.fromJson(
      _map(json['suggested_price'], 'suggested price'),
    ),
    confidence: Confidence.fromJson(_map(json['confidence'], 'confidence')),
    explanation: _stringList(json['explanation']),
  );

  final PricingCosts costs;
  final LabourPricing labour;
  final double desiredMarginPercent;
  final String marginType;
  final String currency;
  final MarketReference marketReference;
  final String marketMatchingBasis;
  final MarketViability marketViability;
  final MarketTrend marketTrend;
  final ProductPositioning productPositioning;
  final PhotoEvidence photoEvidence;
  final FinancialTerms financialTerms;
  final SuggestedPrice suggestedPrice;
  final Confidence confidence;
  final List<String> explanation;
}

class PricingCosts {
  const PricingCosts({
    required this.material,
    required this.labour,
    required this.packaging,
    required this.other,
    required this.total,
  });

  factory PricingCosts.fromJson(Map<String, dynamic> json) => PricingCosts(
    material: _number(json['material']),
    labour: _number(json['labour']),
    packaging: _number(json['packaging']),
    other: _number(json['other']),
    total: _number(json['total']),
  );

  final double material;
  final double labour;
  final double packaging;
  final double other;
  final double total;
}

class LabourPricing {
  const LabourPricing({required this.hours, required this.ratePerHour});

  factory LabourPricing.fromJson(Map<String, dynamic> json) => LabourPricing(
    hours: _number(json['hours']),
    ratePerHour: _number(json['rate_per_hour']),
  );

  final double hours;
  final double ratePerHour;
}

class MarketReference {
  const MarketReference({
    required this.sampleSize,
    this.minimum,
    this.maximum,
    this.median,
    required this.sources,
  });

  factory MarketReference.fromJson(Map<String, dynamic> json) =>
      MarketReference(
        sampleSize: _integer(json['sample_size']),
        minimum: _nullableNumber(json['minimum']),
        maximum: _nullableNumber(json['maximum']),
        median: _nullableNumber(json['median']),
        sources: _stringList(json['sources']),
      );

  final int sampleSize;
  final double? minimum;
  final double? maximum;
  final double? median;
  final List<String> sources;
}

class MarketViability {
  const MarketViability({required this.status, required this.message});

  factory MarketViability.fromJson(Map<String, dynamic> json) =>
      MarketViability(
        status: json['status'] as String,
        message: json['message'] as String,
      );

  final String status;
  final String message;
}

class MarketTrend {
  const MarketTrend({
    required this.direction,
    this.changePercent,
    required this.sampleSize,
    required this.pricingAdjustmentPercent,
    required this.message,
  });

  factory MarketTrend.fromJson(Map<String, dynamic> json) => MarketTrend(
    direction: json['direction'] as String,
    changePercent: _nullableNumber(json['change_percent']),
    sampleSize: _integer(json['sample_size']),
    pricingAdjustmentPercent: _number(json['pricing_adjustment_percent']),
    message: json['message'] as String,
  );

  final String direction;
  final double? changePercent;
  final int sampleSize;
  final double pricingAdjustmentPercent;
  final String message;
}

class ProductPositioning {
  const ProductPositioning({
    required this.available,
    required this.adjustmentPercent,
    required this.reason,
  });

  factory ProductPositioning.fromJson(Map<String, dynamic> json) =>
      ProductPositioning(
        available: json['available'] as bool,
        adjustmentPercent: _number(json['adjustment_percent']),
        reason: json['reason'] as String,
      );

  final bool available;
  final double adjustmentPercent;
  final String reason;
}

class PhotoEvidence {
  const PhotoEvidence({
    required this.available,
    this.score,
    this.band,
    required this.message,
  });

  factory PhotoEvidence.fromJson(Map<String, dynamic> json) => PhotoEvidence(
    available: json['available'] as bool,
    score: _nullableNumber(json['score']),
    band: json['band'] as String?,
    message: json['message'] as String,
  );

  final bool available;
  final double? score;
  final String? band;
  final String message;
}

class FinancialTerms {
  const FinancialTerms({
    required this.costRecovery,
    required this.labourEarnings,
    required this.profitAmount,
    required this.nonLabourCosts,
  });

  factory FinancialTerms.fromJson(Map<String, dynamic> json) => FinancialTerms(
    costRecovery: _number(json['cost_recovery']),
    labourEarnings: _number(json['labour_earnings']),
    profitAmount: _number(json['profit_amount']),
    nonLabourCosts: _number(json['non_labour_costs']),
  );

  final double costRecovery;
  final double labourEarnings;
  final double profitAmount;
  final double nonLabourCosts;
}

class SuggestedPrice {
  const SuggestedPrice({required this.minimum, required this.maximum});

  factory SuggestedPrice.fromJson(Map<String, dynamic> json) => SuggestedPrice(
    minimum: _number(json['minimum']),
    maximum: _number(json['maximum']),
  );

  final double minimum;
  final double maximum;
}

class Confidence {
  const Confidence({required this.level, required this.reason});

  factory Confidence.fromJson(Map<String, dynamic> json) => Confidence(
    level: json['level'] as String,
    reason: json['reason'] as String,
  );

  final String level;
  final String reason;
}

class TargetedQuestion {
  const TargetedQuestion({
    required this.field,
    required this.question,
    required this.guidance,
    required this.inputType,
  });

  factory TargetedQuestion.fromJson(Map<String, dynamic> json) =>
      TargetedQuestion(
        field: json['field'] as String,
        question: json['question'] as String,
        guidance: json['guidance'] as String,
        inputType: json['input_type'] as String,
      );

  final String field;
  final String question;
  final String guidance;
  final String inputType;
}

Map<String, dynamic> _map(dynamic value, String field) {
  if (value is Map<String, dynamic>) return value;
  throw FormatException('The pricing $field is invalid.');
}

double _number(dynamic value) {
  if (value is num) return value.toDouble();
  throw const FormatException('A pricing number is invalid.');
}

double? _nullableNumber(dynamic value) => value == null ? null : _number(value);

int _integer(dynamic value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  throw const FormatException('A pricing integer is invalid.');
}

List<String> _stringList(dynamic value) {
  if (value is List && value.every((item) => item is String)) {
    return value.cast<String>();
  }
  throw const FormatException('A pricing text list is invalid.');
}

bool _hasText(String? value) => value != null && value.trim().isNotEmpty;

String? _dimensions(VoiceDimensions dimensions) {
  final values = [dimensions.length, dimensions.width, dimensions.height]
      .whereType<double>()
      .map((value) => value.toStringAsFixed(value % 1 == 0 ? 0 : 1))
      .toList();
  if (values.isEmpty) return null;
  return '${values.join(' × ')}${dimensions.unit == null ? '' : ' ${dimensions.unit}'}';
}
