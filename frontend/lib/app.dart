import 'package:flutter/material.dart';

import 'app_scope.dart';
import 'core/app_theme.dart';
import 'core/routes/route_generator.dart';
import 'screens/onboarding/splash_screen.dart';
import 'state/app_state.dart';

class KarigarAiApp extends StatelessWidget {
  const KarigarAiApp({super.key, required this.state});
  final AppState state;
  @override
  Widget build(BuildContext context) => AppScope(
    state: state,
    child: MaterialApp(
      title: 'KarigarAI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      onGenerateRoute: RouteGenerator.generate,
      home: SplashScreen(state: state),
    ),
  );
}
