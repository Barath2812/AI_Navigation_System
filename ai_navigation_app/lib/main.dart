import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:vibration/vibration.dart';

List<CameraDescription> cameras = [];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    cameras = await availableCameras();
  } on CameraException catch (e) {
    debugPrint('Error getting cameras: $e');
  }
  runApp(const AINavigationApp());
}

class AINavigationApp extends StatelessWidget {
  const AINavigationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Nav',
      theme: ThemeData.dark(),
      home: const NavigationScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class NavigationScreen extends StatefulWidget {
  const NavigationScreen({super.key});

  @override
  State<NavigationScreen> createState() => _NavigationScreenState();
}

class _NavigationScreenState extends State<NavigationScreen> {
  CameraController? _controller;
  WebSocketChannel? _channel;
  final FlutterTts flutterTts = FlutterTts();

  bool _isStreaming = false;
  bool _isProcessingFrame = false;

  // Morse Code State
  String _currentMorse = '';
  Timer? _morseTimer;

  // *** UPDATE THIS to your computer's local IP address ***
  final String serverUrl = 'ws://192.168.1.100:8000/ws/navigate';

  @override
  void initState() {
    super.initState();
    _initTts();
    _initCamera();
  }

  Future<void> _initTts() async {
    await flutterTts.setLanguage('en-US');
    await flutterTts.setSpeechRate(0.5);
    await flutterTts.setVolume(1.0);
    await flutterTts.setPitch(1.0);
  }

  Future<void> _initCamera() async {
    if (cameras.isEmpty) return;
    _controller = CameraController(
      cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      ),
      ResolutionPreset.low,
      enableAudio: false,
    );
    await _controller!.initialize();
    if (!mounted) return;
    setState(() {});
  }

  void _connectWebSocket() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(serverUrl));
      _channel!.stream.listen(
        (message) {
          final data = jsonDecode(message as String);
          final instruction = data['instruction'] as String?;
          if (instruction != null && instruction.isNotEmpty) {
            _speak(instruction);
          }
        },
        onError: (_) => _speak('Connection error'),
        onDone: _stopStreaming,
      );
      _speak('Connected to server');
    } catch (_) {
      _speak('Failed to connect');
    }
  }

  void _disconnectWebSocket() {
    _channel?.sink.close();
    _channel = null;
    _speak('Disconnected');
  }

  Future<void> _speak(String text) async {
    await flutterTts.speak(text);
  }

  Future<void> _vibrate(int duration) async {
    final hasVibrator = await Vibration.hasVibrator();
    if (hasVibrator == true) {
      Vibration.vibrate(duration: duration);
    }
  }

  void _startStreaming() {
    if (_controller == null || !_controller!.value.isInitialized) return;
    if (_isStreaming) return;
    _connectWebSocket();
    setState(() => _isStreaming = true);

    _controller!.startImageStream((CameraImage image) async {
      if (_isProcessingFrame || _channel == null) return;
      _isProcessingFrame = true;
      try {
        // Send raw Y plane bytes as base64. Server decodes as grayscale fallback.
        final bytes = image.planes[0].bytes;
        final base64Image = base64Encode(bytes);
        _channel!.sink.add(base64Image);
      } catch (e) {
        debugPrint('Frame send error: $e');
      } finally {
        await Future.delayed(const Duration(milliseconds: 300));
        _isProcessingFrame = false;
      }
    });
  }

  void _stopStreaming() {
    if (!_isStreaming) return;
    _controller?.stopImageStream();
    _disconnectWebSocket();
    setState(() => _isStreaming = false);
  }

  // ── Morse Code ──────────────────────────────────────────────────────────────

  void _onTapDown(TapDownDetails _) {
    _morseTimer?.cancel();
  }

  void _onTap() {
    _currentMorse += '.';
    _vibrate(50);
    _startMorseTimeout();
  }

  void _onLongPress() {
    _currentMorse += '-';
    _vibrate(200);
    _startMorseTimeout();
  }

  void _startMorseTimeout() {
    _morseTimer?.cancel();
    _morseTimer =
        Timer(const Duration(milliseconds: 800), _processMorseCommand);
  }

  void _processMorseCommand() {
    final command = _currentMorse;
    _currentMorse = '';
    debugPrint('Morse: $command');

    switch (command) {
      case '...': // S – Start / Stop
        if (_isStreaming) {
          _stopStreaming();
        } else {
          _startStreaming();
        }
      case '---': // O – Status
        _speak(_isStreaming ? 'System active.' : 'System offline.');
      default:
        _speak('Unknown command');
    }
  }

  // ── Widget ──────────────────────────────────────────────────────────────────

  @override
  void dispose() {
    _morseTimer?.cancel();
    _controller?.dispose();
    _channel?.sink.close();
    flutterTts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      backgroundColor: Colors.black,
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: _onTapDown,
        onTap: _onTap,
        onLongPress: _onLongPress,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Camera feed
            CameraPreview(_controller!),

            // Recording indicator
            if (_isStreaming)
              const Positioned(
                top: 54,
                right: 24,
                child: Row(
                  children: [
                    Icon(Icons.circle, color: Colors.red, size: 14),
                    SizedBox(width: 6),
                    Text(
                      'LIVE',
                      style: TextStyle(
                        color: Colors.red,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

            // Overlay hint
            Align(
              alignment: Alignment.bottomCenter,
              child: Container(
                margin: const EdgeInsets.only(bottom: 48),
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Text(
                  'Tap  =  ·   Long Press  =  —\n\n'
                  '· · ·  (S)  →  Start / Stop\n'
                  '— — —  (O)  →  Status',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                    height: 1.6,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
