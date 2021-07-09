/**
 * This module is written for Arduino Nano BLE 33. 
 * 
 * You would need to install LSM9Ds1 & MadgwickAHRS from the Arduino Library ( Go to Tools -> Manage Libraries)
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
#include "MadgwickAHRS.h"
#include <stdlib.h>

#define PIN_LED     (13u)
#define LED_BUILTIN PIN_LED
#define LEDR        (22u)
#define LEDG        (23u)
#define LEDB        (24u)
#define LED_PWR     (25u)


const char* nameOfPeripheral = "ROAR";
const char* controlServiceUUID = "00001101-0000-1000-8000-00805f9b34fb";
const char* sensorsServiceUUID = "00001102-0000-1000-8000-00805f9b34fb";

const char* motorLeftPWMCharRXUUID = "00000000-0000-0000-0000-000000000000";
const char* motorRightPWMCharRXUUID = "00000000-0000-0000-0000-000000000001";
const char* throttlePWMCharTXUUID = "00000000-0000-0000-0000-000000000002";
const char* motorRightPWMCharTXUUID = "00000000-0000-0000-0000-000000000003";

const char* accXcharTxUUID = "00000000-0000-0000-0000-000000000004";
const char* accYcharTxUUID = "00000000-0000-0000-0000-000000000005";
const char* accZcharTxUUID = "00000000-0000-0000-0000-000000000006";
const char* rollcharTxUUID = "00000000-0000-0000-0000-000000000007";
const char* pitchcharTxUUID = "00000000-0000-0000-0000-000000000008";
const char* yawcharTxUUID = "00000000-0000-0000-0000-000000000009";



BLEService controlService(controlServiceUUID);
BLEService sensorsService(sensorsServiceUUID);


BLECharacteristic motorLeftPWMCharRX(motorLeftPWMCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);
BLECharacteristic motorRightPWMCharRX(motorRightPWMCharRXUUID, BLEWrite | BLEWriteWithoutResponse, 4, true);                                    
BLEIntCharacteristic motorLeftPWMCharTX(throttlePWMCharTXUUID, BLERead | BLENotify);     
BLEIntCharacteristic motorRightPWMCharTX(motorRightPWMCharTXUUID, BLERead | BLENotify); 

BLEFloatCharacteristic accXcharTx(accXcharTxUUID, BLERead);
BLEFloatCharacteristic accYcharTx(accYcharTxUUID, BLERead);
BLEFloatCharacteristic accZcharTx(accZcharTxUUID, BLERead);
BLEFloatCharacteristic rollcharTx(rollcharTxUUID, BLERead);
BLEFloatCharacteristic pitchcharTx(pitchcharTxUUID, BLERead);
BLEFloatCharacteristic yawcharTx(yawcharTxUUID, BLERead);


float acc_x = 0;
float acc_y = 0;
float acc_z = 0;
float gyro_x = 0;
float gyro_y = 0;
float gyro_z = 0;
float roll = 0;
float pitch = 0;
float yaw = 0;


volatile int32_t motorLeft = 0;
volatile int32_t motorRight = 0;

// initialize a Madgwick filter:
Madgwick filter;
// sensor's sample rate is fixed at 104 Hz:
const float sensorRate = 104.00;

const int ledPin = LED_BUILTIN;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);

  startBLE();

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  filter.begin(sensorRate);
}

void loop() {
  BLE.poll();
  updateSensors();
  String data = String(String("(") + String(acc_x,3) + "," + String(acc_y,3) + "," + String(acc_z,3) + "," 
                       + String(roll,3) + "," + String(pitch,3) + "," + String(yaw,3) + "," 
                       + String(motorLeft) + "," + String(motorRight) + String(")"));
  Serial.println(data);
}

void updateAcceleration(){
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(acc_x, acc_y, acc_z);
  }
}

void updateGyro() {
    if (IMU.gyroscopeAvailable()) {
        IMU.readGyroscope(gyro_x,gyro_y,gyro_z);
  }
}
void updateOrientation() {
  filter.updateIMU(gyro_x,gyro_y,gyro_z, acc_x, acc_y, acc_z);
  roll = filter.getRoll();
  pitch = filter.getPitch();
  yaw = filter.getYaw();
}


void updateSensors(){
  updateAcceleration();
  updateGyro();
  updateOrientation();
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
  controlService.addCharacteristic(motorLeftPWMCharRX);
  controlService.addCharacteristic(motorRightPWMCharRX);
  controlService.addCharacteristic(motorLeftPWMCharTX);
  controlService.addCharacteristic(motorRightPWMCharTX);

  sensorsService.addCharacteristic(accXcharTx);
  sensorsService.addCharacteristic(accYcharTx);
  sensorsService.addCharacteristic(accZcharTx);
  sensorsService.addCharacteristic(rollcharTx);
  sensorsService.addCharacteristic(pitchcharTx);
  sensorsService.addCharacteristic(yawcharTx);

  
  BLE.addService(controlService);
  BLE.addService(sensorsService);
  
  BLE.setEventHandler(BLEConnected, onBLEConnected);
  BLE.setEventHandler(BLEDisconnected, onBLEDisconnected);

  motorRightPWMCharRX.setEventHandler(BLEWritten, motorRightPWMCharRXWritten);
  motorLeftPWMCharRX.setEventHandler(BLEWritten, motorLeftPWMCharRXWritten);
  motorLeftPWMCharTX.setEventHandler(BLERead, motorLeftPWMCharTXRead);
  motorRightPWMCharTX.setEventHandler(BLERead, motorRightPWMCharTXRead);

  accXcharTx.setEventHandler(BLERead, accXcharTxRead);
  accYcharTx.setEventHandler(BLERead, accYcharTxRead);
  accZcharTx.setEventHandler(BLERead, accZcharTxRead);
  rollcharTx.setEventHandler(BLERead, rollcharTxRead);
  pitchcharTx.setEventHandler(BLERead, pitchcharTxRead);
  yawcharTx.setEventHandler(BLERead, yawcharTxRead);
  
  
  
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
}

void accXcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[5];
  String(acc_x).toCharArray(buf, 5);
  characteristic.writeValue(buf);
}
void accYcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(acc_y).toCharArray(buf, 32);
  characteristic.writeValue(buf);
}
void accZcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(acc_z).toCharArray(buf, 32);
  characteristic.writeValue(buf);
}
void rollcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(roll).toCharArray(buf, 32);
  characteristic.writeValue(buf);
}
void pitchcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(pitch).toCharArray(buf, 32);
  characteristic.writeValue(buf);
  Serial.println("HERE");
}
void yawcharTxRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(yaw).toCharArray(buf, 32);
  characteristic.writeValue(buf);
}


void motorRightPWMCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  char buf[5];
  characteristic.readValue(buf, 5);
  motorRight = atoi(buf);
}

void motorLeftPWMCharRXWritten(BLEDevice central, BLECharacteristic characteristic) {
  char buf[5];
  characteristic.readValue(buf, 5);
  motorLeft = atoi(buf);
  
}

void motorLeftPWMCharTXRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(motorLeft).toCharArray(buf, 32);
  characteristic.writeValue(buf);
}

void motorRightPWMCharTXRead(BLEDevice central, BLECharacteristic characteristic) {
  char buf[32];
  String(motorRight).toCharArray(buf, 32);
  characteristic.writeValue(buf);
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
