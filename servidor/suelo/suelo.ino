#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

#define AOUT_PIN 34
  // Pin analógico del sensor de suelo

// MAC del receptor (ESP32 #3)
uint8_t broadcastAddress[] = {0x94, 0x54, 0xC5, 0x77, 0x39, 0x78};

// 🔥 ESTRUCTURA UNIFICADA (igual en los 3 ESP)
typedef struct struct_message {
  int tipo;          // 1 = DHT, 2 = suelo
  float temperature;
  float humidity;
  int moisture;
} struct_message;

struct_message dataToSend;

unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);

  // Mejor rango ADC
  analogSetAttenuation(ADC_11db);

  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  Serial.print("MAC Emisor Suelo: ");
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
  if (millis() - lastTime > 5000) {
    lastTime = millis();

    int value = analogRead(AOUT_PIN);

    // 🔥 LLENAR ESTRUCTURA
    dataToSend.tipo = 2;       // Sensor de suelo
    dataToSend.temperature = 0;
    dataToSend.humidity = 0;
    dataToSend.moisture = value;

    esp_err_t result = esp_now_send(
      broadcastAddress,
      (uint8_t *)&dataToSend,
      sizeof(dataToSend)
    );

    if (result == ESP_OK) {
      Serial.print("Humedad suelo enviada: ");
      Serial.println(value);
    } else {
      Serial.println("Error al enviar");
    }
  }
}