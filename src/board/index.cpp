#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// Configuração da rede Wi-Fi
const char* ssid = "nome da rede wifi";
const char* password = "senha de wifi";

// IP local do servidor FastAPI (substitua pelo IP real da sua máquina)
const char* serverUrl = "http://seu_ip:8000/detectar";

const int sensorPin = 5;

// Cliente NTP
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -10800, 60000);  // GMT-3 (Brasil)

void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println("Iniciando...");
  pinMode(sensorPin, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");

  timeClient.begin();
}

void loop() {
  delay(2000);
  timeClient.update();

  int motion = digitalRead(sensorPin);
  if (motion == LOW) {
    Serial.println("Movimento detectado!");
    Serial.println(motion);
    
    time_t rawTime = timeClient.getEpochTime();
    struct tm* timeinfo = localtime(&rawTime);
    char dateTime[30];
    strftime(dateTime, sizeof(dateTime), "%Y-%m-%d %H:%M:%S", timeinfo);

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String jsonPayload = "{\"timestamp\": \"" + String(dateTime) + "\"}";
      Serial.println("Enviando: " + jsonPayload);

      int responseCode = http.POST(jsonPayload);

      if (responseCode > 0) {
        String response = http.getString();
        Serial.println("Resposta: " + response);
      } else {
        Serial.print("Erro HTTP: ");
        Serial.println(responseCode);
      }

      http.end();
    }

    delay(5000);
  }

  delay(200);
}