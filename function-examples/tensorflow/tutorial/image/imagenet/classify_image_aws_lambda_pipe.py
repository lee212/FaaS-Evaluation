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

import boto3
import argparse
import os
import re
import time
import numpy as np
import tensorflow as tf
try:
    from multiprocessing import Pool
except:
    pass

client = boto3.client('s3')

# NOTE: Define the environment variable 'model_bucket_name' in
# Lambda before running!

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
  #with tf.gfile.FastGFile(MODEL_GRAPH_DEF_PATH, 'rb') as f:
  graph_def = tf.GraphDef()
  graph_def.ParseFromString(model_body)#f.read())
  _ = tf.import_graph_def(graph_def, name='')


# Creates node ID --> English string lookup.
print('Loading ID-to-string dict from file...')
NODE_LOOKUP = NodeLookup()

# This must be called before create_graph().
print('Loading Model on S3 to memory...')
s_model = time.time()
model_obj = client.get_object(Bucket=os.environ['model_bucket_name'], Key=MODEL_FILENAME)
model_body = model_obj['Body'].read()
e_model = time.time()

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
  """
  if not tf.gfile.Exists(image):
    tf.logging.fatal('File does not exist %s', image)
  image_data = tf.gfile.FastGFile(image, 'rb').read()
  """
  image_data = image

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

def lambda_handler(event, context):
    results = []
    pcs = []
    ps = []
    for record in event['Records']:
      bucket = record['s3']['bucket']['name']
      key = record['s3']['object']['key']

      print('Running Deep Learning example using Tensorflow library ...')
      print('Image to be processed, from: bucket [%s], object key: [%s]' % (bucket, key))

      obj = client.get_object(Bucket=bucket, Key=key)
      body = obj['Body'].read()

      (prediction_label, prediction_prob) = run_inference_on_image(body)[0]
      results.append( (prediction_label, prediction_prob) )
    return results

def get_argparse():
    parser= argparse.ArgumentParser("imagenet example for aws lambda")
    parser.add_argument("-b", "--bucket")
    parser.add_argument("-k", "--key")
    parser.add_argument("-s", "--size", type=int, default=1, help="batch size, e.g. 96 vcpus, 96 batch")
    args = parser.parse_args()
    return args

def rioi(args):
    bucket, key = args
    s3d_start = time.time()
    client = boto3.client("s3")
    obj = client.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()
    s3d_end = time.time()

    start = time.time()
    (prediction_label, prediction_prob) = run_inference_on_image(body)[0]
    end = time.time()
    res = { "result": (prediction_label, prediction_prob),
            "elapsed": end - start,
            "s3d_elapsed": s3d_end - s3d_start }
    return res

def run_inference_concurrent(bucket, keys, size):
    event = { "Records": [] }
    with Pool(processes=size) as p:
        res = []
        for key in keys:
            param = (bucket, key)
            res.append(p.apply_async(rioi, (param,)))

        nres = []
        for i in res:
            nres.append(i.get())
    return nres

def main(bucket, key, batch_size):
    if key != "":
        objs = client.list_objects(Bucket=bucket, Prefix=key)
    else:
        objs = client.list_objects(Bucket=bucket)
    keys = []
    all_res = []
    for obj in objs['Contents']:
        keys.append(obj['Key'])
        if len(keys) == batch_size:
            res = run_inference_concurrent(bucket, keys, batch_size)
            keys = []
            all_res += res
    # residue
    #if cnt == len(objs['Contents']) and loc != 0:
    if keys:
        res = run_inference_concurrent(bucket, keys, batch_size)
        all_res += res

    print (all_res)
    return all_res

if __name__ == "__main__":
    args = get_argparse()
    res = main(args.bucket, args.key, args.size)
    elapsed_total = 0
    s3d_elapsed_total = 0
    for i in res:
        elapsed_total += i["elapsed"]
        s3d_elapsed_total += i["s3d_elapsed"]
    print (("avg elapsed total:{}, avg s3d_elapsed_total:{}, " + \
        "len:{}").format(elapsed_total/len(res), s3d_elapsed_total/len(res), len(res)))

