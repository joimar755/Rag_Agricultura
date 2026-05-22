#include <WiFi.h>
#include <esp_now.h>
#include <DHT.h>
#include <esp_wifi.h> 

#define DHTPIN 33
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

// MAC del receptor (ESP32 #3)
uint8_t broadcastAddress[] = {0x94, 0x54, 0xC5, 0x77, 0x39, 0x78};

// 🔥 ESTRUCTURA UNIFICADA
typedef struct struct_message {
  int tipo;          // 1 = DHT, 2 = suelo
  float temperature;
  float humidity;
  int moisture;
} struct_message;

struct_message dataToSend;

unsigned long tiempo2 = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  Serial.print("MAC Emisor DHT: ");
  Serial.println(WiFi.macAddress());

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Error agregando peer");
    return;
  }
}

void loop() {

  if (millis() - tiempo2 >= 5000) {
    tiempo2 = millis();

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("Error leyendo DHT22");
      return;
    }

    // 🔥 LLENAR ESTRUCTURA
    dataToSend.tipo = 1;           // Sensor DHT
    dataToSend.temperature = t;
    dataToSend.humidity = h;
    dataToSend.moisture = 0;      // No aplica

    esp_err_t result = esp_now_send(
      broadcastAddress, 
      (uint8_t *)&dataToSend, 
      sizeof(dataToSend)
    );

    if (result == ESP_OK) {
      Serial.print(t);
      Serial.print(",");
      Serial.println(h);
    } else {
      Serial.println("Error al enviar");
    }
  }
}