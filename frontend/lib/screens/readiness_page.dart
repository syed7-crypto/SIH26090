import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../widgets/common/karigar_design.dart';
import 'listing_page.dart';

class ReadinessPage extends StatelessWidget {
  const ReadinessPage({super.key});
  @override
  Widget build(BuildContext context) {
    final draft = AppScope.of(context).activeDraft;
    final score = draft?.readiness ?? 0;
    return Scaffold(
      appBar: AppBar(title: const Text('Product Readiness')),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const FlowStepper(currentStep: 5),
              const SizedBox(height: 28),
              Center(
                child: ScoreRing(score: score, label: 'Complete'),
              ),
              const SizedBox(height: 22),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Listing checklist',
                        style: Theme.of(context).textTheme.titleLarge
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      CheckRow(
                        label: 'Product Photos',
                        complete: (draft?.photoPaths.length ?? 0) >= 2,
                      ),
                      CheckRow(
                        label: 'Product Name',
                        complete: draft?.name.isNotEmpty ?? false,
                      ),
                      CheckRow(
                        label: 'Description',
                        complete: draft?.description.isNotEmpty ?? false,
                      ),
                      CheckRow(
                        label: 'Material',
                        complete: draft?.material.isNotEmpty ?? false,
                      ),
                      CheckRow(
                        label: 'Category',
                        complete: draft?.category.isNotEmpty ?? false,
                      ),
                      CheckRow(label: 'Price', complete: draft?.price != null),
                      CheckRow(
                        label: 'Dimensions',
                        complete: draft?.dimensions.isNotEmpty ?? false,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(builder: (_) => const ListingPage()),
                ),
                child: Text(
                  score >= 80
                      ? 'Continue to Listing'
                      : 'Add Missing Information',
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(builder: (_) => const ListingPage()),
                ),
                child: const Text('Continue Anyway'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
