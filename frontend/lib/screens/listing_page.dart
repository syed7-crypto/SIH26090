import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../models/product_draft.dart';

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
    return Scaffold(
      appBar: AppBar(title: const Text('Your market-ready listing')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      height: 180,
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Center(
                        child: Icon(Icons.inventory_2_outlined, size: 60),
                      ),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      draft.name.isEmpty ? 'Untitled product' : draft.name,
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
                await state.saveActive(status: ProductStatus.published);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Product saved to My Products.'),
                    ),
                  );
                }
              },
              icon: const Icon(Icons.save_outlined),
              label: const Text('Save product'),
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
