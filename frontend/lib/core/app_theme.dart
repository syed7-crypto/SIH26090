import 'package:flutter/material.dart';

abstract final class AppTheme {
  static const forest = Color(0xFF123C35);
  static const sage = Color(0xFF1F5C50);
  static const terracotta = Color(0xFFC8753D);
  static const ivory = Color(0xFFF8F5EF);
  static const charcoal = Color(0xFF17201D);
  static const secondaryText = Color(0xFF66716C);
  static const border = Color(0xFFE5E0D7);
  static const success = Color(0xFF3E7658);

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: ivory,
    colorScheme: ColorScheme.fromSeed(
      seedColor: forest,
      primary: forest,
      secondary: terracotta,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: ivory,
      foregroundColor: charcoal,
      elevation: 0,
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: border),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
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
