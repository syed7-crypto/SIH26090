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
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 12),
            const Text(
              'KarigarAI',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.deepForestGreen,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              tr('welcome_tagline', 'Tradition Meets Technology'),
              style: const TextStyle(fontSize: 14, color: AppColors.secondaryText),
            ),
            const SizedBox(height: 24),
            Container(
              height: 190,
              width: double.infinity,
              decoration: BoxDecoration(
                color: AppColors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.border),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: .04),
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
                  SizedBox(height: 16),
                  Text(
                    'Empowering Indian Artisans',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: AppColors.charcoal,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Text(
              tr('welcome_message', 'Turn your handmade products into market-ready digital listings using your voice and photos.'),
              textAlign: TextAlign.center,
              softWrap: true,
              style: TextStyle(color: AppColors.secondaryText, height: 1.4),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.mutedTerracotta,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: onContinue,
                child: Text(
                  tr('get_started', 'Get Started'),
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: OutlinedButton(
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppColors.sageGreen),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: onContinue,
                child: Text(
                  tr('existing_account', 'I Already Have an Account'),
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
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
      ),
    );
  }
}
