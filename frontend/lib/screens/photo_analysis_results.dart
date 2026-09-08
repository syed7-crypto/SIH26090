import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../models/photo_analysis.dart';
import 'voice_product.dart';

class PhotoAnalysisResultsPage extends StatelessWidget {
  const PhotoAnalysisResultsPage({
    super.key,
    required this.result,
    required this.localPhotos,
  });

  final PhotoAnalysisResult result;
  final List<XFile> localPhotos;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Photo Analysis Results')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Your photos are ready',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 20),
              _ReadinessCard(result: result),
              if (result.media.photoReadiness.enhanced > 0) ...[
                const SizedBox(height: 20),
                Text(
                  'AI improved your photos',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                const Text('Lighting, contrast, or sharpness was improved safely.'),
              ],
              if (result.media.recommendedPrimaryPath != null) ...[
                const SizedBox(height: 16),
                _PrimaryMetadataCard(
                  path: result.media.recommendedPrimaryPath!,
                ),
              ],
              const SizedBox(height: 24),
              Text(
                'Your product photos',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              for (var index = 0; index < result.media.images.length; index++)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: _AnalyzedPhotoCard(
                    analysis: result.media.images[index],
                    localPhoto: index < localPhotos.length
                        ? localPhotos[index]
                        : null,
                  ),
                ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton.icon(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => const VoiceProductPage(),
                      ),
                    );
                  },
                  icon: const Icon(Icons.mic_none_outlined),
                  label: const Text('Tell us about your product'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ReadinessCard extends StatelessWidget {
  const _ReadinessCard({required this.result});
  final PhotoAnalysisResult result;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final readiness = result.media.photoReadiness;
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            SizedBox(
              width: 72,
              height: 72,
              child: CircularProgressIndicator(
                value: readiness.score / 100,
                strokeWidth: 8,
                backgroundColor: theme.colorScheme.primaryContainer,
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'E-commerce readiness',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${readiness.score.toStringAsFixed(0)} / 100',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        _ReadinessCounts(readiness: readiness),
      ),
    );
  }
}

class _ReadinessCounts extends StatelessWidget {
  const _ReadinessCounts({required this.readiness});
  final PhotoReadiness readiness;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 6,
      children: [
        Text('${readiness.accepted} photos ready'),
        if (readiness.enhanced > 0) Text('${readiness.enhanced} improved'),
        if (readiness.removed > 0) Text('${readiness.removed} removed'),
        if (readiness.needsRetake > 0) Text('${readiness.needsRetake} to retake'),
      ],
    );
  }
}

class _TypeCard extends StatelessWidget {
  const _TypeCard({
    required this.title,
    required this.values,
    required this.emptyText,
  });
  final String title;
  final List<String> values;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: theme.textTheme.titleSmall),
            const SizedBox(height: 8),
            values.isEmpty
                ? Text(emptyText)
                : Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final value in values) Chip(label: Text(value)),
                    ],
                  ),
          ],
        ),
      ),
    );
  }
}

class _PrimaryMetadataCard extends StatelessWidget {
  const _PrimaryMetadataCard({required this.path});
  final String path;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: ListTile(
        leading: const Icon(Icons.star_outline),
        title: const Text('Recommended primary image'),
        subtitle: Text(path),
      ),
    );
  }
}

class _AnalyzedPhotoCard extends StatelessWidget {
  const _AnalyzedPhotoCard({required this.analysis, this.localPhoto});
  final PhotoImageAnalysis analysis;
  final XFile? localPhoto;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (localPhoto != null) _LocalPhotoPreview(photo: localPhoto!),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      analysis.photoType,
                      style: Theme.of(context).textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    if (analysis.isDuplicate)
                      const Chip(label: Text('Duplicate')),
                  ],
                ),
                const SizedBox(height: 12),
                _MetricRow(label: 'Quality', value: analysis.qualityScore),
                _MetricRow(label: 'Blur', value: analysis.blurScore),
                _MetricRow(
                  label: 'Brightness',
                  value: analysis.brightnessScore,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  const _MetricRow({required this.label, required this.value});
  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(label), Text(value.toStringAsFixed(1))],
      ),
    );
  }
}

class _LocalPhotoPreview extends StatelessWidget {
  const _LocalPhotoPreview({required this.photo});
  final XFile photo;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Uint8List>(
      future: photo.readAsBytes(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const SizedBox(
            height: 180,
            child: Center(child: CircularProgressIndicator()),
          );
        }
        return Image.memory(
          snapshot.data!,
          width: double.infinity,
          height: 180,
          fit: BoxFit.cover,
        );
      },
    );
  }
}
