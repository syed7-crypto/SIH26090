import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../state/app_state.dart';
import '../app_shell.dart';
import 'onboarding_flow.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key, required this.state});
  final AppState state;
  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _open();
  }

  Future<void> _open() async {
    await Future<void>.delayed(const Duration(milliseconds: 700));
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (_) => widget.state.onboardingComplete
            ? const AppShell()
            : OnboardingFlow(state: widget.state),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => const Scaffold(
    body: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 38,
            backgroundColor: AppColors.deepForestGreen,
            child: Icon(Icons.auto_awesome, color: Colors.white, size: 38),
          ),
          SizedBox(height: 16),
          Text(
            'KarigarAI',
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.w800),
          ),
          SizedBox(height: 8),
          Text('Your craft, ready for the world.'),
        ],
      ),
    ),
  );
}
