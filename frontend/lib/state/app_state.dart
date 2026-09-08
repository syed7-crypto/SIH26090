import 'package:flutter/foundation.dart';

import '../models/product_draft.dart';
import '../services/storage_service.dart';

class AppState extends ChangeNotifier {
  AppState(this._storage);

  final StorageService _storage;
  List<ProductDraft> _products = [];
  String _language = 'English';
  ProductDraft? _activeDraft;
  bool _onboardingComplete = false;

  List<ProductDraft> get products => List.unmodifiable(_products);
  String get language => _language;
  ProductDraft? get activeDraft => _activeDraft;
  bool get onboardingComplete => _onboardingComplete;

  Future<void> load() async {
    _products = await _storage.loadProducts();
    _language = await _storage.loadLanguage();
    _onboardingComplete = await _storage.hasCompletedOnboarding();
    notifyListeners();
  }

  ProductDraft startDraft() {
    final id = 'ART-${DateTime.now().millisecondsSinceEpoch}';
    _activeDraft = ProductDraft.empty(id, language: _language);
    notifyListeners();
    return _activeDraft!;
  }

  void openDraft(ProductDraft draft) {
    _activeDraft = draft;
    notifyListeners();
  }

  Future<void> updateDraft(ProductDraft draft) async {
    _activeDraft = draft;
    await _upsert(draft);
    notifyListeners();
  }

  Future<void> saveActive({ProductStatus? status}) async {
    if (_activeDraft == null) return;
    await updateDraft(_activeDraft!.copyWith(status: status));
  }

  Future<void> setLanguage(String language) async {
    _language = language;
    await _storage.saveLanguage(language);
    notifyListeners();
  }

  Future<void> completeOnboarding() async {
    _onboardingComplete = true;
    await _storage.completeOnboarding();
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
