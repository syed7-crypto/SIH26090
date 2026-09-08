import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/product_draft.dart';

class StorageService {
  static const _productsKey = 'karigar_products';
  static const _languageKey = 'karigar_language';

  Future<List<ProductDraft>> loadProducts() async {
    final preferences = await SharedPreferences.getInstance();
    final raw = preferences.getString(_productsKey);
    if (raw == null) return [];
    final values = jsonDecode(raw) as List;
    return values
        .cast<Map<String, dynamic>>()
        .map(ProductDraft.fromJson)
        .toList();
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
}
