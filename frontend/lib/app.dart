import 'package:flutter/material.dart';

import 'app_scope.dart';
import 'core/app_theme.dart';
import 'screens/app_shell.dart';
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
      home: const AppShell(),
    ),
  );
}
