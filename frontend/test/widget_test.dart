import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';
import 'package:frontend/screens/add_product.dart';

void main() {
  testWidgets('shows the artisan home page', (WidgetTester tester) async {
    await tester.pumpWidget(const ArtisanAiApp());

    expect(find.text('Artisan AI'), findsOneWidget);
    expect(find.text('Bring your craft\nto more people.'), findsOneWidget);
    expect(find.text('Add Product'), findsOneWidget);
    expect(find.text('Your Products'), findsOneWidget);
    expect(find.text('No products yet'), findsOneWidget);
  });

  testWidgets('add product opens the photo upload screen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ArtisanAiApp());

    await tester.tap(find.text('Add Product'));
    await tester.pumpAndSettle();

    // Verify the actual user-visible destination reached by Home's route.
    expect(find.text('Add photos of your product'), findsOneWidget);
    expect(find.text('Take photo'), findsOneWidget);
    expect(find.text('Choose photos'), findsOneWidget);
    expect(find.text('Continue →'), findsOneWidget);
  });

  testWidgets('continue is disabled before two photos are selected', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: AddProductPage(productId: 'TEST-PRODUCT')),
    );

    final continueButton = tester.widget<FilledButton>(
      find.ancestor(
        of: find.text('Continue →'),
        matching: find.byType(FilledButton),
      ),
    );
    expect(continueButton.onPressed, isNull);
  });
}
