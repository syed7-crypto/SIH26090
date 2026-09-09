import 'package:flutter/material.dart';

import '../../app_scope.dart';
import '../../services/firestore_service.dart';
import '../home.dart';
import 'artisan_onboarding_screen.dart';
import 'language_select_screen.dart';
import 'welcome_screen.dart';

class OnboardingFlow extends StatefulWidget {
  const OnboardingFlow({super.key});

  @override
  State<OnboardingFlow> createState() => _OnboardingFlowState();
}

class _OnboardingFlowState extends State<OnboardingFlow> {
  var _step = 0;
  String _language = 'English';
  final FirestoreService _firestoreService = FirestoreService();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _language = AppScope.maybeOf(context)?.language ?? _language;
  }

  @override
  Widget build(BuildContext context) {
    if (_step == 0) {
      return WelcomeScreen(onContinue: () => setState(() => _step = 1));
    }
    if (_step == 1) {
      return LanguageSelectScreen(
        selected: _language,
        onSelected: (value) => setState(() => _language = value),
        onContinue: () {
          AppScope.maybeOf(context)?.setLanguage(_language);
          setState(() => _step = 2);
        },
      );
    }
    return ArtisanOnboardingScreen(
      onDone: (name, craft, region) async {
        final state = AppScope.maybeOf(context);
        if (state == null) {
          throw StateError('AppState is not available for onboarding.');
        }

        await _firestoreService.saveArtisan(
          artisanId: FirestoreService.defaultArtisanId,
          name: name,
          craftType: craft,
          region: region,
          language: _language,
          onboardingComplete: true,
        );
        if (!mounted) return;
        state.completeOnboarding();
        await Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute<void>(builder: (_) => const ArtisanHomePage()),
          (route) => false,
        );
      },
    );
  }
}
