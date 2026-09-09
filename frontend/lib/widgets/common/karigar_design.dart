import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class BrandMark extends StatelessWidget {
  const BrandMark({super.key, this.size = 52});
  final double size;

  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: AppColors.ivory,
      borderRadius: BorderRadius.circular(size * .32),
      border: Border.all(color: AppColors.terracotta, width: 2),
    ),
    child: Stack(
      alignment: Alignment.center,
      children: [
        Icon(
          Icons.local_florist_rounded,
          color: AppColors.sage,
          size: size * .6,
        ),
        Positioned(
          bottom: size * .12,
          child: Icon(
            Icons.emoji_food_beverage_rounded,
            color: AppColors.terracotta,
            size: size * .38,
          ),
        ),
      ],
    ),
  );
}

class FlowStepper extends StatelessWidget {
  const FlowStepper({super.key, required this.currentStep});
  final int currentStep;
  static const _labels = ['Photos', 'Voice', 'AI', 'Price', 'Listing'];

  @override
  Widget build(BuildContext context) => Row(
    children: List.generate(_labels.length, (index) {
      final step = index + 1;
      final complete = step < currentStep;
      final active = step == currentStep;
      final color = complete || active
          ? AppColors.terracotta
          : AppColors.border;
      return Expanded(
        child: Column(
          children: [
            Row(
              children: [
                if (index > 0)
                  Expanded(child: Container(height: 2, color: color)),
                CircleAvatar(
                  radius: 12,
                  backgroundColor: color,
                  child: complete
                      ? const Icon(Icons.check, size: 15, color: Colors.white)
                      : Text(
                          '$step',
                          style: TextStyle(
                            fontSize: 12,
                            color: active
                                ? Colors.white
                                : AppColors.secondaryText,
                          ),
                        ),
                ),
                if (index < _labels.length - 1)
                  Expanded(
                    child: Container(
                      height: 2,
                      color: step < currentStep
                          ? AppColors.terracotta
                          : AppColors.border,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 5),
            Text(
              _labels[index],
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 10,
                color: active
                    ? AppColors.deepForestGreen
                    : AppColors.secondaryText,
                fontWeight: active ? FontWeight.w700 : FontWeight.w500,
              ),
            ),
          ],
        ),
      );
    }),
  );
}

class ScoreRing extends StatelessWidget {
  const ScoreRing({
    super.key,
    required this.score,
    this.label = 'Readiness',
    this.size = 150,
  });
  final int score;
  final String label;
  final double size;
  @override
  Widget build(BuildContext context) {
    final value = score.clamp(0, 100) / 100;
    final color = score >= 80 ? AppColors.success : AppColors.warning;
    return SizedBox(
      height: size,
      width: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            height: size,
            width: size,
            child: CircularProgressIndicator(
              value: value,
              strokeWidth: 11,
              backgroundColor: AppColors.border,
              color: color,
              strokeCap: StrokeCap.round,
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '$score%',
                style: TextStyle(
                  fontSize: size * .22,
                  fontWeight: FontWeight.w800,
                  color: AppColors.charcoal,
                ),
              ),
              Text(
                label,
                style: const TextStyle(color: AppColors.secondaryText),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class CheckRow extends StatelessWidget {
  const CheckRow({super.key, required this.label, this.complete = true});
  final String label;
  final bool complete;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 7),
    child: Row(
      children: [
        Icon(
          complete ? Icons.check_circle_rounded : Icons.warning_amber_rounded,
          color: complete ? AppColors.success : AppColors.warning,
        ),
        const SizedBox(width: 10),
        Expanded(child: Text(label, softWrap: true)),
      ],
    ),
  );
}
