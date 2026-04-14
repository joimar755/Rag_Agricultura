#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "JESUS_ES_MI_LUZ";
const char* password = "1045727000";

String serverDatos = "http://192.168.1.4:8000/sensor-data";

typedef struct struct_message {
  float temperature;
  float humidity;
} struct_message;

struct_message incomingData;

// 🔹 Variables de control
bool hayDatos = false;
float tempGlobal = 0;
float humGlobal = 0;

unsigned long tiempo2 = 0;

// 🔹 Callback SOLO guarda datos
void OnDataRecv(const esp_now_recv_info_t* info, const uint8_t* data, int len) {
  memcpy(&incomingData, data, sizeof(incomingData));

  tempGlobal = incomingData.temperature;
  humGlobal = incomingData.humidity;
  hayDatos = true;

  Serial.println("Dato recibido (guardado)");
}

// 🔹 Envío HTTP (fuera del callback)
void enviarDatos(float t, float h) {
  HTTPClient http;

  Serial.println("Enviando a:");
  Serial.println(serverDatos);

  http.begin(serverDatos);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> jsonDoc;
  jsonDoc["temperatura"] = t;
  jsonDoc["humedad"] = h;

  String jsonString;
  serializeJson(jsonDoc, jsonString);

  int httpResponseCode = http.POST(jsonString);

  Serial.print("Código HTTP: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.println("Error en POST (fallo conexión)");
  }

  http.end();
}

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());  // 🔥 IMPORTANTE

  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("Receptor listo...");
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() == WL_CONNECTED) {

    if (now - tiempo2 >= 5000) {  // 🔥 cada 2 segundos (más rápido)
      
      if (hayDatos) {
        enviarDatos(tempGlobal, humGlobal);
        //hayDatos = false;
      }

      tiempo2 = now;
    }

  } else {
    Serial.println("WiFi perdido");
  }
}