import tensorflow as tf 
import numpy as np 
import model as M 
import cv2 


def verify_net(inp,test):
	with tf.variable_scope('detectionLayers'):
		if not test:
			inp = tf.scan(lambda _,y:tf.image.random_brightness(y,20),inp,initializer=tf.constant(0.0,shape=[32,32,3]))
			inp = tf.scan(lambda _,y:tf.image.random_contrast(y,0.5,2),inp,initializer=tf.constant(0.0,shape=[32,32,3]))
			inp = tf.scan(lambda _,y:tf.image.random_saturation(y,0.5,2),inp,initializer=tf.constant(0.0,shape=[32,32,3]))
		mod = M.Model(inp,[None,32,32,3])
		mod.convLayer(5,16,stride=1,activation=M.PARAM_RELU)		#32_8x8
		mod.maxpoolLayer(2)
		mod.convLayer(5,64,stride=1,activation=M.PARAM_RELU)	#16_16x16
		mod.maxpoolLayer(2)
		mod.convLayer(3,128,stride=1,activation=M.PARAM_RELU)	#8_16x16	
		mod.maxpoolLayer(2)
		mod.flatten()
		mod.fcLayer(300,activation=M.PARAM_RELU)
		mod.fcLayer(1)		
		return mod.get_current_layer()

def RPN(inp,test):
	with tf.variable_scope('mainModel'):
		if not test:
			inp = tf.scan(lambda _,y:tf.image.random_brightness(y,20),inp,initializer=tf.constant(0.0,shape=[256,256,3]))
			inp = tf.scan(lambda _,y:tf.image.random_contrast(y,0.5,2),inp,initializer=tf.constant(0.0,shape=[256,256,3]))
			inp = tf.scan(lambda _,y:tf.image.random_saturation(y,0.5,2),inp,initializer=tf.constant(0.0,shape=[256,256,3]))
		mod = M.Model(inp,[None,256,256,3])
		mod.convLayer(5,16,stride=2,activation=M.PARAM_RELU)#128_2x2
		mod.convLayer(4,32,stride=2,activation=M.PARAM_RELU)#64_4x4
		mod.convLayer(3,64,stride=2,activation=M.PARAM_MFM)#32_8x8
		mod.convLayer(3,128,activation=M.PARAM_MFM)#32_8x8
		mod.convLayer(3,256,stride=2,activation=M.PARAM_RELU)#16_16x16
		mod.convLayer(3,256,activation=M.PARAM_RELU)
		mod.convLayer(3,256,activation=M.PARAM_RELU)
		feature =mod.convLayer(1,128*2,activation=M.PARAM_RELU)
		bias = mod.convLayer(1,4)  #x_bias, y_bias
		mod.set_current(feature)
		conf = mod.convLayer(1,1)  #confidence of object
		return conf[0],bias[0],feature[0]

