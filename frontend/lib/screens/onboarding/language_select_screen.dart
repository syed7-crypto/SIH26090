import 'package:flutter/material.dart';

import '../../core/constants/languages.dart';

class LanguageSelectScreen extends StatelessWidget {
  const LanguageSelectScreen({
    super.key,
    required this.selected,
    required this.onSelected,
    required this.onContinue,
  });
  final String selected;
  final ValueChanged<String> onSelected;
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Choose your language')),
    body: SafeArea(
      child: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Choose Your Language',
                    style: Theme.of(context).textTheme.headlineSmall
                        ?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  const Text('You can speak in your preferred language.'),
                  const SizedBox(height: 24),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    childAspectRatio: 2.35,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    children: [
                      for (final language in supportedLanguages)
                        _LanguageTile(
                          language: language,
                          selected: selected == language,
                          onTap: () => onSelected(language),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: FilledButton(
              onPressed: onContinue,
              child: const Text('Continue'),
            ),
          ),
        ],
      ),
    ),
  );
}

class _LanguageTile extends StatelessWidget {
  const _LanguageTile({
    required this.language,
    required this.selected,
    required this.onTap,
  });
  final String language;
  final bool selected;
  final VoidCallback onTap;
  static const scripts = {
    'English': 'English',
    'Hindi': 'हिन्दी',
    'Kannada': 'ಕನ್ನಡ',
    'Marathi': 'मराठी',
    'Tamil': 'தமிழ்',
    'Telugu': 'తెలుగు',
    'Bengali': 'বাংলা',
    'Malayalam': 'മലയാളം',
  };
  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(16),
    child: AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      decoration: BoxDecoration(
        color: selected
            ? Theme.of(context).colorScheme.primaryContainer
            : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: selected
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).dividerColor,
          width: selected ? 2 : 1,
        ),
      ),
      child: Center(
        child: Text(
          scripts[language] ?? language,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
    ),
  );
}
