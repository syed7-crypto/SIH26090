import 'package:flutter/material.dart';

import '../../app_scope.dart';
import '../../core/constants/languages.dart';

/// Canonical language-selection route used by the standalone flow.
class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  static const _scripts = <String, String>{
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
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Choose your language')),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Choose Your Language',
                style: Theme.of(context).textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              const Text('You can speak in your preferred language.'),
              const SizedBox(height: 24),
              ListenableBuilder(
                listenable: state,
                builder: (context, _) => GridView.count(
                  crossAxisCount: 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 2.3,
                  children: [
                    for (final language in supportedLanguages)
                      _LanguageTile(
                        label: _scripts[language] ?? language,
                        selected: state.language == language,
                        onTap: () => state.setLanguage(language),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              FilledButton(
                onPressed: () =>
                    Navigator.of(context).pushReplacementNamed('/home'),
                child: const Text('Continue'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LanguageTile extends StatelessWidget {
  const _LanguageTile({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(16),
    child: Container(
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: selected
            ? Theme.of(context).colorScheme.primaryContainer
            : Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: selected
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).dividerColor,
          width: selected ? 2 : 1,
        ),
      ),
      child: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
    ),
  );
}
