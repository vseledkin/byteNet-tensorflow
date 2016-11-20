#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tensorflow as tf
import numpy as np
import argparse
import model_config
import data_loader
from ByteNet import model
import utils

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--learning_rate', type=float, default=0.001,
					   help='Learning Rate')
	parser.add_argument('--batch_size', type=int, default=1,
					   help='Learning Rate')
	parser.add_argument('--max_epochs', type=int, default=1000,
					   help='Max Epochs')
	parser.add_argument('--beta1', type=float, default=0.5,
					   help='Momentum for Adam Update')
	parser.add_argument('--resume_model', type=str, default=None,
                       help='Pre-Trained Model Path, to resume from')
	parser.add_argument('--data_dir', type=str, default='Data',
                       help='Data Directory')



	args = parser.parse_args()

	# model_config = json.loads( open('model_config.json').read() )

	config = model_config.predictor_config

	model_options = {
		'n_source_quant' : config['n_source_quant'],
		'n_target_quant' : config['n_target_quant'],
		'residual_channels' : config['residual_channels'],
		'decoder_dilations' : config['decoder_dilations'],
		'sample_size' : config['sample_size'],
		'decoder_filter_width' : config['decoder_filter_width'],
		'batch_size' : args.batch_size,
	}

	byte_net = model.Byte_net_model( model_options )
	bn_tensors = byte_net.build_prediction_model()

	optim = tf.train.AdamOptimizer(
		args.learning_rate,
		beta1 = args.beta1).minimize(bn_tensors['loss'], var_list=bn_tensors['variables'])

	sess = tf.InteractiveSession()
	tf.initialize_all_variables().run()
	saver = tf.train.Saver()

	if args.resume_model:
		saver.restore(sess, args.resume_model)

	dl = data_loader.Data_Loader({'model_type' : 'generator', 'dir_name' : args.data_dir})
	text_samples = dl.load_generator_data( config['sample_size'])
	print(text_samples.shape)

	for i in range(args.max_epochs):
		batch_no = 0
		batch_size = args.batch_size
		while (batch_no+1) * batch_size < text_samples.shape[0]:
			text_batch = text_samples[batch_no*batch_size : (batch_no + 1)*batch_size, :]
			_, loss, prediction = sess.run( [optim, bn_tensors['loss'], bn_tensors['prediction']], feed_dict = {
				bn_tensors['sentence'] : text_batch
				})
			print("-------------------------------------------------------")
			print(utils.list_to_string(prediction))
			print("Loss", i, batch_no, loss)
			print("********************************************************")
			# print prediction
			batch_no += 1

			if (batch_no % 500) == 0:
				save_path = saver.save(sess, "Data/Models/model_epoch_{}.ckpt".format(i))

if __name__ == '__main__':
	main()
