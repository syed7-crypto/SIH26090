import 'package:flutter/foundation.dart';

import '../core/constants/languages.dart';
import '../models/voice_analysis.dart';

/// In-memory coordination state for the app shell.
///
/// FirestoreService remains the source of truth for persisted artisans and
/// products. This class deliberately does not persist or duplicate them.
class AppState extends ChangeNotifier {
  String _language = 'English';
  bool _onboardingComplete = false;
  String? _activeProductId;
  VoiceProductInfo? _activeProduct;

  String get language => _language;
  String get languageCode => languageCodeFor(_language);
  bool get onboardingComplete => _onboardingComplete;
  String? get activeProductId => _activeProductId;
  VoiceProductInfo? get activeVoiceProduct => _activeProduct;
  // Compatibility alias for callers using the shorter name.
  VoiceProductInfo? get activeProduct => _activeProduct;

  void setLanguage(String language) {
    if (!supportedLanguages.contains(language) || language == _language) return;
    _language = language;
    notifyListeners();
  }

  void completeOnboarding() {
    if (_onboardingComplete) return;
    _onboardingComplete = true;
    notifyListeners();
  }

  void resetOnboarding() {
    if (!_onboardingComplete) return;
    _onboardingComplete = false;
    notifyListeners();
  }

  void setActiveProduct(String productId, VoiceProductInfo product) {
    _activeProductId = productId;
    _activeProduct = product;
    notifyListeners();
  }

  /// Select a persisted product by its Firestore document ID.
  ///
  /// The full Firestore product remains owned by FirestoreService; only the
  /// selection is kept here for coordination between screens.
  void selectActiveProduct(String productId) {
    if (productId.trim().isEmpty) return;
    _activeProductId = productId;
    _activeProduct = null;
    notifyListeners();
  }

  void clearActiveProduct() {
    _activeProductId = null;
    _activeProduct = null;
    notifyListeners();
  }
}
