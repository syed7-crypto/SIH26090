import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/theme/app_colors.dart';
import '../../providers/artisan_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final artisan = context.watch<ArtisanProvider>().artisan;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      const CircleAvatar(
                        radius: 30,
                        child: Icon(Icons.person, size: 34),
                      ),
                      const SizedBox(width: 14),
                      Flexible(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              artisan.name.toUpperCase(),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.titleLarge
                                  ?.copyWith(fontWeight: FontWeight.w800),
                            ),
                            Text(
                              '${artisan.craftType.toUpperCase()}, ${artisan.region}',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              for (final item in _settings)
                ListTile(
                  leading: Icon(item.icon),
                  title: Text(item.title),
                  trailing: const Icon(Icons.chevron_right),
                ),
              const SizedBox(height: 20),
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.warning,
                ),
                onPressed: () => _showExitDialog(context),
                icon: const Icon(Icons.logout),
                label: const Text('Log Out'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showExitDialog(BuildContext context) => showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Leave the App?'),
      content: const Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Your saved products and drafts will remain available.'),
          SizedBox(height: 12),
          Chip(label: Text('You have an unfinished draft')),
        ],
      ),
      actions: [
        FilledButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Save & Exit'),
        ),
        OutlinedButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Exit Without Saving'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
      ],
    ),
  );
}

class _ProfileSetting {
  const _ProfileSetting(this.icon, this.title);
  final IconData icon;
  final String title;
}

const _settings = [
  _ProfileSetting(Icons.badge_outlined, 'Personal Information'),
  _ProfileSetting(Icons.handyman_outlined, 'Craft Information'),
  _ProfileSetting(Icons.language, 'Language'),
  _ProfileSetting(Icons.notifications_outlined, 'Notifications'),
  _ProfileSetting(Icons.mic_none_outlined, 'Voice Settings'),
  _ProfileSetting(Icons.help_outline, 'Help & Support'),
  _ProfileSetting(Icons.privacy_tip_outlined, 'Privacy'),
];
