import 'package:flutter/foundation.dart';

import '../models/artisan.dart';
import '../services/storage_service.dart';

class ArtisanProvider extends ChangeNotifier {
  ArtisanProvider(this._storage);
  final StorageService _storage;
  Artisan _artisan = const Artisan();
  Artisan get artisan => _artisan;
  Future<void> load() async {
    _artisan = await _storage.loadArtisan();
    notifyListeners();
  }

  Future<void> update(Artisan artisan) async {
    _artisan = artisan;
    await _storage.saveArtisan(artisan);
    notifyListeners();
  }
}
