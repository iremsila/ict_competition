import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class SustainabilityAdvicePage extends StatelessWidget {
  const SustainabilityAdvicePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SustainabilityAdvicePage '),
      ),
      body: const Center(
        child: Text('This is the Environmental Analysis Page'),
      ),
    );
  }
}