import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import 'package:frontend/models/voice_analysis.dart';
import 'package:frontend/models/photo_analysis.dart';
import 'package:frontend/screens/photo_analysis_results.dart';
import 'package:frontend/screens/voice_product.dart';
import 'package:frontend/services/api_service.dart';

class _FakeClient extends http.BaseClient {
  _FakeClient(this.statusCode, this.body);

  final int statusCode;
  final String body;
  http.BaseRequest? lastRequest;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    lastRequest = request;
    return http.StreamedResponse(
      Stream.value(utf8.encode(body)),
      statusCode,
      headers: {'content-type': 'application/json'},
    );
  }
}

const _voiceJson = {
  'product_id': 'ART-001',
  'product': {
    'name': 'Silk scarf',
    'category': null,
    'subcategory': null,
    'material': 'silk',
    'color': 'blue',
    'craft_type': 'hand-woven',
    'description': null,
    'dimensions': {'length': 6, 'width': 2, 'height': null, 'unit': 'ft'},
    'weight': {'value': null, 'unit': null},
    'usage': 'wearing',
    'pattern': null,
    'special_features': ['handmade'],
    'production_time': '3 days',
  },
  'voice': {
    'language_code': 'en',
    'original_transcript': 'A blue silk scarf',
    'translated_transcript': null,
    'confidence': 0.9,
  },
  'missing_fields': ['category', 'subcategory', 'weight', 'pattern'],
  'field_confidence': {'name': 1.0},
};

void main() {
  test('parses the actual VoiceProcessingResult response', () {
    final result = VoiceAnalysisResult.fromJson(_voiceJson);

    expect(result.voice.languageCode, 'en');
    expect(result.voice.originalTranscript, 'A blue silk scarf');
    expect(result.product.name, 'Silk scarf');
    expect(result.product.dimensions.length, 6);
    expect(result.product.weight.value, isNull);
    expect(result.missingFields, contains('category'));
  });

  test('returns a typed voice result from a successful API response', () async {
    final client = _FakeClient(200, jsonEncode(_voiceJson));
    final service = ApiService(client: client);

    final result = await service.analyzeVoice(
      productId: 'ART-001',
      audio: XFile.fromData(Uint8List.fromList([1, 2]), name: 'voice.wav'),
    );

    expect(result.product.material, 'silk');
    expect(result.product.color, 'blue');
    final request = client.lastRequest! as http.MultipartRequest;
    expect(request.files.single.filename, 'artisan_voice.wav');
    expect(request.files.single.contentType.toString(), 'audio/wav');
  });

  test('turns a voice HTTP error into ApiException', () async {
    final service = ApiService(
      client: _FakeClient(502, '{"detail":"Voice processing failed."}'),
    );

    expect(
      () => service.analyzeVoice(
        productId: 'ART-001',
        audio: XFile.fromData(Uint8List.fromList([1, 2]), name: 'voice.wav'),
      ),
      throwsA(
        isA<ApiException>().having(
          (error) => error.message,
          'message',
          contains('Voice processing failed'),
        ),
      ),
    );
  });

  test('preserves the selected audio filename and MIME type', () async {
    final client = _FakeClient(200, jsonEncode(_voiceJson));
    final service = ApiService(client: client);

    await service.analyzeVoice(
      productId: 'ART-001',
      audio: XFile.fromData(Uint8List.fromList([1, 2]), name: 'story.ogg'),
    );

    final request = client.lastRequest! as http.MultipartRequest;
    expect(request.files.single.filename, 'story.ogg');
    expect(request.files.single.contentType.toString(), 'audio/ogg');
  });

  test('turns an unsupported voice format into a useful message', () async {
    final service = ApiService(
      client: _FakeClient(415, '{"detail":"Not supported format"}'),
    );

    expect(
      () => service.analyzeVoice(
        productId: 'ART-001',
        audio: XFile.fromData(Uint8List.fromList([1, 2]), name: 'voice.wav'),
      ),
      throwsA(
        isA<ApiException>().having(
          (error) => error.message,
          'message',
          'This recording format is not supported. Please record again and try once more.',
        ),
      ),
    );
  });

  testWidgets('voice screen starts with recording controls', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: VoiceProductPage(productId: 'TEST-PRODUCT'),
      ),
    );

    expect(find.text('Tell us about your product'), findsOneWidget);
    expect(find.text('Start recording'), findsOneWidget);
    expect(find.text('00:00'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
  });

  testWidgets('photo results navigate to voice screen', (
    WidgetTester tester,
  ) async {
    final result = PhotoAnalysisResultForTest.result;
    await tester.pumpWidget(
      MaterialApp(
        home: PhotoAnalysisResultsPage(
          result: result,
          localPhotos: const [],
          productId: 'TEST-PRODUCT',
        ),
      ),
    );

    await tester.tap(find.text('Continue →'));
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Speak naturally in your language.'),
      findsOneWidget,
    );
    expect(find.text('Start recording'), findsOneWidget);
  });
}

class PhotoAnalysisResultForTest {
  static PhotoAnalysisResult get result => PhotoAnalysisResult.fromJson({
    'product_id': 'ART-001',
    'media': {
      'images': [],
      'available_types': [],
      'missing_types': [],
      'media_readiness_score': 0,
      'recommended_primary_path': null,
    },
  });
}
