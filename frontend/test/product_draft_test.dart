import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/models/product_draft.dart';

void main() {
  test('retains no more than ten product photo paths', () {
    final draft = ProductDraft.empty('ART-001')
        .copyWith(photoPaths: List.generate(11, (index) => '$index.jpg'));

    expect(draft.photoPaths, List.generate(10, (index) => '$index.jpg'));
  });

  test('awards the full image readiness weight for two photos', () {
    final onePhoto = ProductDraft.empty('ART-001')
        .copyWith(photoPaths: const ['one.jpg']);
    final twoPhotos = ProductDraft.empty('ART-002')
        .copyWith(photoPaths: const ['one.jpg', 'two.jpg']);

    expect(onePhoto.readiness, 10);
    expect(twoPhotos.readiness, 20);
  });

  test('normalizes user-entered product labels to uppercase', () {
    final draft = ProductDraft.empty('ART-003').copyWith(
      name: 'Handcrafted clay pot',
      category: 'Traditional pottery',
      craftType: 'Handmade pottery',
    );

    expect(draft.name, 'HANDCRAFTED CLAY POT');
    expect(draft.category, 'TRADITIONAL POTTERY');
    expect(draft.craftType, 'HANDMADE POTTERY');
  });
}
