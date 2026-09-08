import 'package:flutter/material.dart';

import '../../screens/app_shell.dart';
import '../../screens/add_product.dart';
import '../../screens/pricing_page.dart';
import '../../screens/listing_page.dart';
import '../../screens/settings_screen.dart';
import '../../screens/share_page.dart';
import 'app_routes.dart';

abstract final class RouteGenerator {
  static Route<dynamic> generate(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.home:
      case AppRoutes.products:
      case AppRoutes.marketplace:
      case AppRoutes.profile:
        return MaterialPageRoute<void>(builder: (_) => const AppShell());
      case AppRoutes.photoCapture:
      case AppRoutes.qualityCheck:
        return MaterialPageRoute<void>(builder: (_) => const AddProductPage());
      case AppRoutes.pricing:
        return MaterialPageRoute<void>(builder: (_) => const PricingPage());
      case AppRoutes.listingReady:
      case AppRoutes.preview:
        return MaterialPageRoute<void>(builder: (_) => const ListingPage());
      case AppRoutes.share:
        return MaterialPageRoute<void>(builder: (_) => const SharePage());
      case AppRoutes.settings:
        return MaterialPageRoute<void>(builder: (_) => const SettingsScreen());
      default:
        return MaterialPageRoute<void>(builder: (_) => const AppShell());
    }
  }
}
