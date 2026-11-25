#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ============================================================
// CONFIGURAÇÃO (preencha antes de gravar; não faça commit da senha real)
// ============================================================

const char *WIFI_NOME  = "NOME_DO_WIFI";
const char *WIFI_SENHA = "SENHA_DO_WIFI";

// IP da máquina que roda o backend (mesma rede do ESP32) + porta 8000
const char *SERVIDOR = "http://192.168.0.12:8000";

// codigo_unidade do locker no banco (tabela lockers)
const char *CODIGO_LOCKER = "UNI01";

// Mesmo valor de LOCKER_DEVICE_TOKEN em backend/.env
const char *TOKEN_LOCKER = "COLE_AQUI_O_LOCKER_DEVICE_TOKEN";

// De quanto em quanto tempo pergunta ao backend se há comando
const unsigned long INTERVALO_CONSULTA = 1000;

// ============================================================
// LED AZUL
// ============================================================

const int LED_AZUL = 2;

// ============================================================
// BOTÕES
// ============================================================

const int BOTAO_DIREITA = 23;
const int BOTAO_ESQUERDA = 22;

// ============================================================
// L9110
// ============================================================

const int MOTOR_A = 18;
const int MOTOR_B = 19;

const unsigned long TEMPO_MOTOR = 2000;

// ============================================================
// ESTADO DO MOTOR
// ============================================================

enum EstadoMotor {
    MOTOR_PARADO,
    MOTOR_ABRINDO,
    MOTOR_FECHANDO
};

EstadoMotor estadoMotor = MOTOR_PARADO;

unsigned long inicioMotor = 0;
unsigned long ultimaConsulta = 0;

// ============================================================
// LED
// ============================================================

void piscarLed(int quantidade, int tempo) {

    for (int i = 0; i < quantidade; i++) {

        digitalWrite(LED_AZUL, HIGH);
        delay(tempo);

        digitalWrite(LED_AZUL, LOW);
        delay(tempo);
    }
}


// ============================================================
// CONTROLE DO MOTOR
// ============================================================

void pararMotor() {

    digitalWrite(MOTOR_A, LOW);
    digitalWrite(MOTOR_B, LOW);

    estadoMotor = MOTOR_PARADO;
}


// ============================================================

void abrir() {

    digitalWrite(MOTOR_A, HIGH);
    digitalWrite(MOTOR_B, LOW);

    estadoMotor = MOTOR_ABRINDO;
    inicioMotor = millis();
}


// ============================================================

void fechar() {

    digitalWrite(MOTOR_A, LOW);
    digitalWrite(MOTOR_B, HIGH);

    estadoMotor = MOTOR_FECHANDO;
    inicioMotor = millis();
}


// ============================================================
// COMANDO (o mesmo texto que vinha pelo Bluetooth)
// ============================================================

void executarComando(String comando) {

    comando.trim();
    comando.toUpperCase();

    if (comando == "ABRIR") {

        abrir();

    } else if (comando == "FECHAR") {

        fechar();

    } else if (comando == "PARAR") {

        pararMotor();
    }
}


// ============================================================
// WI-FI
// ============================================================

bool conectarWifi() {

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_NOME, WIFI_SENHA);

    // Espera até 15 s, piscando o LED
    unsigned long inicio = millis();

    while (WiFi.status() != WL_CONNECTED && millis() - inicio < 15000) {

        digitalWrite(LED_AZUL, !digitalRead(LED_AZUL));
        delay(250);
    }

    digitalWrite(LED_AZUL, LOW);

    return WiFi.status() == WL_CONNECTED;
}


// ============================================================
// CONSULTA AO BACKEND
// GET /lockers/<codigo>/comando  ->  "ABRIR", "FECHAR" ou vazio
// ============================================================

void consultarComando() {

    if (WiFi.status() != WL_CONNECTED) {

        WiFi.reconnect();
        return;
    }

    HTTPClient http;

    String url = String(SERVIDOR) + "/lockers/" + CODIGO_LOCKER + "/comando";

    http.begin(url);
    http.setTimeout(3000);
    http.addHeader("X-Locker-Token", TOKEN_LOCKER);

    int status = http.GET();

    if (status == 200) {

        executarComando(http.getString());

    } else if (status == 401) {

        // Token errado: 2 piscadas rápidas
        piscarLed(2, 80);
    }

    http.end();
}


// ============================================================
// SETUP
// ============================================================

void setup() {

    // LED
    pinMode(LED_AZUL, OUTPUT);
    digitalWrite(LED_AZUL, LOW);

    // INDICAÇÃO DE BOOT: 3 piscadas rápidas
    piscarLed(3, 200);

    // BOTÕES
    pinMode(BOTAO_DIREITA, INPUT_PULLUP);
    pinMode(BOTAO_ESQUERDA, INPUT_PULLUP);

    // MOTOR
    pinMode(MOTOR_A, OUTPUT);
    pinMode(MOTOR_B, OUTPUT);

    pararMotor();

    // WI-FI
    bool wifiOK = conectarWifi();

    if (wifiOK) {

        // Wi-Fi conectado: 1 piscada longa de 1 segundo
        digitalWrite(LED_AZUL, HIGH);
        delay(1000);
        digitalWrite(LED_AZUL, LOW);

    } else {

        // Wi-Fi falhou: 5 piscadas rápidas (os botões continuam funcionando
        // e o loop tenta reconectar sozinho)
        piscarLed(5, 100);
    }
}


// ============================================================
// LOOP
// ============================================================

void loop() {

    // CONTROLE DO TEMPO DO MOTOR
    if (estadoMotor != MOTOR_PARADO) {

        if (millis() - inicioMotor >= TEMPO_MOTOR) {

            pararMotor();
        }
    }

    // CONSULTA AO BACKEND
    // Só com o motor parado: a requisição pode demorar e o motor
    // passaria do TEMPO_MOTOR enquanto espera.
    if (estadoMotor == MOTOR_PARADO && millis() - ultimaConsulta >= INTERVALO_CONSULTA) {

        ultimaConsulta = millis();
        consultarComando();
    }

    // BOTÃO DIREITA
    if (digitalRead(BOTAO_DIREITA) == LOW) {

        if (estadoMotor != MOTOR_ABRINDO) {

            abrir();

            while (digitalRead(BOTAO_DIREITA) == LOW) {
                delay(1);
            }
        }
    }

    // BOTÃO ESQUERDA
    if (digitalRead(BOTAO_ESQUERDA) == LOW) {

        if (estadoMotor != MOTOR_FECHANDO) {

            fechar();

            while (digitalRead(BOTAO_ESQUERDA) == LOW) {
                delay(1);
            }
        }
    }
}
