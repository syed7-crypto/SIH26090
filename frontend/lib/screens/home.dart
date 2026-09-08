import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../core/theme/app_colors.dart';
import '../models/product_draft.dart';
import '../widgets/common/local_product_image.dart';
import 'add_product.dart';

class ArtisanHomePage extends StatelessWidget {
  const ArtisanHomePage({super.key});
  @override
  Widget build(BuildContext context) {
    final state = AppScope.maybeOf(context);
    return state == null
        ? const _HomeBody(products: [])
        : ListenableBuilder(
            listenable: state,
            builder: (context, _) => _HomeBody(products: state.products),
          );
  }
}

class _HomeBody extends StatelessWidget {
  const _HomeBody({required this.products});
  final List<ProductDraft> products;
  @override
  Widget build(BuildContext context) {
    final state = AppScope.maybeOf(context);
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.auto_awesome, color: Colors.white),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                state?.translate('app_name') ?? 'Artisan AI',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        top: false,
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const CircleAvatar(child: Icon(Icons.person_outline)),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Hello, Artisan',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const Text('Let us share your craft with the world.'),
                      ],
                    ),
                  ),
                  const Icon(Icons.notifications_none_rounded),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                'Bring your craft\nto more people.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: AppColors.secondaryText,
                ),
              ),
              const SizedBox(height: 20),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.mutedTerracotta,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.add_circle, color: Colors.white, size: 34),
                    const SizedBox(height: 14),
                    Text(
                      'Create New Product',
                      style: theme.textTheme.titleLarge?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Turn your product into a market-ready listing',
                      style: TextStyle(color: Colors.white),
                    ),
                    const SizedBox(height: 14),
                    FilledButton.icon(
                      onPressed: () async {
                        state?.startDraft();
                        await Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (_) => const AddProductPage(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.add),
                      label: const Text('Add Product'),
                      style: FilledButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppColors.mutedTerracotta,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _Metric(
                      label: 'Total Products',
                      value: '${products.length}',
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Metric(
                      label: 'Drafts',
                      value:
                          '${products.where((p) => p.status == ProductStatus.draft).length}',
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Metric(
                      label: 'Ready',
                      value:
                          '${products.where((p) => p.status == ProductStatus.ready).length}',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 28),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Recent Products',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  const Text('View All >'),
                ],
              ),
              const Text('Your Products', style: TextStyle(fontSize: 0)),
              const SizedBox(height: 12),
              if (products.isEmpty)
                const _EmptyProductsCard()
              else
                for (final product in products.take(3))
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _HomeProductCard(product: product),
                  ),
              if (state?.activeDraft?.status == ProductStatus.draft)
                OutlinedButton.icon(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => const AddProductPage(),
                    ),
                  ),
                  icon: const Icon(Icons.edit_outlined),
                  label: const Text('Resume draft'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 6),
    decoration: BoxDecoration(
      color: AppColors.white,
      borderRadius: BorderRadius.circular(14),
      border: Border.all(color: AppColors.border),
    ),
    child: Column(
      children: [
        Text(value, style: const TextStyle(fontWeight: FontWeight.w800)),
        Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontSize: 10, color: AppColors.secondaryText),
        ),
      ],
    ),
  );
}

class _HomeProductCard extends StatelessWidget {
  const _HomeProductCard({required this.product});
  final ProductDraft product;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          LocalProductImage(
            path: product.photoPaths.isEmpty ? null : product.photoPaths.first,
            width: 76,
            height: 76,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product.name.isEmpty
                      ? 'UNTITLED PRODUCT'
                      : product.name.toUpperCase(),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  product.price == null
                      ? 'Price not set'
                      : '₹${product.price!.toStringAsFixed(0)}',
                ),
                _HomeStatus(status: product.status),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class _EmptyProductsCard extends StatelessWidget {
  const _EmptyProductsCard();
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Icon(Icons.inventory_2_outlined, size: 36),
          const SizedBox(height: 10),
          Text(
            'No products yet',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const Text(
            'Your products will appear here.\nStart by adding your first creation.',
            textAlign: TextAlign.center,
            softWrap: true,
          ),
        ],
      ),
    ),
  );
}

class _HomeStatus extends StatelessWidget {
  const _HomeStatus({required this.status});
  final ProductStatus status;

  @override
  Widget build(BuildContext context) {
    final state = AppScope.maybeOf(context);
    final color = switch (status) {
      ProductStatus.draft => Theme.of(context).colorScheme.tertiary,
      ProductStatus.ready => Theme.of(context).colorScheme.secondary,
      ProductStatus.published => Colors.green.shade700,
    };
    return Text(
      state?.translate(status.name) ?? status.name,
      style: TextStyle(color: color, fontWeight: FontWeight.w700),
    );
  }
}
