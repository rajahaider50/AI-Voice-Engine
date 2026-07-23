import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/models.dart';

class TTSProvider extends ChangeNotifier {
  String _baseUrl = 'http://localhost:8000/api/v1';
  bool _isLoading = false;
  String? _error;
  List<Voice> _voices = [];
  List<HistoryEntry> _history = [];
  TTSResult? _lastResult;

  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Voice> get voices => _voices;
  List<HistoryEntry> get history => _history;
  TTSResult? get lastResult => _lastResult;

  void setBaseUrl(String url) {
    _baseUrl = url;
    notifyListeners();
  }

  Future<void> loadVoices() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/voices'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _voices = (data['voices'] as List)
            .map((v) => Voice.fromJson(v))
            .toList();
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to load voices: $e';
      notifyListeners();
    }
  }

  Future<void> loadHistory() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/history'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _history = (data['history'] as List)
            .map((h) => HistoryEntry.fromJson(h))
            .toList();
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to load history: $e';
      notifyListeners();
    }
  }

  Future<TTSResult?> generateSpeech({
    required String text,
    required String voiceId,
    double speed = 1.0,
    double pitch = 1.0,
    double volume = 1.0,
    String emotion = 'neutral',
    String language = 'en',
    bool breathEffect = true,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/tts'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'text': text,
          'voice_id': voiceId,
          'speed': speed,
          'pitch': pitch,
          'volume': volume,
          'emotion': emotion,
          'language': language,
          'breath_effect': breathEffect,
        }),
      );

      if (response.statusCode == 200) {
        _lastResult = TTSResult.fromJson(json.decode(response.body));
        await loadHistory();
        _isLoading = false;
        notifyListeners();
        return _lastResult;
      } else {
        final errorData = json.decode(response.body);
        _error = errorData['detail'] ?? 'Generation failed';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Network error: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  String getAudioUrl(String filename) {
    return '$_baseUrl/../audio/$filename';
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
