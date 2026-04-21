#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 🔹 WiFi
const char* ssid = "Joimar";
const char* password = "Joimar***";

// 🔹 API
String serverDatos = "http://10.42.0.1:8000/sensor-data";

// 🔥 ESTRUCTURA UNIFICADA (igual en TODOS los ESP)
typedef struct struct_message {
  int tipo;  // 1 = DHT, 2 = suelo
  float temperature;
  float humidity;
  int moisture;
} struct_message;

struct_message incomingData;

// 🔹 Variables globales
float tempGlobal = 0;
float humGlobal = 0;
int soilGlobal = 0;

bool hayDatos = false;
unsigned long tiempo2 = 0;

// 🔥 CALLBACK ESP-NOW
void OnDataRecv(const esp_now_recv_info_t* info, const uint8_t* data, int len) {

  memcpy(&incomingData, data, sizeof(incomingData));

  // Identificar qué sensor envió
  if (incomingData.tipo == 1) {
    tempGlobal = incomingData.temperature;
    humGlobal = incomingData.humidity;
    Serial.println("📡 Datos DHT recibidos");
  }

  if (incomingData.tipo == 2) {
    soilGlobal = incomingData.moisture;
    Serial.println("🌱 Datos suelo recibidos");
  }

  // Mostrar MAC del emisor (opcional debug)
  Serial.print("Desde: ");
  for (int i = 0; i < 6; i++) {
    Serial.print(info->src_addr[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.println();

  hayDatos = true;
}

// 🔥 FUNCIÓN PARA ENVIAR A FASTAPI
void enviarDatos() {
  HTTPClient http;

  http.begin(serverDatos);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> jsonDoc;
  jsonDoc["temperatura"] = tempGlobal;
  jsonDoc["humedad"] = humGlobal;
  jsonDoc["humedad_suelo"] = soilGlobal;


  String jsonString;
  serializeJson(jsonDoc, jsonString);

  int httpResponseCode = http.POST(jsonString);

  Serial.print("Código HTTP: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.println("Error en POST");
  }

  http.end();
}

void setup() {
  Serial.begin(115200);

  // 🔹 Conectar WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());

  // 🔹 Canal ESP-NOW (igual en todos)
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  // 🔹 Inicializar ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("✅ Receptor listo...");
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() == WL_CONNECTED) {

    if (now - tiempo2 >= 5000) {
      tiempo2 = now;

      if (hayDatos) {
        enviarDatos();
        // hayDatos = false; // opcional si quieres evitar envíos repetidos

        Serial.print(tempGlobal);
        Serial.print(",");
        Serial.print(humGlobal);
        Serial.print(",");
        Serial.println(soilGlobal);
      }
    }

  } else {
    Serial.println("WiFi perdido");
  }
}