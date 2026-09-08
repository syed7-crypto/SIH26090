import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/core/constants/languages.dart';

void main() {
  test(
    'every supported language has the visible welcome and dashboard labels',
    () {
      const keys = [
        'welcome_tagline',
        'welcome_message',
        'get_started',
        'existing_account',
        'hello_artisan',
        'home_support',
        'create_new_product',
        'create_support',
        'total_products',
        'recent_products',
        'view_all',
      ];

      for (final language in supportedLanguages) {
        final dictionary = translations[languageCodeFor(language)];
        expect(dictionary, isNotNull, reason: '$language has a dictionary');
        for (final key in keys) {
          expect(
            dictionary![key],
            isNotNull,
            reason: '$language translates $key',
          );
        }
      }
    },
  );
}
