// ignore_for_file: deprecated_member_use

import 'package:flutter/material.dart';

import '../../core/constants/languages.dart';

class LanguageSelectScreen extends StatelessWidget {
  const LanguageSelectScreen({
    super.key,
    required this.selected,
    required this.onSelected,
  });
  final String selected;
  final ValueChanged<String> onSelected;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Choose your language')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('You can change this later in Profile.'),
        const SizedBox(height: 12),
        for (final language in supportedLanguages)
          Card(
            child: RadioListTile<String>(
              value: language,
              groupValue: selected,
              title: Text(language),
              onChanged: (value) {
                if (value != null) onSelected(value);
              },
            ),
          ),
      ],
    ),
  );
}
