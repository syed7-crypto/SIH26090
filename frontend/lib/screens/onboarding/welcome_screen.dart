import 'package:flutter/material.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key, required this.onContinue});
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Spacer(),
            Icon(
              Icons.handyman_outlined,
              size: 72,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 28),
            Text(
              'Bring your craft to more people.',
              style: Theme.of(context).textTheme.displaySmall
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            const Text(
              'KarigarAI helps you use photos and your own voice to prepare a clear product listing.',
            ),
            const Spacer(),
            FilledButton(
              onPressed: onContinue,
              child: const Text('Get started'),
            ),
          ],
        ),
      ),
    ),
  );
}
