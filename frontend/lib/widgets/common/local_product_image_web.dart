import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

/// Browser implementation: image-picker paths are browser/blob URLs, not files.
class LocalProductImage extends StatelessWidget {
  const LocalProductImage({
    super.key,
    required this.path,
    this.height,
    this.width,
    this.borderRadius = 12,
  });
  final String? path;
  final double? height;
  final double? width;
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    final source = path;
    final image = source == null || source.isEmpty
        ? _fallback()
        : Image.network(
            source,
            width: width,
            height: height,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) => _fallback(),
          );
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: SizedBox(width: width, height: height, child: image),
    );
  }

  Widget _fallback() => const ColoredBox(
    color: AppColors.ivory,
    child: Center(
      child: Icon(
        Icons.image_not_supported_rounded,
        color: AppColors.secondaryText,
        size: 34,
      ),
    ),
  );
}
