import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../core/constants/languages.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final state = AppScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          SwitchListTile(
            title: const Text('Notifications'),
            subtitle: const Text('Product reminders and updates'),
            value: state.notificationsEnabled,
            onChanged: state.setNotificationsEnabled,
          ),
          ListTile(
            title: const Text('Preferred language'),
            subtitle: Text(state.language),
            trailing: DropdownButton<String>(
              value: state.language,
              items: supportedLanguages
                  .map(
                    (value) =>
                        DropdownMenuItem(value: value, child: Text(value)),
                  )
                  .toList(),
              onChanged: (value) {
                if (value != null) state.setLanguage(value);
              },
            ),
          ),
          ListTile(
            title: const Text('Voice guidance speed'),
            subtitle: Slider(
              value: state.voiceGuidanceSpeed,
              min: .75,
              max: 1.5,
              divisions: 3,
              label: '${state.voiceGuidanceSpeed}x',
              onChanged: state.setVoiceGuidanceSpeed,
            ),
          ),
          const ListTile(
            title: Text('Privacy'),
            subtitle: Text('Manage device data and permissions'),
          ),
          OutlinedButton.icon(
            onPressed: () async {
              await state.resetOnboarding();
              if (context.mounted) {
                Navigator.of(context).popUntil((route) => route.isFirst);
              }
            },
            icon: const Icon(Icons.restart_alt),
            label: const Text('Reset onboarding'),
          ),
        ],
      ),
    );
  }
}
