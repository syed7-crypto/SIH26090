import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app_scope.dart';
import 'core/app_theme.dart';
import 'core/routes/route_generator.dart';
import 'screens/onboarding/splash_screen.dart';
import 'services/storage_service.dart';
import 'state/app_state.dart';
import 'providers/artisan_provider.dart';
import 'providers/language_provider.dart';

class KarigarAiApp extends StatelessWidget {
  const KarigarAiApp({super.key, required this.state});
  final AppState state;
  @override
  Widget build(BuildContext context) => MultiProvider(
    providers: [
      ChangeNotifierProvider<AppState>.value(value: state),
      ChangeNotifierProvider(
        create: (_) => ArtisanProvider(StorageService())..load(),
      ),
      ChangeNotifierProvider(
        create: (_) =>
            LanguageProvider(StorageService(), initialLanguage: state.language),
      ),
    ],
    child: AppScope(
      state: state,
      child: MaterialApp(
        title: 'KarigarAI',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        onGenerateRoute: RouteGenerator.generate,
        home: SplashScreen(state: state),
      ),
    ),
  );
}
