import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../models/photo_analysis.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiService {
  ApiService({String? baseUrl, http.Client? client})
    : baseUrl = baseUrl ?? 'http://localhost:8000',
      _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  Future<PhotoAnalysisResult> analyzePhotos({
    required String productId,
    required List<XFile> photos,
  }) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/products/${Uri.encodeComponent(productId)}/photos/analyze',
    );
    final request = http.MultipartRequest('POST', uri);

    for (final photo in photos) {
      request.files.add(
        http.MultipartFile.fromBytes(
          'photos',
          await photo.readAsBytes(),
          filename: photo.name,
        ),
      );
    }

    try {
      final response = await _client.send(request);
      final body = await response.stream.bytesToString();
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw ApiException(
          _errorMessage(body),
          statusCode: response.statusCode,
        );
      }

      final decoded = jsonDecode(body);
      if (decoded is! Map<String, dynamic>) {
        throw const ApiException('The server returned an invalid response.');
      }
      return PhotoAnalysisResult.fromJson(decoded);
    } on ApiException {
      rethrow;
    } on FormatException {
      throw const ApiException('The server returned an invalid response.');
    } on http.ClientException catch (error) {
      throw ApiException('Could not connect to the server: ${error.message}');
    } catch (error) {
      throw ApiException('Photo upload failed: $error');
    }
  }

  String _errorMessage(String body) {
    try {
      final decoded = jsonDecode(body);
      if (decoded is Map<String, dynamic> && decoded['detail'] is String) {
        return decoded['detail'] as String;
      }
    } on FormatException {
      // Fall through to a safe generic message for non-JSON errors.
    }
    return 'Photo upload failed. Please try again.';
  }
}
