#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include <uri/UriBraces.h>
#include <ESP32Servo.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include "esp_camera.h"
#define ENA    12
#define IN1    2 
#define IN2    14 
#define IN3    15 
#define IN4    13
#define ENB    16

#define THROTTLE_PIN 14
#define STEERING_PIN 2
#define FLASH_LED_PIN 4
#define RED_LED_PIN 33


// CHANGE YOUR WIFI CREDENTIALS!
char* WIFI_SSID = "NETGEAR05";
char* WIFI_PASS = "wuxiaohua1011";
const uint8_t fps = 10;    //sets minimum delay between frames, HW limits of ESP32 allows about 12fps @ 800x600


static auto loRes = esp32cam::Resolution::find(320, 240);
const char HANDSHAKE_START = '(';

WebServer server(80);
AsyncWebServer asyncServer(81);
AsyncWebSocket controlWS("/control");

Servo throttleServo;
Servo steeringServo;
volatile int32_t ws_throttle_read = 1500;
volatile int32_t ws_steering_read = 1500;


volatile bool isClientConnected = false;
bool isFlashLightOn = false;
bool isRedLEDOn = false;


void setup()
{
  Serial.begin(115200);
  Serial.setDebugOutput(false);

  Serial.println();
  pinMode(RED_LED_PIN, OUTPUT);

//  setupCamera();
//  setupWifi();
//  setupRoutes();
  setupMotor();
//  initWebSocket();

}


void loop()
{
//  server.handleClient();
//  controlWS.cleanupClients();

  leftForwardMode();
  rightForwardMode();


  ledcWrite(0, 200);   
  ledcWrite(1, 200); 
  Serial.println("Forward");

  delay(1000);

  leftBackwardMode();
  rightBackwardMode();
  Serial.println("Backward");
  delay(1000);

  
}

void setupMotor() {
  
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  ledcSetup(0, 30000, 8);
  ledcAttachPin(ENA, 0);

  ledcSetup(1, 30000, 8);
  ledcAttachPin(ENB, 1);
}

void onControlEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("Control WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("Control WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleControlWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void handleControlWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  char buf[len] = "\0";
  memcpy(buf, data, len);
  Serial.println(buf); 
}



void initWebSocket() {  
  asyncServer.begin();
  controlWS.onEvent(onControlEvent);
  asyncServer.addHandler(&controlWS);
}




// setup functions

void setupRoutes() {
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");
  Serial.println("  :81/control");

  server.on("/cam-lo.jpg", handleJpgLo);
  server.begin();
}


void setupWifi() {
  WiFi.disconnect(true);

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting ...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    blinkRedLED();
    Serial.print(".");
  }
  digitalWrite(RED_LED_PIN, LOW);
  Serial.println("Connected!");
}
void setupCamera() {
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(loRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(10);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
}

// handle routes
void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleMjpeg() {
  Serial.println("STREAM BEGIN");
  WiFiClient client = server.client();
  auto startTime = millis();
  int res = esp32cam::Camera.streamMjpeg(client);
  if (res <= 0) {
    Serial.printf("STREAM ERROR %d\n", res);
    return;
  }
  auto duration = millis() - startTime;
  Serial.printf("STREAM END %dfrm %0.2ffps\n", res, 1000.0 * res / duration);
}


// Utility functions
void blinkFlashlight() {
  if (isFlashLightOn) {
    ledcWrite(FLASH_LED_PIN, 0);
    isFlashLightOn = false;
  } else {
    ledcWrite(FLASH_LED_PIN, 100);
    isFlashLightOn = true;
  }
}

void blinkRedLED() {
  if (isRedLEDOn) {
    digitalWrite(RED_LED_PIN, HIGH);
    isRedLEDOn = false;
  } else {
    digitalWrite(RED_LED_PIN, LOW);
    isRedLEDOn = true;
  }
}



void leftForwardMode() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
}

void leftBackwardMode() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
}

void rightForwardMode() {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
} 
void rightBackwardMode() {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
}

void stopMode() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
