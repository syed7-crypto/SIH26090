import 'package:cloud_firestore/cloud_firestore.dart';

import '../models/voice_analysis.dart';

class FirestoreServiceException implements Exception {
  const FirestoreServiceException(this.message);

  final String message;

  @override
  String toString() => message;
}

class FirestoreService {
  static const defaultArtisanId = 'ART-001';

  FirestoreService({this._firestore});

  final FirebaseFirestore? _firestore;

  FirebaseFirestore get _db => _firestore ?? FirebaseFirestore.instance;

  /// Returns a new product document ID without writing an empty document.
  String createProductId(String artisanId) => _db
      .collection('artisans')
      .doc(artisanId)
      .collection('products')
      .doc()
      .id;

  /// Save or update an artisan profile.
  Future<void> saveArtisan({
    required String artisanId,
    required String name,
    String? phone,
    String? language,
  }) async {
    try {
      await _db.collection('artisans').doc(artisanId).set({
        'name': name,
        ..._optionalText('phone', phone),
        ..._optionalText('language', language),
        'updatedAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } on FirebaseException catch (error) {
      throw FirestoreServiceException(
        _message('save the artisan profile', error),
      );
    }
  }

  /// Fetch an artisan profile.
  Future<Map<String, dynamic>?> getArtisan(String artisanId) async {
    try {
      final doc = await _db.collection('artisans').doc(artisanId).get();

      if (!doc.exists) return null;
      return doc.data();
    } on FirebaseException catch (error) {
      throw FirestoreServiceException(
        _message('load the artisan profile', error),
      );
    }
  }

  /// Create/update a product under an artisan.
  Future<void> saveProduct({
    required String artisanId,
    required String productId,
    required Map<String, dynamic> product,
  }) async {
    try {
      await _db
          .collection('artisans')
          .doc(artisanId)
          .collection('products')
          .doc(productId)
          .set({
            ...product,
            'updatedAt': FieldValue.serverTimestamp(),
          }, SetOptions(merge: true));
    } on FirebaseException catch (error) {
      throw FirestoreServiceException(_message('save the product', error));
    }
  }

  /// Saves only the structured product fields returned by Voice Intelligence.
  /// Missing fields remain absent; no product attributes or costs are inferred.
  Future<void> saveVoiceProduct({
    required String artisanId,
    required VoiceAnalysisResult result,
  }) {
    return saveProduct(
      artisanId: artisanId,
      productId: result.productId,
      product: voiceProductData(result.product),
    );
  }

  /// Fetch all products belonging to an artisan.
  Future<List<Map<String, dynamic>>> getProducts(String artisanId) async {
    try {
      final snapshot = await _db
          .collection('artisans')
          .doc(artisanId)
          .collection('products')
          .get();

      return snapshot.docs.map((doc) {
        return {'id': doc.id, ...doc.data()};
      }).toList();
    } on FirebaseException catch (error) {
      throw FirestoreServiceException(_message('load saved products', error));
    }
  }

  static Map<String, dynamic> voiceProductData(VoiceProductInfo product) {
    return {
      if (_hasText(product.name)) 'name': product.name,
      if (_hasText(product.category)) 'category': product.category,
      if (_hasText(product.subcategory)) 'subcategory': product.subcategory,
      if (_hasText(product.material)) 'material': product.material,
      if (_hasText(product.color)) 'color': product.color,
      if (_hasText(product.craftType)) 'craftType': product.craftType,
      if (_hasText(product.description)) 'description': product.description,
      if (_hasText(product.usage)) 'usage': product.usage,
      if (_hasText(product.pattern)) 'pattern': product.pattern,
      if (_hasText(product.productionTime))
        'productionTime': product.productionTime,
      if (product.specialFeatures.isNotEmpty)
        'specialFeatures': List<String>.from(product.specialFeatures),
      if (product.dimensions.hasValue) 'dimensions': product.dimensions.toMap(),
      if (product.weight.hasValue) 'weight': product.weight.toMap(),
    };
  }

  static bool _hasText(String? value) =>
      value != null && value.trim().isNotEmpty;

  static Map<String, String> _optionalText(String key, String? value) =>
      value == null ? const {} : {key: value};

  static String _message(String action, FirebaseException error) {
    if (error.code == 'permission-denied') {
      return 'We could not $action because access was denied.';
    }
    return 'We could not $action. Please check your connection and try again.';
  }
}

extension on VoiceDimensions {
  bool get hasValue =>
      length != null || width != null || height != null || unit != null;

  Map<String, dynamic> toMap() => {
    if (length != null) 'length': length,
    if (width != null) 'width': width,
    if (height != null) 'height': height,
    if (unit != null) 'unit': unit,
  };
}

extension on VoiceWeight {
  bool get hasValue => value != null || unit != null;

  Map<String, dynamic> toMap() => {
    if (value != null) 'value': value,
    if (unit != null) 'unit': unit,
  };
}
