#include <WiFi.h>
#include <esp_now.h>
#include <DHT.h>
#include <esp_wifi.h>  // Para fijar canal

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Dirección MAC del receptor (reemplaza con la real del receptor)
uint8_t broadcastAddress[] = {0xC8, 0xF0, 0x9E, 0xF2, 0xE7, 0xB4};  // <-- CAMBIA ESTO

typedef struct struct_message {
  float temperature;
  float humidity;
} struct_message;

struct_message dataToSend;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);  // Ambos deben usar el mismo canal
  dht.begin();

  Serial.print("Mi MAC (emisor): ");
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
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println("Lectura inválida del DHT11");
  } else {
    dataToSend.temperature = t;
    dataToSend.humidity = h;

    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &dataToSend, sizeof(dataToSend));

    if (result == ESP_OK) {
      Serial.print("Enviado: ");
      Serial.print(t);
      Serial.print(" °C, ");
      Serial.print(h);
      Serial.println(" %");
    } else {
      Serial.println("Error al enviar");
    }
  }

  delay(3000); // Espera mínima recomendada para DHT11
}