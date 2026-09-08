import 'package:flutter/foundation.dart';

import '../models/product_draft.dart';
import '../core/constants/languages.dart';
import '../services/storage_service.dart';

class AppState extends ChangeNotifier {
  AppState(this._storage);

  final StorageService _storage;
  List<ProductDraft> _products = [];
  String _language = 'English';
  ProductDraft? _activeDraft;
  bool _onboardingComplete = false;
  bool _notificationsEnabled = true;
  double _voiceGuidanceSpeed = 1;

  List<ProductDraft> get products => List.unmodifiable(_products);
  String get language => _language;
  String get languageCode => languageCodeFor(_language);
  ProductDraft? get activeDraft => _activeDraft;
  bool get onboardingComplete => _onboardingComplete;
  bool get notificationsEnabled => _notificationsEnabled;
  double get voiceGuidanceSpeed => _voiceGuidanceSpeed;

  Future<void> load() async {
    _products = await _storage.loadProducts();
    _language = await _storage.loadLanguage();
    _onboardingComplete = await _storage.hasCompletedOnboarding();
    _notificationsEnabled = await _storage.loadNotificationsEnabled();
    _voiceGuidanceSpeed = await _storage.loadVoiceGuidanceSpeed();
    _activeDraft = await _storage.loadActiveDraft();
    notifyListeners();
  }

  ProductDraft startDraft() {
    final id = 'ART-${DateTime.now().millisecondsSinceEpoch}';
    _activeDraft = ProductDraft.empty(id, language: _language);
    _storage.saveActiveDraft(_activeDraft);
    notifyListeners();
    return _activeDraft!;
  }

  void openDraft(ProductDraft draft) {
    _activeDraft = draft;
    _storage.saveActiveDraft(draft);
    notifyListeners();
  }

  Future<void> updateDraft(ProductDraft draft) async {
    _activeDraft = draft;
    await _storage.saveActiveDraft(draft);
    await _upsert(draft);
    notifyListeners();
  }

  Future<void> saveActive({ProductStatus? status}) async {
    if (_activeDraft == null) return;
    await updateDraft(_activeDraft!.copyWith(status: status));
  }

  Future<void> publishActive() async {
    if (_activeDraft == null || _activeDraft!.readiness < 80) return;
    await updateDraft(_activeDraft!.copyWith(status: ProductStatus.published));
  }

  Future<void> deleteDraft(String id) async {
    _products = _products.where((product) => product.id != id).toList();
    if (_activeDraft?.id == id) {
      _activeDraft = null;
      await _storage.saveActiveDraft(null);
    }
    await _storage.saveProducts(_products);
    notifyListeners();
  }

  Future<void> setLanguage(String language) async {
    _language = language;
    await _storage.saveLanguage(language);
    notifyListeners();
  }

  String translate(String key) =>
      translations[languageCode]?[key] ?? translations['en']?[key] ?? key;

  Future<void> completeOnboarding() async {
    _onboardingComplete = true;
    await _storage.completeOnboarding();
    notifyListeners();
  }

  Future<void> resetOnboarding() async {
    _onboardingComplete = false;
    await _storage.resetOnboarding();
    notifyListeners();
  }

  Future<void> setNotificationsEnabled(bool value) async {
    _notificationsEnabled = value;
    await _storage.saveNotificationsEnabled(value);
    notifyListeners();
  }

  Future<void> setVoiceGuidanceSpeed(double value) async {
    _voiceGuidanceSpeed = value;
    await _storage.saveVoiceGuidanceSpeed(value);
    notifyListeners();
  }

  Future<void> _upsert(ProductDraft draft) async {
    final index = _products.indexWhere((item) => item.id == draft.id);
    if (index == -1) {
      _products = [draft, ..._products];
    } else {
      _products[index] = draft;
    }
    await _storage.saveProducts(_products);
  }
}
