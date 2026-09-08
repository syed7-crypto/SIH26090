import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

/// Keeps desktop/web previews visually equivalent to a compact phone screen.
class MobileViewport extends StatelessWidget {
  const MobileViewport({super.key, required this.child, this.maxWidth = 390});
  final Widget child;
  final double maxWidth;
  @override
  Widget build(BuildContext context) => Center(
    child: ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: child,
    ),
  );
}

class FloatingBubbles extends StatefulWidget {
  const FloatingBubbles({super.key, required this.child});
  final Widget child;
  @override
  State<FloatingBubbles> createState() => _FloatingBubblesState();
}

class _FloatingBubblesState extends State<FloatingBubbles>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 5))..repeat(reverse: true);
  }
  @override
  void dispose() { _controller.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _controller,
    child: widget.child,
    builder: (context, child) {
      final shift = (_controller.value - .5) * 14;
      return Stack(children: [
        Positioned(top: 18 + shift, right: -14, child: _bubble(58, AppColors.sageGreen.withValues(alpha: .10))),
        Positioned(top: 230 - shift, left: -22, child: _bubble(76, AppColors.mutedTerracotta.withValues(alpha: .08))),
        Positioned(bottom: 60 + shift, right: 4, child: _bubble(34, AppColors.sageGreen.withValues(alpha: .08))),
        child!,
      ]);
    },
  );
  Widget _bubble(double size, Color color) => IgnorePointer(child: Container(width: size, height: size, decoration: BoxDecoration(shape: BoxShape.circle, color: color)));
}
