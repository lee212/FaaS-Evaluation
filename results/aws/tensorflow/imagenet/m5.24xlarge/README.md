# TensorFlow imagenet examples on AWS EC2

## Description

929 images are processed to measure elapsed time on a particular server type

Training images (Task 3) are used from http://www.image-net.org/challenges/LSVRC/2012/nnoupb/ILSVRC2012_img_train_t3.tar

## Command
 ```
for i in `ls -d ILSVRC2012/*[0-9]`; do  dirname=${i##*/};  { time python classify_image.pipe.py --image_dir $i  2> /dev/null > $dirname.$parallel.$try.result ; }  2> $dirname.$parallel.$try.time ; done
```

## m5.24xlarge


