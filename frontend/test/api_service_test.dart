import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import 'package:frontend/models/photo_analysis.dart';
import 'package:frontend/services/api_service.dart';

const _responseJson = {
  'product_id': 'ART-001',
  'media': {
    'images': [
      {
        'image_id': 'img-1',
        'storage_path': 'photo_analysis/a/img-1.jpg',
        'quality_score': 80,
        'blur_score': 70.5,
        'brightness_score': 90,
        'is_duplicate': false,
        'photo_type': 'primary',
        'is_recommended_primary': true,
      },
    ],
    'available_types': ['primary'],
    'missing_types': ['detail', 'lifestyle'],
    'media_readiness_score': 62.5,
    'recommended_primary_path': 'photo_analysis/a/img-1.jpg',
  },
};

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

void main() {
  test('parses the actual Photo Intelligence response shape', () {
    final result = PhotoAnalysisResult.fromJson(_responseJson);

    expect(result.productId, 'ART-001');
    expect(result.media.mediaReadinessScore, 62.5);
    expect(result.media.availableTypes, ['primary']);
    expect(result.media.missingTypes, ['detail', 'lifestyle']);
    expect(result.media.recommendedPrimaryPath, contains('img-1.jpg'));
    expect(result.media.images.single.qualityScore, 80);
    expect(result.media.images.single.photoType, 'primary');
  });

  test('uploads repeated photos and returns a typed success result', () async {
    final client = _FakeClient(200, jsonEncode(_responseJson));
    final service = ApiService(
      baseUrl: 'http://localhost:8000',
      client: client,
    );

    final result = await service.analyzePhotos(
      productId: 'ART-001',
      photos: [
        XFile.fromData(Uint8List.fromList([1, 2, 3]), name: 'one.jpg'),
        XFile.fromData(Uint8List.fromList([4, 5, 6]), name: 'two.jpg'),
      ],
    );

    expect(result.productId, 'ART-001');
    expect(client.request.url.path, '/api/v1/products/ART-001/photos/analyze');
    expect(client.request is http.MultipartRequest, isTrue);
    expect((client.request as http.MultipartRequest).files, hasLength(2));
    expect(
      (client.request as http.MultipartRequest).files.every(
        (file) => file.field == 'photos',
      ),
      isTrue,
    );
  });

  test('converts HTTP errors into a useful ApiException', () async {
    final client = _FakeClient(
      422,
      '{"detail":"Upload between 2 and 5 photos."}',
    );
    final service = ApiService(client: client);

    expect(
      () => service.analyzePhotos(productId: 'ART-001', photos: []),
      throwsA(
        isA<ApiException>()
            .having((error) => error.statusCode, 'status code', 422)
            .having((error) => error.message, 'message', contains('2 and 5')),
      ),
    );
  });
}
