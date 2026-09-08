import 'package:flutter/material.dart';

import '../models/pricing_analysis.dart';
import '../models/voice_analysis.dart';
import '../services/api_service.dart';

class PricingPage extends StatefulWidget {
  const PricingPage({
    super.key,
    required this.productId,
    required this.product,
    this.apiService,
  });

  final String productId;
  final VoiceProductInfo product;
  final ApiService? apiService;

  @override
  State<PricingPage> createState() => _PricingPageState();
}

class _PricingPageState extends State<PricingPage> {
  final _formKey = GlobalKey<FormState>();
  final _materialController = TextEditingController();
  final _hoursController = TextEditingController();
  final _rateController = TextEditingController();
  final _packagingController = TextEditingController();
  final _otherController = TextEditingController();
  final _marginController = TextEditingController();
  late final ApiService _apiService = widget.apiService ?? ApiService();
  PricingAnalysisResult? _result;
  bool _isProcessing = false;

  @override
  void dispose() {
    for (final controller in [
      _materialController,
      _hoursController,
      _rateController,
      _packagingController,
      _otherController,
      _marginController,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _isProcessing) return;
    final costs = ArtisanCosts(
      material: double.parse(_materialController.text.trim()),
      labourHours: double.parse(_hoursController.text.trim()),
      labourRatePerHour: double.parse(_rateController.text.trim()),
      packaging: double.parse(_packagingController.text.trim()),
      other: double.parse(_otherController.text.trim()),
      desiredMarginPercent: double.parse(_marginController.text.trim()),
    );

    setState(() => _isProcessing = true);
    try {
      final result = await _apiService.analyzePricing(
        productId: widget.productId,
        product: ProductPricingInput.fromVoiceProduct(widget.product),
        artisanCosts: costs,
      );
      if (mounted) setState(() => _result = result);
    } on ApiException catch (error) {
      if (mounted) _showMessage(error.message);
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  String? _validateNumber(
    String? value, {
    required String label,
    double? maximum,
  }) {
    if (value == null || value.trim().isEmpty) return '$label is required.';
    final number = double.tryParse(value.trim());
    if (number == null || !number.isFinite) return 'Enter a valid $label.';
    if (number < 0) return '$label cannot be negative.';
    if (maximum != null && number >= maximum) {
      return '$label must be less than $maximum.';
    }
    return null;
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final result = _result;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Price your product'),
        leading: const BackButton(),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
          child: result == null
              ? _buildForm(context)
              : _buildResult(context, result),
        ),
      ),
    );
  }

  Widget _buildForm(BuildContext context) {
    final theme = Theme.of(context);
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.product.name ?? 'Your product',
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _productSummary(),
            style: theme.textTheme.bodyLarge?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Tell us what it costs to make',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 12),
          _moneyField(_materialController, 'Material cost'),
          _numberField(_hoursController, 'Labour hours'),
          _moneyField(_rateController, 'Labour rate per hour'),
          _moneyField(_packagingController, 'Packaging cost'),
          _moneyField(_otherController, 'Other costs'),
          _numberField(_marginController, 'Desired margin %', maximum: 100),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 56,
            child: FilledButton(
              onPressed: _isProcessing ? null : _submit,
              child: _isProcessing
                  ? const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 12),
                        Text('Working out a fair price...'),
                      ],
                    )
                  : const Text('Get Price Recommendation'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _moneyField(TextEditingController controller, String label) =>
      _numberField(controller, label);

  Widget _numberField(
    TextEditingController controller,
    String label, {
    double? maximum,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: controller,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          prefixText: label.contains('margin') || label.contains('hours')
              ? null
              : '₹ ',
          border: const OutlineInputBorder(),
        ),
        validator: (value) => _validateNumber(
          value,
          label: label.toLowerCase(),
          maximum: maximum,
        ),
      ),
    );
  }

  Widget _buildResult(BuildContext context, PricingAnalysisResult result) {
    if (result is NeedsInputPricingResult) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'More information is needed',
            style: Theme.of(context).textTheme.headlineSmall
                ?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 12),
          const Text(
            'Please provide these details before we can suggest a price:',
          ),
          const SizedBox(height: 12),
          ...result.missingInputs.map(
            (input) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Text('• ${_friendlyName(input)}'),
            ),
          ),
          if (result.targetedQuestions.isNotEmpty) ...[
            const SizedBox(height: 12),
            ...result.targetedQuestions.map(
              (question) => Text('${question.question}\n${question.guidance}'),
            ),
          ],
          const SizedBox(height: 20),
          OutlinedButton(
            onPressed: () => setState(() => _result = null),
            child: const Text('Review inputs'),
          ),
        ],
      );
    }

    final priced = result as PricedPricingResult;
    final pricing = priced.pricing;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Price recommendation',
          style: Theme.of(context).textTheme.headlineMedium
              ?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        Text(widget.product.name ?? 'Your product'),
        const SizedBox(height: 20),
        _resultCard(
          context,
          'Suggested selling range',
          '₹${pricing.suggestedPrice.minimum.toStringAsFixed(0)} – ₹${pricing.suggestedPrice.maximum.toStringAsFixed(0)}',
        ),
        _resultCard(
          context,
          'Break-even price',
          _rupees(priced.financialBreakdown.breakEvenPrice),
        ),
        _resultCard(
          context,
          'Total production cost',
          _rupees(pricing.costs.total),
        ),
        _resultCard(
          context,
          'Labour',
          '${pricing.labour.hours} hours × ${_rupees(pricing.labour.ratePerHour)} per hour',
        ),
        _resultCard(
          context,
          'Desired margin',
          '${pricing.desiredMarginPercent.toStringAsFixed(1)}%',
        ),
        _resultCard(
          context,
          'Market information',
          pricing.marketViability.message,
        ),
        _resultCard(
          context,
          'Market trend',
          '${pricing.marketTrend.direction} — ${pricing.marketTrend.message}',
        ),
        _resultCard(
          context,
          'Confidence',
          '${pricing.confidence.level}: ${pricing.confidence.reason}',
        ),
        _resultCard(
          context,
          'Cost details',
          'Labour earnings: ${_rupees(pricing.financialTerms.labourEarnings)}\n'
              'Non-labour costs: ${_rupees(pricing.financialTerms.nonLabourCosts)}\n'
              'Profit at requested margin: ${_rupees(pricing.financialTerms.profitAmount)}',
        ),
        const SizedBox(height: 12),
        Text(
          'Why this price?',
          style: Theme.of(context).textTheme.titleLarge
              ?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 8),
        ...pricing.explanation.map(
          (line) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text('• $line'),
          ),
        ),
      ],
    );
  }

  Widget _resultCard(BuildContext context, String title, String value) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 4),
        child: Text(value),
      ),
    ),
  );

  String _productSummary() {
    final values = [
      widget.product.category,
      widget.product.material,
      widget.product.craftType,
    ].where((value) => value != null && value.trim().isNotEmpty).toList();
    return values.isEmpty
        ? 'Product information from your recording.'
        : values.join(' • ');
  }

  String _rupees(double value) => '₹${value.toStringAsFixed(2)}';

  String _friendlyName(String value) => value
      .split('_')
      .map(
        (word) => word.isEmpty
            ? word
            : '${word[0].toUpperCase()}${word.substring(1)}',
      )
      .join(' ');
}
