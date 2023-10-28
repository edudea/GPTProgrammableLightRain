import os
import openai
import re

openai.organization = "org-KkiGJrxFd5s302zC8XS3Icev"
openai.api_key = os.getenv("OPENAI_API_KEY")

instruction = ('Du hilfst einer Person ohne Programmierkenntnisse eine Lichterkette zu steuern. Schreibe ein Programm'
               'für Arduino IDE, dass ein neopixel led strip steuert. Die Lichterkette hat 20 LEDs und wird über'
               ' PIN 4 gesteuert. Erkläre wie du die Anforderungen verstanden hast, stelle gegebenenfalls nachfragen'
               ' und gib den Quellcode aus.')
request = ('Die LEDs sollen ihre Farbe langsam von dunkel zu rot und wieder zurück wechseln. Der Farbwechsel soll wie'
           ' eine Welle sanft durch die Lichterkette laufen und keine starken Übergänge haben.')


# completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": instruction},
#                                                                            {"role": "user", "content": request}])
# print(completion)
# answer = completion.choices[0].message.content

answer = "Sicher! Hier ist ein Beispielcode, der dies erm\u00f6glicht:\n\n```cpp\n#include <Adafruit_NeoPixel.h>\n\n#define LED_PIN    4\n#define NUM_LEDS   20\n\nAdafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);\n\nvoid setup() {\n  strip.begin();\n  strip.show(); // Setze alle LEDs aus\n\n  // Die Geschwindigkeit des Farbwechsels kann hier angepasst werden\n  // Je gr\u00f6\u00dfer die Zahl, desto langsamer der Farbwechsel\n  int fadeSpeed = 10;\n\n  for (int i = 0; i < NUM_LEDS; i++) {\n    strip.setPixelColor(i, 255, 0, 0); // Setze die LEDs auf Rot\n    strip.show();\n    delay(fadeSpeed);\n  }\n\n  for (int i = NUM_LEDS - 1; i >= 0; i--) {\n    strip.setPixelColor(i, 0, 0, 0); // Schalte die LEDs aus\n    strip.show();\n    delay(fadeSpeed);\n  }\n}\n\nvoid loop() {\n  // Du kannst hier weitere Aktionen einf\u00fcgen, die parallel zum Farbwechsel ausgef\u00fchrt werden sollen\n}\n```\n\nDieser Code verwendet die Adafruit_NeoPixel-Bibliothek, um den Neopixel LED-Strip zu steuern. Zuerst werden die Anzahl der LEDs und der gew\u00fcnschte Pin definiert. In der `setup`-Funktion wird der Strip initialisiert und alle LEDs ausgeschaltet. Dann wird in einer Schleife die Farbe der LEDs langsam von aus bis rot gewechselt und danach wieder zur\u00fcck. Die Geschwindigkeit des Farbwechsels kann durch die Variable `fadeSpeed` angepasst werden. \n\nIn der `loop`-Funktion k\u00f6nnen weitere Aktionen hinzugef\u00fcgt werden, die parallel zum Farbwechsel ausgef\u00fchrt werden sollen. Beachte jedoch, dass der Code in der `setup`-Funktion einmalig ausgef\u00fchrt wird und danach in der `loop`-Funktion endlos wiederholt wird."

split = re.compile(".*```.{0,4}\\n(.*)```\\n.*", flags=re.DOTALL).split(answer)
code = ""
if len(split) > 1:
    code = split[1]

splitCode=(re.compile("(?P<init>.*)(void setup[^\n]*)(?P<setup>(.(?<!\n}\n))*)(\n}\n)"
                      "(?P<inbetween>(.(?<!void loop\(\)))*)(void loop\(\)[^\n]+)(?P<loop>(.(?<!\n}\n))*)(\n}\n{0,1}){1}"
                      "(?P<end>(.(?<!\n}))*)", flags=re.DOTALL)
           .search(code))
print(len(splitCode.groups()))

print("INIT", splitCode.group("init"))
print("SETUP", splitCode.group("setup"))
print("LOOP", splitCode.group("loop"))
print("HELPERS", splitCode.group("inbetween"), "\n", splitCode.group("end"))
