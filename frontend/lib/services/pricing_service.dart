class PriceRecommendation {
  const PriceRecommendation({
    required this.minimum,
    required this.recommended,
    required this.maximum,
    required this.note,
  });
  final double minimum;
  final double recommended;
  final double maximum;
  final String note;
}

/// Local, transparent fallback used only until FastAPI exposes pricing routes.
class PricingService {
  PriceRecommendation estimate({
    required double materialCost,
    required double labourCost,
    double packagingCost = 0,
    double otherCost = 0,
  }) {
    final cost = materialCost + labourCost + packagingCost + otherCost;
    return PriceRecommendation(
      minimum: cost * 1.2,
      recommended: cost * 1.5,
      maximum: cost * 1.8,
      note: 'Offline estimate based on the costs you entered.',
    );
  }
}
