import time
import sys
import torch
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch.nn as nn
from torch.autograd import Variable

from CustomDataset import CustomDataset
from Two_Input_Net import Two_Input_Net


# Creates the dataframe
def get_data():
    return pd.read_csv('crafted_features.csv')


# Splits the features and output and creates training and testing data
def data_train_test_split(df, test_split=0.20):
    X = df.copy()
    # These features are all non-numeric
    unneeded_cols = ['UserID', 'createdAt', 'CollectedAt', 'userTweets', 'SeriesOfNumberOfFollowings', 'sequence']
    X = df.drop(unneeded_cols, axis=1)
    y = X['userType']
    del X['userType']
    # Split the data into training and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split)
    return X_train, X_test, y_train, y_test


# Performs min-max normalisation for profile features (numerical)
def normalise_numerical_features(X_train, X_test):
    columns = [col for col in X_train.columns if col != 'cleanTweets']
    # Min-Max Normalisation
    X_train[columns] = (X_train[columns] - X_train[columns].min()) / (X_train[columns].max() - X_train[columns].min())
    X_test[columns] = (X_test[columns] - X_test[columns].min()) / (X_test[columns].max() - X_test[columns].min())
    # Get values only
    X2_train = X_train[columns].values
    X2_test = X_test[columns].values
    return X2_train, X2_test

# Calculate vocabulary size for complete dataset
def vocab_size(df):
    # Tokenize the sentences
    tokenizer = Tokenizer(num_words=5000)
    # Preparing vocabulary on whole dataset
    tokenizer.fit_on_texts(df['cleanTweets'].tolist())
    return len(tokenizer.word_index) + 1

# Converts text entries into integer sequences and then performs padding
def text_preprocess(X_train, X_test, maxlen=150, max_num_words=5000):
    # Tokenize the sentences
    tokenizer = Tokenizer(num_words=max_num_words)
    # Preparing vocabulary
    tokenizer.fit_on_texts(X_train['cleanTweets'].tolist())
    # Convert Text to integer sequences
    X1_train = tokenizer.texts_to_sequences(X_train['cleanTweets'].tolist())
    X1_test = tokenizer.texts_to_sequences(X_test['cleanTweets'].tolist())
    # Padding to ensure all entries are the same length
    X1_train = torch.Tensor(pad_sequences(X1_train, maxlen=maxlen, padding='post'))
    X1_test = torch.Tensor(pad_sequences(X1_test, maxlen=maxlen, padding='post'))
    return X1_train, X1_test, tokenizer


# Loads the GloVe Pre-Trained Embedding
def load_embedding(path):
    embeddings_index = dict()
    f = open(path, 'r', encoding="utf8")
    for line in f:
        try:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        except:
            f.__next__()
    f.close()
    print('Loaded %s word vectors.' % len(embeddings_index))
    return embeddings_index


# Create the GloVe embedding based on text from dataframe
def create_embedding_matrix(size_of_vocabulary, pretrained_embedding_dim, tokenizer, embeddings_index):
    # Create empty matrix
    embedding_weights = torch.Tensor(size_of_vocabulary, pretrained_embedding_dim)
    # Add relevant word into matrix
    # If not included add a random initialisation based on a normal distribution
    for word, i in tokenizer.word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_weights[i] = embedding_vector
        else:
            embedding_weights[i] = torch.from_numpy(np.random.normal(scale=0.6, size=(pretrained_embedding_dim,)))
    return embedding_weights


# Calculate the accuracy of model
def calculate_accuracy(y_pred, y):
    binaryConverted = torch.round(y_pred)
    correct = (binaryConverted == y).sum()
    return correct.float() / y.shape[0]


# Main model training phase
def model_train(model, epoch, train_loader, optimizer, criterion):
    train_loss = 0
    train_acc = 0
    count = 0

    # MODEL: TRAIN
    model.train()

    print(f"---------------------Starting Epoch.. {(epoch + 1)} ---------------------")
    for text_data, meta_data, labels in train_loader:
        count += 1
        # Clear the gradients
        optimizer.zero_grad()
        # Compute the model output
        yhat = model([text_data, meta_data])
        # Calculate loss
        labels = labels.unsqueeze(1)
        loss = criterion(yhat, labels.float())
        # Calculate accuracy
        acc = calculate_accuracy(yhat, labels.float())
        # Credit assignment
        loss.backward()
        # Update model weights
        optimizer.step()
        # Total training loss and accuracy
        train_loss += loss.item()
        train_acc += acc.item()
        # Update Print Statement
        sys.stdout.write('\rPercentage Complete:  ' + str(round(count / len(train_loader) * 100)) + "%")
        sys.stdout.flush()
    # Ensures all new print statements all on next line
    print("")
    return (train_loss / len(train_loader)), (train_acc / len(train_loader))


