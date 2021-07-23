/**
 * This module is written for Arduino Nano BLE 33. 
 * 
 * You would need to install LSM9Ds1 & MadgwickAHRS from the Arduino Library ( Go to Tools -> Manage Libraries)
 * 
 * Also Ultrasonic by Erick Simões
 * https://github.com/ErickSimoes/Ultrasonic
 * 
 * The Service and Characteristics and UUID are hard set in the bluetooth module. However, the device UUID is not. 
 * 
 * User need to query the device ID by scanning all surrounding BLE device. This device should show up with the name of `ROAR`
 * 
 * 
 * 
 */

#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
#include <stdlib.h>
#include <Ultrasonic.h>

#define PIN_LED     (13u)
#define LED_BUILTIN PIN_LED
#define LEDR        (22u)
#define LEDG        (23u)
#define LEDB        (24u)
#define LED_PWR     (25u)


/*
 * These are the pins that you need to plug in
 */
const int motorLeftPWMPin = 2;
const int motorLeftpin1 = 3;
const int motorLeftpin2 = 4;
const int motorRightpin1 = 5;
const int motorRightpin2 = 6;
const int motorRightPWMPin = 7;
const int leftTrackingSensorPin = 8;
const int rightTrackingSensorPin = 9;
const int triggerPin = 10;
const int echoPin = 11;


const char* nameOfPeripheral = "ROAR";
const char* controlServiceUUID = "00001101-0000-1000-8000-00805f9b34fb";
const char* sensorsServiceUUID = "00001102-0000-1000-8000-00805f9b34fb";

const char* lineTrackingAndUltrasonicServiceUUID = "00001103-0000-1000-8000-00805f9b34fb";

const char* motorLeftPWMCharRXUUID = "00000000-0000-0000-0000-000000000000";
const char* motorRightPWMCharRXUUID = "00000000-0000-0000-0000-000000000001";
const char* motorLeftPWMCharTXUUID = "00000000-0000-0000-0000-000000000002";
const char* motorRightPWMCharTXUUID = "00000000-0000-0000-0000-000000000003";

const char* motorLeftModeCharRXUUID = "00000000-0000-0000-0000-000000000010";
const char* motorRightModeCharRXUUID = "00000000-0000-0000-0000-000000000011";
const char* motorLeftModeCharTXUUID = "00000000-0000-0000-0000-000000000012";
const char* motorRightModeCharTXUUID = "00000000-0000-0000-0000-000000000013";

const char* accXcharTxUUID = "00000000-0000-0000-0000-000000000004";
const char* accYcharTxUUID = "00000000-0000-0000-0000-000000000005";
const char* accZcharTxUUID = "00000000-0000-0000-0000-000000000006";
const char* gyroXcharTxUUID = "00000000-0000-0000-0000-000000000007";
const char* gyroYcharTxUUID = "00000000-0000-0000-0000-000000000008";
const char* gyroZcharTxUUID = "00000000-0000-0000-0000-000000000009";
const char* magXcharTxUUID = "00000000-0000-0000-0000-000000000017";
const char* magYcharTxUUID = "00000000-0000-0000-0000-000000000018";
const char* magZcharTxUUID = "00000000-0000-0000-0000-000000000019";

const char* leftLineTrackingTxUUID = "00000000-0000-0000-0000-000000000014";
const char* rightLineTrackingTxUUID = "00000000-0000-0000-0000-000000000015";
const char* UltrasonicTxUUID = "00000000-0000-0000-0000-000000000016";



BLEService controlService(controlServiceUUID);
BLEService sensorsService(sensorsServiceUUID);
BLEService lineTrackingAndUltrasonicService(lineTrackingAndUltrasonicServiceUUID);

BLECharacteristic motorLeftPWMCharRX(motorLeftPWMCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);
BLECharacteristic motorRightPWMCharRX(motorRightPWMCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);                                    
BLEIntCharacteristic motorLeftPWMCharTX(motorLeftPWMCharTXUUID, BLERead | BLENotify);     
BLEIntCharacteristic motorRightPWMCharTX(motorRightPWMCharTXUUID, BLERead | BLENotify); 

BLECharacteristic motorLeftModeCharRX(motorLeftModeCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);
BLECharacteristic motorRightModeCharRX(motorRightModeCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);                                    
BLEBoolCharacteristic motorLeftModeCharTX(motorLeftModeCharTXUUID, BLERead | BLENotify);     
BLEBoolCharacteristic motorRightModeCharTX(motorRightModeCharTXUUID, BLERead | BLENotify); 

