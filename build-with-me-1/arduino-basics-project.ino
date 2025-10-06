#include "LiquidCrystal_I2C.h"
#include "IRremote.h"

#define ECHO_PIN 3
#define TRIGGER_PIN 4

#define LIGHT_LED_PIN 10
#define WARNING_LED_PIN 11
#define ERROR_LED_PIN 12

#define BUTTON_PIN 2
#define PHOTORESISTOR_PIN A0

#define IR_RECEIVE_PIN 5
#define IR_BUTTON_PLAY 71

#define LOCK_DISTANCE 6.0
#define WARNING_DISTANCE 12.0

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Ultrasonic
unsigned long lastTimeUltrasonicTrigger = millis();
unsigned long ultrasonicTriggerDelay = 100;

volatile unsigned long pulseInTimeBegin;
volatile unsigned long pulseInTimeEnd;
volatile bool newDistanceAvail = false;

// Warning LED
unsigned long lastTimeWarningLEDBlinked = millis();
unsigned long warningLEDDelay = 500;
byte warningLEDState = LOW;

// Error LED
unsigned long lastTimeErrorLEDBlinked = millis();
unsigned long errorLEDDelay = 300;
byte errorLEDState = LOW;

// Push button
unsigned long lastTimeButtonChanged = millis();
unsigned long buttonDebounceDelay = 300;
byte buttonState;

// Photoresistor
unsigned long lastTimeReadLuminosity = millis();
unsigned long readLuminosityDelay = 100;

bool isLock = false;

void triggerUltrasonicSensor() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
}

double getUltrasonicDistance() {
  double durationMicros = pulseInTimeEnd - pulseInTimeBegin;
  double distance = durationMicros / 58.0; // cm
  return distance;
}

void echoPinInterrupt() {
  if (digitalRead(ECHO_PIN) == HIGH) { // start measuring
    pulseInTimeBegin = micros();
  } else { // stop measuring
    pulseInTimeEnd = micros();
    newDistanceAvail = true;
  }
}

void toggleWarningLED() {
  warningLEDState = !warningLEDState;
  digitalWrite(WARNING_LED_PIN, warningLEDState);
}

void toggleErrorLED() {
  errorLEDState = !errorLEDState;
  digitalWrite(ERROR_LED_PIN, errorLEDState);
}

void setWarningLEDBlinkRateFromDistance(double distance) {
  warningLEDDelay = distance * 4; // 0..400cm -> 0..1600ms
}

void lock() {
  if (!isLock) {
    isLock = true;
    errorLEDState = LOW;
    warningLEDState = LOW;
  }

}

void unlock() {
  if (isLock) {
    isLock = false;
    errorLEDState = LOW;
    digitalWrite(ERROR_LED_PIN, errorLEDState);
  }
}

void printDistanceOnLCD(double distance) {
  if (isLock) {
    lcd.setCursor(0, 0);
    lcd.print("OBSTAClE!!!       ");
    lcd.setCursor(0, 1);
    lcd.print("Press to unlock.  ");
  } else {
    lcd.setCursor(0, 0);
    lcd.print("Dist: ");
    lcd.print(distance);
    lcd.print(" cm           ");

    lcd.setCursor(0, 1);
    if (distance > WARNING_DISTANCE) {
      lcd.print("No obstacle.      ");
    } else {
      lcd.print("WARNING!!!        ");
    }
  }
}

void handleIRCommand(long command) {
  switch (command) {
    case IR_BUTTON_PLAY: {
      unlock();
      break;
    }
    default: { }
  }
}

void setLEDLightFromLuminosity(int luminosity) {
  byte brightness = 255 - luminosity / 4;
  analogWrite(LIGHT_LED_PIN, brightness);
}

void setup() {
  Serial.begin(115200);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);

  IrReceiver.begin(IR_RECEIVE_PIN);

  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(WARNING_LED_PIN, OUTPUT);
  pinMode(ERROR_LED_PIN, OUTPUT);
  pinMode(LIGHT_LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);

  buttonState = digitalRead(BUTTON_PIN);

  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), echoPinInterrupt, CHANGE);

  lcd.print("Initializing...");
  delay(1000);
  lcd.clear();
}

void loop() {
  unsigned long timeNow = millis();

  if (timeNow - lastTimeUltrasonicTrigger > ultrasonicTriggerDelay) {
    lastTimeUltrasonicTrigger += ultrasonicTriggerDelay;

    // Trigger sensor
    triggerUltrasonicSensor();
  }

  if (isLock) {
    if (timeNow - lastTimeErrorLEDBlinked > errorLEDDelay) {
      lastTimeErrorLEDBlinked += errorLEDDelay;
      toggleErrorLED();
      toggleWarningLED();
    }

    if (timeNow - lastTimeButtonChanged > buttonDebounceDelay) {
      byte newButtonState = digitalRead(BUTTON_PIN);
      if (newButtonState != buttonState) {
        lastTimeButtonChanged = timeNow;
        buttonState = newButtonState;
        // Unlock when releasing
        if (buttonState == LOW) {
          unlock();
        }
      }
    }
  } else {
    if (timeNow - lastTimeWarningLEDBlinked > warningLEDDelay) {
      lastTimeWarningLEDBlinked += warningLEDDelay;
      toggleWarningLED();
    }
  }

  if (newDistanceAvail) {
    newDistanceAvail = false;
    double distance = getUltrasonicDistance();
    setWarningLEDBlinkRateFromDistance(distance);
    // Serial.println(distance);
    printDistanceOnLCD(distance);
    if (distance < LOCK_DISTANCE) {
      lock();
    }
  }

  if (IrReceiver.decode()) {
    IrReceiver.resume();
    // Serial.println(IrReceiver.decodedIRData.command);
    long command = IrReceiver.decodedIRData.command;
    handleIRCommand(command);
  }

  if (timeNow - lastTimeReadLuminosity > readLuminosityDelay) {
    lastTimeReadLuminosity += readLuminosityDelay;
    int luminosity = analogRead(PHOTORESISTOR_PIN);
    setLEDLightFromLuminosity(luminosity);
  }
}
