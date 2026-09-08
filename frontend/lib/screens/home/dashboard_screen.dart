import 'package:flutter/material.dart';

import '../home.dart';

/// Canonical dashboard path; behavior lives in the tested home implementation.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});
  @override
  Widget build(BuildContext context) => const ArtisanHomePage();
}
