class MegaPiPort: public MeMegaPiDCMotor {
  public:
    // Volatile used on class variables to read them from memory in case they changed since the last read
    bool  backwards; // For when the motor needs to be reversed
    volatile uint8_t port; // Motor port connected to MegaPi
    volatile uint8_t intPin; // Interrupt pin used with motor
    volatile uint8_t encPin; // Encoder pin for motor port
    volatile long    count; // Encoder count

    // Constructor
    MegaPiPort(uint8_t port_num, uint8_t interupt_pin, uint8_t encoder_pin)
      : MeMegaPiDCMotor(port_num), port(port_num), intPin(interupt_pin), encPin(encoder_pin), backwards(false) { };

    // Sets the speed of the motors
    inline void setMotorSpeed(int16_t spd) {
      // Set motor speed
      int true_speed = (backwards) ? -spd : spd;
      // Run specified speed
      MeMegaPiDCMotor::run(true_speed);
      
    };
};
