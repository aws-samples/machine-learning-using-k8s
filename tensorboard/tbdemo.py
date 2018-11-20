import tensorflow as tf
# To clear the defined variables and operations of the previous cell
tf.reset_default_graph()
# create graph
a = tf.constant(5, name="x")
b = tf.constant(4, name="y")
c = tf.add(a, b, name="addition")
# creating the writer out of the session
# writer = tf.summary.FileWriter('./graphs', tf.get_default_graph())
# launch the graph in a session
with tf.Session() as sess:
    # or creating the writer inside the session
    writer = tf.summary.FileWriter('./graphs', sess.graph)
    print(sess.run(c))