def model_eval(model, eval_loader, criterion):
    # MODEL: EVAL
    model.eval()

    eval_loss = 0
    eval_acc = 0

    with torch.no_grad():
        for text_data, meta_data, labels in eval_loader:
            yhat = model([text_data, meta_data])
            # calculate loss
            labels = labels.unsqueeze(1)
            loss = criterion(yhat, labels.float())
            # Calculate accuracy
            acc = calculate_accuracy(yhat, labels.float())
            # Total training loss and accuracy
            eval_loss += loss.item()
            eval_acc += acc.item()

    return (eval_loss / len(eval_loader)), (eval_acc / len(eval_loader))


def output(epoch, time, train_loss, train_acc, eval_loss, eval_acc):
    print(f'Epoch: {(epoch + 1)} | Epoch Duration (Seconds): {time:.2f}')
    print(f'\tTrain Loss: {train_loss:.5f} | Train Accuracy: {train_acc:.5f}')
    print(f'\t Val. Loss: {eval_loss:.5f} |  Val. Accuracy: {eval_acc:.5f}')
    print(f"-------------------------------------------------------------")


def run_model(model, total_epoch, train_loader, eval_loader):
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    best_accuracy = -float('inf')

    for epoch in range(total_epoch):
        # Model TRAIN
        start_time = time.time()
        train_loss, train_acc = model_train(model, epoch, train_loader, optimizer, criterion)
        end_time = time.time()
        # Model EVAL
        eval_loss, eval_acc = model_eval(model, eval_loader, criterion)
        # Model output details
        output(epoch, (end_time - start_time), train_loss, train_acc, eval_loss, eval_acc)
        # Save Model with best accuracy
        if (eval_acc > best_accuracy):
            print("Updated Best Saved Model With Accuracy", eval_acc)
            best_accuracy = eval_acc
            torch.save(model, 'two_input_NN_best_model.pt')


def runner():
    # Default Params
    maxlen = 150
    pretrained_embedding_dim = 300
    max_num_words = 5000
    total_epoch = 8
    # Get data
    print("Getting Data...")
    df = get_data()
    # Load GloVe model
    print("Loading GloVe Embedding...")
    embeddings_index = load_embedding('glove.840B.300d.txt')
    # Create training/testing data
    X_train, X_test, y_train, y_test = data_train_test_split(df, test_split=0.20)
    # Normalise numerical features
    X2_train, X2_test = normalise_numerical_features(X_train, X_test)
    X2_train_shape = X2_train.shape[1]
    # Tokenize and pad text
    X1_train, X1_test, tokenizer = text_preprocess(X_train, X_test, maxlen, max_num_words)
    size_of_vocabulary = vocab_size(df)
    # Create GloVe embedding based on dataframe
    embedding_weights = create_embedding_matrix(size_of_vocabulary, pretrained_embedding_dim, tokenizer,
                                                embeddings_index)
    # Initialise Model
    print("Initialising Model...")
    model = Two_Input_Net(X2_train.shape[1], X1_train.shape[1], embedding_weights, size_of_vocabulary,
                          pretrained_embedding_dim, X2_train_shape, maxlen)
    # Convert profile features to Variable format
    X2_train = Variable(torch.Tensor(X2_train).float())
    X2_test = Variable(torch.Tensor(X2_test).float())
    # Convert to Variable format
    y_train = np.array(y_train)
    y_train = Variable(torch.LongTensor(y_train))
    y_test = np.array(y_test)
    y_test = Variable(torch.LongTensor(y_test))
    # Create the Custom Dataset for both training and validation set
    print("Preparing Dataset...")
    training_dataset = CustomDataset(X1_train, X2_train, y_train)
    eval_dataset = CustomDataset(X1_test, X2_test, y_test)
    # Create the data loaders for both the training and validation set
    train_loader = torch.utils.data.DataLoader(training_dataset, batch_size=128, shuffle=True)
    eval_loader = torch.utils.data.DataLoader(eval_dataset, batch_size=128, shuffle=False)
    # Run main model
    print("Model Running...")
    run_model(model, total_epoch, train_loader, eval_loader)


if __name__ == '__main__':
    runner()
