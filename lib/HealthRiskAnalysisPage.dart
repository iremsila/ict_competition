import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class HealthRiskAnalysisPage extends StatelessWidget {
  const HealthRiskAnalysisPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HealthRisk Analysis'),
      ),
      body: const Center(
        child: Text('This is the Environmental Analysis Page'),
      ),
    );
  }
}