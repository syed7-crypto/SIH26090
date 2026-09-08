import 'package:flutter/material.dart';

class ArtisanOnboardingScreen extends StatefulWidget {
  const ArtisanOnboardingScreen({super.key, required this.onDone});
  final void Function(String name, String craft, String region) onDone;
  @override
  State<ArtisanOnboardingScreen> createState() =>
      _ArtisanOnboardingScreenState();
}

class _ArtisanOnboardingScreenState extends State<ArtisanOnboardingScreen> {
  final _name = TextEditingController();
  final _craft = TextEditingController();
  final _region = TextEditingController();
  @override
  void dispose() {
    _name.dispose();
    _craft.dispose();
    _region.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tell us about you')),
    body: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'This helps us make your product listings feel personal.',
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _name,
              decoration: const InputDecoration(labelText: 'Your name'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _craft,
              decoration: const InputDecoration(labelText: 'Your craft'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _region,
              decoration: const InputDecoration(
                labelText: 'Your town or region',
              ),
            ),
            const Spacer(),
            FilledButton(
              onPressed: () => widget.onDone(
                _name.text.trim(),
                _craft.text.trim(),
                _region.text.trim(),
              ),
              child: const Text('Continue to KarigarAI'),
            ),
          ],
        ),
      ),
    ),
  );
}
