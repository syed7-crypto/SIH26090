import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';

import '../app_scope.dart';

class SharePage extends StatelessWidget {
  const SharePage({super.key});
  @override
  Widget build(BuildContext context) {
    final draft = AppScope.of(context).activeDraft;
    final title = draft?.name.isEmpty ?? true
        ? 'My artisan product'
        : draft!.name;
    return Scaffold(
      appBar: AppBar(title: const Text('Share your listing')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Ready to share',
              style: Theme.of(context).textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 12),
            Text(
              '$title${draft?.price == null ? '' : ' · ₹${draft!.price!.toStringAsFixed(0)}'}',
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed: () => Share.share(
                '$title${draft?.description.isEmpty ?? true ? '' : '\n${draft!.description}'}',
              ),
              icon: const Icon(Icons.share),
              label: const Text('Share listing'),
            ),
          ],
        ),
      ),
    );
  }
}
