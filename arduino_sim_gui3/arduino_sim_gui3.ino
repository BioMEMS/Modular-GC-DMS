//Author: Ilya Anishchenko
//
//MR-GC-DMS GUI software is the proprietary property of The Regents of the University of California (“The Regents.”)
//
//Copyright © 2013-18 The Regents of the University of California, Davis campus. All Rights Reserved.  
//
//Redistribution and use in source and binary forms, with or without modification, are permitted by nonprofit, research institutions for research use only, provided that the following conditions are met:
//•	Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
//•	Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 
//•	The name of The Regents may not be used to endorse or promote products derived from this software without specific prior written permission. 
//The end-user understands that the program was developed for research purposes and is advised not to rely exclusively on the program for any reason.
//THE SOFTWARE PROVIDED IS ON AN "AS IS" BASIS, AND THE REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. THE REGENTS SPECIFICALLY DISCLAIMS ANY EXPRESS OR IMPLIED 
//WARRANTIES, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, 
//SPECIAL, INCIDENTAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES, INCLUDING BUT NOT LIMITED TO  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR PROFITS, OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND UNDER 
//ANY THEORY OF LIABILITY WHETHER IN CONTRACT, STRICT LIABILITY OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY 
//OF SUCH DAMAGE. 
//
//If you do not agree to these terms, do not download or use the software.  This license may be modified only in a writing signed by authorized signatory of both parties.
//For commercial license information please contact copyright@ucdavis.edu



#include <Arduino.h>
#include <Math.h>
#include <String.h>
//#define ARDUINO_DUE
#include<runEvent.h>          //Structs for how events are stored and processed
#include<mySerialProtocol.h>  //How serial messages are recieved and handled from PC
#include<stdint.h>            //Standard library
#include<tempProfile.h>       //Structs for GC Profile. Maybe should be merged with runEvent?
#include<TrapLib_Rev2.h>      //PID Library for the trap.
#include<CPID.h>              //Generic PID library used in other libraries
#include<Serial_SPI_Sensors.h>  //For managed SPI Sensor Board
#include<Column_Lib.h>        //Equivalent of TrapLib 2 for RTD
#include<DuePWM.h>            //DuePWM library to reduce noise on the RTD line
#include<RTD.h>               //Library to encapsulate some of the RTD utilities/calculations
#include<SerialUtils.h>       //Useful serial commands, including clearing the terminal

//PID Defines, should move into header-file...
#define SETPOINT 35
//Transfer Line PID Constants
#define KP 3                  //Proportional
#define KI 0.1                //Integral
#define KD 0.1                //Derivative
//Column Module PID Constants
#define CKP 25                //Proportional
#define CKI 0.5               //Integral
#define CKD 1                 //Derivative
//Trap PID Constants
#define TKP 11                //Proportional 3
#define TKI .07               //Integral   0.1
#define TKD 0                 //Derivative   1
//Guard Column PID Constants (Still needs to be tuned)
#define GKP 25                //Proportional
#define GKI .1                //Integral
#define GKD 0                 //Derivative
#define DT 100                //DT for PID run time
#define CURRENT 0.00075       //Current used on RTD excitation (Calculation only)
#define RREF 1976             //Reference Resistor Values used in RTD calc
#define GCFREQ 15             //Column PWM Frequency, this seems high.....
#define T_SETPOINT 150        //Trap Setpoint
#define GCE_SETPOINT 100      //Guard Column Enclosure setpoint
#define ADS_BITS 15           //Bits resolution for the RTD ADC

//Pin name definitions
const uint8_t aOutTransfer1 = 2;  //Transfer line 1 of Column Module
const uint8_t aOutTransfer2 = 3;  //Transfer line 2 of Column Module
const uint8_t aOutModule = 6;     //Column heater
const uint8_t aOutTrap = 4;       //Trap Heater
const uint8_t aOutGCE = 7;        //Guard Column Enclosure heater
const uint8_t LED = 13;           //Unnecessary, LED pin
const uint8_t dOutFan = 5;        //Column Fan
const uint8_t dInSwitch = 23;     //Override switch, becoming unnecessary
const uint8_t dOutPump1 = 25;     //Circulation Pump
const uint8_t dOutPump2 = 24;     //Sample Pump
const uint8_t dOut2Valve = 26;    //2 way valve
const uint8_t dOut3Valve = 27;    //3 way valve

