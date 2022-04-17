#ifndef _PID_H_
#define _PID_H_

double PID(double error, double &pastError, double &integral, double kp, double ki, double kd);

#endif
