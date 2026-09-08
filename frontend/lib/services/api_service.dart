import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../models/photo_analysis.dart';
import '../models/voice_analysis.dart';

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

  Future<VoiceAnalysisResult> analyzeVoice({
    required String productId,
    required XFile audio,
  }) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/products/${Uri.encodeComponent(productId)}/voice/analyze',
    );
    final filename = _audioFilename(
      audio.name.isNotEmpty ? audio.name : audio.path,
    );
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes(
          'audio',
          await audio.readAsBytes(),
          filename: filename,
          contentType: _audioContentType(filename),
        ),
      );

    try {
      final response = await _client
          .send(request)
          .timeout(const Duration(seconds: 60));
      final body = await response.stream.bytesToString();
      if (response.statusCode < 200 || response.statusCode >= 300) {
        final message = _errorMessage(
          body,
          fallback: 'Voice upload failed. Please try again.',
        );
        throw ApiException(
          response.statusCode == 415 && message.toLowerCase().contains('format')
              ? 'This recording format is not supported. Please record again and try once more.'
              : message,
          statusCode: response.statusCode,
        );
      }

      final decoded = jsonDecode(body);
      if (decoded is! Map<String, dynamic>) {
        throw const ApiException('The server returned an invalid response.');
      }
      return VoiceAnalysisResult.fromJson(decoded);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw const ApiException(
        'Voice processing took too long. Please try again.',
      );
    } on FormatException {
      throw const ApiException('The server returned an invalid response.');
    } on http.ClientException catch (error) {
      throw ApiException('Could not connect to the server: ${error.message}');
    } catch (error) {
      throw ApiException('Voice upload failed: $error');
    }
  }

  String _errorMessage(
    String body, {
    String fallback = 'Photo upload failed. Please try again.',
  }) {
    try {
      final decoded = jsonDecode(body);
      if (decoded is Map<String, dynamic> && decoded['detail'] is String) {
        return decoded['detail'] as String;
      }
    } on FormatException {
      // Fall through to a safe generic message for non-JSON errors.
    }
    return fallback;
  }

  http.MediaType _audioContentType(String filename) {
    switch (filename.split('.').last.toLowerCase()) {
      case 'mp3':
        return http.MediaType('audio', 'mpeg');
      case 'flac':
        return http.MediaType('audio', 'flac');
      case 'ogg':
        return http.MediaType('audio', 'ogg');
      case 'wav':
      default:
        return http.MediaType('audio', 'wav');
    }
  }

  String _audioFilename(String name) {
    final filename = name.split(RegExp(r'[\\/]')).last;
    final lastDot = filename.lastIndexOf('.');
    final extension = lastDot > 0 && lastDot < filename.length - 1
        ? filename.substring(lastDot + 1).toLowerCase()
        : '';
    const supported = {'wav', 'mp3', 'flac', 'ogg'};
    return supported.contains(extension) ? filename : 'artisan_voice.wav';
  }
}
