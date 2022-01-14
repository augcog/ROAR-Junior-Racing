#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "NETGEAR78";
const char* WIFI_PASS = "wuxiaohua1011";

WebServer server(80);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);

#define LEFT_PIN_1 2
#define LEFT_PIN_2 14
#define RIGHT_PIN_1 15
#define RIGHT_PIN_2 13


void setup() {
  Serial.begin(115200);

  pinMode(LEFT_PIN_1, OUTPUT);
  pinMode(LEFT_PIN_2, OUTPUT);
  pinMode(RIGHT_PIN_1, OUTPUT);
  pinMode(RIGHT_PIN_2, OUTPUT);

  stop();

  setupCamera();
  setupWiFi();
}

void loop() {
  server.handleClient();
  
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
}

void handleBackward() {
  backward();
  server.send(200, "text");
}

void handleStop() {
  stop();
  server.send(200, "text");
}

void handleTurnLeft(){ 
  turnLeft();
  server.send(200, "text");
}
void handleTurnRight(){ 
  turnRight();
  server.send(200, "text");
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
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

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
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

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

  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");
  Serial.println("  /forward");
  Serial.println("  /stop");
  Serial.println("  /backward");
  Serial.println("  /turnLeft");
  Serial.println("  /turnRight");

  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);

  server.on("/forward", handleForward);
  server.on("/backward", handleBackward);
  server.on("/stop", handleStop);
  server.on("/turnLeft", handleTurnLeft);
  server.on("/turnRight", handleTurnRight);

  server.begin();
}