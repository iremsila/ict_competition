import 'package:permission_handler/permission_handler.dart';

Future<void> requestLocationPermission() async {
  // Konum iznini kontrol et
  PermissionStatus status = await Permission.location.request();

  // İzin durumu kontrol et
  if (status.isGranted) {
    print("Location permission granted");
    // İzin verildiyse, konum verisini alabilirsiniz
  } else if (status.isDenied) {
    print("Location permission denied");
    // İzin reddedildiyse kullanıcıyı bilgilendirebilirsiniz
  } else if (status.isPermanentlyDenied) {
    print("Location permission permanently denied");
    // Kalıcı olarak reddedildiyse, ayarlara yönlendirme yapabilirsiniz
  }
}
