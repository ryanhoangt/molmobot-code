# Build the Person-Following Drone with Tello and OpenCV

## MobileNet-SSD Weights and Prototxt

Download the MobileNet-SSD weights and prototxt files from the following links:

- [MobileNet-SSD Caffe Model](https://github.com/chuanqi305/MobileNet-SSD/blob/master/MobileNetSSD_deploy.caffemodel)
- [MobileNet-SSD Prototxt](https://github.com/chuanqi305/MobileNet-SSD/blob/master/MobileNetSSD_deploy.prototxt)

You can use the following commands to download them directly:

```bash
mkdir -p **resources**
curl -L -o resources/mobilenet_ssd_deploy.prototxt https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt
curl -L -o resources/mobilenet_ssd.caffemodel https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.caffemodel
```
