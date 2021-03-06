# -*- coding: utf-8 -*-
"""Image Recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17eRrYI9Y024QK4aRXj2hG09OxNVTYkLN
"""

from torchvision.datasets import MNIST
import numpy as np
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import copy
import torch.nn as nn
import matplotlib.pyplot as plt

# Outputs: weights, biases
# weights -> shape(10, 784)
# biases -> shape(10, 1)
def create_model():
  ###### YOUR CODE HERE ########
  weights = np.array(np.random.normal(0, 1.0, (10,784)))
  biases = np.zeros((10,1))

  return weights, biases

# inputs: scores -> shape(10, 1)
# outputs: softmax_probs -> shape(10, 1)
def softmax(scores):
  ###### YOUR CODE HERE ########
  exponents = np.exp(scores - max(scores))
  denominator = sum(exponents)
  softmax_probs = exponents/denominator

  return softmax_probs

# inputs:
#       probabilities -> shape (10, 1)
#       ground_truth -> scalar
# outputs:
#       loss -> scalar
def loss_function(probabilities, ground_truth):
  ###### YOUR CODE HERE ########
  loss = -(np.log(probabilities[ground_truth]/np.sum(probabilities)))

  return loss

# inputs:
#       probabilities -> shape (10, 1)
#       ground_truth -> scalar
# outputs:
#       grads -> shape (10, 1)
def grad_loss_s(probabilities, ground_truth):
  ######### YOUR CODE HERE ########
  p_gt = probabilities[ground_truth]

  grads = np.empty(shape=(10, 1))

  for j, p_j in enumerate(probabilities):
    if j == ground_truth:
      ######### YOUR CODE HERE ########
      grad_j = p_gt - 1
    else:
      ######### YOUR CODE HERE ########
      grad_j = p_j
    
    grads[j] = grad_j
  
  return grads

# inputs:
#       grad_s -> gradient of L_i wrt s_i -> shape(10, 1)
#       input -> x_i -> shape(784, 1)
# outputs:
#       weight_grad -> shape(10, 784)
#       bias_grad -> shape(10, 1)
def grad_loss_theta(grad_s, input):
  weight_grad = np.empty(shape = (10, 784))
  bias_grad = np.empty(shape = (10, 1))
  
  for idx in range(10): #10 categories or labels in total
    ######### YOUR CODE HERE ##########
    # idx represents the cateogry or the class
    grad_weight = grad_s[idx]*input.T
    grad_bias = grad_s[idx]

    weight_grad[idx] = grad_weight
    bias_grad[idx] = grad_bias
  
  return weight_grad, bias_grad

def train(train_loader, epochs, lr):
  weights, biases = create_model()

  for epoch in range(epochs):
    epoch_acc = 0
    epoch_loss = 0
    epoch_size = 0
    for batch in train_loader:
      datum, labels = batch

      batch_b_grad = np.zeros_like(biases)
      batch_w_grad = np.zeros_like(weights)
      batch_size = 0

      for idx in range(len(datum)):
        x = datum[idx] #input image
        y = labels[idx] #ground truth label

        x = x.numpy().reshape(784, 1) #reshaping input image
        ground_truth = y.numpy()
        
        ########### YOUR CODE HERE #######
        s_i = np.dot(weights,x) + biases#calculate the scores using Wx + b
        probs = softmax(s_i)#calculate softmax probabilities
        loss = loss_function(probs, ground_truth)#calculate the negative log-likelihood loss
        grad_loss_s_i = grad_loss_s(probs, ground_truth)#calculate gradient of Loss wrt s_i
        grad_w, grad_b = grad_loss_theta(grad_loss_s_i, x)#calculate gradient of Loss wrt w, b

        batch_w_grad += grad_w
        batch_b_grad += grad_b

        batch_size += 1

        preds = np.argmax(probs.reshape(10,))

        if preds == y:
          epoch_acc += 1
        epoch_size += 1
        epoch_loss += loss

      batch_w_grad /= batch_size
      batch_b_grad /= batch_size

      weights += -lr * batch_w_grad
      biases += -lr * batch_b_grad
      
    print("epoch: {} accuracy: {} loss: {}".format(epoch, epoch_acc / epoch_size, epoch_loss / epoch_size))

  return weights, biases

#### YOUR CODE HERE #####
epochs = 12
lr = 0.1
weights, biases = train(train_loader, epochs, lr)

def predict(weights, biases, testloader):
  acc = 0.0
  size = 0.0
  for batch in testloader:
    x, y = batch
    x = x.numpy().reshape(1, 784)
    y = y.numpy()

    output = weights @ x.T + biases
    preds = np.argmax(output.reshape(10,))

    if preds == y:
      acc += 1
    size += 1
  
  # print("Test accuracy: {}".format(acc / size))
  return acc / size

acc = predict(weights, biases, test_loader)
print("Accuracy on test dataset: {}", acc)