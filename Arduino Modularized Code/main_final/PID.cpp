float PID(float error, float &pastError, float &integral, float kp, float ki, float kd){
 
  float derivative = error-pastError;
  integral = integral + error;

  pastError = error;
  return((kp*error)+(ki*integral)+(kd*derivative));
 
}
