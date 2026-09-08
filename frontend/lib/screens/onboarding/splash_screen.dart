import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});
  @override
  Widget build(BuildContext context) => const Scaffold(
    body: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 38,
            backgroundColor: AppColors.forest,
            child: Icon(Icons.auto_awesome, color: Colors.white, size: 38),
          ),
          SizedBox(height: 16),
          Text(
            'KarigarAI',
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.w800),
          ),
          SizedBox(height: 8),
          Text('Your craft, ready for the world.'),
        ],
      ),
    ),
  );
}
