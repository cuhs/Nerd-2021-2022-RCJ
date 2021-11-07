function W = randInitializeWeights(L_in, L_out)

W = zeros(L_out, 1 + L_in);

W = rand(L_out, L_in+1);
W(:,1) = 1;


end
