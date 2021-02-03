#include <Adafruit_NeoPixel.h>
#include <errno.h>
#include <ctype.h>

// Giving some default values here.
const int LightPin = 3;

// Motor controlling pins
const int M1_1_Pin = 4;
const int M1_2_Pin = 5;
const int M2_1_Pin = 6;
const int M2_2_Pin = 7;

struct RelayMotorController {
  int relay1 = 0;
  int relay2 = 0;

  RelayMotorController(int pin1, int pin2)
    :relay1(pin1), relay2(pin2)
  {
    if (relay1 >= 0) {
      pinMode(relay1, OUTPUT);
      digitalWrite(relay1, LOW);
    }
    if (relay2 >= 0) {
      pinMode(relay2, OUTPUT);
      digitalWrite(relay2, LOW);
    }
  }

  ~RelayMotorController() {
    if (relay1 >= 0)
      pinMode(relay1, INPUT);
    if (relay2 >= 0)
      pinMode(relay2, INPUT);
  }

  void forward() {
    digitalWrite(relay1, HIGH);
    digitalWrite(relay2, LOW);
  }

  void backward() {
    digitalWrite(relay1, LOW);
    digitalWrite(relay2, HIGH);
  }

  void off() {
    digitalWrite(relay1, LOW);
    digitalWrite(relay2, LOW);
  }
};

// Gloabls
size_t PixelCount = 3;
Adafruit_NeoPixel *Pixels = nullptr;
RelayMotorController* M1 = nullptr;
RelayMotorController* M2 = nullptr;

// Types
using Color = uint32_t;




// Actual physical color configuration
// Blue->Green->Red
// But for whatever reason the physical light color doesn't match up with the
// library colors.
void setup() {
  Pixels = new Adafruit_NeoPixel(PixelCount, LightPin, NEO_GRB + NEO_KHZ800);
  M1 = new RelayMotorController(M1_1_Pin, M1_2_Pin);
  M2 = new RelayMotorController(M2_1_Pin, M2_2_Pin);
  Serial.begin(115200);
  Pixels->begin();
  Serial.println("ready");
}

enum { 
  ReadingCmd,
  ReadingArgs,
  ReadingTillEOL 
};

int State = ReadingCmd;
String Command;
String IntegerBuffer;
uint8_t ArgCount = 0;
int Args[6];

const char *pixels_Reset = "pixels.reset";
const char *pixels_show = "pixels.show";
const char *pixels_setPixelColor = "pixels.setPixelColor";
const char *pixels_fill = "pixels.fill";
const char *pixels_clear = "pixels.clear";
const char *pixels_setBrightness = "pixels.setBrightness";
const char *pixels_getBrightness = "pixels.getBrightness";
const char *pixels_getPin = "pixels.getPin";
const char *pixels_size = "pixels.size";
const char *motor1_open = "m1.open";
const char *motor1_close = "m1.close";
const char *motor1_off = "m1.off";
const char *motor2_open = "m2.open";
const char *motor2_close = "m2.close";
const char *motor2_off = "m2.off";

// const char *pixels_getPixelColor = "pixels.getPixelColor";
// const char pixels_setPin = "pixels.setPin";
// const char pixels_getPixels = "pixels.getPixels";

enum {
  cmd_pixels_Reset,
  cmd_pixels_show,
  cmd_pixels_setPixelColor,
  cmd_pixels_fill,
  cmd_pixels_clear,
  cmd_pixels_setBrightness,
  cmd_pixels_getBrightness,
  cmd_pixels_getPin,
  cmd_pixels_size,
  cmd_open_door_1,
  cmd_close_door_1,
  cmd_off_door_1,
  cmd_open_door_2,
  cmd_close_door_2,
  cmd_off_door_2,
};

int parsedCmd = -1;

void loop() {
  while(Serial.available() > 0) {
    switch(State) {
    case ReadingCmd:
    readCommand();
    break;
    case ReadingArgs:
    readArgs();
    break;
    case ReadingTillEOL:
    readTillEOL();
    break;
    default:
    break;
    }
  }
}

void readCommand() {
  char C = Serial.read();
  if (C == '\r')
    return;

  if (C == '\n') {
    if (Command.length() == 0)
      return;
    // This means we reached the end of a command.
    parsedCmd = decodeCommand();
    processCommand(parsedCmd);
    return;
  }

  if (C == ',') {
    // parsedCmd
    parsedCmd = decodeCommand();
    if(parsedCmd == -1)
      State = ReadingTillEOL;
    else {
      ArgCount = 0;
      State = ReadingArgs;
      IntegerBuffer = "";
    }
    return;
  }
  Command += C;
}

void readArgs() {
  char C = Serial.read();
  if (C == '\r') return;
  if (C == '\n') {
    if (IntegerBuffer.length() != 0) {
      Args[ArgCount] = IntegerBuffer.toInt();
      ++ArgCount;
      if (ArgCount == 6) {
        State = ReadingTillEOL;
        Serial.println("ERR: to many arguments");
        return;
      }
    }
    // This means we reached the end of a command.
    processCommand(parsedCmd);
    return;
  }
  if (IntegerBuffer.length() == 0) {
    if (isspace(C)) return;
    if (!isdigit(C)) {
      State = ReadingTillEOL;
      return;
    } else {
      IntegerBuffer += C;
    }
  } else {
    if (C == ',') {
      Args[ArgCount] = IntegerBuffer.toInt();
      ++ArgCount;
      IntegerBuffer = "";
      if (ArgCount == 6) {
        State = ReadingTillEOL;
        Serial.println("ERR: to many arguments");
      }
    } else {
      if (!isdigit(C)) {
        State = ReadingTillEOL;
        Serial.println("ERR: Invalid argument format");
      } else {
        IntegerBuffer += C;
      }
    }
  }
}

