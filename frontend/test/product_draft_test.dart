import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/models/product_draft.dart';

void main() {
  test('retains no more than two product photo paths', () {
    final draft = ProductDraft.empty('ART-001')
        .copyWith(photoPaths: const ['one.jpg', 'two.jpg', 'three.jpg']);

    expect(draft.photoPaths, const ['one.jpg', 'two.jpg']);
  });

  test('awards the full image readiness weight for two photos', () {
    final onePhoto = ProductDraft.empty('ART-001')
        .copyWith(photoPaths: const ['one.jpg']);
    final twoPhotos = ProductDraft.empty('ART-002')
        .copyWith(photoPaths: const ['one.jpg', 'two.jpg']);

    expect(onePhoto.readiness, 10);
    expect(twoPhotos.readiness, 20);
  });
}
