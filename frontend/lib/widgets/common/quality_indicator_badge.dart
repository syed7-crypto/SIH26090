import 'package:flutter/material.dart';

class QualityIndicatorBadge extends StatelessWidget {
  const QualityIndicatorBadge({
    super.key,
    required this.label,
    required this.good,
  });
  final String label;
  final bool good;
  @override
  Widget build(BuildContext context) => Chip(
    avatar: Icon(
      good ? Icons.check_circle : Icons.info_outline,
      color: good ? Colors.green : Colors.orange,
    ),
    label: Text(label),
  );
}
