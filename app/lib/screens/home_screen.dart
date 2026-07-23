import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/tts_provider.dart';
import 'package:audioplayers/audioplayers.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _textController = TextEditingController();
  final AudioPlayer _audioPlayer = AudioPlayer();

  String _selectedVoice = 'female1';
  double _speed = 1.0;
  double _pitch = 1.0;
  double _volume = 1.0;
  String _selectedEmotion = 'neutral';
  bool _breathEffect = true;
  bool _isPlaying = false;

  final List<Map<String, String>> _emotions = [
    {'value': 'neutral', 'label': 'Neutral'},
    {'value': 'happy', 'label': 'Happy'},
    {'value': 'sad', 'label': 'Sad'},
    {'value': 'angry', 'label': 'Angry'},
    {'value': 'surprised', 'label': 'Surprised'},
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TTSProvider>().loadVoices();
    });
  }

  @override
  void dispose() {
    _textController.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _generateSpeech() async {
    if (_textController.text.trim().isEmpty) return;

    final provider = context.read<TTSProvider>();
    final result = await provider.generateSpeech(
      text: _textController.text.trim(),
      voiceId: _selectedVoice,
      speed: _speed,
      pitch: _pitch,
      volume: _volume,
      emotion: _selectedEmotion,
      breathEffect: _breathEffect,
    );

    if (result != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Generated: ${result.duration.toStringAsFixed(1)}s'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  Future<void> _playAudio(String filename) async {
    try {
      final provider = context.read<TTSProvider>();
      final url = provider.getAudioUrl(filename);
      await _audioPlayer.play(UrlSource(url));
      setState(() => _isPlaying = true);
      _audioPlayer.onPlayerComplete.listen((_) {
        setState(() => _isPlaying = false);
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Playback error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Voice Engine'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => _showHistory(context),
          ),
        ],
      ),
      body: Consumer<TTSProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildTextInput(),
                const SizedBox(height: 16),
                _buildVoiceSelector(provider),
                const SizedBox(height: 16),
                _buildControls(),
                const SizedBox(height: 16),
                _buildEmotionSelector(),
                const SizedBox(height: 16),
                _buildGenerateButton(provider),
                if (provider.error != null) ...[
                  const SizedBox(height: 8),
                  _buildErrorBanner(provider),
                ],
                if (provider.isLoading) ...[
                  const SizedBox(height: 16),
                  const Center(child: CircularProgressIndicator()),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildTextInput() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Text Input', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _textController,
              maxLines: 5,
              decoration: InputDecoration(
                hintText: 'Enter text to convert to speech...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${_textController.text.length} / 5000 characters',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVoiceSelector(TTSProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Voice Selection', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (provider.voices.isEmpty)
              const Center(child: CircularProgressIndicator())
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: provider.voices.map((voice) {
                  final isSelected = _selectedVoice == voice.id;
                  return ChoiceChip(
                    label: Text(voice.name),
                    selected: isSelected,
                    selectedColor: const Color(0xFF6C63FF),
                    onSelected: (selected) {
                      setState(() => _selectedVoice = voice.id);
                    },
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildControls() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Controls', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _buildSlider('Speed', _speed, 0.5, 2.0, (v) => setState(() => _speed = v)),
            _buildSlider('Pitch', _pitch, 0.5, 2.0, (v) => setState(() => _pitch = v)),
            _buildSlider('Volume', _volume, 0.0, 2.0, (v) => setState(() => _volume = v)),
            SwitchListTile(
              title: const Text('Breath Effect'),
              value: _breathEffect,
              onChanged: (v) => setState(() => _breathEffect = v),
              contentPadding: EdgeInsets.zero,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSlider(String label, double value, double min, double max, ValueChanged<double> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(width: 60, child: Text(label)),
          Expanded(
            child: Slider(
              value: value,
              min: min,
              max: max,
              onChanged: onChanged,
            ),
          ),
          SizedBox(width: 40, child: Text(value.toStringAsFixed(1))),
        ],
      ),
    );
  }

  Widget _buildEmotionSelector() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Emotion', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _emotions.map((emotion) {
                final isSelected = _selectedEmotion == emotion['value'];
                return ChoiceChip(
                  label: Text(emotion['label']!),
                  selected: isSelected,
                  selectedColor: const Color(0xFF6C63FF),
                  onSelected: (selected) {
                    setState(() => _selectedEmotion = emotion['value']!);
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGenerateButton(TTSProvider provider) {
    return ElevatedButton(
      onPressed: provider.isLoading ? null : _generateSpeech,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF6C63FF),
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: provider.isLoading
          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
          : const Text('Generate Speech', style: TextStyle(fontSize: 16)),
    );
  }

  Widget _buildErrorBanner(TTSProvider provider) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.error, color: Colors.red),
          const SizedBox(width: 8),
          Expanded(child: Text(provider.error!, style: const TextStyle(color: Colors.red))),
          IconButton(
            icon: const Icon(Icons.close, size: 16),
            onPressed: provider.clearError,
          ),
        ],
      ),
    );
  }

  void _showHistory(BuildContext context) {
    final provider = context.read<TTSProvider>();
    provider.loadHistory();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.9,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) {
          return Consumer<TTSProvider>(
            builder: (context, provider, _) {
              return Container(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text('History', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Expanded(
                      child: provider.history.isEmpty
                          ? const Center(child: Text('No history yet'))
                          : ListView.builder(
                              controller: scrollController,
                              itemCount: provider.history.length,
                              itemBuilder: (context, index) {
                                final entry = provider.history[index];
                                return Card(
                                  child: ListTile(
                                    leading: IconButton(
                                      icon: const Icon(Icons.play_arrow),
                                      onPressed: () => _playAudio(entry.filename),
                                    ),
                                    title: Text(
                                      entry.text,
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    subtitle: Text(
                                      'Voice: ${entry.voiceId} | ${entry.duration.toStringAsFixed(1)}s',
                                    ),
                                    trailing: Text(
                                      entry.language.toUpperCase(),
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
