import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../app_scope.dart';
import '../core/app_theme.dart';
import '../models/product_draft.dart';
import '../providers/language_provider.dart';
import '../widgets/common/local_product_image.dart';
import 'add_product.dart';
import 'home.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _index = 0;

  void _create() {
    AppScope.of(context).startDraft();
    Navigator.of(context)
        .push(MaterialPageRoute<void>(builder: (_) => const AddProductPage()));
  }

  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    return ListenableBuilder(
      listenable: state,
      builder: (context, _) {
        final pages = [
          const ArtisanHomePage(),
          const _ProductsPage(),
          const SizedBox.shrink(),
          const _MarketplacePage(),
          const _ProfilePage(),
        ];
        return Scaffold(
          body: IndexedStack(index: _index, children: pages),
          bottomNavigationBar: NavigationBar(
            selectedIndex: _index,
            onDestinationSelected: (value) =>
                value == 2 ? _create() : setState(() => _index = value),
            destinations: [
              const NavigationDestination(
                icon: Icon(Icons.home_outlined),
                selectedIcon: Icon(Icons.home),
                label: 'Home',
              ),
              NavigationDestination(
                icon: const Icon(Icons.inventory_2_outlined),
                selectedIcon: const Icon(Icons.inventory_2),
                label: state.translate('products'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.add_circle_outline),
                selectedIcon: const Icon(Icons.add_circle),
                label: state.translate('create'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.storefront_outlined),
                selectedIcon: const Icon(Icons.storefront),
                label: state.translate('marketplace'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.person_outline),
                selectedIcon: const Icon(Icons.person),
                label: state.translate('profile'),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProductsPage extends StatefulWidget {
  const _ProductsPage();
  @override
  State<_ProductsPage> createState() => _ProductsPageState();
}

class _ProductsPageState extends State<_ProductsPage> {
  String _query = '';
  ProductStatus? _filter;
  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    final products = state.products
        .where(
          (product) =>
              (_filter == null || product.status == _filter) &&
              product.name.toLowerCase().contains(_query.toLowerCase()),
        )
        .toList();
    return Scaffold(
      appBar: AppBar(title: Text(state.translate('products'))),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              onChanged: (value) => setState(() => _query = value),
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search),
                hintText: 'Search your products',
              ),
            ),
            const SizedBox(height: 12),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _FilterChip(
                    label: 'All',
                    selected: _filter == null,
                    onTap: () => setState(() => _filter = null),
                  ),
                  _FilterChip(
                    label: 'Draft',
                    selected: _filter == ProductStatus.draft,
                    onTap: () => setState(() => _filter = ProductStatus.draft),
                  ),
                  _FilterChip(
                    label: 'Ready',
                    selected: _filter == ProductStatus.ready,
                    onTap: () => setState(() => _filter = ProductStatus.ready),
                  ),
                  _FilterChip(
                    label: 'Published',
                    selected: _filter == ProductStatus.published,
                    onTap: () =>
                        setState(() => _filter = ProductStatus.published),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: products.isEmpty
                  ? const _EmptyProducts()
                  : GridView.builder(
                      itemCount: products.length,
                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            mainAxisSpacing: 12,
                            crossAxisSpacing: 12,
                            childAspectRatio: .78,
                          ),
                      itemBuilder: (_, index) =>
                          _ProductCard(product: products[index]),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(right: 8),
    child: ChoiceChip(
      label: Text(label),
      selected: selected,
      onSelected: (_) => onTap(),
    ),
  );
}

class _EmptyProducts extends StatelessWidget {
  const _EmptyProducts();
  @override
  Widget build(BuildContext context) => const Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.inventory_2_outlined, size: 48),
        SizedBox(height: 12),
        Text('No products here yet'),
        Text('Create your first product when you are ready.'),
      ],
    ),
  );
}

class _ProductCard extends StatelessWidget {
  const _ProductCard({required this.product});
  final ProductDraft product;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => AppScope.of(context).openDraft(product),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              LocalProductImage(
                path: product.photoPaths.isEmpty
                    ? null
                    : product.photoPaths.first,
                height: 88,
                width: double.infinity,
              ),
              const Spacer(),
              Text(
                product.name.isEmpty
                    ? 'UNTITLED PRODUCT'
                    : product.name.toUpperCase(),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.titleSmall,
              ),
              Text(
                product.price == null
                    ? 'Price not set'
                    : '₹${product.price!.toStringAsFixed(0)}',
              ),
              _StatusChip(status: product.status),
            ],
          ),
        ),
      ),
    );
  }
}

