#include <Arduino.h>
#include <Wire.h>
#include "registers.h"

#define I2C_ADDR 0x21

// Définition des broches
#define RESET 33
#define VSYNC 52
#define PCLK  32
#define XCLK   7  // PWML6

#define D0 51
#define D1 50
#define D2 49
#define D3 48
#define D4 47
#define D5 46
#define D6 45
#define D7 44

#define WIDTH  320
#define HEIGHT 240

// Protocole de communication
#define SYNC_HEADER 0xAA
#define SYNC_FOOTER 0x55
#define CAPTURE_CMD 'C'

void setupDefault();
void setupQVGA();
void setupYUV422();
bool captureImg(uint16_t width, uint16_t height, byte* frame);
void sendImageData(byte* frame, uint32_t size);

void writeReg(byte regID, byte regVal) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(regID);
  Wire.write(regVal);
  Wire.endTransmission();
  delay(10);
}

byte readReg(byte regID) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(regID);
  Wire.endTransmission();
  Wire.requestFrom(I2C_ADDR, 1);
  while (Wire.available() == 0);
  return Wire.read();
}

void setupXCLK() {
  // Configuration de XCLK (10.5MHz) pour Arduino Due
  PMC->PMC_PCER1 |= PMC_PCER1_PID36;  // Activer PWM
  PIOC->PIO_PDR |= PIO_PDR_P19;      // Désactiver GPIO pour PC19 (broche 7)
  PIOC->PIO_ABSR |= PIO_ABSR_P19;    // Sélectionner périphérique B
  
  PWM->PWM_CLK = PWM_CLK_PREA(0) | PWM_CLK_DIVA(1);  // Horloge = 84MHz
  PWM->PWM_CH_NUM[6].PWM_CMR = PWM_CMR_CPRE_CLKA;    // Canal 6 (PWML6)
  PWM->PWM_CH_NUM[6].PWM_CPRD = 8;    // Période (84MHz/8 = 10.5MHz)
  PWM->PWM_CH_NUM[6].PWM_CDTY = 4;    // Rapport cyclique 50%
  PWM->PWM_ENA = PWM_ENA_CHID6;       // Activer le canal PWM
}

void setup() {
  // Initialisation hardware
  pinMode(RESET, OUTPUT);
  digitalWrite(RESET, HIGH);
  delay(100);
  digitalWrite(RESET, LOW);
  delay(100);
  digitalWrite(RESET, HIGH);
  
  // Configuration des broches
  pinMode(D0, INPUT);
  pinMode(D1, INPUT);
  pinMode(D2, INPUT);
  pinMode(D3, INPUT);
  pinMode(D4, INPUT);
  pinMode(D5, INPUT);
  pinMode(D6, INPUT);
  pinMode(D7, INPUT);
  pinMode(VSYNC, INPUT);
  pinMode(PCLK, INPUT);

  // Configuration XCLK
  setupXCLK();

  // Initialisation communication
  Serial.begin(921600);
  Wire.begin();
  
  // Configuration caméra
  setupDefault();
  setupQVGA();
  setupYUV422();
  
  writeReg(R_CLKRC, 0x06); // Horloge externe
  
  Serial.println("System Ready");
}

void loop() {
  static byte frame[WIDTH * HEIGHT];
  
  // Attendre activement la commande
  while (Serial.available() > 0) {
    char cmd = Serial.read();
    
    if (cmd == CAPTURE_CMD) {
      // Vidage du buffer série
      while(Serial.available() > 0) Serial.read();
      
      // En-tête avec vérification
      Serial.write(SYNC_HEADER);
      Serial.flush();
      
      // Capture avec vérification
      if (captureImg(WIDTH, HEIGHT, frame)) {
        sendImageData(frame, WIDTH * HEIGHT);
      }
      
      // Pied de page avec vérification
      Serial.write(SYNC_FOOTER);
      Serial.flush();
      
      // Pause pour stabilisation
      delay(50);
    }
  }
}
bool captureImg(uint16_t width, uint16_t height, byte* frame) {
  uint32_t timeout = millis() + 1000; // Timeout après 1s
  noInterrupts();
  
  // Attendre début de frame
  while (digitalRead(VSYNC) == HIGH) {
    if (millis() > timeout) {
      interrupts();
      return false;
    }
  }
  while (digitalRead(VSYNC) == LOW) {
    if (millis() > timeout) {
      interrupts();
      return false;
    }
  }

  // Capture des pixels
  for (uint16_t y = 0; y < height; y++) {
    for (uint16_t x = 0; x < width; x++) {
      // Attendre front descendant de PCLK
      while (digitalRead(PCLK) == HIGH) {
        if (millis() > timeout) {
          interrupts();
          return false;
        }
      }
      
      // Lecture des données
      frame[y * width + x] = 
        (digitalRead(D7) << 7) |
        (digitalRead(D6) << 6) |
        (digitalRead(D5) << 5) |
        (digitalRead(D4) << 4) |
        (digitalRead(D3) << 3) |
        (digitalRead(D2) << 2) |
        (digitalRead(D1) << 1) |
        digitalRead(D0);
      
      // Attendre front montant de PCLK
      while (digitalRead(PCLK) == LOW) {
        if (millis() > timeout) {
          interrupts();
          return false;
        }
      }
    }
  }
  
  interrupts();
  return true;
}

void sendImageData(byte* frame, uint32_t size) {
  // Envoi par blocs de 64 octets pour optimisation
  const uint32_t blockSize = 64;
  uint32_t sent = 0;
  
  while (sent < size) {
    uint32_t remaining = size - sent;
    uint32_t toSend = (remaining < blockSize) ? remaining : blockSize;
    
    Serial.write(frame + sent, toSend);
    sent += toSend;
  }
}

void setupDefault() {
  writeReg(R_COM7, 0x80); // Reset
  delay(100);
  
  writeReg(R_TSLB, 0x04);
  writeReg(R_COM10, 0x20); // PCLK ne bascule pas pendant le blanking
  
  writeReg(R_COM8, 0xC5); // AGC, AWB, AE
  writeReg(R_COM9, 0x18); // Gain 4x
}

void setupQVGA() {
  writeReg(R_COM3, 0x04);
  writeReg(R_COM14, 0x19);
  writeReg(R_HSTART, 0x16);
  writeReg(R_HSTOP, 0x04);
  writeReg(R_HREF, 0x24);
  writeReg(R_VSTRT, 0x02);
  writeReg(R_VSTOP, 0x7A);
  writeReg(R_VREF, 0x0A);
  writeReg(R_SCALING_DCWCTR, 0x11);
  writeReg(R_SCALING_PCLK_DIV, 0xF1);
}

void setupYUV422() {
  writeReg(R_COM15, 0xC0); // YUV422, plage complète
  writeReg(R_COM13, 0x40); // Ajustement saturation UV
}
