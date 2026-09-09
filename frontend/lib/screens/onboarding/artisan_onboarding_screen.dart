import 'package:flutter/material.dart';

import '../../widgets/common/karigar_design.dart';

class ArtisanOnboardingScreen extends StatefulWidget {
  const ArtisanOnboardingScreen({super.key, required this.onDone});
  final Future<void> Function(String name, String craft, String region) onDone;

  @override
  State<ArtisanOnboardingScreen> createState() =>
      _ArtisanOnboardingScreenState();
}

class _ArtisanOnboardingScreenState extends State<ArtisanOnboardingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _craft = TextEditingController();
  final _region = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _name.dispose();
    _craft.dispose();
    _region.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false) || _saving) return;
    setState(() => _saving = true);
    try {
      await widget.onDone(
        _name.text.trim(),
        _craft.text.trim(),
        _region.text.trim(),
      );
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('We could not save your profile. Please try again.'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tell us about you')),
    body: SafeArea(
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const FlowStepper(currentStep: 1),
              const SizedBox(height: 28),
              Text(
                'Step 1 of 3',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              const SizedBox(height: 8),
              Text(
                'Tell Us About Yourself',
                style: Theme.of(context).textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              const Text(
                'This helps us create better product listings for you.',
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _name,
                decoration: const InputDecoration(labelText: 'Your Name'),
                validator: _required('Enter your name.'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _craft,
                decoration: const InputDecoration(
                  labelText: 'Craft Type',
                  suffixIcon: Icon(Icons.expand_more),
                ),
                validator: _required('Enter your craft type.'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _region,
                decoration: const InputDecoration(
                  labelText: 'Region',
                  suffixIcon: Icon(Icons.expand_more),
                ),
                validator: _required('Enter your location.'),
              ),
              const SizedBox(height: 12),
              const InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Preferred Language',
                  suffixIcon: Icon(Icons.language),
                ),
                child: Text('Selected in the previous step'),
              ),
              const SizedBox(height: 28),
              FilledButton(
                onPressed: _saving ? null : _submit,
                child: Text(_saving ? 'Saving profile...' : 'Continue'),
              ),
              TextButton(
                onPressed: _saving ? null : _submit,
                child: const Text('Skip for now'),
              ),
            ],
          ),
        ),
      ),
    ),
  );

  String? Function(String?) _required(String message) =>
      (value) => value == null || value.trim().isEmpty ? message : null;
}
