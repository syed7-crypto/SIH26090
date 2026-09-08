import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/product_draft.dart';
import '../models/artisan.dart';

class StorageService {
  static const _productsKey = 'karigar_products';
  static const _languageKey = 'karigar_language';
  static const _onboardingKey = 'karigar_onboarding_done';
  static const _artisanKey = 'karigar_artisan';
  static const _activeDraftKey = 'karigar_active_draft';
  static const _notificationsKey = 'karigar_notifications_enabled';
  static const _voiceSpeedKey = 'karigar_voice_guidance_speed';

  Future<List<ProductDraft>> loadProducts() async {
    final preferences = await SharedPreferences.getInstance();
    final raw = preferences.getString(_productsKey);
    if (raw == null) return [];
    try {
      final values = jsonDecode(raw) as List;
      return values
          .map((value) => ProductDraft.fromJson(Map<String, dynamic>.from(value as Map)))
          .toList();
    } on FormatException {
      return [];
    } on TypeError {
      return [];
    }
  }

  Future<void> saveProducts(List<ProductDraft> products) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(
      _productsKey,
      jsonEncode(products.map((product) => product.toJson()).toList()),
    );
  }

  Future<String> loadLanguage() async {
    final preferences = await SharedPreferences.getInstance();
    return preferences.getString(_languageKey) ?? 'English';
  }

  Future<void> saveLanguage(String language) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_languageKey, language);
  }

  Future<bool> hasCompletedOnboarding() async =>
      (await SharedPreferences.getInstance()).getBool(_onboardingKey) ?? false;
  Future<void> completeOnboarding() async =>
      (await SharedPreferences.getInstance()).setBool(_onboardingKey, true);
  Future<Artisan> loadArtisan() async {
    final raw = (await SharedPreferences.getInstance()).getString(_artisanKey);
    if (raw == null) return const Artisan();
    try {
      return Artisan.fromJson(
        Map<String, dynamic>.from(jsonDecode(raw) as Map),
      );
    } on FormatException {
      return const Artisan();
    } on TypeError {
      return const Artisan();
    }
  }

  Future<void> saveArtisan(Artisan artisan) async =>
      (await SharedPreferences.getInstance()).setString(
        _artisanKey,
        jsonEncode(artisan.toJson()),
      );

  Future<ProductDraft?> loadActiveDraft() async {
    final raw = (await SharedPreferences.getInstance()).getString(
      _activeDraftKey,
    );
    if (raw == null) return null;
    try {
      return ProductDraft.fromJson(
        Map<String, dynamic>.from(jsonDecode(raw) as Map),
      );
    } on FormatException {
      return null;
    } on TypeError {
      return null;
    }
  }

  Future<void> saveActiveDraft(ProductDraft? draft) async {
    final preferences = await SharedPreferences.getInstance();
    if (draft == null) {
      await preferences.remove(_activeDraftKey);
    } else {
      await preferences.setString(_activeDraftKey, jsonEncode(draft.toJson()));
    }
  }

  Future<bool> loadNotificationsEnabled() async =>
      (await SharedPreferences.getInstance()).getBool(_notificationsKey) ??
      true;
  Future<void> saveNotificationsEnabled(bool value) async =>
      (await SharedPreferences.getInstance()).setBool(_notificationsKey, value);
  Future<double> loadVoiceGuidanceSpeed() async =>
      (await SharedPreferences.getInstance()).getDouble(_voiceSpeedKey) ?? 1;
  Future<void> saveVoiceGuidanceSpeed(double value) async =>
      (await SharedPreferences.getInstance()).setDouble(_voiceSpeedKey, value);
  Future<void> resetOnboarding() async =>
      (await SharedPreferences.getInstance()).setBool(_onboardingKey, false);
}
