import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../models/product_draft.dart';
import 'readiness_page.dart';

class PricingPage extends StatefulWidget {
  const PricingPage({super.key});

  @override
  State<PricingPage> createState() => _PricingPageState();
}

class _PricingPageState extends State<PricingPage> {
  final _price = TextEditingController();

  @override
  void dispose() {
    _price.dispose();
    super.dispose();
  }

  Future<void> _continue() async {
    final value = double.tryParse(_price.text.trim());
    if (value == null || value <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter a valid price in rupees.')),
      );
      return;
    }
    final state = AppScope.of(context);
    final draft = state.activeDraft;
    if (draft != null) {
      final pricedDraft = draft.copyWith(price: value);
      await state.updateDraft(
        pricedDraft.copyWith(
          status: pricedDraft.readiness >= 80
              ? ProductStatus.ready
              : ProductStatus.draft,
        ),
      );
    }
    if (mounted) {
      Navigator.of(context)
          .push(MaterialPageRoute<void>(builder: (_) => const ReadinessPage()));
    }
  }

  @override
  Widget build(BuildContext context) {
    final draft = AppScope.of(context).activeDraft;
    final previewPrice = double.tryParse(_price.text) ?? draft?.price;
    final readiness = draft?.copyWith(price: previewPrice).readiness;
    return Scaffold(
      appBar: AppBar(title: const Text('Set your price')),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Price your work fairly',
                style: Theme.of(context).textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 10),
              const Text(
                'Pricing intelligence is not exposed by the current backend API. '
                'Set the price you want to use; this can be replaced with a real '
                'recommendation when that endpoint is available.',
              ),
              const SizedBox(height: 24),
              TextField(
                controller: _price,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  prefixText: '₹ ',
                  labelText: 'Your selling price',
                ),
              ),
              if (readiness != null)
                Padding(
                  padding: const EdgeInsets.only(top: 20),
                  child: Text('Listing readiness: $readiness%'),
                ),
              const SizedBox(height: 36),
              FilledButton(
                onPressed: _continue,
                child: const Text('Review listing'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
