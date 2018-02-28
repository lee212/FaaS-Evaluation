# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Simple image classification with Inception.

Run image classification with Inception trained on ImageNet 2012 Challenge data
set.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

Change the --image_file argument to any jpg image to compute a
classification of that image.

Please see the tutorial and website for a detailed description of how
to use this script to perform image recognition.

https://tensorflow.org/tutorials/image_recognition/
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import boto3
import argparse
import os
import re
import tempfile

import numpy as np
from six.moves import urllib
import tensorflow as tf
from multiprocessing import Process, Pipe

s3 = boto3.resource('s3')

# NOTE: Define the environment variable 'model_bucket_name' in
# Lambda before running!

MODEL_GRAPH_DEF_PATH = os.path.join(os.sep, 'tmp', 'model.pb')

# Feel free to load these as environment variables through Lambda.
LABEL_STRINGS_FILENAME = os.path.join(
    'imagenet', 'imagenet_2012_challenge_label_map_proto.pbtxt')
LABEL_IDS_FILENAME = os.path.join(
    'imagenet', 'imagenet_synset_to_human_label_map.txt')

MODEL_FILENAME = 'classify_image_graph_def.pb'

class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = LABEL_STRINGS_FILENAME
    if not uid_lookup_path:
      uid_lookup_path = LABEL_IDS_FILENAME
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]


def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with tf.gfile.FastGFile(MODEL_GRAPH_DEF_PATH, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')


# Creates node ID --> English string lookup.
print('Loading ID-to-string dict from file...')
NODE_LOOKUP = NodeLookup()

# This must be called before create_graph().
print('Downloading Model from S3...')
s3.Bucket(os.environ['model_bucket_name']).download_file(
                                                      MODEL_FILENAME,
                                                      MODEL_GRAPH_DEF_PATH)

# Creates graph from saved GraphDef.
print('Creating TF computation graph...')
create_graph()

def run_inference_on_image(image):
  """Runs inference on an image.

  Args:
    image: Image file name.

  Returns:
    Nothing
  """
  if not tf.gfile.Exists(image):
    tf.logging.fatal('File does not exist %s', image)
  image_data = tf.gfile.FastGFile(image, 'rb').read()

  with tf.Session() as sess:
    # Some useful tensors:
    # 'softmax:0': A tensor containing the normalized prediction across
    #   1000 labels.
    # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
    #   float description of the image.
    # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
    #   encoding of the image.
    # Runs the softmax tensor by feeding the image_data as input to the graph.
    softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
    predictions = sess.run(softmax_tensor,
                           {'DecodeJpeg/contents:0': image_data})
    predictions = np.squeeze(predictions)

    num_top_predictions = 5
    top_k = predictions.argsort()[-num_top_predictions:][::-1]
    results = []
    for node_id in top_k:
      human_string = NODE_LOOKUP.id_to_string(node_id)
      score = predictions[node_id]
      results.append((human_string, score))

    return results
    # print('%s (score = %.5f)' % (human_string, score))

def rioim(bucket, key, conn):
    # load image
    tmp = tempfile.NamedTemporaryFile()
    #with open(tmp.name, 'wb') as f:
    s3.Bucket(bucket).download_file(key, tmp.name)
    tmp.flush()

    (prediction_label, prediction_prob) = run_inference_on_image(tmp.name)[0]

    conn.send(['(%s, %s)' % (str(prediction_prob), prediction_label)])
    conn.close()

def lambda_handler(event, context):
  results = []
  pcs = []
  ps = []
  for record in event['Records']:
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    print('Running Deep Learning example using Tensorflow library ...')
    print('Image to be processed, from: bucket [%s], object key: [%s]' % (bucket, key))

    parent_conn, child_conn = Pipe()
    pcs.append(parent_conn)
    process = Process(target=rioim, args=(bucket, key, child_conn,))
    ps.append(process)
  for p in ps:
    p.start()
  print ("start done")
  for p in ps:
    p.join()
  print ("join done")
  for pc in pcs:
    results.append(pc.recv())
  print (results)
  return results


