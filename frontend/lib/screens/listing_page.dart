import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../core/theme/app_colors.dart';
import '../models/product_draft.dart';
import '../widgets/common/local_product_image.dart';
import '../widgets/common/karigar_design.dart';

class ListingPage extends StatelessWidget {
  const ListingPage({super.key});
  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    final draft = state.activeDraft;
    if (draft == null) {
      return const Scaffold(
        body: Center(child: Text('No product draft open.')),
      );
    }
    final saveStatus = draft.status == ProductStatus.published
        ? ProductStatus.published
        : draft.readiness >= 80
        ? ProductStatus.ready
        : ProductStatus.draft;
    return Scaffold(
      appBar: AppBar(title: const Text('Your Listing is Ready!')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const FlowStepper(currentStep: 5),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.success.withValues(alpha: .12),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Row(
                children: [
                  Icon(Icons.celebration_rounded, color: AppColors.success),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Your product has been converted into a market-ready digital listing',
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    LocalProductImage(
                      path: draft.photoPaths.isEmpty
                          ? null
                          : draft.photoPaths.first,
                      height: 180,
                      width: double.infinity,
                      borderRadius: 14,
                    ),
                    const SizedBox(height: 18),
                    Text(
                      draft.name.isEmpty
                          ? 'UNTITLED PRODUCT'
                          : draft.name.toUpperCase(),
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      draft.description.isEmpty
                          ? 'Add a description before publishing.'
                          : draft.description,
                    ),
                    const SizedBox(height: 14),
                    Text(
                      draft.price == null
                          ? 'Price not set'
                          : '₹${draft.price!.toStringAsFixed(0)}',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    Chip(
                      label: Text(
                        draft.readiness >= 85
                            ? 'Market ready'
                            : 'Needs a few details',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: () async {
                await state.saveActive(status: saveStatus);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Product saved to My Products.'),
                    ),
                  );
                }
              },
              icon: const Icon(Icons.save_outlined),
              label: Text('Save as ${saveStatus.name}'),
            ),
            if (draft.readiness >= 80)
              FilledButton.icon(
                onPressed: () async {
                  await state.publishActive();
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Product published to Marketplace.'),
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.public),
                label: const Text('Publish to Marketplace'),
              ),
            OutlinedButton.icon(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Share integration can be added when a sharing package is approved.',
                    ),
                  ),
                );
              },
              icon: const Icon(Icons.share_outlined),
              label: const Text('Share listing'),
            ),
          ],
        ),
      ),
    );
  }
}
