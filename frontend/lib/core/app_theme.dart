import 'package:flutter/material.dart';

import 'theme/app_colors.dart';

abstract final class AppTheme {
  static const forest = AppColors.deepForestGreen;
  static const sage = AppColors.sageGreen;
  static const terracotta = AppColors.mutedTerracotta;
  static const ivory = AppColors.ivory;
  static const charcoal = AppColors.charcoal;
  static const secondaryText = AppColors.secondaryText;
  static const border = AppColors.border;
  static const success = AppColors.success;

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: ivory,
    colorScheme: ColorScheme.fromSeed(
      seedColor: forest,
      primary: forest,
      secondary: sage,
      tertiary: terracotta,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: ivory,
      foregroundColor: charcoal,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: border),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: terracotta,
        foregroundColor: Colors.white,
        minimumSize: const Size.fromHeight(56),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: border),
      ),
    ),
  );
}
