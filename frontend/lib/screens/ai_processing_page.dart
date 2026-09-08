import 'dart:async';

import 'package:flutter/material.dart';

import '../core/theme/app_colors.dart';

class AiProcessingPage extends StatefulWidget {
  const AiProcessingPage({super.key, this.onComplete});
  final VoidCallback? onComplete;

  @override
  State<AiProcessingPage> createState() => _AiProcessingPageState();
}

class _AiProcessingPageState extends State<AiProcessingPage> {
  static const _steps = [
    'Voice converted to text',
    'Language detected',
    'Attributes extracted',
    'Photos analyzed',
  ];
  Timer? _timer;
  int _completed = 0;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(milliseconds: 700), (timer) {
      if (!mounted) return;
      if (_completed >= _steps.length) {
        timer.cancel();
        widget.onComplete?.call();
        return;
      }
      setState(() => _completed++);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final percent = ((_completed / _steps.length) * 100).round();
    return Scaffold(
      appBar: AppBar(title: const Text('Creating Your Product Information')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.all(24),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const CircleAvatar(
                        radius: 38,
                        backgroundColor: AppColors.sageGreen,
                        child: Icon(
                          Icons.psychology_alt_rounded,
                          color: Colors.white,
                          size: 42,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'AI is building your listing',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.titleLarge
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Photos and voice are being turned into product information.',
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 28),
                      for (var index = 0; index < _steps.length; index++)
                        _CheckpointRow(
                          label: _steps[index],
                          visible: index < _completed,
                        ),
                      const SizedBox(height: 24),
                      TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0, end: _completed / _steps.length),
                        duration: const Duration(milliseconds: 450),
                        builder: (context, value, _) => LinearProgressIndicator(
                          value: value,
                          minHeight: 10,
                          borderRadius: BorderRadius.circular(99),
                          color: AppColors.success,
                          backgroundColor: AppColors.border,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        '$percent% ${percent >= 100 ? 'Complete' : 'Almost ready...'}',
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          color: AppColors.sageGreen,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CheckpointRow extends StatelessWidget {
  const _CheckpointRow({required this.label, required this.visible});
  final String label;
  final bool visible;
  @override
  Widget build(BuildContext context) => AnimatedOpacity(
    opacity: visible ? 1 : .35,
    duration: const Duration(milliseconds: 350),
    child: AnimatedSlide(
      offset: visible ? Offset.zero : const Offset(-.08, 0),
      duration: const Duration(milliseconds: 350),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 9),
        child: Row(
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: visible ? AppColors.success : AppColors.border,
              ),
              child: Icon(
                visible ? Icons.check : Icons.more_horiz,
                size: 15,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(label)),
          ],
        ),
      ),
    ),
  );
}
