function [J, grad] = lRcostfunction(theta, X, y, lambda)

m = length(y); % number of training examples


J = 0;
grad = zeros(size(theta));


theProd = X*theta;
J = (1/m) * (sum(((-1.*y).*log(sigmoid(theProd))) - ((1.-y).*log(1.-sigmoid(theProd)))))+((lambda/(2*m))*sum(theta(2:end).^2));
B = sigmoid(theProd)-y;
grad = ((1/m).*(X'*B)) + ((lambda/m)*theta);
grad(1) = (1/m)*sum(X(:,1)'*B);

grad = grad(:);

end
