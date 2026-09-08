import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../models/voice_analysis.dart';
import 'pricing_page.dart';

class ProductReviewPage extends StatefulWidget {
  const ProductReviewPage({super.key, required this.result});
  final VoiceAnalysisResult result;
  @override
  State<ProductReviewPage> createState() => _ProductReviewPageState();
}

class _ProductReviewPageState extends State<ProductReviewPage> {
  late final Map<String, TextEditingController> _controllers;
  @override
  void initState() {
    super.initState();
    final product = widget.result.product;
    _controllers = {
      'name': TextEditingController(text: product.name ?? ''),
      'category': TextEditingController(text: product.category ?? ''),
      'material': TextEditingController(text: product.material ?? ''),
      'colour': TextEditingController(text: product.color ?? ''),
      'craft': TextEditingController(text: product.craftType ?? ''),
      'dimensions': TextEditingController(text: _dimensions(product)),
      'description': TextEditingController(
        text:
            product.description ?? widget.result.voice.originalTranscript ?? '',
      ),
    };
  }

  @override
  void dispose() {
    for (final controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  String _dimensions(VoiceProductInfo product) {
    final values =
        [
          product.dimensions.length,
          product.dimensions.width,
          product.dimensions.height,
        ].whereType<double>().map(
          (value) => value.toStringAsFixed(value % 1 == 0 ? 0 : 1),
        );
    return values.isEmpty
        ? ''
        : '${values.join(' × ')} ${product.dimensions.unit ?? ''}'.trim();
  }

  Future<void> _continue() async {
    final state = AppScope.of(context);
    final current = state.activeDraft ?? state.startDraft();
    final draft = current.copyWith(
      name: _controllers['name']!.text.trim(),
      category: _controllers['category']!.text.trim(),
      material: _controllers['material']!.text.trim(),
      colour: _controllers['colour']!.text.trim(),
      craftType: _controllers['craft']!.text.trim(),
      dimensions: _controllers['dimensions']!.text.trim(),
      description: _controllers['description']!.text.trim(),
      voiceTranscript: widget.result.voice.originalTranscript ?? '',
    );
    await state.updateDraft(draft);
    if (mounted) {
      Navigator.of(context)
          .push(MaterialPageRoute<void>(builder: (_) => const PricingPage()));
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Review your product')),
    body: SafeArea(
      child: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Text(
                  'Check the details',
                  style: Theme.of(context).textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 8),
                const Text(
                  'We filled these from your voice. Change anything that is not right.',
                ),
                const SizedBox(height: 20),
                for (final item in [
                  ('name', 'Product name'),
                  ('category', 'Category'),
                  ('material', 'Material'),
                  ('colour', 'Colour'),
                  ('craft', 'Craft type'),
                  ('dimensions', 'Dimensions'),
                  ('description', 'Description'),
                ])
                  Padding(
                    padding: const EdgeInsets.only(bottom: 14),
                    child: TextField(
                      controller: _controllers[item.$1],
                      maxLines: item.$1 == 'description' ? 3 : 1,
                      decoration: InputDecoration(labelText: item.$2),
                    ),
                  ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: FilledButton(
              onPressed: _continue,
              child: const Text('Continue to price'),
            ),
          ),
        ],
      ),
    ),
  );
}
