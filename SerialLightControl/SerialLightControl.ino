#include <Adafruit_NeoPixel.h>
#include <errno.h>

// Giving some default values here.
const int LightPin = 3;
size_t PixelCount = 3;
Adafruit_NeoPixel *Pixels = nullptr;
using Color = uint32_t;

// Actual physical color configuration
// Blue->Green->Red
// But for whatever reason the physical light color doesn't match up with the
// library colors.
void setup() {
  Pixels = new Adafruit_NeoPixel(PixelCount, LightPin, NEO_RBG + NEO_KHZ800);
  Serial.begin(9600);
  Pixels->begin();
}

// We allow for a maximum of 5 arguments for any functionaliy.
const byte numChars = 64;
char receivedChars[numChars];
// temporary array for use when parsing
char tempChars[numChars];

// variables to hold the parsed data
char command[numChars] = {0};
// int integerFromPC = 0;
// float floatFromPC = 0.0;
boolean newData = false;


void loop() {
  recvWithStartEndMarkers();
  if (newData == true) {
      strcpy(tempChars, receivedChars);
          // this temporary copy is necessary to protect the original data
          //   because strtok() used in parseData() replaces the commas with \0
      parseData();
      newData = false;
  }
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

const char *pixels_Reset = "pixels.reset";
const char *pixels_show = "pixels.show";
const char *pixels_setPixelColor = "pixels.setPixelColor";
const char *pixels_getPixelColor = "pixels.getPixelColor";
const char *pixels_fill = "pixels.fill";
const char *pixels_clear = "pixels.clear";
const char *pixels_setBrightness = "pixels.setBrightness";
const char *pixels_getBrightness = "pixels.getBrightness";
const char *pixels_getPin = "pixels.getPin";
// const char pixels_setPin = "pixels.setPin";
// const char pixels_getPixels = "pixels.getPixels";
const char *pixels_size = "pixels.size";

void printIncorrectNumberOfArgumentsError(int Expected, int Actual) {
  Serial.print("ERR: incorrect number of aguments for command ");
  Serial.print(command);
  Serial.print(" expected ");
  Serial.print(Expected);
  Serial.print(" arguments. Received ");
  Serial.print(Actual);
  Serial.println(".");
}

void printIncorrectNumberOfArgumentsErrorRange(int MinExpected,
                                               int MaxExpected, int Actual) {
  Serial.print("ERR: incorrect number of aguments for command ");
  Serial.print(command);
  Serial.print(" expected between ");
  Serial.print(MinExpected);
  Serial.print(" - ");
  Serial.print(MaxExpected);
  Serial.print(" arguments. Received ");
  Serial.print(Actual);
  Serial.println(".");
}
void logCall(uint8_t *args, int count) {
  Serial.print("DEBUG: ");
  Serial.print(command);
  Serial.print("(");
  for(int i = 0;i < count;){
    Serial.print(args[i]);
    ++i;
    if (i != count) {
      Serial.print(", ");
    }
  }
  Serial.println(")");
}

void invalidPixelInstance() {
  Serial.println("ERR: unable to process command invalid pixel reference");
}

void parseData() {

   // this is used by strtok() as an index
  char * strtokIndx;
  errno = 0;

  // get the first part - the string
  strtokIndx = strtok(tempChars, ",");

  // copy it to command
  strcpy(command, strtokIndx);

  uint8_t ArgCount = 0;
  uint8_t Args[5] = {0, 0, 0, 0, 0};
  strtokIndx = strtok(NULL, " ");
  while (strtokIndx && ArgCount < 5) {
    errno = 0;
    Args[ArgCount] = atoi(strtokIndx);
    if (errno != 0) {
      Serial.println("ERR: Invalid Command");
      return;
    }
    ++ArgCount;
    strtokIndx = strtok(NULL, " ");
  }

  // We received to many arguments and were unable to fully process them.
  if (strtokIndx && ArgCount == 5) {
    Serial.println("ERR: To many arguments");
    return;
  }
  logCall(Args, ArgCount);
  if(strcmp(command, pixels_Reset) == 0) {
    if (ArgCount != 2) {
      printIncorrectNumberOfArgumentsError(2, ArgCount);
      return;
    }
    if (Pixels){
      delete Pixels;
    }
    Pixels = new Adafruit_NeoPixel(Args[0], Args[1], NEO_GRB + NEO_KHZ800);;
    if (Pixels) {
      Pixels->begin();
      Serial.print("OK: Attempting to create new neopixel with ");
      Serial.print(Args[0]);
      Serial.print(" Lights using pin ");
      Serial.print(Args[1]);
      Serial.println();
    } else {
      Serial.println("ERR: failed to create a new neopixel instance.");
    }


  } else if(strcmp(command, pixels_show) == 0) {
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Pixels->show();
    Serial.println("OK");


  } else if(strcmp(command, pixels_setPixelColor) == 0) {
    if (ArgCount < 4 || ArgCount > 5) {
      printIncorrectNumberOfArgumentsErrorRange(4, 5, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    if (ArgCount == 4) {
      Pixels->setPixelColor(Args[0], Args[1], Args[2], Args[3]);
    } else {
      Pixels->setPixelColor(Args[0], Args[1], Args[2], Args[3], Args[4]);
    }
    Serial.println("OK");
  // } else if(strcmp(command, pixels_getPixelColor) == 0) {
    


  } else if(strcmp(command, pixels_fill) == 0) {
    if (ArgCount < 4 || ArgCount > 5) {
      printIncorrectNumberOfArgumentsErrorRange(4, 5, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    if (ArgCount == 4) {
      Pixels->fill(Adafruit_NeoPixel::Color(Args[0], Args[1], Args[2]),
                   Args[3]);
    } else {
      Pixels->fill(Adafruit_NeoPixel::Color(Args[0], Args[1], Args[2]),
                   Args[3], Args[4]);
    }
    Serial.println("OK");

  } else if(strcmp(command, pixels_clear) == 0) {
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Pixels->clear();
    Serial.println("OK");


  } else if(strcmp(command, pixels_setBrightness) == 0) {
    if (ArgCount != 1) {
      printIncorrectNumberOfArgumentsError(1, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Pixels->setBrightness(Args[0]);
    Serial.println("OK");


  } else if(strcmp(command, pixels_getBrightness) == 0) {
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Serial.print("OK: ");
    Serial.println(Pixels->getBrightness());


  } else if(strcmp(command, pixels_getPin) == 0) {
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Serial.print("OK: ");
    Serial.println(Pixels->getPin());
  // } else if(strcmp(command, pixels_setPin) == 0) {
    
  // } else if(strcmp(command, pixels_getPixels) == 0) {
    
  } else if(strcmp(command, pixels_size) == 0) {
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      return;
    }
    if (!Pixels) {
      invalidPixelInstance();
      return;
    }
    Serial.print("OK: ");
    Serial.println(Pixels->numPixels());


  } else {
    Serial.print("ERR: invalid command ");
    Serial.println(command);
    return;
  }
//   void              begin(void);
//   void              show(void);
//   void              setPin(uint16_t p);
//   void              setPixelColor(uint16_t n, uint8_t r, uint8_t g, uint8_t b);
//   void              setPixelColor(uint16_t n, uint8_t r, uint8_t g, uint8_t b,
//                       uint8_t w);
//   void              setPixelColor(uint16_t n, uint32_t c);
//   void              fill(uint32_t c=0, uint16_t first=0, uint16_t count=0);
//   void              setBrightness(uint8_t);
//   void              clear(void);
//   void              setPin(uint16_t p);
// uint8_t           getBrightness(void) const;
// int16_t           getPin(void) const { return pin; };
// uint16_t          numPixels(void) const { return numLEDs; }
// uint32_t          getPixelColor(uint16_t n) const;
  // }
  // strtokIndx = strtok(NULL, " ");
  // floatFromPC = atof(strtokIndx);     // convert this part to a float
}

// //============

// void showParsedData() {
//     Serial.print("Message ");
//     Serial.println(command);
//     Serial.print("Integer ");
//     Serial.println(integerFromPC);
//     Serial.print("Float ");
//     Serial.println(floatFromPC);
// }
