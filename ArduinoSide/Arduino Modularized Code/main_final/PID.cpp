#include "PID.h"
double PID(double error, double &pastError, double &integral, double kp, double ki, double kd){
 
  double derivative = error-pastError;
  integral = integral + error;

  pastError = error;
  return((kp*error)+(ki*integral)+(kd*derivative));
 
}
