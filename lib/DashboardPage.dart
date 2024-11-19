import 'package:flutter/material.dart';

import 'EnvironmentalAnalysisPage.dart';
import 'HealthRiskAnalysisPage.dart';
import 'ProfilePage.dart';
import 'SustainabilityAdvicePage.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({Key? key}) : super(key: key);

  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _currentIndex = 0;

  // Her sekmeye karşılık gelen sayfalar
  final List<Widget> _pages = [
    const CustomDashboardScreen(), // Yeni Dashboard ekranı
    const EnvironmentalAnalysisPage(),
    const HealthRiskAnalysisPage(),
    const SustainabilityAdvicePage(),
    const ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex], // Aktif sekmeye göre sayfayı göster
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.black54,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map),
            label: 'Environment',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.health_and_safety),
            label: 'Health Risk',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.eco),
            label: 'Sustainability',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class CustomDashboardScreen extends StatelessWidget {
  const CustomDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.blue.shade900, Colors.blue.shade300],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Dashboard",
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 20),
                Expanded(
                  child: ListView(
                    children: [
                      const SectionTitle(title: "Health Summary"),
                      const HealthCard(
                        icon: Icons.favorite,
                        title: "Heart Rate",
                        value: "76 bpm",
                        color: Colors.red,
                      ),
                      const SectionTitle(title: "Environmental Summary"),
                      const EnvironmentCard(
                        icon: Icons.air,
                        title: "Air Quality",
                        value: "Good (AQI 45)",
                        color: Colors.green,
                      ),
                      EnvironmentCard(
                        icon: Icons.thermostat,
                        title: "Temperature",
                        value: "22°C",
                        color: Colors.orange,
                      ),
                      EnvironmentCard(
                        icon: Icons.opacity,
                        title: "Humidity",
                        value: "60%",
                        color: Colors.lightBlue,
                      ),

                      SectionTitle(title: "Notifications & Alerts"),
                      NotificationCard(
                        title: "Stay Hydrated",
                        message: "It's a hot day. Drink plenty of water!",
                      ),
                      NotificationCard(
                        title: "Air Quality Alert",
                        message: "Avoid outdoor activities due to poor air quality.",
                      ),

                      SectionTitle(title: "History & Trends"),
                      // Placeholder for future charts
                      Container(
                        height: 200,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 10,
                              offset: Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            "Graph Visualizations Placeholder",
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// Bölüm Başlıkları için Widget
class SectionTitle extends StatelessWidget {
  final String title;
  const SectionTitle({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
    );
  }
}

// Sağlık ve Çevresel Kartlar için Widget
class HealthCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const HealthCard({
    Key? key,
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 4,
      color: color.withOpacity(0.8),
      child: ListTile(
        leading: Icon(icon, size: 36, color: Colors.white),
        title: Text(
          title,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          value,
          style: const TextStyle(color: Colors.white70),
        ),
      ),
    );
  }
}

class EnvironmentCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const EnvironmentCard({
    Key? key,
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return HealthCard(icon: icon, title: title, value: value, color: color);
  }
}

// Bildirim Kartları için Widget
class NotificationCard extends StatelessWidget {
  final String title;
  final String message;

  const NotificationCard({
    Key? key,
    required this.title,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 4,
      color: Colors.yellow.shade200,
      child: ListTile(
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(message),
      ),
    );
  }
}


