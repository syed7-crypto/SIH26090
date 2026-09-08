import 'dart:io';

import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

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
    final file = path == null || path!.isEmpty ? null : File(path!);
    final image = file != null && file.existsSync()
        ? Image.file(
            file,
            width: width,
            height: height,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) => _fallback(),
          )
        : _fallback();
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