void readTillEOL() {
  char C = Serial.read();
  if (C == '\n') {
    Serial.println("ERR: invalid command " + Command);
    State = ReadingCmd;
    Command = "";
    ArgCount = 0;
    return;
  }
  Command += C;
}

int decodeCommand() {
  if(Command == pixels_Reset) {
    return cmd_pixels_Reset;
  } else if(Command == pixels_show) {
    return cmd_pixels_show;
  } else if(Command == pixels_setPixelColor) {
    return cmd_pixels_setPixelColor;
  } else if(Command == pixels_fill) {
    return cmd_pixels_fill;
  } else if(Command == pixels_clear) {
    return cmd_pixels_clear;
  } else if(Command == pixels_setBrightness) {
    return cmd_pixels_setBrightness;
  } else if(Command == pixels_getBrightness) {
    return cmd_pixels_getBrightness;
  } else if(Command == pixels_getPin) {
    return cmd_pixels_getPin;
  } else if(Command == pixels_size) {
    return cmd_pixels_size;
  } else if (Command == motor1_open) {
    return cmd_open_door_1;
  } else if (Command == motor1_close) {
    return cmd_close_door_1;
  } else if (Command == motor2_open) {
    return cmd_open_door_2;
  } else if (Command == motor2_close) {
    return cmd_close_door_2;
  } else if (Command == motor1_off) {
    return cmd_off_door_1;
  } else if (Command == motor2_off) {
    return cmd_off_door_2;
  } else
    return -1;
}

void printIncorrectNumberOfArgumentsError(int Expected, int Actual) {
  Serial.print("ERR: incorrect number of aguments for command ");
  Serial.print(Command);
  Serial.print(" expected ");
  Serial.print(Expected);
  Serial.print(" arguments. Received ");
  Serial.print(Actual);
  Serial.println(".");
}

void printIncorrectNumberOfArgumentsErrorRange(int MinExpected,
                                               int MaxExpected, int Actual) {
  Serial.print("ERR: incorrect number of aguments for command ");
  Serial.print(Command);
  Serial.print(" expected between ");
  Serial.print(MinExpected);
  Serial.print(" - ");
  Serial.print(MaxExpected);
  Serial.print(" arguments. Received ");
  Serial.print(Actual);
  Serial.println(".");
}

void logCall(int *args, int count) {
  Serial.print("DEBUG: ");
  Serial.print(Command);
  Serial.print("(");
  for(int i = 0;i < count;) {
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


void processCommand(int Cmd) {
  logCall(Args, ArgCount);
  switch(Cmd) {
  case cmd_pixels_Reset:
    if (ArgCount != 2) {
      printIncorrectNumberOfArgumentsError(2, ArgCount);
      break;
    }
    if (Pixels) {
      delete Pixels;
    }
    Pixels = new Adafruit_NeoPixel(Args[0], Args[1], NEO_GRB + NEO_KHZ800);;
    if (Pixels) {
      Pixels->begin();
      Serial.println("OK");
    } else {
      Serial.println("ERR: failed to create a new neopixel instance.");
    }
    break;
    
  case cmd_pixels_show:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    Pixels->show();
    Serial.println("OK");
    break;

  case cmd_pixels_setPixelColor:
    if (ArgCount < 4 || ArgCount > 5) {
      printIncorrectNumberOfArgumentsErrorRange(4, 5, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    if (ArgCount == 4) {
      Pixels->setPixelColor(Args[0], Args[1], Args[2], Args[3]);
    } else {
      Pixels->setPixelColor(Args[0], Args[1], Args[2], Args[3], Args[4]);
    }
    Serial.println("OK");
    break;
    
  case cmd_pixels_fill:
    if (ArgCount < 4 || ArgCount > 5) {
      printIncorrectNumberOfArgumentsErrorRange(4, 5, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    if (ArgCount == 4) {
      Pixels->fill(Adafruit_NeoPixel::Color(Args[0], Args[1], Args[2]),
                   Args[3]);
    } else {
      Pixels->fill(Adafruit_NeoPixel::Color(Args[0], Args[1], Args[2]),
                   Args[3], Args[4]);
    }
    Serial.println("OK");
    break;

  case cmd_pixels_clear:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }

    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    Pixels->clear();
    Serial.println("OK");
    break;

  case cmd_pixels_setBrightness:
    if (ArgCount != 1) {
      printIncorrectNumberOfArgumentsError(1, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    Pixels->setBrightness(Args[0]);
    Serial.println("OK");
    break;

  case cmd_pixels_getPin:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    Serial.print("OK: ");
    Serial.println(Pixels->getPin());
    break;

  case cmd_pixels_size:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    if (!Pixels) {
      invalidPixelInstance();
      break;
    }
    Serial.print("OK: ");
    Serial.println(Pixels->numPixels());
    break;

  case cmd_open_door_1:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M1->forward();
    Serial.println("OK");
    break;

  case cmd_close_door_1:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M1->backward();
    Serial.println("OK");
    break;

  case cmd_open_door_2:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M2->forward();
    Serial.println("OK");
    break;

  case cmd_close_door_2:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M2->backward();
    Serial.println("OK");
    break;

  case cmd_off_door_1:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M1->off();
    Serial.println("OK");
    break;

  case cmd_off_door_2:
    if (ArgCount != 0) {
      printIncorrectNumberOfArgumentsError(0, ArgCount);
      break;
    }
    M2->off();
    Serial.println("OK");
    break;
  default:
    Serial.println("ERR: unknown command " + Command);
    break;
  }
  Command = "";
  ArgCount = 0;
  State = ReadingCmd;
}
