import 'package:flutter/material.dart';

import '../../screens/app_shell.dart';
import 'app_routes.dart';

abstract final class RouteGenerator {
  static Route<dynamic> generate(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.home:
      default:
        return MaterialPageRoute<void>(builder: (_) => const AppShell());
    }
  }
}
