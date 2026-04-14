#include <WiFi.h>
#include <esp_now.h>
#include <DHT.h>
#include <esp_wifi.h> 


#define DHTPIN 33
#define DHTTYPE DHT22


//DHTTYPE = DHT11, but there are also DHT22 and 21
DHT dht(DHTPIN, DHTTYPE);  // constructor to declare our sensor

// Dirección MAC del receptor (reemplaza con la real del receptor)
uint8_t broadcastAddress[] = {0x94, 0x54, 0xC5, 0x77, 0x39, 0x78};  // <-- CAMBIA ESTO

typedef struct struct_message {
  float temperature;
  float humidity;
} struct_message;

struct_message dataToSend;


unsigned long tiempo2 = 0;

int LED1 = 27;
int LED2 = 26;
int LED3 = 25;


const int BTN1 = 13;
const int BTN2 = 12;
const int BTN3 = 14;

bool lastBtn1 = LOW;
bool lastBtn2 = LOW;
bool lastBtn3 = LOW;

bool statusE1 = false, statusE2 = false, statusE3 = false;

void setup() {
  Serial.begin(115200);
  dht.begin();

  //wifi y mac
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

  // leds y botones
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(BTN1, INPUT);
  pinMode(BTN2, INPUT);
  pinMode(BTN3, INPUT);

  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
}
void loop() {
  //Led();
  bool currentBtn1 = digitalRead(BTN1);
  if (lastBtn1 == HIGH && currentBtn1 == LOW) {  // transición ALTO → BAJO (pulsado)
    statusE1 = !statusE1;                        // cambiar estado del LED
    digitalWrite(LED1, statusE1);
    Serial.println(statusE1 ? "LED1 ENCENDIDO" : "LED1 APAGADO");
    delay(50);  // antirrebote
  }
  lastBtn1 = currentBtn1;

  // --- BOTÓN 2 ---
  bool currentBtn2 = digitalRead(BTN2);
  if (lastBtn2 == HIGH && currentBtn2 == LOW) {
    statusE2 = !statusE2;
    digitalWrite(LED2, statusE2);
    Serial.println(statusE2 ? "LED2 ENCENDIDO" : "LED2 APAGADO");
    delay(50);
  }
  lastBtn2 = currentBtn2;

  // --- BOTÓN 3 ---
  bool currentBtn3 = digitalRead(BTN3);
  if (lastBtn3 == HIGH && currentBtn3 == LOW) {
    statusE3 = !statusE3;
    digitalWrite(LED3, statusE3);
    Serial.println(statusE3 ? "LED3 ENCENDIDO" : "LED3 APAGADO");
    delay(50);
  }
  lastBtn3 = currentBtn3;

  if (millis() - tiempo2 >= 5000) {
    tiempo2 = millis();
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("Failed reception");
      return;
    } else {
      dataToSend.temperature = t;
      dataToSend.humidity = h;

      esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&dataToSend, sizeof(dataToSend));
      if (result == ESP_OK) {
        Serial.print(t);
        Serial.print(";");
        Serial.println(h);
      } else {
        Serial.println("Error al enviar");
      }
    }
  }
}