boolean spump = false;
boolean cpump = true;
boolean valve2way = false;
boolean valve3way = false;
boolean gccFan = true;
boolean sysRun = false;

//Start Serial Protocol Class
MySerialProtocol sProtocol('#', '!', 16);

uint8_t startBit = sProtocol.getStartByte();    //These should probably be constant, initialize constructor with them as well?
uint8_t stopBit = sProtocol.getStopByte();      //These should probably be constant, initialize constructor with them as well?
uint8_t messageLength = sProtocol.getPayloadSizeMax();

//Trap lib is encapsulating the generic PID library, interfacing with the thermocouple, and PWM out
TrapLib Transfer1(Serial1, 1);  //Thermocouple 1
TrapLib Transfer2(Serial1, 2);  //Thermocouple 2
TrapLib Trap(Serial1, 3);       //Thermocouple 3
TrapLib guardCE(Serial1, 4);    //Thermocouple 4

//I never encapsulated the ADS header, maybe still should
Column_Lib Column(Serial1);

String sum = "";
uint32_t global_time;
uint32_t next_print = 0;
uint32_t next_ct_time = 0;
uint32_t inc_time = 1000;
uint32_t inc_ct_time = 400;
uint32_t timeout;
uint32_t time_offset = 0;
uint32_t system_time = 0;

boolean blit = true;
char mode = '3';
char mode_send = '3';
char lastmode = '3';

int cycle_repeat = 0;
int cycle_current = 1;

uint32_t eventsTime[20] = {0};   int i1 = 0;  //should always have an event at 0sec time!!!
uint32_t eventsType[20] = {5};

uint32_t gcTime[20] = {0};   int i2 = 0;      //should always have time start at 0 and temp at 20.0!!!
float gcTemp[20] = {20.0};

uint32_t trapTime[20] = {0};   int i3 = 0;
float trapTemp[20] = {20.0};

uint32_t dummy32[] = {0};   //int i4 = 0;
float dummyfloat[] = {0.0};

float default_temp[10] = {0.0, 20.0, 20.0, 20.0, 20.0, 20.0};
float init_temp[10] = {0.0, 10.0, 10.0, 10.0, 10.0, 10.0};


String events_time_str = "";
String events_type_str = "";
String gc_time_str = "";
String gc_temp_str = "";
String trap_time_str = "";
String trap_temp_str = "";

float gc_ct;
float trap_ct;
float tf1_ct;
float tf2_ct;
float guard_ct;

char buff[100];
boolean initials_bool = false;
int end_send_counter = 50;

void setup()
{
  eventsTime[17] = 172800000; //48 hour timeout for the system
  eventsType[17] = 9; //call to end run
  
  for (int inc_i = 1; inc_i < 18; inc_i++)
  {
    gcTime[inc_i] = 172800000;
    gcTemp[inc_i] = 20.0;
  }  
  
  trapTime[17] = 172800000;
  trapTemp[17] = 20.0;
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(250000);      //Do not change without also changing baud on the ATMega328

  pinMode(LED, OUTPUT);       //Debug only
  pinMode(dOutFan, OUTPUT);
  pinMode(dInSwitch, INPUT_PULLUP);
  pinMode(dOutPump1, OUTPUT);
  pinMode(dOutPump2, OUTPUT);
  pinMode(dOut2Valve, OUTPUT);
  pinMode(dOut3Valve, OUTPUT);
  //Might be able to get some of these config calls into constructors for the classes
  configColumnClasses();    //Set up Column Control parameters
  configTrapClass();        //Set up trap control parameters
  configGCEClass();         //Set up guard column control parameters

  delay(50);
  systemIdle();
  global_time = millis();
  //Serial.println("exited setup");
  
}

