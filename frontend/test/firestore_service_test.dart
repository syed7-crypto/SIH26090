import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/models/voice_analysis.dart';
import 'package:frontend/services/firestore_service.dart';

void main() {
  test(
    'maps available voice product fields without inventing missing values',
    () {
      const product = VoiceProductInfo(
        name: 'Silk scarf',
        category: 'Textiles',
        material: 'Silk',
        dimensions: VoiceDimensions(length: 6, width: 2, unit: 'ft'),
        weight: VoiceWeight(value: 120, unit: 'g'),
        specialFeatures: ['Hand-woven'],
      );

      final data = FirestoreService.voiceProductData(product);

      expect(data['name'], 'Silk scarf');
      expect(data['category'], 'Textiles');
      expect(data['material'], 'Silk');
      expect(data['dimensions'], {'length': 6, 'width': 2, 'unit': 'ft'});
      expect(data['weight'], {'value': 120, 'unit': 'g'});
      expect(data['specialFeatures'], ['Hand-woven']);
      expect(data.containsKey('color'), isFalse);
      expect(data.containsKey('craftType'), isFalse);
    },
  );

  test('does not persist empty nested voice values', () {
    final data = FirestoreService.voiceProductData(
      VoiceProductInfo(
        dimensions: VoiceDimensions(),
        weight: VoiceWeight(),
        specialFeatures: [],
      ),
    );

    expect(data, isEmpty);
  });
}
