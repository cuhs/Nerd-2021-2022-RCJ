function [J grad] = nnCostFunction(nn_params, ...
                                   input_layer_size, ...
                                   hidden_layer_size, ...
                                   num_labels, ...
                                   X, y, lambda)

Theta1 = reshape(nn_params(1:hidden_layer_size * (input_layer_size + 1)), ...
                 hidden_layer_size, (input_layer_size + 1));

Theta2 = reshape(nn_params((1 + (hidden_layer_size * (input_layer_size + 1))):end), ...
                 num_labels, (hidden_layer_size + 1));

% Setup some useful variables
m = size(X, 1);
         
% You need to return the following variables correctly 
J = 0;
Theta1_grad = zeros(size(Theta1));
Theta2_grad = zeros(size(Theta2));


reg = 0;
y_matrix = eye(num_labels)(y,:);
a1 = [ones(m, 1), X];
z2 = a1*Theta1';
a2 = sigmoid(z2);
a2 = [ones(m,1) a2];
z3 = a2*Theta2';
a3 = sigmoid(z3);%mx10
J = (1/m) * sum(sum(((-1*y_matrix).*log(a3))-((1-y_matrix).*log(1-a3))));
reg = (lambda/(2*m))*(sum(sum(Theta1(:,2:end).^2))+sum(sum(Theta2(:,2:end).^2)));
J = J + reg;


%backpropagation
d3 = a3 - y_matrix;
d2 = (d3*Theta2(:,2:end)).*sigmoidGradient(z2);
Delta1 = d2'*a1;
Delta2 = d3'*a2;
Theta1_grad = (1/m)*Delta1;
Theta2_grad = (1/m)*Delta2;
Theta1(:,1) = 0;
Theta2(:,1) = 0;
Theta1 = Theta1 * (lambda/m);
Theta2 = Theta2 * (lambda/m);
Theta1_grad = Theta1_grad + Theta1;
Theta2_grad = Theta2_grad + Theta2;







grad = [Theta1_grad(:) ; Theta2_grad(:)];


end
