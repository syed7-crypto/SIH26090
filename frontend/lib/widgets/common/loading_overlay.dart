import 'package:flutter/material.dart';

class LoadingOverlay extends StatelessWidget {
  const LoadingOverlay({
    super.key,
    required this.loading,
    required this.child,
    this.label = 'Please wait…',
  });
  final bool loading;
  final Widget child;
  final String label;

  @override
  Widget build(BuildContext context) => Stack(
    children: [
      child,
      if (loading)
        Positioned.fill(
          child: ColoredBox(
            color: Colors.black45,
            child: Center(
              child: Semantics(
                label: label,
                child: const CircularProgressIndicator(),
              ),
            ),
          ),
        ),
    ],
  );
}
