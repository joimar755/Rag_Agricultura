#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

// Estructura de datos que se recibirá
typedef struct struct_message {
  float temperature;
  float humidity;
} struct_message;

struct_message incomingData;

void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  memcpy(&incomingData, data, sizeof(incomingData));

  Serial.println("===== DATO RECIBIDO =====");
  Serial.print("Temperatura: ");
  Serial.print(incomingData.temperature);
  Serial.println(" °C");

  Serial.print("Humedad: ");
  Serial.print(incomingData.humidity);
  Serial.println(" %");
  Serial.println("=========================");
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);  // Coincidir con el emisor

  Serial.print("MAC del receptor: ");
  Serial.println(WiFi.macAddress());

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("Receptor listo, esperando datos...");
}

void loop() {
  // Nada aquí, el callback gestiona todo
}