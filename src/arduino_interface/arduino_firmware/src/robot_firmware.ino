// =====================================================
// ROS2 Robot Firmware for Arduino Uno
// Hardware:
//   - L298N with ENA/ENB for PWM speed control
//   - 4 DC motors (left pair, right pair)
//   - Ultrasonic sensor (HC-SR04) on pins 3,4
//   - Buzzer on pin 2
//
// Protocol (Serial @ 115200):
//   Jetson -> Arduino:
//      CMDVEL:<linear>,<angular>
//      BUZZER:0 or 1
//
//   Arduino -> Jetson:
//      DIST:<value_cm>
//
// =====================================================

#include <Arduino.h>

// ----------------------- Pin Definitions -----------------------
const int trigPin   = 3;
const int echoPin   = 4;

const int buzzerPin = 2;

// L298N motor driver pins
const int ENA = 6;   // Left motor enable (PWM)
const int ENB = 5;   // Right motor enable (PWM)

const int IN1 = 8;   // Left direction 1
const int IN2 = 9;   // Left direction 2
const int IN3 = 10;  // Right direction 1
const int IN4 = 11;  // Right direction 2

// ---------------------- Control Parameters ----------------------
const int MAX_PWM   = 255;    // Max PWM value
const int MIN_PWM   = 80;     // Minimum useful PWM to overcome friction
const float SPEED_SCALE = 200.0;  // Scale linear velocity to PWM
const float TURN_SCALE  = 150.0;  // Scale angular velocity to PWM

// ----------------------- Ultrasonic -----------------------------
unsigned long lastDistSend = 0;

float readDistanceCM() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);

    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 25000); // timeout 25ms
    if (duration == 0) return -1;

    float dist = duration * 0.0343f / 2.0f;
    if (dist < 2 || dist > 400) return -1;

    return dist;
}

// ---------------------- Motor Control ---------------------------
//
// linear  (m/s-ish)  -> forward/back
// angular (rad/s-ish)-> turning left/right
//
void driveMotors(float linear, float angular) {
    // Compute target "speed" values (not physical units, just scaled)
    float left_speed  = (linear * SPEED_SCALE) - (angular * TURN_SCALE);
    float right_speed = (linear * SPEED_SCALE) + (angular * TURN_SCALE);

    // Clamp
    if (left_speed > MAX_PWM) left_speed = MAX_PWM;
    if (left_speed < -MAX_PWM) left_speed = -MAX_PWM;

    if (right_speed > MAX_PWM) right_speed = MAX_PWM;
    if (right_speed < -MAX_PWM) right_speed = -MAX_PWM;

    // Deadband (prevent jitter)
    if (abs(left_speed) < MIN_PWM) left_speed = 0;
    if (abs(right_speed) < MIN_PWM) right_speed = 0;

    // LEFT MOTOR: direction on IN1/IN2, speed on ENA
    if (left_speed > 0) {
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, (int)left_speed);
    } else if (left_speed < 0) {
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, HIGH);
        analogWrite(ENA, (int)(-left_speed));
    } else {
        // stop
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 0);
    }

    // RIGHT MOTOR: direction on IN3/IN4, speed on ENB
    if (right_speed > 0) {
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, (int)right_speed);
    } else if (right_speed < 0) {
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, HIGH);
        analogWrite(ENB, (int)(-right_speed));
    } else {
        // stop
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 0);
    }
}

// --------------------- Serial Parsing ---------------------------
void parseCommand(String cmd) {
    cmd.trim();
    if (cmd.length() == 0) return;

    // BUZZER:0/1
    if (cmd.startsWith("BUZZER:")) {
        int val = cmd.substring(7).toInt();
        digitalWrite(buzzerPin, val > 0 ? HIGH : LOW);
        return;
    }

    // CMDVEL:linear,angular
    if (cmd.startsWith("CMDVEL:")) {
        String values = cmd.substring(7);
        int comma_pos = values.indexOf(',');
        if (comma_pos > 0) {
            float lin = values.substring(0, comma_pos).toFloat();
            float ang = values.substring(comma_pos + 1).toFloat();
            driveMotors(lin, ang);
        }
        return;
    }

    // Unknown command -> ignore
}

// =====================================================
// Setup
// =====================================================
void setup() {
    Serial.begin(115200);

    pinMode(ENA, OUTPUT);
    pinMode(ENB, OUTPUT);

    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);

    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);

    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);

    // Stop motors on startup
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

// =====================================================
// Loop
// =====================================================
void loop() {

    // ---- Send distance every 100 ms ----
    if (millis() - lastDistSend > 100) {
        lastDistSend = millis();
        float d = readDistanceCM();
        Serial.print("DIST:");
        Serial.println(d);
    }

    // ---- Receive commands from Jetson ----
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        parseCommand(cmd);
    }
}
