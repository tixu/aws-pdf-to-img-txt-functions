import asyncio
from contextlib import closing
import concurrent.futures
import io
import os
import json
import logging
import os
import re
import subprocess
from tempfile import NamedTemporaryFile
import time
from uuid import uuid4
import urllib
import subprocess


import boto3

LAMBDA_TASK_ROOT = os.environ.get('LAMBDA_TASK_ROOT', os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(LAMBDA_TASK_ROOT, 'bin')
LIB_DIR = os.path.join(LAMBDA_TASK_ROOT, 'lib')
TESSDATA_DIR = os.path.join(LAMBDA_TASK_ROOT, 'tessdata')
s3 = boto3.resource('s3')
logging.basicConfig(format='%(asctime)-15s [%(name)s-%(process)d] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def F(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    for record in event['Records']:
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        try:
          print("Bucket: "+ bucket)
          print("Key: "+ key)

          predicat,suffix =  os.path.splitext(key)          
          obj = s3.Object(bucket_name=bucket, key=record['s3']['object']['key'])
        except Exception as e:
          print(e)
          print('Error getting object {} from bucket {}. Make sure they exist '
                'and your bucket is in the same region as this '
                'function.'.format(key, bucket))
          raise e
        response = obj.get()
        body = response['Body']
        with NamedTemporaryFile(mode='wb', suffix=".pdf", prefix="rec_", delete=False) as f:
            print (f.name)
            document_path = f.name
            print ("about to write pdf".format(document_path))
            try:
               with io.FileIO(f.name, 'w') as file:
                  while file.write(body.read(amt=512)):
                        pass
            except Exception as e:
               print(e)
               print('Error writing file')
               raise e
            try:
              image_path = pdf_to_img(f.name)
              text_path  = pdf_to_text(image_path)
              s3.Object('telos-2', "{}.png".format(predicat)).put(Body=open(image_path, 'rb'))
              s3.Object('telos-2', "{}.txt".format(predicat)).put(Body=open(text_path, 'rb'))

            except Exception as e:
              print(e)
      #end_with
# end_def
def pdf_to_img(input):
       with NamedTemporaryFile(mode='wb', suffix=".png", prefix="gs_", delete=False) as f:
            print (f.name)
            cmdline = [os.path.join(BIN_DIR, 'gs'), '-sDEVICE=png16m', '-dINTERPOLATE', '-r300', '-o', f.name , input, ]  # extract the page as an image
            print(cmdline)
            output=subprocess.run(cmdline)
            if os.path.getsize(f.name) == 0:
                 raise Exception('Ghostscript image extraction failed with output:\n{}'.format(output))
       return f.name
# end_def

def pdf_to_text(input):
      print('received file {}'.format(input))
      if os.path.getsize(input) == 0:
         raise Exception('pdf_to_text_receive_an empty file {}'.format(imagepath))

      with NamedTemporaryFile(mode='wb', prefix="tesr_", delete=True) as f:
            print (f.name)
            command = '{}/tesseract {} {}'.format(
                    BIN_DIR,
                    input,
                    f.name,
            )

            try:
              print (command)
              output = subprocess.run(command, shell=True)          
              print(output)

              if os.path.getsize("{}.txt".format(f.name)) == 0:
                 raise Exception('OCR failed:\n{}'.format(output))
              return "{}.txt".format(f.name)
            except Exception as e:
               print('exception')
               print(e)

#end_def