void loop()
{
  global_time = millis();
  update_ct();
  //Serial.println("update ct executed");
  update_gui();
  //Serial.println("update gui executed");
  delay(45); //slow down just in case libraries take a while to respond



  if ((mode == '1') && (mode_send != '7')) //run mode characteristics
  {
    if (initials())
    {
      lastmode = '1';
      mode_send = '1';
      system_time = global_time - time_offset;

      switch (getSystemCommand())
      {
        case 1: gccFan = true; break;
        case 2: valve2way = true; break;
        case 3: valve3way = true; break;
        case 4: spump = true; break;
        case 5: gccFan = false; break;
        case 6: valve2way = false; break;        
        case 7: valve3way = false; break;
        case 8: spump = false; break;
        case 9: endReached(); break;
        default: mode_send = '7'; break; //mode_send 7 = the run has already been completed
      }
      if (mode_send != '7')
      {
        systemRun();      
      }      
    }
    else
    {
      mode_send = '6';  //mode_send = 6 means run is exectuing and hasnt reached the initial starting temperature
      update_pid(init_temp[1], init_temp[2], init_temp[3], init_temp[4], init_temp[5]);
      time_offset = millis();
      system_time = 0;
    }
  }
  else if ((mode == '2') || (mode_send == '7')) //active mode properties
  {
    resetRun();
    update_pid(init_temp[1], init_temp[2], init_temp[3], init_temp[4], init_temp[5]);
    lastmode = '2';
    if (mode_send == '7')
    {
      if (end_send_counter > 0)
      {
        end_send_counter -= 1;
      }
      else
      {
        mode_send = '2';
        end_send_counter = 50;
      }      
    }
    else
    {
      mode_send = '2';  
    }
    mode = '2';
    system_time = 0;
    time_offset = millis();
    initials_bool = false;
  }
  else if (mode == '3') //idle mode properties
  {
    systemIdle();
    lastmode = '3';
    mode_send = '3';
    system_time = 0;
    initials_bool = false;
  }
  else if (mode == '4') //loading run data
  {
    //load run data properties
    //stay in this mode for about 2000ms then timeout into the last mode if recieved nothing
    timeout = millis() + 6000;
    mode = '2';
    if (load_32array(timeout, &eventsType[0], &dummyfloat[0], true))
    {
      if (load_32array(timeout, &eventsTime[0], &dummyfloat[0], true))
      {
        if (load_32array(timeout, &dummy32[0], &trapTemp[0], false))
        {
          if (load_32array(timeout, &trapTime[0], &dummyfloat[0], true))
          {
            if (load_32array(timeout, &dummy32[0], &gcTemp[0], false))
            {
              if (load_32array(timeout, &gcTime[0], &dummyfloat[0], true))
              {
                if (getcycle(timeout))
                {
                  if (greenlight(timeout))
                  {
                    mode = '1';
                    time_offset = millis();
                    //run one time active mode initializations here
                    gcTemp[0] = init_temp[2];
                    end_send_counter = 50;
                    cycle_current = 1;
                  }
                }
              }
            }
          }
        }
      }
    }
    //write to peripherals... the temperature sets

  }
  else if (mode == '5') //loading initials
  {
    //loading initial properties stay in this mode for 2 seconds then timeout into last mode
    timeout = millis() + 2000;
    mode = '3';
    if (load_32array(timeout, &dummy32[0], &init_temp[0], false))
    {
      if (greenlight(timeout))
      {
        mode = '2';
        // run one time active mode initializations here
      }
    }
  }
}

void endReached()
{
  if (cycle_repeat == 0)
  {
    cycle_current = 1;
    mode_send = '7';
    mode = '2';
  }
  else
  {
    cycle_repeat -= 1;
    cycle_current++;
    initials_bool = false;    
  }
  resetRun();
}

void systemRun()
{
  float gcSetpoint;
  float trapSetpoint;

  gcSetpoint = getGCTemp();
  trapSetpoint = getTrapTemp();
  update_pid(trapSetpoint, gcSetpoint, gcSetpoint, gcSetpoint, init_temp[5]);

}

boolean initials()
{
  boolean ret2 = false;
  if (initials_bool)
  {
    ret2 = true;
  }
  else
  {
    if (check_range(trap_ct, init_temp[1], 3.0))
    {
      if (check_range(gc_ct, init_temp[2], 3.0))
      {
        if (check_range(tf1_ct, init_temp[3], 3.0))
        {
          if (check_range(tf2_ct, init_temp[4], 3.0))
          {
            if (check_range(guard_ct, init_temp[5], 3.0))
            {
              initials_bool = true;
              ret2 = true;
            }
          }
        }
      }
    }
  }
  return ret2;
}

boolean check_range(float currentT, float wantedT, float rangeT)
{
  if (abs(currentT - wantedT) > rangeT)
  {
    return false;
  }
  else
  {
    return true;
  }
}

