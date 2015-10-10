// sample value
int value;

void sendID()
{
  Serial.println("spectrum_analyzer");
  Serial.println("version:0.01");
}

void setup()
{
  // start connection at baud rate of 115200
  Serial.begin(115200);
  sendID();
  delay(200);
}


// should have less statments here
void loop()
{
  // this will take about 0.0001s (100 micro-second)
  value = analogRead(A0);

  // value is 10 bits
  // 0x00 is the sample identifier
  Serial.write(0x00);
  Serial.write(value & 0xff);
  Serial.write((value >> 8) & 0x03);
}

