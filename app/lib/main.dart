import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/tts_provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const AIVoiceApp());
}

class AIVoiceApp extends StatelessWidget {
  const AIVoiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => TTSProvider(),
      child: MaterialApp(
        title: 'AI Voice Engine',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6C63FF),
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xFF0D1117),
          cardTheme: CardTheme(
            color: const Color(0xFF161B22),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: Color(0xFF30363D)),
            ),
          ),
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
