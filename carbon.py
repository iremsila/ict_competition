import requests
import pandas as pd
import io
import datetime
import hmac
import hashlib
import base64
import geocoder

# OBS Bağlantısı ve Veri Çekme
def fetch_data_from_obs():
    access_key = 'FHVV7UVUMRCHAUCWUX1R'  # Access Key ID
    secret_key = 'suqbDXVYpfqIP3rFKe1tkIfjdzMBLfoqIRDkwBcm'  # Secret Access Key
    bucket_name = 'enes'  # OBS Bucket adı
    object_name = 'karbon_ayak_izi.csv'  # Dosya adı
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

    # Eğer istek başarılıysa CSV verisini döndür
    if response.status_code == 200:
        print("OBS'den veri alındı!")
        csv_data = response.text
        return csv_data
    else:
        print(f"OBS'den veri alınamadı. Hata: {response.status_code}, {response.text}")
        return None

def display_csv_content(csv_data):
    csv_file = io.StringIO(csv_data)
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
    except UnicodeDecodeError:
        print("UTF-8 kodlamasında sorun oluştu, latin1 ile yeniden deniyoruz.")
        df = pd.read_csv(csv_file, encoding='latin1')

    df.columns = [col.encode('latin1').decode('utf-8') for col in df.columns]
    print("\nCSV Dosyasının Temizlenmiş İçeriği:")
    print(df)

# WAQI API URL ve Token
WAQI_BASE_URL = "https://api.waqi.info/feed"
WAQI_API_TOKEN = "demo"

# Hava kirliliği için eşik değerler
AIR_QUALITY_THRESHOLDS = {
    "pm10": 50,
    "pm2_5": 25,
    "so2": 20,
    "no2": 40,
    "co": 10,
}

# Risk seviyesine göre öneriler
AIR_QUALITY_RECOMMENDATIONS = {
    "Low": "Hava kaliteli. Açık havada aktiviteler için uygun.",
    "Moderate": "Hava kalitesi orta seviyede. Hassas gruplar dikkatli olmalı.",
    "High": "Hava sağlıksız seviyede. Açık hava aktivitelerinden kaçının.",
    "Very High": "Hava çok sağlıksız. Mümkünse evde kalın ve maske kullanın.",
}

TRANSPORT_OPTIONS = {
    1: "araba",
    2: "uçak",
    3: "tren",
    4: "bisiklet",
    5: "toplu_tasima",
}

ENERGY_OPTIONS = {
    1: "dogal_gaz",
    2: "elektrik",
    3: "yenilenebilir",
}

DIET_OPTIONS = {
    1: "et_agirlikli",
    2: "vejetaryen",
    3: "vegan",
}

def calculate_detailed_carbon_footprint(transport, transport_distance, energy, energy_usage, diet, waste, flights):
    transport_emission_factors = {
        "araba": 0.21,
        "uçak": 0.15,
        "tren": 0.05,
        "bisiklet": 0,
        "toplu_tasima": 0.1,
    }
    energy_emission_factors = {
        "dogal_gaz": 0.2,
        "elektrik": 0.15,
        "yenilenebilir": 0,
    }
    diet_emission_factors = {
        "et_agirlikli": 7,
        "vegan": 2,
        "vejetaryen": 4,
    }
    waste_emission_factor = 0.45
    flight_emission = flights * 90

    transport_emission = transport_emission_factors.get(transport, 0) * transport_distance
    energy_emission = energy_emission_factors.get(energy, 0) * energy_usage
    diet_emission = diet_emission_factors.get(diet, 0)
    waste_emission = waste * waste_emission_factor

    total_emission = transport_emission + energy_emission + diet_emission + waste_emission + flight_emission
    return total_emission

def get_user_location():
    location = geocoder.ip("me")
    if location.ok:
        return location.latlng
    else:
        raise Exception("Kullanıcının konumu alınamadı.")

def get_air_quality_data(lat, lon):
    """
    Hava kirliliği verilerini WAQI API'den alır.
    """
    url = f"{WAQI_BASE_URL}/geo:{lat};{lon}/?token={WAQI_API_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                iaqi = data["data"]["iaqi"]
                return {
                    "pm10": iaqi.get("pm10", {}).get("v", None),
                    "pm2_5": iaqi.get("pm25", {}).get("v", None),
                    "so2": iaqi.get("so2", {}).get("v", None),
                    "no2": iaqi.get("no2", {}).get("v", None),
                    "co": iaqi.get("co", {}).get("v", None),
                }
            else:
                raise ValueError(f"API yanıtı hatalı: {data.get('data', 'Bilinmeyen hata')}")
        else:
            raise ConnectionError(f"API isteği başarısız oldu. Durum kodu: {response.status_code}")
    except Exception as e:
        print(f"Hava kirliliği verisi alınırken hata oluştu: {e}")
        return None

def analyze_air_quality(air_quality_data):
    risks = []
    risk_level = "Low"

    for pollutant, value in air_quality_data.items():
        if value is not None and pollutant in AIR_QUALITY_THRESHOLDS:
            if value > AIR_QUALITY_THRESHOLDS[pollutant]:
                risks.append(f"{pollutant.upper()} yüksek: {value}")
                if value > AIR_QUALITY_THRESHOLDS[pollutant] * 2:
                    risk_level = "Very High"
                elif value > AIR_QUALITY_THRESHOLDS[pollutant] * 1.5:
                    risk_level = "High"
                elif value > AIR_QUALITY_THRESHOLDS[pollutant]:
                    risk_level = "Moderate"

    return risk_level, risks

