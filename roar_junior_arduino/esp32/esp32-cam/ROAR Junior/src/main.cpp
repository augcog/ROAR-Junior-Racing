#include <Arduino.h>

#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include "ESPAsyncWebServer.h"


#define ENA 12
#define LEFT_PIN_1 13
#define LEFT_PIN_2 15
#define RIGHT_PIN_1 14
#define RIGHT_PIN_2 2
#define ENB 16
#define FLASH_LIGHT_PIN 4

#define TRIGGER_PIN 3 // this HAS to be a TX pin, or GPIO 3
#define ECHO_PIN 1 // this HAS to be a RX pin, or GPIO 1

#define ENA_PWM_Channel 14 
#define ENB_PWM_Channel 15
#define FLASH_LIGHT_CHANNEL 0
#define SOUND_SPEED 0.034

const char* WIFI_SSID = "NETGEAR78";
const char* WIFI_PASS = "wuxiaohua1011";

WebServer server(80);
AsyncWebServer asyncServer(81);

volatile float ultrasonic_reading = 0;

// Setting PWM properties
const int freq = 30000;
const int pwmChannel = 2;
const int resolution = 8;
int dutyCycle = 255;

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);



void stop();
void setupCamera();
void setupWiFi();
float pullUltrasonicReading();
void processSpdLeft(float val) ;
void processSpdRight(float val) ;


void processSpdLeft(float val) {
  uint8_t pwm = (uint8_t)(val*255.99);
  ledcWrite(ENA_PWM_Channel, pwm);
}
void processSpdRight(float val) {
  uint8_t pwm = (uint8_t)(val*255.99);
  ledcWrite(ENB_PWM_Channel, pwm);
}
void turnRight() {
    digitalWrite(LEFT_PIN_1, 1);
    digitalWrite(LEFT_PIN_2, 0);
    digitalWrite(RIGHT_PIN_1, 0);
    digitalWrite(RIGHT_PIN_2, 1);
}

void turnLeft() {
    digitalWrite(LEFT_PIN_1, 0);
    digitalWrite(LEFT_PIN_2, 1);
    digitalWrite(RIGHT_PIN_1, 1);
    digitalWrite(RIGHT_PIN_2, 0);
}

void forward(){
    digitalWrite(LEFT_PIN_1, 1);
    digitalWrite(LEFT_PIN_2, 0);
    digitalWrite(RIGHT_PIN_1, 1);
    digitalWrite(RIGHT_PIN_2, 0);
}

void backward(){
    digitalWrite(LEFT_PIN_1, 0);
    digitalWrite(LEFT_PIN_2, 1);
    digitalWrite(RIGHT_PIN_1, 0);
    digitalWrite(RIGHT_PIN_2, 1);
}

void stop() {
  digitalWrite(LEFT_PIN_1, 0);
  digitalWrite(LEFT_PIN_2, 0);
  digitalWrite(RIGHT_PIN_1, 0);
  digitalWrite(RIGHT_PIN_2, 0);
}


void handleForward() {
  forward();
  server.send(200, "text");
  Serial.println("Forward Mode");
}

void handleBackward() {
  backward();
  server.send(200, "text");
  Serial.println("Backward Mode");
}

void handleStop() {
  stop();
  server.send(200, "text");
  Serial.println("Stop Mode");
}

void handleTurnLeft(){ 
  turnLeft();
  server.send(200, "text");
  Serial.println("Left Turn Mode");
}
void handleTurnRight(){ 
  turnRight();
  server.send(200, "text");
  Serial.println("Right Turn Mode");
}

void
handleBmp()
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
  // Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
  //               static_cast<int>(frame->size()));

  if (!frame->toBmp()) {
    Serial.println("CONVERT FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CONVERT OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/bmp");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void
serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  // Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
  //               static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void
handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void
handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void
handleJpg()
{
  server.sendHeader("Location", "/cam-hi.jpg");
  server.send(302, "", "");
}

void
handleMjpeg()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }

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

void setupCamera() {
{
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }  
}

void setupWiFi() {
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);

  server.begin();


  asyncServer.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
              {
                int paramsNr = request->params();
                for (int i = 0; i < paramsNr; i++)
                {
                  AsyncWebParameter *p = request->getParam(i);

                  String name = p->name();
                  String val = p-> value();

                  if (name == "forward" && val == String("True")) {
                    forward();
                  } else if (name == "backward" && val == String("True")) {
                    backward();
                  } else if (name == "stop" && val == "True") {
                    stop(); 
                  } else if (name == "turnLeft" && val == "True") {
                    turnLeft();
                  } else if (name == "turnRight" && val == "True") {
                    turnRight();
                  } else if (name == "left_spd") {
                      processSpdLeft(val.toFloat());
                  } else if (name == "right_spd") {
                      processSpdRight(val.toFloat());
                  } else {
                    Serial.println("Unknown Name and val found: ");
                    Serial.print("Param name: ");
                    Serial.println(p->name());
                    Serial.print("Param value: ");
                    Serial.println(p->value());
                    Serial.println("------");
                  }
                }
                request->send(200, "text/plain", 
                    String(pullUltrasonicReading())
                  );
              });

    asyncServer.begin();

  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println(":80");
  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");
  Serial.println("  ");

  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81");
}

void setup() {
  Serial.begin(115200);

  // // MOTOR
  pinMode(LEFT_PIN_1, OUTPUT);
  pinMode(LEFT_PIN_2, OUTPUT);
  pinMode(RIGHT_PIN_1, OUTPUT);
  pinMode(RIGHT_PIN_2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  ledcSetup(ENA_PWM_Channel, 30000, 8);
  ledcAttachPin(ENA, ENA_PWM_Channel);

  ledcSetup(ENB_PWM_Channel, 30000, 8);
  ledcAttachPin(ENB, ENB_PWM_Channel);
  stop();

  // FLASHLIGHT  
  ledcSetup(FLASH_LIGHT_PIN, 5000, 8);
  ledcAttachPin(FLASH_LIGHT_PIN, FLASH_LIGHT_CHANNEL);
  ledcWrite(FLASH_LIGHT_CHANNEL, 0);

  // Ultrasonic Sensor
  pinMode(TRIGGER_PIN, OUTPUT); // Sets the trigPin as an Output
  pinMode(ECHO_PIN, INPUT); // Sets the echoPin as an Input

  setupCamera();
  setupWiFi();


}

void loop() {
  server.handleClient();
}

float pullUltrasonicReading() {
  // Clears the trigPin
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  long duration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate the distance
  float distanceCm = duration * SOUND_SPEED/2;
  return distanceCm;
}