boolean load_32array(uint32_t t, uint32_t *myarray, float *myarray2, boolean q)
{
  char a;
  String blend = "";
  boolean fb = false;
  int loc_t = 0;

  global_time = millis();
  while (!Serial.available() && (t > global_time))
  {
    delay(1);
    global_time = millis();
  }
  if (t > global_time)
  {
    while (loc_t < 50)
    {
      while (Serial.available())
      {
        a = Serial.read();
        delay(1);
        loc_t = 0;
        blend += String(a);
      }
      delay(1);
      loc_t++;
    }
    StringTo32Array(&blend, myarray, myarray2, q);
    delay(5);
    Serial.print(blend);
    delay(5);
    fb = true;
  }
  return fb;
}

boolean getcycle(uint32_t t)
{
  char b;
  String blend = "";
  boolean fb = false;
  global_time = millis();
  while (!Serial.available() && (t > global_time))
  {
    delay(1);
    global_time = millis();
  }
  if (t > global_time)
  {
    while (Serial.available())
    {
      b = Serial.read();
      delay(1);
      blend += String(b);
    }
    cycle_repeat = String(blend).toInt();
    delay(5);
    Serial.print(blend);
    delay(200);
    fb = true;
  }
  return fb;
}

boolean greenlight(uint32_t t)
{
  char b;
  boolean fb = false;
  global_time = millis();
  while (!Serial.available() && (t > global_time))
  {
    delay(1);
    global_time = millis();
  }
  if (t > global_time)
  {
    b = Serial.read();
    if (b == 'g')
    {
      fb = true;
      delay(5);
      Serial.print(b);
      delay(200);
    }
  }
  return fb;
}

//This should print the various read celcius values and print them to the gui...
//i might include error checking later
void update_gui()
{
  if ((global_time > next_print) && (!Serial.available()))
  {
    sum = "";
    int i;
    int c1 = 11;
    uint32_t t = global_time / 1000;

    sum = "$";
    sum += String(int(trap_ct)) + "," + String(int(gc_ct)) + "," + String(int(tf1_ct)) + "," + String(int(tf2_ct)) + "," + String(int(guard_ct)) + ","; //temperatures
    sum += String((gccFan) ? 1 : 0) + ",";
    sum += String((valve2way) ? 1 : 0) + ",";
    sum += String((valve3way) ? 1 : 0) + ",";
    sum += String((spump) ? 1 : 0) + ",";
    //sum += "0,1,0,1,"; //boolean on valves and pumps and fans
    sum += String(cycle_current) + ","; //cycle number
    sum += String((system_time) / 1000) + ",";
    sum += String(mode_send) + "%";

    next_print += inc_time;
    Serial.print(sum);
    delay(50);
  }
  else
  {
    mode = listen_gui(mode);
  }
}

void update_ct()
{
  if (global_time > next_ct_time)
  {
    tf1_ct = Transfer1.readCelsius();
    tf2_ct = Transfer2.readCelsius();
    gc_ct = Column.readCelsius();
    trap_ct = Trap.readCelsius();
    guard_ct = guardCE.readCelsius();

    next_ct_time += inc_ct_time;
  }
}

char listen_gui(char b)
{
  if (Serial.available())
  {
    digitalWrite(13, blit ? HIGH : LOW);
    b = Serial.read();
    delay(10);
    Serial.print(b);
    delay(50);
    blit = !blit;
  }
  return b;
}

void StringTo32Array(String *mystring, uint32_t *myarray, float *myarray2, boolean q)
{
  int I = 1;
  char temp;
  String num_temp = "";
  char char_buff[100];
  (*mystring).toCharArray(char_buff, 99);
  for (int i = 0; i < (*mystring).length(); i++)
  {
    temp = char_buff[i];
    if (isDigit(temp))
    {
      do
      {
        num_temp += String(temp);
        i++;
        temp = char_buff[i];
      } while (isDigit(temp));
      if (q)
      {
        *(myarray + I) = uint32_t(num_temp.toInt());
        I++;
      }
      else
      {
        *(myarray2 + I) = float(num_temp.toInt());
        I++;
      }
      num_temp = "";
    }
  }
}





void resetRun()
{
  spump = false;
  cpump = true;
  valve2way = false;
  valve3way = false;
  gccFan = true;
  i1 = 0;
  i2 = 0;
  i3 = 0;
  time_offset = millis();
}

