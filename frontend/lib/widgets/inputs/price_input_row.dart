import 'package:flutter/material.dart';

class PriceInputRow extends StatelessWidget {
  const PriceInputRow({
    super.key,
    required this.label,
    required this.controller,
  });
  final String label;
  final TextEditingController controller;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: TextField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label, prefixText: '₹ '),
    ),
  );
}