class _MarketplacePage extends StatelessWidget {
  const _MarketplacePage();
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Marketplace')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: const [
        Text(
          'Discover artisan work',
          style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800),
        ),
        SizedBox(height: 8),
        Text(
          'A catalogue for inspiration and discovery. No payments are collected here.',
        ),
        SizedBox(height: 20),
        _MarketCard(
          title: 'Handcrafted Clay Pot',
          detail: 'Karnataka · Handmade Pottery · ₹1,100',
        ),
        _MarketCard(
          title: 'Hand-woven Cotton Stole',
          detail: 'Karnataka · Handloom · ₹1,450',
        ),
      ],
    ),
  );
}

class _MarketCard extends StatelessWidget {
  const _MarketCard({required this.title, required this.detail});
  final String title, detail;
  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      leading: CircleAvatar(
        backgroundColor: AppTheme.terracotta.withValues(alpha: .2),
        child: const Icon(Icons.storefront),
      ),
      title: Text(title),
      subtitle: Text(detail),
      trailing: const Icon(Icons.chevron_right),
    ),
  );
}

class _ProfilePage extends StatelessWidget {
  const _ProfilePage();
  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    const languages = [
      'English',
      'Hindi',
      'Kannada',
      'Marathi',
      'Tamil',
      'Telugu',
      'Bengali',
      'Malayalam',
    ];
    return Scaffold(
      appBar: AppBar(title: Text(state.translate('profile'))),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const CircleAvatar(radius: 36, child: Icon(Icons.person, size: 36)),
          const SizedBox(height: 12),
          Center(
            child: Text(
              'Your artisan profile',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          const SizedBox(height: 20),
          const _SettingRow(
            icon: Icons.badge_outlined,
            title: 'Personal information',
            subtitle: 'Add your name and region',
          ),
          const _SettingRow(
            icon: Icons.handyman_outlined,
            title: 'Craft information',
            subtitle: 'Tell us about your craft',
          ),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text('Preferred language'),
            subtitle: Text(state.language),
            trailing: DropdownButton<String>(
              value: state.language,
              underline: const SizedBox(),
              items: languages
                  .map(
                    (language) => DropdownMenuItem(
                      value: language,
                      child: Text(language),
                    ),
                  )
                  .toList(),
              onChanged: (value) async {
                if (value != null) {
                  await state.setLanguage(value);
                  if (context.mounted) {
                    await context.read<LanguageProvider>().setLanguage(value);
                  }
                }
              },
            ),
          ),
          const _SettingRow(
            icon: Icons.notifications_outlined,
            title: 'Notifications',
            subtitle: 'Manage alerts',
          ),
          const _SettingRow(
            icon: Icons.mic_none_outlined,
            title: 'Voice settings',
            subtitle: 'Recording preferences',
          ),
          const _SettingRow(
            icon: Icons.help_outline,
            title: 'Help & support',
            subtitle: 'Get assistance',
          ),
          const _SettingRow(
            icon: Icons.privacy_tip_outlined,
            title: 'Privacy',
            subtitle: 'Your data and permissions',
          ),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: Text(state.translate('settings')),
            subtitle: const Text('Language, notifications and voice guidance'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).pushNamed('/settings'),
          ),
          OutlinedButton.icon(
            onPressed: () => showDialog<void>(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('Log out?'),
                content: const Text('Your saved drafts stay on this device.'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                  FilledButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Log out'),
                  ),
                ],
              ),
            ),
            icon: const Icon(Icons.logout),
            label: const Text('Log out'),
          ),
        ],
      ),
    );
  }
}

class _SettingRow extends StatelessWidget {
  const _SettingRow({
    required this.icon,
    required this.title,
    required this.subtitle,
  });
  final IconData icon;
  final String title, subtitle;
  @override
  Widget build(BuildContext context) => ListTile(
    leading: Icon(icon),
    title: Text(title),
    subtitle: Text(subtitle),
    trailing: const Icon(Icons.chevron_right),
    onTap: () => ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$title settings will be available here.')),
    ),
  );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});
  final ProductStatus status;

  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    final (color, label) = switch (status) {
      ProductStatus.draft => (AppTheme.terracotta, state.translate('draft')),
      ProductStatus.ready => (AppTheme.sage, state.translate('ready')),
      ProductStatus.published => (
        Colors.green.shade700,
        state.translate('published'),
      ),
    };
    return Chip(
      backgroundColor: color.withValues(alpha: .14),
      side: BorderSide(color: color.withValues(alpha: .35)),
      label: Text(label, style: TextStyle(color: color)),
    );
  }
}
