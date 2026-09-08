import 'package:flutter/material.dart';

abstract final class AppColors {
  static const deepForestGreen = Color.fromARGB(255, 61, 4, 232);
  static const sageGreen = Color.fromARGB(255, 31, 189, 241);
  static const mutedTerracotta = Color.fromARGB(255, 123, 134, 146);
  static const ivory = Color(0xFFF8F5EF);
  static const white = Color(0xFFFFFFFF);
  static const charcoal = Color(0xFF17201D);
  static const secondaryText = Color(0xFF66716C);
  static const border = Color(0xFFE5E0D7);
  static const success = Color.fromARGB(255, 72, 66, 186);

  // Existing concise aliases retained for compatibility with current widgets.
  static const forest = deepForestGreen;
  static const sage = sageGreen;
  static const terracotta = mutedTerracotta;
}
