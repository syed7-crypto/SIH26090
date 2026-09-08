import 'package:flutter/material.dart';

import '../../models/artisan.dart';
import '../../services/storage_service.dart';
import '../../state/app_state.dart';
import 'artisan_onboarding_screen.dart';
import 'language_select_screen.dart';
import 'welcome_screen.dart';

class OnboardingFlow extends StatefulWidget {
  const OnboardingFlow({super.key, required this.state});
  final AppState state;
  @override
  State<OnboardingFlow> createState() => _OnboardingFlowState();
}

class _OnboardingFlowState extends State<OnboardingFlow> {
  var _step = 0;
  String _language = 'English';
  @override
  void initState() {
    super.initState();
    _language = widget.state.language;
  }

  @override
  Widget build(BuildContext context) {
    if (_step == 0) {
      return WelcomeScreen(onContinue: () => setState(() => _step = 1));
    }
    if (_step == 1) {
      return LanguageSelectScreen(
        selected: _language,
        onSelected: (value) {
          widget.state.setLanguage(value);
          setState(() {
            _language = value;
            _step = 2;
          });
        },
      );
    }
    return ArtisanOnboardingScreen(
      onDone: (name, craft, region) async {
        await StorageService().saveArtisan(
          Artisan(
            name: name,
            craftType: craft,
            region: region,
            language: _language,
          ),
        );
        await widget.state.completeOnboarding();
      },
    );
  }
}
