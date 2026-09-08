import 'package:flutter/material.dart';

import 'add_product.dart';
import '../services/firestore_service.dart';

class ArtisanHomePage extends StatefulWidget {
  const ArtisanHomePage({super.key, this.firestoreService});

  final FirestoreService? firestoreService;

  @override
  State<ArtisanHomePage> createState() => _ArtisanHomePageState();
}

class _ArtisanHomePageState extends State<ArtisanHomePage> {
  late final FirestoreService _firestoreService =
      widget.firestoreService ?? FirestoreService();
  List<Map<String, dynamic>> _products = const [];

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    try {
      await _firestoreService.getArtisan(FirestoreService.defaultArtisanId);
      final products = await _firestoreService.getProducts(
        FirestoreService.defaultArtisanId,
      );
      if (mounted) setState(() => _products = products);
    } on FirestoreServiceException {
      // Home remains usable offline; a future sync indicator can be added here.
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        titleSpacing: 20,
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
            Text(
              'Artisan AI',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        top: false,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Bring your craft\nto more people.',
                style: theme.textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.w800,
                  height: 1.1,
                  letterSpacing: -0.6,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: 14),
              Text(
                'Add your handmade products and let Artisan AI help you share their story.',
                style: theme.textTheme.bodyLarge?.copyWith(
                  height: 1.45,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                height: 58,
                child: FilledButton.icon(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => const AddProductPage(),
                      ),
                    );
                  },
                  icon: const Icon(Icons.add, size: 26),
                  label: const Text('Add Product'),
                  style: FilledButton.styleFrom(
                    textStyle: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 40),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'Your Products',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                  Text(
                    '${_products.length} ${_products.length == 1 ? 'item' : 'items'}',
                    style: theme.textTheme.labelLarge?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              if (_products.isEmpty)
                _EmptyProductsCard(theme: theme)
              else
                for (final product in _products)
                  _ProductCard(product: product, theme: theme),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProductCard extends StatelessWidget {
  const _ProductCard({required this.product, required this.theme});

  final Map<String, dynamic> product;
  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    final name = product['name'] as String?;
    final category = product['category'] as String?;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: theme.colorScheme.primaryContainer,
          child: Icon(
            Icons.inventory_2_outlined,
            color: theme.colorScheme.primary,
          ),
        ),
        title: Text(name == null || name.isEmpty ? 'Saved product' : name),
        subtitle: category == null || category.isEmpty ? null : Text(category),
      ),
    );
  }
}

class _EmptyProductsCard extends StatelessWidget {
  const _EmptyProductsCard({required this.theme});

  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.inventory_2_outlined,
              size: 30,
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),
          const SizedBox(height: 18),
          Text(
            'No products yet',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your products will appear here.\nStart by adding your first creation.',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              height: 1.45,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}
