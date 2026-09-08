import 'package:flutter/material.dart';

class BottomNavBar extends StatelessWidget {
  const BottomNavBar({
    super.key,
    required this.index,
    required this.onSelected,
  });
  final int index;
  final ValueChanged<int> onSelected;
  @override
  Widget build(BuildContext context) => NavigationBar(
    selectedIndex: index,
    onDestinationSelected: onSelected,
    destinations: const [
      NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
      NavigationDestination(
        icon: Icon(Icons.inventory_2_outlined),
        label: 'Products',
      ),
      NavigationDestination(
        icon: Icon(Icons.add_circle_outline),
        label: 'Create',
      ),
      NavigationDestination(
        icon: Icon(Icons.storefront_outlined),
        label: 'Marketplace',
      ),
      NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
    ],
  );
}
