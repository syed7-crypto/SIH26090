import 'package:flutter/material.dart';

import '../../screens/app_shell.dart';
import '../../screens/pricing_page.dart';
import '../../screens/listing_page.dart';
import '../../screens/settings_screen.dart';
import '../../screens/share_page.dart';
import '../../screens/home/dashboard_screen.dart';
import '../../screens/onboarding/language_screen.dart';
import '../../screens/product/create_product_screen.dart';
import '../../screens/product/my_products_screen.dart';
import '../../screens/profile/profile_screen.dart';
import 'app_routes.dart';

abstract final class RouteGenerator {
  static Route<dynamic> generate(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.languageSelect:
        return MaterialPageRoute<void>(builder: (_) => const LanguageScreen());
      case AppRoutes.home:
        return MaterialPageRoute<void>(builder: (_) => const DashboardScreen());
      case AppRoutes.products:
        return MaterialPageRoute<void>(
          builder: (_) => const MyProductsScreen(),
        );
      case AppRoutes.marketplace:
        return MaterialPageRoute<void>(builder: (_) => const AppShell());
      case AppRoutes.profile:
        return MaterialPageRoute<void>(builder: (_) => const ProfileScreen());
      case AppRoutes.photoCapture:
      case AppRoutes.qualityCheck:
        return MaterialPageRoute<void>(
          builder: (_) => const CreateProductScreen(),
        );
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
