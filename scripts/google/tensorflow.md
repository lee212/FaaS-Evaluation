# Tensorflow Experiment on Google Functions

- Luckily, AWS packages for tensorflow, numpy works. simply downloads the libs and imports.
- Pipe does not show any benefits, e.g. two images:  17290ms, one image: 8640ms
- this is currently tested on systemcall function

```
{"cmd":"curl","params":["-s", "-L", "https://s3.amazonaws.com/aws-ml-blog/artifacts/Deep-Learning-On-AWS-Lambda-With-Tensorflow/DeepLearningAndAI-Bundle.zip", "-o", "/tmp/dl.zip"]}

{"cmd":"python","params":["/tmp/t/classify_image.py"]}
```


