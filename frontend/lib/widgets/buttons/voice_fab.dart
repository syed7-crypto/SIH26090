import 'package:flutter/material.dart';

class VoiceFab extends StatelessWidget {
  const VoiceFab({super.key, required this.onPressed});
  final VoidCallback onPressed;
  @override
  Widget build(BuildContext context) => FloatingActionButton.extended(
    onPressed: onPressed,
    icon: const Icon(Icons.mic_none_outlined),
    label: const Text('Speak'),
  );
}
