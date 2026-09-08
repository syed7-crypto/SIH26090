import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../app_scope.dart';
import '../screens/photo_analysis_results.dart';
import '../services/api_service.dart';
import '../widgets/common/karigar_design.dart';

class AddProductPage extends StatefulWidget {
  const AddProductPage({super.key, this.apiService});

  final ApiService? apiService;

  @override
  State<AddProductPage> createState() => _AddProductPageState();
}

class _AddProductPageState extends State<AddProductPage> {
  static const _maxPhotos = 10;
  static const _productId = 'ART-001';
  final ImagePicker _picker = ImagePicker();
  final List<XFile> _photos = [];
  late final ApiService _apiService = widget.apiService ?? ApiService();
  bool _isProcessing = false;

  Future<void> _takePhoto() async {
    if (_photos.length >= _maxPhotos) {
      _showMessage('Maximum 10 images allowed per product listing.');
      return;
    }
    final photo = await _picker.pickImage(source: ImageSource.camera);
    if (!mounted || photo == null) return;
    setState(() => _photos.add(photo));
  }

  Future<void> _choosePhotos() async {
    if (_photos.length >= _maxPhotos) {
      _showMessage('Maximum 10 images allowed per product listing.');
      return;
    }
    final pickedPhotos = await _picker.pickMultiImage();
    if (!mounted || pickedPhotos.isEmpty) return;

    final remainingSlots = _maxPhotos - _photos.length;
    if (pickedPhotos.length > remainingSlots) {
      _showMessage('Maximum 10 images allowed per product listing.');
    }
    setState(() => _photos.addAll(pickedPhotos.take(remainingSlots)));
  }

  void _removePhoto(int index) {
    setState(() => _photos.removeAt(index));
    _showMessage('Photo removed.');
  }

  Future<void> _continue() async {
    if (_photos.length < 2 || _isProcessing) return;
    setState(() => _isProcessing = true);

    try {
      final result = await _apiService.analyzePhotos(
        productId: _productId,
        photos: List<XFile>.unmodifiable(_photos),
      );
      if (!mounted) return;
      final state = AppScope.maybeOf(context);
      final draft = state?.activeDraft;
      if (draft != null) {
        await state!.updateDraft(
          draft.copyWith(
            photoPaths: _photos.map((photo) => photo.path).toList(),
            photoReadiness: result.media.photoReadiness.score,
          ),
        );
      }
      if (!mounted) return;
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (_) => PhotoAnalysisResultsPage(
            result: result,
            localPhotos: List<XFile>.unmodifiable(_photos),
          ),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) _showMessage(error.message);
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Product'),
        leading: const BackButton(),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const FlowStepper(currentStep: 1),
                    const SizedBox(height: 24),
                    Text(
                      'Add Your Product Photos',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Show us your product',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Take at least 2 clear photos from different angles. You can add up to 10 photos.',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        height: 1.45,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 24),
                    _PhotoActions(
                      onCameraPressed: _photos.length < _maxPhotos
                          ? _takePhoto
                          : null,
                      onGalleryPressed: _photos.length < _maxPhotos
                          ? _choosePhotos
                          : null,
                    ),
                    const SizedBox(height: 28),
                    _PhotoGuidance(theme: theme),
                    const SizedBox(height: 28),
                    Text(
                      '${_photos.length} / $_maxPhotos Photos Captured',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _photos.isEmpty
                        ? _EmptyPhotoState(theme: theme)
                        : _PhotoGrid(photos: _photos, onRemove: _removePhoto),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton(
                  onPressed: _photos.length >= 2 && !_isProcessing
                      ? _continue
                      : null,
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
                            Text('Processing photos...'),
                          ],
                        )
                      : const Text('Continue'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PhotoActions extends StatelessWidget {
  const _PhotoActions({
    required this.onCameraPressed,
    required this.onGalleryPressed,
  });
  final VoidCallback? onCameraPressed;
  final VoidCallback? onGalleryPressed;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: FilledButton.icon(
            onPressed: onCameraPressed,
            icon: const Icon(Icons.camera_alt_outlined),
            label: const Text('Take photo'),
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(56),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: onGalleryPressed,
            icon: const Icon(Icons.photo_library_outlined),
            label: const Text('Choose photos'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(56),
            ),
          ),
        ),
      ],
    );
  }
}

class _PhotoGuidance extends StatelessWidget {
  const _PhotoGuidance({required this.theme});
  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    const guidance = [
      'Add at least 2 clear photos (up to 10)',
      'Include a front or product view',
      'Add a close-up or detail view',
      'If possible, show it being used or worn',
    ];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.secondaryContainer.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Good photos help people understand your craft',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          for (final item in guidance)
            Padding(
              padding: const EdgeInsets.only(bottom: 7),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('•  '),
                  Expanded(child: Text(item)),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _EmptyPhotoState extends StatelessWidget {
  const _EmptyPhotoState({required this.theme});
  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 20),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Column(
        children: [
          Icon(
            Icons.photo_camera_back_outlined,
            size: 36,
            color: theme.colorScheme.primary,
          ),
          const SizedBox(height: 10),
          Text(
            'No photos selected yet',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Choose photos or take a new one to get started.',
            textAlign: TextAlign.center,
            style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}

class _PhotoGrid extends StatelessWidget {
  const _PhotoGrid({required this.photos, required this.onRemove});
  final List<XFile> photos;
  final ValueChanged<int> onRemove;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: photos.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemBuilder: (context, index) =>
          _PhotoTile(photo: photos[index], onRemove: () => onRemove(index)),
    );
  }
}

class _PhotoTile extends StatelessWidget {
  const _PhotoTile({required this.photo, required this.onRemove});
  final XFile photo;
  final VoidCallback onRemove;

  Future<Uint8List> _readPhoto() => photo.readAsBytes();

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: Stack(
        fit: StackFit.expand,
        children: [
          FutureBuilder<Uint8List>(
            future: _readPhoto(),
            builder: (context, snapshot) {
              if (!snapshot.hasData) {
                return const ColoredBox(
                  color: Color(0xFFE8E5DE),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              return Image.memory(snapshot.data!, fit: BoxFit.cover);
            },
          ),
          Positioned(
            top: 8,
            right: 8,
            child: IconButton.filledTonal(
              onPressed: onRemove,
              tooltip: 'Remove photo',
              icon: const Icon(Icons.close),
            ),
          ),
        ],
      ),
    );
  }
}
