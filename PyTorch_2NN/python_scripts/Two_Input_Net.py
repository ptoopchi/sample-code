import torch
import torch.nn as nn
import numpy as np

class Two_Input_Net(nn.Module):
    def __init__(self, hidden_size, lin_size, embedding_matrix, size_of_vocabulary, pretrained_embedding_dim, X2_train_shape, maxlen):
        super(Two_Input_Net, self).__init__()

        # Layer 1a: Embedding Layer (Input)
        self.embedding = nn.Embedding(size_of_vocabulary, pretrained_embedding_dim)
        self.embedding.weight = nn.Parameter(torch.tensor(embedding_matrix, dtype=torch.float32))
        self.embedding.weight.requires_grad = False

        # Layer 1b: Bidirectional LSTM
        self.lstm = nn.LSTM(pretrained_embedding_dim, maxlen, bidirectional=True)

        # Layer 1c: MaxPooling, BatchNormalisation and Dropout
        self.globalMaxPool = nn.AdaptiveMaxPool1d(1)
        self.batchnorm = nn.BatchNorm1d(maxlen)
        self.dropout = nn.Dropout2d(0.5)

        # Layer 2a: Dense Layer (Input)
        self.linear_one = nn.Linear(X2_train_shape, 10)
        self.relu = nn.ReLU()

        # Layer 2b: Dense Layer
        self.linear_two = nn.Linear(10, lin_size)
        self.relu = nn.ReLU()

        # Layer 3a: Concatation Section which is described in forward().

        # Layer 3b: Dense Layer
        self.linear = nn.Linear(300, 10)
        self.relu = nn.ReLU()

        # Layer 4: Output Layer return probability value from 0 to 1.
        self.out = nn.Linear(10, 1)
        self.outFunc = nn.Sigmoid()

    def forward(self, x):
        # x[0] is the text feautes
        # x[1] is the numerical profile features

        # LSTM Layer
        h_embedding = self.embedding(x[0].long())
        h_embedding = torch.squeeze(torch.unsqueeze(h_embedding, 0))
        x[0], _ = self.lstm(h_embedding)

        # MaxPooling, BatchNormalisation and Dropout Layer
        x[0] = self.globalMaxPool(x[0])
        x[0] = self.batchnorm(x[0])
        x[0] = self.dropout(x[0])

        # Ensure x[1] is tensor format as float
        # 2 Dense Layers
        x[1] = torch.tensor(x[1], dtype=torch.float)
        x[1] = self.relu(self.linear_one(x[1]))
        x[1] = self.relu(self.linear_two(x[1]))

        # Layer 3a: Concatenate the outputs of x[0] and x[1]
        # x[0] has the 3rd dimension removed as its in the form [??,??,1] (ensures both x[0] and x[1] are same shape)
        x[0] = x[0][:, :, -1]
        conc = torch.cat((x[0], x[1]), 1)

        # Concatenated tensor passed through Dense Layer
        conc = self.relu(self.linear(conc))
        # Dense Layer which uses sigmoid activation function to return value between 0 and 1.
        out = self.out(conc)
        outF = self.outFunc(out)
        return outF