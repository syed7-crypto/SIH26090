import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../widgets/common/karigar_design.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key, required this.onContinue});
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            minHeight: MediaQuery.sizeOf(context).height - 48,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              const BrandMark(size: 62),
              const SizedBox(height: 22),
              Text(
                'Welcome, Artisan',
                style: Theme.of(context).textTheme.displaySmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 16),
              const Text(
                'Turn your handmade products into market-ready digital listings using your voice and photos.',
                softWrap: true,
              ),
              const SizedBox(height: 28),
              Container(
                height: 220,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: AppColors.sageGreen.withValues(alpha: .13),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.auto_awesome_rounded,
                      size: 74,
                      color: AppColors.deepForestGreen,
                    ),
                    SizedBox(height: 12),
                    Text(
                      'Your craft has a story to tell',
                      style: TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              FilledButton(
                onPressed: onContinue,
                child: const Text('Get Started'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: onContinue,
                child: const Text('I Already Have an Account'),
              ),
              const SizedBox(height: 18),
              const Wrap(
                alignment: WrapAlignment.center,
                spacing: 8,
                runSpacing: 8,
                children: [
                  _FeatureTag('Simple'),
                  _FeatureTag('Voice Enabled'),
                  _FeatureTag('AI Powered'),
                ],
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class _FeatureTag extends StatelessWidget {
  const _FeatureTag(this.label);
  final String label;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
    decoration: BoxDecoration(
      color: AppColors.white,
      borderRadius: BorderRadius.circular(99),
      border: Border.all(color: AppColors.border),
    ),
    child: Text(
      label,
      style: const TextStyle(fontSize: 12, color: AppColors.sageGreen),
    ),
  );
}
