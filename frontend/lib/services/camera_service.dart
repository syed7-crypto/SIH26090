import 'package:image_picker/image_picker.dart';

class CameraService {
  CameraService({ImagePicker? picker}) : _picker = picker ?? ImagePicker();
  final ImagePicker _picker;
  Future<XFile?> capturePhoto() =>
      _picker.pickImage(source: ImageSource.camera);
  Future<List<XFile>> pickPhotos() => _picker.pickMultiImage();
}
