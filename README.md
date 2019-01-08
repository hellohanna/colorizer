Colorize Beyond
===
**Deep learning pix2pix colorizer**

http://colorizebeyond.com/

The basic feature of this web app allows you to upload and
colorize grayscale pictures using a deep learning pix2pix model, which I pre-trained on a
portraits dataset sourced from Pinterest.
The model is based on the
[PyTorch pix2pix implementation by Jun-Yan Zhu](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix).

There is also a training feature that allows you to train models on your own datasets.
With it, you can create models that will be able to colorize other types of images.
The training backend is implemented as an async worker that can be scaled to multiple
GPU machines. Trained models can be used from web UI.

## About this project
This project was originally created as a student project for Hackbright Academy by engineering student, Hanna 
Babushkina.

Tech stack: Flask, PIL, ImageMagick, PyTorch, PostgreSQL, JavaScript.
