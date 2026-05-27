import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_xlog/flutter_xlog.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

var cacheDir = '';
var logDir = '';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cacheDir = (await getApplicationCacheDirectory()).path;
  logDir = '';
  if (Platform.isAndroid) {
    logDir = (await getExternalCacheDirectories())?[0].path ?? cacheDir;
  } else if (Platform.isIOS) {
    logDir = (await getApplicationSupportDirectory()).path;
  }
  await XLog.open(XLogConfig(cacheDir: cacheDir, logDir: logDir, consoleLogOpen: true));
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {

  Future<void> _exportLogs(BuildContext context) async {
    final messenger = ScaffoldMessenger.of(context);
    try {
      XLog.i("MyApp", "export logs clicked");
      await XLog.flush(isSync: true);

      final dir = Directory(logDir);
      if (!await dir.exists()) {
        messenger.showSnackBar(
          const SnackBar(content: Text('Log directory not found')),
        );
        return;
      }

      final logFiles = await dir
          .list()
          .where((entity) => entity is File && entity.path.endsWith('.xlog'))
          .map((entity) => XFile(entity.path))
          .toList();

      if (logFiles.isEmpty) {
        messenger.showSnackBar(
          const SnackBar(content: Text('No .xlog files to export')),
        );
        return;
      }

      await SharePlus.instance.share(ShareParams(
        files: logFiles,
        subject: 'XLog export',
        text: 'Exported ${logFiles.length} xlog file(s) from $logDir',
      ));
    } catch (e, stack) {
      XLog.e("MyApp", "export logs failed: $e\n$stack");
      messenger.showSnackBar(
        SnackBar(content: Text('Export failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    XLog.i("MyApp", "build _MyAppState");
    compute((message) {
      XLog.i("MyApp", "$message in Isolate");
    }, "compute in build");
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('FlutterXLog example app'),
        ),
        body: Builder(
          builder: (context) => Column(
            children: [
              Text('Cached XLog in $cacheDir \nWrite XLog to $logDir \n'),
              TextButton(
                  onPressed: () {
                    XLog.i("MyApp", "click");
                    XLog.close();
                  },
                  child: const Text('close XLog')),
              TextButton(
                  onPressed: () => _exportLogs(context),
                  child: const Text('export XLog')),
            ],
          ),
        ),
      ),
    );
  }
}