void systemIdle()
{
  resetRun();
  booleanEvents();
  analogWrite(aOutTransfer1, 0);
  analogWrite(aOutTransfer2, 0);
  Column.pinDuty(aOutModule, 0);
  analogWrite(aOutTrap, 0);
  analogWrite(aOutGCE, 0);
  delay(30);
  update_pid(default_temp[1], default_temp[2], default_temp[3], default_temp[4], default_temp[5]);
  
}

void update_pid(float trap_s, float gc_s, float tf1_s, float tf2_s, float guard_s)
{
  booleanEvents();

  Transfer1.setSetpoint(tf1_s);
  Transfer2.setSetpoint(tf2_s);
  Column.setSetpoint(gc_s);
  Trap.setSetpoint(trap_s);
  guardCE.setSetpoint(guard_s);

  Transfer1.conditionalRun();
  Transfer2.conditionalRun();
  Column.conditionalRun();
  Trap.conditionalRun();
  guardCE.conditionalRun();

}

void booleanEvents()
{
  digitalWrite(dOutFan, (gccFan) ? HIGH : LOW);
  digitalWrite(dOutPump1, (cpump) ? HIGH : LOW);
  digitalWrite(dOutPump2, (spump) ? HIGH : LOW);
  digitalWrite(dOut2Valve, (valve2way) ? HIGH : LOW);
  digitalWrite(dOut3Valve, (valve3way) ? HIGH : LOW);
}



uint32_t getSystemCommand()
{
  if (eventsTime[i1] <= system_time)
  {
    i1++;
  }
  return eventsType[i1 - 1];
}

float getTrapTemp()
{
  if (trapTime[i3] <= system_time)
  {
    i3++;
  }
  return trapTemp[i3 - 1];
}


float getGCTemp()
{
  static float old_stemp;
  static float old_time;
  if (gcTime[i2] < system_time)
  {
    old_stemp = gcTemp[i2];
    old_time = gcTime[i2];
    i2++;
  }
  return (((gcTemp[i2] - old_stemp) / float(gcTime[i2] - old_time)) * float(system_time - old_time) + old_stemp);
}

//This function should probably be renamed
void configColumnClasses() {
  //Transfer line 1
  Transfer1.setPIDValues(KP, KI, KD);     //Set PID Constants
  Transfer1.connectTime(&global_time);    //Give class global time
  Transfer1.setPWM_Out(aOutTransfer1);    //Set PID Output Pin
  digitalWrite(aOutTransfer1, LOW);       //Check this line...
  Transfer1.setDTime(DT);                 //Set DT for PID Loop, Constant should be changed if this is edited
  Transfer1.setSetpoint(SETPOINT);        //Set Setpoint

  //transfer line 2
  Transfer2.setPIDValues(KP, KI, KD);     //Set PID Constant
  Transfer2.connectTime(&global_time);    //Give class global time
  Transfer2.setPWM_Out(aOutTransfer2);    //Set PID Output Pin
  digitalWrite(aOutTransfer2, LOW);       //Check this line...
  Transfer2.setDTime(DT);                 //Set DT for PID Loop, edit constants if changed
  Transfer2.setSetpoint(SETPOINT);        //Set Setpoint

  //Column module
  Column.setPIDValues(CKP, CKI, CKD);     //Set PID Constants
  Column.connectTime(&global_time);       //Give class global time
  Column.setDTime(DT);                    //Set DT for PID loop
  Column.setSetpoint(SETPOINT);           //Set Setpoint
  Column.setFreq1(GCFREQ);                //Set Output pin frequency
  Column.setPWM_Out(aOutModule);          //Set PWM output pin
}

void configTrapClass() {
  Trap.setPIDValues(TKP, TKI, TKD);     //Load PID constants into class
  Trap.connectTime(&global_time);       //connect global time variable to class
  Trap.setPWM_Out(aOutTrap);            //Give class pwm pin identifier
  Trap.setDTime(DT);                    //dT for trap control system
  Trap.setSetpoint(T_SETPOINT);         //Give set point to trap  class
  analogWrite(aOutTrap, 0);             //Default the output to zero
}

void configGCEClass() {
  guardCE.setPIDValues(GKP, GKI, GKD);  //Load PID constants into class
  guardCE.connectTime(&global_time);    //connect global time variable to class
  guardCE.setPWM_Out(aOutGCE);          //Give class pwm pin identifier
  guardCE.setDTime(DT);                 //dT for trap control system
  guardCE.setSetpoint(GCE_SETPOINT);    //Give set point to trap  class
  analogWrite(aOutGCE, 0);              //Default the output to zero
}


