import 'package:flutter/material.dart';

import 'app.dart';
import 'core/app_theme.dart';
import 'screens/home.dart';
import 'services/storage_service.dart';
import 'state/app_state.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final state = AppState(StorageService());
  await state.load();
  runApp(KarigarAiApp(state: state));
}

/// Backwards-compatible test entry point for the original home widget tests.
class ArtisanAiApp extends StatelessWidget {
  const ArtisanAiApp({super.key});
  @override
  Widget build(BuildContext context) =>
      MaterialApp(theme: AppTheme.light, home: const ArtisanHomePage());
}
