import 'package:flutter/material.dart';

import '../../app_scope.dart';
import '../../core/theme/app_colors.dart';
import '../../widgets/common/mobile_viewport.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key, required this.onContinue});
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    final state = AppScope.maybeOf(context);
    String tr(String key, String fallback) => state?.translate(key) ?? fallback;
    return Scaffold(
      backgroundColor: AppColors.ivory,
      body: FloatingBubbles(
        child: SafeArea(
          child: MobileViewport(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22),
              child: Column(
                children: [
                  const SizedBox(height: 10),
                  const Text(
                    'KarigarAI',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                      color: AppColors.deepForestGreen,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    tr('welcome_tagline', 'Tradition Meets Technology'),
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppColors.secondaryText,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Container(
                    height: 190,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: AppColors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.border),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.charcoal.withValues(alpha: .05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: const Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.storefront_rounded,
                          size: 58,
                          color: AppColors.sageGreen,
                        ),
                        SizedBox(height: 12),
                        Text(
                          'Empowering Indian Artisans',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: AppColors.charcoal,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    tr(
                      'welcome_message',
                      'Turn your handmade products into market-ready digital listings using your voice and photos.',
                    ),
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 14,
                      height: 1.4,
                      color: AppColors.secondaryText,
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: onContinue,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.mutedTerracotta,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        tr('get_started', 'Get Started'),
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: OutlinedButton(
                      onPressed: onContinue,
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: AppColors.sageGreen),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        tr('existing_account', 'I Already Have an Account'),
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          color: AppColors.sageGreen,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