BLEFloatCharacteristic accXcharTx(accXcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic accYcharTx(accYcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic accZcharTx(accZcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic gyroXcharTx(gyroXcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic gyroYcharTx(gyroYcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic gyroZcharTx(gyroZcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic magXcharTx(magXcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic magYcharTx(magYcharTxUUID, BLERead | BLENotify);
BLEFloatCharacteristic magZcharTx(magZcharTxUUID, BLERead | BLENotify);

BLEBoolCharacteristic leftLineTrackingTx(leftLineTrackingTxUUID, BLERead | BLENotify);
BLEBoolCharacteristic rightLineTrackingTx(rightLineTrackingTxUUID, BLERead | BLENotify);
BLEIntCharacteristic ultrasonicTx(UltrasonicTxUUID, BLERead | BLENotify);

float acc_x = 0;
float acc_y = 0;
float acc_z = 0;
float gyro_x = 0;
float gyro_y = 0;
float gyro_z = 0;
float mag_x = 0;
float mag_y = 0;
float mag_z = 0;
float roll = 0;
float pitch = 0;
float yaw = 0;

int ultrasonicDistance = 300;

bool isLeftTracking = false;
bool isRightTracking = false;

volatile int32_t motorLeftPWM = 0;
volatile int32_t motorRightPWM = 0;
volatile bool motorLeftMode = true; // true == forward, false == backward
volatile bool motorRightMode = true;

const int ledPin = LED_BUILTIN;
Ultrasonic ultrasonic(triggerPin, echoPin);


void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);

  startBLE();

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  startMotor();
  pinMode(leftTrackingSensorPin, INPUT);
  pinMode(rightTrackingSensorPin, INPUT);
}


void loop() {
  BLE.poll();
  updateSensors();
  writeToMotor();
  printStatus();

  BLEDevice central = BLE.central();
  if (central) {

    motorLeftPWMCharTX.writeValue(motorLeftPWM);
    motorRightPWMCharTX.writeValue(motorRightPWM);
    motorLeftModeCharTX.writeValue(motorLeftMode);
    motorRightModeCharTX.writeValue(motorRightMode);

    
    accXcharTx.writeValue(acc_x);
    accYcharTx.writeValue(acc_y);
    accZcharTx.writeValue(acc_z);
    
    gyroXcharTx.writeValue(gyro_x);
    gyroYcharTx.writeValue(gyro_y);
    gyroZcharTx.writeValue(gyro_z);

    magXcharTx.writeValue(mag_x);
    magYcharTx.writeValue(mag_y);
    magZcharTx.writeValue(mag_z);
    
    leftLineTrackingTx.writeValue(isLeftTracking);
    rightLineTrackingTx.writeValue(isRightTracking);
    ultrasonicTx.writeValue(ultrasonicDistance);
  } else{
//    Serial.println("No device connected");
  }
  
}

void printStatus() {
    String data = String(String("(") + String(acc_x,3) + "," + String(acc_y,3) + "," + String(acc_z,3) + "," 
                       + String(roll,3) + "," + String(pitch,3) + "," + String(yaw,3) + "," 
                       + String(motorLeftPWM) + "," + String(motorRightPWM) + ","
                       + String(motorLeftMode) + "," + String(motorRightMode) + "," 
                       + String(isLeftTracking) + "," + String(isRightTracking) + "," + String(ultrasonicDistance) +
                       String(")"));
    Serial.println(data);
}

void startMotor() {
  pinMode(motorLeftpin1, OUTPUT);
  pinMode(motorLeftpin2, OUTPUT);
  pinMode(motorRightpin1, OUTPUT);
  pinMode(motorRightpin2, OUTPUT);

  pinMode(motorLeftPWMPin, OUTPUT); 
  pinMode(motorRightPWMPin, OUTPUT);
}
void writeToMotor() {
  if (motorLeftMode == true) {
    leftMotorForwardMode();
  } else {
    leftMotorReverseMode();
  }

  if (motorRightMode == true) {
    rightMotorForwardMode();
  } else {
    rightMotorReverseMode();
  }

  analogWrite(motorLeftPWMPin, motorLeftPWM); 
  analogWrite(motorRightPWMPin, motorRightPWM); 
}

void leftMotorForwardMode() {
  digitalWrite(motorLeftpin1, HIGH);
  digitalWrite(motorLeftpin2, LOW);
}
void leftMotorReverseMode() {
  digitalWrite(motorLeftpin1, LOW);
  digitalWrite(motorLeftpin2, HIGH);
}
void rightMotorForwardMode() {
  digitalWrite(motorRightpin1, HIGH);
  digitalWrite(motorRightpin2, LOW);
}
void rightMotorReverseMode() {
  digitalWrite(motorRightpin1, LOW);
  digitalWrite(motorRightpin2, HIGH);
}
void motorForwardMode() {
  leftMotorForwardMode();
  rightMotorForwardMode();
}
void motorReverseMode() {
  leftMotorReverseMode();
  rightMotorReverseMode();
}


void updateUltrasonic() {
  ultrasonicDistance = ultrasonic.read();
}
void updateLineTracking() {
  isLeftTracking = digitalRead(leftTrackingSensorPin);
  isRightTracking = digitalRead(rightTrackingSensorPin);
}

void updateSensors(){

    if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable() && IMU.magneticFieldAvailable()) {
      IMU.readAcceleration(acc_x, acc_y, acc_z);
      IMU.readGyroscope(gyro_x,gyro_y,gyro_z);
      IMU.readMagneticField(mag_x, mag_y, mag_z);
    }
  

  updateUltrasonic();
  updateLineTracking();
}

void startBLE() {
    // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("ROAR");
  BLE.setAdvertisedService(controlService);
  BLE.setAdvertisedService(sensorsService);
  BLE.setAdvertisedService(lineTrackingAndUltrasonicService);
  
  controlService.addCharacteristic(motorLeftPWMCharRX);
  controlService.addCharacteristic(motorRightPWMCharRX);
  controlService.addCharacteristic(motorLeftPWMCharTX);
  controlService.addCharacteristic(motorRightPWMCharTX);
  controlService.addCharacteristic(motorLeftModeCharRX);
  controlService.addCharacteristic(motorRightModeCharRX);
  controlService.addCharacteristic(motorLeftModeCharTX);
  controlService.addCharacteristic(motorRightModeCharTX);

  sensorsService.addCharacteristic(accXcharTx);
  sensorsService.addCharacteristic(accYcharTx);
  sensorsService.addCharacteristic(accZcharTx);
  sensorsService.addCharacteristic(gyroXcharTx);
  sensorsService.addCharacteristic(gyroYcharTx);
  sensorsService.addCharacteristic(gyroZcharTx);
  sensorsService.addCharacteristic(magXcharTx);
  sensorsService.addCharacteristic(magYcharTx);
  sensorsService.addCharacteristic(magZcharTx);
  
  

  lineTrackingAndUltrasonicService.addCharacteristic(leftLineTrackingTx);
  lineTrackingAndUltrasonicService.addCharacteristic(rightLineTrackingTx);
  lineTrackingAndUltrasonicService.addCharacteristic(ultrasonicTx);
  
  BLE.addService(controlService);
  BLE.addService(sensorsService);
  BLE.addService(lineTrackingAndUltrasonicService);
  
  BLE.setEventHandler(BLEConnected, onBLEConnected);
  BLE.setEventHandler(BLEDisconnected, onBLEDisconnected);

  motorLeftPWMCharRX.setEventHandler(BLEWritten, motorLeftPWMCharRXWritten);
  motorRightPWMCharRX.setEventHandler(BLEWritten, motorRightPWMCharRXWritten);


  motorLeftModeCharRX.setEventHandler(BLEWritten, motorLeftModeCharRXWritten);
  motorRightModeCharRX.setEventHandler(BLEWritten, motorRightModeCharRXWritten);

  BLE.advertise();
  disconnectedLight();
  Serial.println("Bluetooth device active, waiting for connections...");
}



void onBLEConnected(BLEDevice central) {
  Serial.print("Connected event, central: ");
  Serial.println(central.address());
  BLEconnectedLight();
}

void onBLEDisconnected(BLEDevice central) {
  Serial.print("Disconnected event, central: ");
  Serial.println(central.address());
  disconnectedLight();
  // ensure that vehicle stop if connection stopped
  motorLeftPWM = 0;
  motorRightPWM = 0;
}


void motorRightPWMCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  char buf[5];
  characteristic.readValue(buf, 5);
  motorRightPWM = atoi(buf);
  
}

void motorLeftPWMCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  char buf[5];
  characteristic.readValue(buf, 5);
  motorLeftPWM = atoi(buf);  
}
void motorRightModeCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  byte state;
  characteristic.readValue(state);
  if (state == 84) {
      motorRightMode = true;
  } else {
      motorRightMode = false;
  }  
}

void motorLeftModeCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  byte state;
  characteristic.readValue(state);
  if (state == 84) {
      motorLeftMode = true;
  } else {
      motorLeftMode = false;
  }  
}


/*
 * LEDS
 */
void BLEconnectedLight() {
  digitalWrite(LEDR, HIGH);
  digitalWrite(LEDB, LOW);
}


void disconnectedLight() {
  digitalWrite(LEDR, LOW);
  digitalWrite(LEDB, HIGH);
}
