import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart'; // Google Maps package
import 'package:geolocator/geolocator.dart'; // Geolocation package
import 'package:fl_chart/fl_chart.dart'; // FlChart package for graph

class EnvironmentalAnalysisPage extends StatefulWidget {
  const EnvironmentalAnalysisPage({Key? key}) : super(key: key);

  @override
  _EnvironmentalAnalysisPageState createState() =>
      _EnvironmentalAnalysisPageState();
}

class _EnvironmentalAnalysisPageState extends State<EnvironmentalAnalysisPage> {
  late GoogleMapController mapController;
  Set<Marker> _markers = {};
  Position? _currentPosition;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    mapController.dispose(); // Harita kontrolcüsünü temizliyoruz
    super.dispose();
  }

  Future<void> _getCurrentLocation() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        _assignDefaultLocation();
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      _assignDefaultLocation();
      return;
    }

    try {
      // Konumu alma
      Position position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high);
      if (!mounted) return; // Widget ağacında olmadığını kontrol ediyoruz
      setState(() {
        _currentPosition = position;
        _markers.add(Marker(
          markerId: MarkerId('current_location'),
          position: LatLng(position.latitude, position.longitude),
          infoWindow: InfoWindow(title: 'Your Location'),
        ));
      });
    } catch (e) {
      _assignDefaultLocation();
    }
  }

  // Varsayılan konum atama fonksiyonu
  void _assignDefaultLocation() {
    if (!mounted) return; // Widget ağacında olmadığını kontrol ediyoruz
    setState(() {
      _currentPosition = Position(
        latitude: 37.7749, // Örnek enlem
        longitude: -122.4194, // Örnek boylam
        timestamp: DateTime.now(),
        accuracy: 0.0,
        altitude: 0.0,
        heading: 0.0,
        speed: 0.0,
        speedAccuracy: 0.0,
        altitudeAccuracy: 0.0,
        headingAccuracy: 0.0,
      );
      _markers.add(Marker(
        markerId: MarkerId('default_location'),
        position: LatLng(37.7749, -122.4194),
        infoWindow: InfoWindow(title: 'Default Location'),
      ));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Environmental Analysis'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              _showRiskAlert();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Harita Entegrasyonu
          Expanded(
            child: _currentPosition == null
                ? Center(child: CircularProgressIndicator())
                : GoogleMap(
              onMapCreated: (GoogleMapController controller) {
                mapController = controller;
              },
              initialCameraPosition: CameraPosition(
                target: LatLng(_currentPosition!.latitude,
                    _currentPosition!.longitude),
                zoom: 12,
              ),
              markers: _markers,
            ),
          ),
          // Çevresel Faktörlerin Zaman İçindeki Değişimi Grafiği
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: LineChart(
              LineChartData(
                gridData: FlGridData(show: true),
                titlesData: FlTitlesData(show: true),
                borderData: FlBorderData(show: true),
                minX: 0,
                maxX: 7,
                minY: 0,
                maxY: 100,
                lineBarsData: [
                  LineChartBarData(
                    spots: [
                      FlSpot(0, 20),
                      FlSpot(1, 40),
                      FlSpot(2, 60),
                      FlSpot(3, 50),
                      FlSpot(4, 80),
                      FlSpot(5, 70),
                      FlSpot(6, 90),
                    ]
                        .where((spot) =>
                    !spot.y.isNaN && !spot.y.isInfinite)
                        .toList(),
                    isCurved: true,
                    color: Colors.blue,
                    dotData: FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: Colors.blue.withOpacity(0.3),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showRiskAlert() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Risk Alert'),
        content: const Text(
            'The air quality is unhealthy. Avoid outdoor activities.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