def evaluate_carbon_footprint(carbon_footprint):
    """
    Karbon ayak izini değerlendirir ve uygun öneriler sunar.
    """
    THRESHOLD_LOW = 200  # kg CO2/ay
    THRESHOLD_HIGH = 500  # kg CO2/ay

    if carbon_footprint <= THRESHOLD_LOW:
        evaluation = "İdeal"
        recommendations = [
            "Harika! Karbon ayak iziniz düşük. Bu sürdürülebilir alışkanlıklarınızı korumaya devam edin.",
            "Toplu taşıma, bisiklet veya yürüyüş gibi çevre dostu ulaşım araçlarını kullanmaya devam edin.",
            "Geri dönüşüm alışkanlıklarınızı artırabilir ve başkalarını da teşvik edebilirsiniz."
        ]
    elif THRESHOLD_LOW < carbon_footprint <= THRESHOLD_HIGH:
        evaluation = "Orta"
        recommendations = [
            "Karbon ayak iziniz ortalama seviyede. Daha çevre dostu alışkanlıklar benimseyebilirsiniz.",
            "Daha az enerji tüketen cihazlar kullanarak enerji tasarrufu yapabilirsiniz.",
            "Haftalık et tüketiminizi azaltarak karbon emisyonlarınızı düşürebilirsiniz."
        ]
    else:
        evaluation = "Yüksek"
        recommendations = [
            "Karbon ayak iziniz yüksek. Çevreyi korumak için aşağıdaki önerilere göz atabilirsiniz:",
            "- Araba yerine toplu taşıma veya bisiklet tercih edin.",
            "- Evde enerji verimliliğini artırarak enerji tüketiminizi azaltın.",
            "- Gıda israfını önlemek için yemeklerinizi planlı tüketin ve yerel ürünler satın alın."
        ]

    return evaluation, recommendations

def main():
    print("Karbon Ayak İzi Uygulaması")
    print("1. Geçmiş karbon ayak izini görmek")
    print("2. Yeni karbon ayak izi hesaplamak ve hava kirliliği verilerini görüntülemek")
    choice = int(input("Bir seçim yapın (1 veya 2): "))

    if choice == 1:
        csv_data = fetch_data_from_obs()
        if csv_data:
            display_csv_content(csv_data)
        else:
            print("OBS'den veri alınamadı.")
    elif choice == 2:
        print("\nKarbon Ayak İzi Hesaplayıcı")

        # Ulaşım tercihi
        print("\nUlaşım seçenekleri: ")
        for key, value in TRANSPORT_OPTIONS.items():
            print(f"{key}: {value}")
        transport_choice = int(input("Ulaşım tercihiniz (1-5): "))
        transport = TRANSPORT_OPTIONS.get(transport_choice, "toplu_tasima")
        transport_distance = float(input("Günlük ulaşım mesafesi (km): "))

        # Enerji tercihi
        print("\nEnerji kullanım seçenekleri: ")
        for key, value in ENERGY_OPTIONS.items():
            print(f"{key}: {value}")
        energy_choice = int(input("Enerji kullanım tercihiniz (1-3): "))
        energy = ENERGY_OPTIONS.get(energy_choice, "elektrik")
        energy_usage = float(input("Aylık enerji tüketiminiz (kWh): "))

        # Beslenme tercihi
        print("\nBeslenme seçenekleri: ")
        for key, value in DIET_OPTIONS.items():
            print(f"{key}: {value}")
        diet_choice = int(input("Beslenme tercihiniz (1-3): "))
        diet = DIET_OPTIONS.get(diet_choice, "vejetaryen")

        # Diğer girdiler
        waste = float(input("\nHaftalık atık miktarınız (kg): "))
        flights = int(input("Yıllık uçuş sayınız: "))

        # Karbon ayak izi hesapla
        carbon_footprint = calculate_detailed_carbon_footprint(
            transport, transport_distance, energy, energy_usage, diet, waste, flights
        )
        print(f"\nToplam Karbon Ayak İziniz: {carbon_footprint:.2f} kg CO2")

        # Karbon ayak izi değerlendirme ve öneriler
        evaluation, recommendations = evaluate_carbon_footprint(carbon_footprint)
        print(f"\nKarbon Ayak İzi Değerlendirmesi: {evaluation}")
        print("Karbon Ayak İzi Azaltma Önerileri:")
        for rec in recommendations:
            print(f"- {rec}")

        # Hava kirliliği bilgilerini al
        try:
            lat, lon = get_user_location()
            print(f"\nKullanıcı Konumu: Enlem: {lat}, Boylam: {lon}")

            air_quality_data = get_air_quality_data(lat, lon)
            if air_quality_data:
                print("\nHava Kalitesi Verileri:")
                for key, value in air_quality_data.items():
                    print(f"  {key.upper()}: {value}")

                # Hava kirliliği analizi
                risk_level, risks = analyze_air_quality(air_quality_data)
                print(f"\nHava Kalitesi Risk Seviyesi: {risk_level}")
                if risks:
                    print("Hava Kalitesi Riskli Durumlar:")
                    for risk in risks:
                        print(f"  - {risk}")

                air_quality_recommendations = AIR_QUALITY_RECOMMENDATIONS.get(risk_level, "Duruma göre dikkatli olun.")
                print(f"\nHava Kalitesi Önerileri: {air_quality_recommendations}")
            else:
                print("\nHava kirliliği verileri alınamadı veya bulunamadı.")

        except Exception as e:
            print(f"\nHata: Hava kirliliği bilgileri alınırken sorun oluştu: {e}")

    else:
        print("Geçersiz seçim.")

if __name__ == "__main__":
    main()
