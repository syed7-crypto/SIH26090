import 'package:flutter/material.dart';

import '../../app_scope.dart';
import '../../widgets/common/local_product_image.dart';
import '../add_product.dart';

class MyProductsScreen extends StatelessWidget {
  const MyProductsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('My Products')),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: state,
          builder: (context, _) => SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.search),
                    hintText: 'Search products...',
                  ),
                ),
                const SizedBox(height: 12),
                const Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(label: Text('All')),
                    Chip(label: Text('Draft')),
                    Chip(label: Text('Ready')),
                    Chip(label: Text('Published')),
                  ],
                ),
                const SizedBox(height: 16),
                if (state.products.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 36),
                    child: Center(
                      child: Text(
                        'No products yet. Create your first listing.',
                      ),
                    ),
                  )
                else
                  GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: state.products.length,
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                          childAspectRatio: .8,
                        ),
                    itemBuilder: (context, index) {
                      final product = state.products[index];
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(10),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              LocalProductImage(
                                path: product.photoPaths.isEmpty
                                    ? null
                                    : product.photoPaths.first,
                                height: 92,
                                width: double.infinity,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                product.name.isEmpty
                                    ? 'UNTITLED PRODUCT'
                                    : product.name.toUpperCase(),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              Text(
                                product.price == null
                                    ? 'Price not set'
                                    : '₹${product.price!.toStringAsFixed(0)}',
                              ),
                              Text(product.status.name),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                const SizedBox(height: 20),
                FilledButton.icon(
                  onPressed: () {
                    state.startDraft();
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => const AddProductPage(),
                      ),
                    );
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('Create New Product'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
