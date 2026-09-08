import 'package:flutter/material.dart';

import '../models/voice_analysis.dart';

class VoiceResultsPage extends StatelessWidget {
  const VoiceResultsPage({super.key, required this.result});

  final VoiceAnalysisResult result;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final product = result.product;
    final fields = <String, String?>{
      'Product': product.name,
      'Material': product.material,
      'Category': product.category,
      'Subcategory': product.subcategory,
      'Craft type': product.craftType,
      'Colour': product.color,
      'Dimensions': _dimensions(product.dimensions),
      'Weight': _weight(product.weight),
      'Usage': product.usage,
      'Pattern': product.pattern,
      'Production time': product.productionTime,
    };
    final availableFields = fields.entries
        .where((entry) => entry.value != null && entry.value!.trim().isNotEmpty)
        .toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Voice Results')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'AI understood',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 20),
              _InfoCard(
                title: 'Language',
                child: Text(result.voice.languageCode ?? 'Not detected'),
              ),
              const SizedBox(height: 12),
              _InfoCard(
                title: 'What you said',
                child: Text(
                  result.voice.originalTranscript ?? 'No transcript available.',
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Product information',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              _InfoCard(
                title: availableFields.isEmpty ? 'No details found' : null,
                child: availableFields.isEmpty
                    ? const Text(
                        'No product details were found in the recording.',
                      )
                    : Column(
                        children: [
                          for (final field in availableFields)
                            _FieldRow(label: field.key, value: field.value!),
                        ],
                      ),
              ),
              if (result.missingFields.isNotEmpty) ...[
                const SizedBox(height: 20),
                Text(
                  'Still needed',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                ...result.missingFields.map(
                  (field) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Row(
                      children: [
                        const Text('•  '),
                        Text(_friendlyFieldName(field)),
                      ],
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Continue later'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.child});
  final String? title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null) ...[
              Text(
                title!,
                style: Theme.of(context).textTheme.titleSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
            ],
            child,
          ],
        ),
      ),
    );
  }
}

class _FieldRow extends StatelessWidget {
  const _FieldRow({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

String? _dimensions(VoiceDimensions dimensions) {
  final values = [dimensions.length, dimensions.width, dimensions.height]
      .whereType<double>()
      .map((value) => value.toStringAsFixed(value % 1 == 0 ? 0 : 1))
      .toList();
  if (values.isEmpty) return null;
  return '${values.join(' × ')}${dimensions.unit == null ? '' : ' ${dimensions.unit}'}';
}

String? _weight(VoiceWeight weight) {
  if (weight.value == null) return null;
  final value = weight.value!.toStringAsFixed(weight.value! % 1 == 0 ? 0 : 1);
  return '$value${weight.unit == null ? '' : ' ${weight.unit}'}';
}

String _friendlyFieldName(String field) {
  final words = field.split('_');
  return words
      .map(
        (word) => word.isEmpty
            ? word
            : '${word[0].toUpperCase()}${word.substring(1)}',
      )
      .join(' ')
      .replaceFirst('Color', 'Colour');
}
