import 'package:flutter/foundation.dart';

import '../core/constants/languages.dart';
import '../services/storage_service.dart';

/// A lightweight reactive language selection model for Provider-based widgets.
class LanguageProvider extends ChangeNotifier {
  LanguageProvider(this._storage, {String initialLanguage = 'English'})
    : _language = initialLanguage;

  final StorageService _storage;
  String _language;

  String get language => _language;
  String get languageCode => languageCodeFor(_language);
  String translate(String key) =>
      translations[languageCode]?[key] ?? translations['en']?[key] ?? key;

  Future<void> setLanguage(String language) async {
    if (!languageCodes.containsKey(language) || _language == language) return;
    _language = language;
    await _storage.saveLanguage(language);
    notifyListeners();
  }
}
