abstract final class ApiConstants {
  static const baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const defaultBaseUrl = baseUrl;
  static const photoAnalysisPath = '/api/v1/products/{id}/photos/analyze';
  static const voiceAnalysisPath = '/api/v1/products/{id}/voice/analyze';
}
