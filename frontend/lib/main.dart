import 'package:flutter/material.dart';

import 'screens/home.dart';

void main() {
  runApp(const ArtisanAiApp());
}

class ArtisanAiApp extends StatelessWidget {
  const ArtisanAiApp({super.key});

  @override
  Widget build(BuildContext context) {
    const brandGreen = Color(0xFF176B5B);

    return MaterialApp(
      title: 'Artisan AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: brandGreen,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF9F7F2),
        useMaterial3: true,
        fontFamily: 'sans-serif',
      ),
      home: const ArtisanHomePage(),
    );
  }
}
