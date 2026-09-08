class VoiceService {
  static const supportedExtensions = {'wav', 'mp3', 'flac', 'ogg'};
  bool isSupportedFilename(String filename) {
    final dot = filename.lastIndexOf('.');
    return dot > 0 &&
        supportedExtensions.contains(filename.substring(dot + 1).toLowerCase());
  }
}
