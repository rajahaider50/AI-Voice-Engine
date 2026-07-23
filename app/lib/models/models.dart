class Voice {
  final String id;
  final String name;
  final String gender;
  final String style;
  final String language;

  Voice({
    required this.id,
    required this.name,
    required this.gender,
    required this.style,
    required this.language,
  });

  factory Voice.fromJson(Map<String, dynamic> json) {
    return Voice(
      id: json['id'],
      name: json['name'],
      gender: json['gender'],
      style: json['style'],
      language: json['language'] ?? 'en',
    );
  }

  String get displayName => '$name ($style)';
}

class TTSResult {
  final String audioUrl;
  final double duration;
  final int sampleRate;
  final String voiceId;
  final String filename;

  TTSResult({
    required this.audioUrl,
    required this.duration,
    required this.sampleRate,
    required this.voiceId,
    required this.filename,
  });

  factory TTSResult.fromJson(Map<String, dynamic> json) {
    return TTSResult(
      audioUrl: json['audio_url'],
      duration: (json['duration'] as num).toDouble(),
      sampleRate: json['sample_rate'],
      voiceId: json['voice_id'],
      filename: json['filename'],
    );
  }
}

class HistoryEntry {
  final String timestamp;
  final String text;
  final String voiceId;
  final String language;
  final double duration;
  final String filename;

  HistoryEntry({
    required this.timestamp,
    required this.text,
    required this.voiceId,
    required this.language,
    required this.duration,
    required this.filename,
  });

  factory HistoryEntry.fromJson(Map<String, dynamic> json) {
    return HistoryEntry(
      timestamp: json['timestamp'],
      text: json['text'],
      voiceId: json['voice_id'],
      language: json['language'],
      duration: (json['duration'] as num).toDouble(),
      filename: json['filename'],
    );
  }
}
