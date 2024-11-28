import requests
import datetime
import hashlib
import hmac
import base64
import csv
import io

# OBS Bağlantısı ve Veri Çekme
def fetch_data_from_obs(user_name):
    access_key = 'FHVV7UVUMRCHAUCWUX1R'  # Access Key ID
    secret_key = 'suqbDXVYpfqIP3rFKe1tkIfjdzMBLfoqIRDkwBcm'  # Secret Access Key
    bucket_name = 'enes'  # OBS Bucket adı
    object_name = 'health_data.csv'  # Dosya adı
    endpoint = 'https://obs.tr-west-1.myhuaweicloud.com'  # OBS endpoint

    # OBS URL
    url = f"{endpoint}/{bucket_name}/{object_name}"

    # İstek zamanı
    now = datetime.datetime.utcnow()
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

    # İmzalama işlemi (Authorization header'ı oluşturmak için)
    string_to_sign = f"GET\n\n\n{date_str}\n/{bucket_name}/{object_name}"
    h = hmac.new(secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(h.digest()).decode('utf-8')
    authorization_header = f"AWS {access_key}:{signature}"

    # HTTP GET isteği
    headers = {
        'Date': date_str,
        'Authorization': authorization_header
    }

    response = requests.get(url, headers=headers)

    # Eğer istek başarılıysa, veriyi CSV olarak işleyelim
    if response.status_code == 200:
        print("OBS'den veri alındı!")
        csv_data = response.text

        # Veriyi işleyelim (CSV formatını Python listesine dönüştürelim)
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.reader(csv_file)

        user_data = None
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue  # Skip header row
            if row[0].lower() == user_name.lower():
                user_data = row
                break

        if user_data:
            return user_data
        else:
            print(f"{user_name} kullanıcısına ait veri bulunamadı.")
            return None
    else:
        print(f"OBS'den veri alınamadı. Hata: {response.status_code}, {response.text}")
        return None

# Risk Analizi ve Rapor Oluşturma
def generate_risk_report(data):
    name = data[0]
    try:
        pulse = int(data[1])  # Nabız
        blood_pressure = int(data[2])  # Kan Basıncı
        sleep_duration = float(data[3])  # Uyku Süresi
        blood_sugar = int(data[4])  # Kan Şekeri
        cholesterol = int(data[5])  # Kolesterol
        step_count = int(data[6])  # Adım Sayısı
        water_intake = float(data[7])  # Su Tüketimi (litre)
    except ValueError:
        return "Verilerde hata tespit edildi. Lütfen geçerli veriler girildiğinden emin olun."

    report = f"Detaylı Risk Raporu - {name}:\n\n"

    # Nabız riski
    if pulse < 60:
        report += "⚠ Düşük Nabız: Nabzınız çok düşük görünüyor. Bir doktora başvurmanız önerilir. Potansiyel bradikardi riski.\n"
    elif pulse > 100:
        report += "⚠ Yüksek Nabız: Nabzınız normalden yüksek. Stres veya kardiyovasküler sorunlar olabilir. Rahatlama teknikleri deneyin ve bir uzmana danışın.\n"
    else:
        report += "✅ Nabız Normal: Nabzınız normal seviyede. Takip etmeye devam edin.\n"

    # Kan basıncı riski
    if blood_pressure < 90:
        report += "⚠ Düşük Kan Basıncı: Tansiyonunuz çok düşük olabilir. Halsizlik veya baş dönmesi yaşayabilirsiniz. Hafif tuz artışı ve yeterli su tüketimi önerilir.\n"
    elif blood_pressure > 140:
        report += "⚠ Yüksek Kan Basıncı: Hipertansiyon belirtileri gösteriyorsunuz. Tuz tüketimini azaltın ve bir uzmana danışın.\n"
    else:
        report += "✅ Kan Basıncı Normal: Tansiyon değerleriniz normal seviyede. Dengeli beslenmeye devam edin.\n"

    # Uyku süresi riski
    if sleep_duration < 7:
        report += "⚠ Yetersiz Uyku: Uyku süreniz önerilen 7-9 saatin altında. Daha fazla dinlenmeye çalışın.\n"
    elif sleep_duration > 9:
        report += "⚠ Fazla Uyku: Uyku süreniz 9 saatten fazla. Bu, sağlık sorunlarına işaret edebilir. Bir doktora danışın.\n"
    else:
        report += "✅ Uyku Süresi Normal: Uyku süreniz önerilen aralıkta. İyi bir uyku sağlığınız için önemlidir.\n"

    # Kan şekeri riski
    if blood_sugar < 70:
        report += "⚠ Düşük Kan Şekeri: Kan şekeriniz düşük. Hipoglisemiyi önlemek için bir şeyler yemeniz önerilir.\n"
    elif blood_sugar > 140:
        report += "⚠ Yüksek Kan Şekeri: Kan şekeriniz yüksek. Diyetinizi gözden geçirin ve bir doktora danışın. Egzersiz yapın.\n"
    else:
        report += "✅ Kan Şekeri Normal: Kan şekeriniz normal seviyede. Dengeli bir diyet uygulamaya devam edin.\n"

    # Kolesterol riski
    if cholesterol > 200:
        report += "⚠ Yüksek Kolesterol: Kolesterol seviyeniz yüksek. Doymuş yağ tüketimini azaltın ve egzersiz yapın. Bir uzmana danışın.\n"
    else:
        report += "✅ Kolesterol Normal: Kolesterol seviyeniz normal. Sağlıklı beslenmeye devam edin.\n"

    # Adım sayısı riski
    if step_count < 5000:
        report += "⚠ Düşük Adım Sayısı: Günlük adım sayınız çok düşük. Daha fazla yürümeye çalışın.\n"
    elif step_count < 8000:
        report += "⚠ Yetersiz Adım Sayısı: Günlük adım hedefinize ulaşmak için daha fazla hareket edin. 10.000 adım hedeflenmeli.\n"
    elif step_count >= 10000:
        report += "✅ Harika Adım Sayısı: Aktif bir yaşam tarzını koruyorsunuz! Devam edin.\n"
    else:
        report += "✅ Adım Sayısı Normal: Adım sayınız yeterli ancak mümkünse daha fazla hareket etmeyi hedefleyin.\n"

    # Su tüketimi riski
    if water_intake < 1.5:
        report += "⚠ Düşük Su Tüketimi: Günlük su tüketiminiz çok düşük. Vücut fonksiyonlarınızı sürdürebilmek için en az 2 litre su içmeye çalışın.\n"
    elif water_intake < 2:
        report += "⚠ Az Su Tüketimi: Su tüketiminizi artırın ve günlük en az 2 litre su içmeye çalışın.\n"
    elif water_intake > 3.5:
        report += "⚠ Aşırı Su Tüketimi: Aşırı su içmek elektrolit dengesini bozabilir. İhtiyacınıza uygun şekilde su tüketin.\n"
    else:
        report += "✅ Su Tüketimi Normal: Su tüketiminiz önerilen seviyede. Doğru hidrasyon sağlık için önemlidir.\n"

    return report

# Kullanıcı adı soralım ve raporu oluşturalım
user_name = input("Lütfen kullanıcı adınızı girin: ").strip()
data = fetch_data_from_obs(user_name)

if data:
    risk_report = generate_risk_report(data)
    print(risk_report)
else:
    print("Kullanıcı verisi bulunamadı!")
