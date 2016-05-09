

import tensorflow as tf
from tensorflow.models.rnn import rnn, rnn_cell
from tensorflow.contrib import ctc

import numpy as np

import mnist_input_data
mnist = mnist_input_data.read_data_sets("/tmp/data/", one_hot=True)



# Global parameters
learning_rate = 0.001
learning_iterations = 100  # number of mini-batches
mini_batch_size = 100
n_hidden_layer = 128
n_output_classes = 28  # Number of letters in our alphabet


# Input Data Parameters
batch_size = 128  # (i, o) Divide input into batches of max input size of i timesteps and max output label size o. If < i or < o should be padded accordingly
n_input = 8  # Number of input features for each sliding window of 1px
max_input_timesteps = 50

# Network weights. Does not depend on batch size
hidden_weights = tf.Variable(tf.random_normal([n_input, 2 * n_hidden_layer]))  # 2 * n_hidden_layer for forward and backward layer
hidden_biases = tf.Variable(tf.random_normal([2 * n_hidden_layer]))

output_weights = tf.Variable(tf.random_normal([2 * n_hidden_layer, n_output_classes]))
output_biases = tf.Variable(tf.random_normal([n_output_classes]))


# Tensorflow graph inout/output
x = tf.placeholder("float", [None, max_input_timesteps, n_input])
x_length = tf.placeholder("int32", [None])
y = tf.placeholder("int32", [None, n_output_classes])

istate_fw = tf.placeholder("float", [None, 2 * n_hidden_layer])
istate_bw = tf.placeholder("float", [None, 2 * n_hidden_layer])


# Adapted for different length of input batches code from brnn minst tutorial.
# Used to calculate forward pass of network
# n_steps - number of timesteps in current batch
def blstm_layer(_X, _istate_fw, _istate_bw, _x_length):

    # input shape: (batch_size, n_steps, n_input)
    _X = tf.transpose(_X, [1, 0, 2])  # permute n_steps and batch_size
    # Reshape to prepare input to hidden activation
    _X = tf.reshape(_X, [-1, n_input])  # (n_steps*batch_size, n_input)
    # Linear activation
    _X = tf.matmul(_X, hidden_weights) + hidden_biases

    # Define lstm cells with tensorflow
    # Forward direction cell
    lstm_fw_cell = rnn_cell.BasicLSTMCell(n_hidden_layer, forget_bias=1.0)
    # Backward direction cell
    lstm_bw_cell = rnn_cell.BasicLSTMCell(n_hidden_layer, forget_bias=1.0)
    # Split data because rnn cell needs a list of inputs for the RNN inner loop
    _X = tf.split(0, max_input_timesteps, _X)  # n_steps * (batch_size, n_hidden)

    # Get lstm cell output
    outputs = rnn.bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, _X,
                                            initial_state_fw=_istate_fw,
                                            initial_state_bw=_istate_bw,
                                            sequence_length=_x_length
                                    )

    # Linear activation
    # Get inner loop last output
    # TODO Should be all outputs? Not only last ones
    return tf.matmul(outputs, output_weights) + output_biases

prediction = blstm_layer(x, istate_fw, istate_bw, x_length)

cost = ctc.ctc_loss(prediction, y, x_length)
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)
    step = 1
    # Keep training until reach max iterations
    while step < learning_iterations:
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        # Reshape data to get 28 seq of 28 elements
        batch_xs = batch_xs.reshape((batch_size, max_input_timesteps, n_input))
        # Fit training using batch data
        sess.run(optimizer, feed_dict={x: batch_xs, y: batch_ys,
                                       istate_fw: np.zeros((batch_size, 2 * n_hidden_layer)),
                                       istate_bw: np.zeros((batch_size, 2 * n_hidden_layer))})
        if step % display_step == 0:
            # # Calculate batch accuracy
            # acc = sess.run(accuracy, feed_dict={x: batch_xs, y: batch_ys,
            #                                     istate_fw: np.zeros((batch_size, 2 * n_hidden_layer)),
            #                                     istate_bw: np.zeros((batch_size, 2 * n_hidden_layer))})
            # Calculate batch loss
            loss = sess.run(cost, feed_dict={x: batch_xs, y: batch_ys,
                                             istate_fw: np.zeros((batch_size, 2 * n_hidden_layer)),
                                             istate_bw: np.zeros((batch_size, 2 * n_hidden_layer))})
            print("Iter " + str(step * batch_size) + ", Minibatch Loss= " + "{:.6f}".format(loss) + \
                  ", Training Accuracy= " + "{:.5f}".format(0))
        step += 1
    print("Optimization Finished!")
    # Calculate accuracy for 128 mnist test images
    test_len = 128
    test_data = mnist.test.images[:test_len].reshape((-1, max_input_timesteps, n_input))
    test_label = mnist.test.labels[:test_len]
    print("Testing Accuracy:", sess.run(accuracy, feed_dict={x: test_data, y: test_label,
                                                             istate_fw: np.zeros((test_len, 2 * n_hidden_layer)),
                                                             istate_bw: np.zeros((test_len, 2 * n_hidden_layer))}))

    
