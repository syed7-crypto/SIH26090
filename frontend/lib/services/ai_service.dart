import 'package:image_picker/image_picker.dart';

import '../models/photo_analysis.dart';
import '../models/voice_analysis.dart';
import 'api_service.dart';

/// Thin UI-facing abstraction for the two AI capabilities exposed by FastAPI.
class AiService {
  AiService({ApiService? api}) : _api = api ?? ApiService();
  final ApiService _api;
  Future<PhotoAnalysisResult> analyzePhotos(
    String productId,
    List<XFile> photos,
  ) => _api.analyzePhotos(productId: productId, photos: photos);
  Future<VoiceAnalysisResult> analyzeVoice(String productId, XFile audio) =>
      _api.analyzeVoice(productId: productId, audio: audio);
}
