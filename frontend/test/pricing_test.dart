import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:frontend/models/pricing_analysis.dart';
import 'package:frontend/models/voice_analysis.dart';
import 'package:frontend/services/api_service.dart';

class _FakeClient extends http.BaseClient {
  _FakeClient(this.statusCode, this.body);

  final int statusCode;
  final String body;
  late http.BaseRequest request;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    this.request = request;
    return http.StreamedResponse(
      Stream<List<int>>.value(utf8.encode(body)),
      statusCode,
      headers: {'content-type': 'application/json'},
    );
  }
}

const _pricedResponse = {
  'product_id': 'ART-001',
  'status': 'priced',
  'financial_breakdown': {
    'break_even_price': 950,
    'artisan_take_home': 916.67,
    'reinvestment_fund': 350,
    'profit_margin_amount': 316.67,
  },
  'pricing': {
    'costs': {
      'material': 300,
      'labour': 600,
      'packaging': 30,
      'other': 20,
      'total': 950,
    },
    'labour': {'hours': 6, 'rate_per_hour': 100},
    'desired_margin_percent': 25,
    'margin_type': 'gross_margin',
    'currency': 'INR',
    'market_reference': {
      'sample_size': 0,
      'minimum': null,
      'maximum': null,
      'median': null,
      'sources': [],
    },
    'market_matching_basis': 'none',
    'market_viability': {
      'status': 'no_market_data',
      'message': 'No market data.',
    },
    'market_trend': {
      'direction': 'insufficient_data',
      'change_percent': null,
      'sample_size': 0,
      'pricing_adjustment_percent': 0,
      'message': 'Not enough data.',
    },
    'product_positioning': {
      'available': false,
      'adjustment_percent': 0,
      'reason': 'No signal.',
    },
    'photo_evidence': {
      'available': false,
      'score': null,
      'message': 'No photo evidence.',
    },
    'financial_terms': {
      'cost_recovery': 950,
      'labour_earnings': 600,
      'profit_amount': 316.67,
      'non_labour_costs': 350,
    },
    'suggested_price': {'minimum': 1270, 'maximum': 1400},
    'confidence': {'level': 'low', 'reason': 'Cost based only.'},
    'explanation': ['Production cost is ₹950.00.'],
  },
};

void main() {
  test(
    'serializes pricing request with backend field names and no fake costs',
    () {
      const product = VoiceProductInfo(
        name: 'Hand-Woven Silk Scarf',
        category: 'scarves',
        material: 'silk',
        craftType: 'hand-woven',
        dimensions: VoiceDimensions(length: 6, width: 2, unit: 'ft'),
        weight: VoiceWeight(),
        specialFeatures: [],
      );
      final request = PricingRequest(
        product: ProductPricingInput.fromVoiceProduct(product),
        artisanCosts: const ArtisanCosts(
          material: 300,
          labourHours: 6,
          labourRatePerHour: 100,
          packaging: 30,
          other: 20,
          desiredMarginPercent: 25,
        ),
      );

      final json = request.toJson();

      expect(json['currency'], 'INR');
      expect(json['product']['craft_type'], 'hand-woven');
      expect(json['product']['dimensions'], '6 × 2 ft');
      expect(json['artisan_costs']['labour_hours'], 6);
      expect(json['artisan_costs']['margin_type'], 'gross_margin');
      expect(json['product'].containsKey('color'), isFalse);
    },
  );

  test('parses priced response and nullable market fields', () {
    final result = PricingAnalysisResult.fromJson(_pricedResponse);

    expect(result, isA<PricedPricingResult>());
    final priced = result as PricedPricingResult;
    expect(priced.pricing.suggestedPrice.minimum, 1270);
    expect(priced.pricing.marketReference.minimum, isNull);
    expect(priced.pricing.marketTrend.changePercent, isNull);
    expect(priced.pricing.financialTerms.nonLabourCosts, 350);
  });

  test('parses needs_input response', () {
    final result = PricingAnalysisResult.fromJson({
      'product_id': 'ART-001',
      'status': 'needs_input',
      'missing_inputs': ['material', 'packaging'],
      'targeted_questions': [],
      'financial_breakdown': null,
    });

    expect(result, isA<NeedsInputPricingResult>());
    expect((result as NeedsInputPricingResult).missingInputs, [
      'material',
      'packaging',
    ]);
  });

  test('sends pricing request and surfaces HTTP 422', () async {
    final client = _FakeClient(
      422,
      '{"detail":"desired margin must be less than 100"}',
    );
    final service = ApiService(
      baseUrl: 'http://localhost:8000',
      client: client,
    );

    await expectLater(
      service.analyzePricing(
        productId: 'ART-001',
        product: const ProductPricingInput(name: 'Scarf'),
        artisanCosts: const ArtisanCosts(
          material: 300,
          labourHours: 6,
          labourRatePerHour: 100,
          packaging: 30,
          other: 20,
          desiredMarginPercent: 25,
        ),
      ),
      throwsA(
        isA<ApiException>()
            .having((error) => error.statusCode, 'status code', 422)
            .having(
              (error) => error.message,
              'message',
              contains('less than 100'),
            ),
      ),
    );
    expect(client.request.url.path, '/api/v1/products/ART-001/pricing/analyze');
    expect((client.request as http.Request).body, contains('labour_hours'));
  });
}
