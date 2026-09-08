import 'dart:async';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

import '../app_scope.dart';
import '../core/theme/app_colors.dart';
import '../screens/voice_results.dart';
import '../services/api_service.dart';

class VoiceProductPage extends StatefulWidget {
  const VoiceProductPage({super.key, this.apiService});

  final ApiService? apiService;

  @override
  State<VoiceProductPage> createState() => _VoiceProductPageState();
}

class _VoiceProductPageState extends State<VoiceProductPage>
    with SingleTickerProviderStateMixin {
  static const _recordConfig = RecordConfig(encoder: AudioEncoder.wav);
  final AudioRecorder _recorder = AudioRecorder();
  late final ApiService _apiService = widget.apiService ?? ApiService();
  Timer? _timer;
  Duration _elapsed = Duration.zero;
  String? _recordingPath;
  XFile? _selectedAudio;
  bool _isRecording = false;
  bool _isProcessing = false;
  late final AnimationController _waveController;

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 850),
    );
  }

  Future<void> _startRecording() async {
    try {
      if (!await _recorder.hasPermission()) {
        _showMessage('Microphone permission is needed to record your story.');
        return;
      }

      final path = await _recordingFilePath();
      await _recorder.start(_recordConfig, path: path);
      if (!mounted) return;
      setState(() {
        _recordingPath = null;
        _selectedAudio = null;
        _elapsed = Duration.zero;
        _isRecording = true;
      });
      _waveController.repeat(reverse: true);
      _timer = Timer.periodic(const Duration(seconds: 1), (_) {
        if (mounted) setState(() => _elapsed += const Duration(seconds: 1));
      });
    } catch (_) {
      _showMessage('We could not start recording. Please try again.');
    }
  }

  Future<void> _stopRecording() async {
    _timer?.cancel();
    _timer = null;
    try {
      final path = await _recorder.stop();
      if (!mounted) return;
      if (path == null || path.isEmpty) {
        setState(() => _isRecording = false);
        _showMessage('We could not save that recording. Please try again.');
        return;
      }
      setState(() {
        _recordingPath = path;
        _selectedAudio = XFile(path);
        _isRecording = false;
      });
      _waveController.stop();
    } catch (_) {
      if (mounted) setState(() => _isRecording = false);
      _showMessage('We could not save that recording. Please try again.');
    }
  }

  Future<String> _recordingFilePath() async {
    if (kIsWeb) {
      return 'artisan_voice_${DateTime.now().millisecondsSinceEpoch}.wav';
    }
    final directory = await getTemporaryDirectory();
    return '${directory.path}/artisan_voice_${DateTime.now().millisecondsSinceEpoch}.wav';
  }

  Future<void> _continue() async {
    final audio =
        _selectedAudio ??
        (_recordingPath == null ? null : XFile(_recordingPath!));
    if (audio == null || _isProcessing) return;
    setState(() => _isProcessing = true);
    try {
      final result = await _apiService.analyzeVoice(
        productId: AppScope.maybeOf(context)?.activeDraft?.id ?? 'ART-001',
        audio: audio,
      );
      if (!mounted) return;
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (_) => VoiceResultsPage(result: result),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) _showMessage(error.message);
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  Future<void> _pickAudioFile() async {
    if (_isRecording || _isProcessing) return;
    try {
      final selection = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: const ['wav', 'mp3', 'flac', 'ogg'],
        withData: true,
      );
      if (selection == null || selection.files.isEmpty) return;

      final file = selection.files.single;
      final extension = file.extension?.toLowerCase();
      if (extension == null ||
          !{'wav', 'mp3', 'flac', 'ogg'}.contains(extension)) {
        _showMessage('Please choose a WAV, MP3, FLAC, or OGG audio file.');
        return;
      }

      final audio = file.bytes != null
          ? XFile.fromData(file.bytes!, name: file.name)
          : file.path == null
          ? null
          : XFile(file.path!);
      if (audio == null) {
        _showMessage('We could not read that audio file. Please try again.');
        return;
      }

      if (!mounted) return;
      setState(() {
        _selectedAudio = audio;
        _recordingPath = audio.path;
        _elapsed = Duration.zero;
      });
    } catch (_) {
      _showMessage('We could not choose that audio file. Please try again.');
    }
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  void dispose() {
    _timer?.cancel();
    _waveController.dispose();
    _recorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasRecording = _recordingPath != null && !_isRecording;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tell us about your product'),
        leading: const BackButton(),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                child: Column(
                  children: [
                    Text(
                      'Speak naturally in your language. Tell us what you made, what it is made of, and anything special about it.',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyLarge?.copyWith(
                        height: 1.45,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 40),
                    _RecordingWave(
                      controller: _waveController,
                      isRecording: _isRecording,
                    ),
                    const SizedBox(height: 20),
                    Text(
                      _isRecording
                          ? 'Listening...'
                          : hasRecording
                          ? 'Recording ready'
                          : 'Tap below to begin',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _formatDuration(_elapsed),
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.5,
                      ),
                    ),
                    const SizedBox(height: 32),
                    if (_isRecording)
                      FilledButton.icon(
                        onPressed: _stopRecording,
                        icon: const Icon(Icons.stop_circle_outlined),
                        label: const Text('Stop recording'),
                        style: FilledButton.styleFrom(
                          minimumSize: const Size.fromHeight(56),
                        ),
                      )
                    else
                      OutlinedButton.icon(
                        onPressed: _isProcessing ? null : _startRecording,
                        icon: const Icon(Icons.mic_none_outlined),
                        label: Text(
                          hasRecording ? 'Record again' : 'Start recording',
                        ),
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size.fromHeight(56),
                        ),
                      ),
                    const SizedBox(height: 12),
                    TextButton.icon(
                      onPressed: _isProcessing ? null : _pickAudioFile,
                      icon: const Icon(Icons.upload_file_outlined),
                      label: const Text('Upload an audio file'),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      'You can speak for as long as you need. Tell us in your own words.',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
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
                  onPressed: hasRecording && !_isProcessing ? _continue : null,
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
                            Text('Processing your story...'),
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

class _RecordingWave extends StatelessWidget {
  const _RecordingWave({required this.controller, required this.isRecording});
  final Animation<double> controller;
  final bool isRecording;

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: controller,
    builder: (context, _) {
      final phase = controller.value;
      return SizedBox(
        height: 166,
        width: 220,
        child: Stack(
          alignment: Alignment.center,
          children: [
            if (isRecording)
              Container(
                width: 156 + (phase * 20),
                height: 156 + (phase * 20),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.sageGreen.withValues(alpha: .25),
                    width: 3,
                  ),
                ),
              ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: List.generate(7, (index) {
                final base = 24 + ((index % 4) * 10);
                final direction = index.isEven ? phase : 1 - phase;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 100),
                  width: 7,
                  height: isRecording ? base + (direction * 32) : 12,
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  decoration: BoxDecoration(
                    color: isRecording
                        ? AppColors.sageGreen
                        : AppColors.secondaryText.withValues(alpha: .45),
                    borderRadius: BorderRadius.circular(99),
                  ),
                );
              }),
            ),
            Positioned(
              bottom: 0,
              child: Container(
                width: 58,
                height: 58,
                decoration: const BoxDecoration(
                  color: AppColors.mutedTerracotta,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.mic, color: Colors.white),
              ),
            ),
          ],
        ),
      );
    },
  );
}
