The repository stores the binary executable of StructVIO. Please see the [project page](http://drone.sjtu.edu.cn/dpzou/project/structvio/structvio.html) for more details.

![Mahattan world vs Atlanta world](http://drone.sjtu.edu.cn/dpzou/project/structvio/images/manhattan.png)
![structvio](http://drone.sjtu.edu.cn/dpzou/project/structvio/images/structvio.png)

# Running StructVIO
After downloading the [binary file](https://github.com/danping/structvio/blob/master/binary/structvio) and extraction of 'Soft-01.zip' to the 'Soft-01' folder, we run the following command to start VIO.
```shell
./structvio -i ./Soft-01 -n Soft-01 -r Soft-01-res -c structvio_data.yaml
```
Here, 'structvio_data.yaml' is a configuration file for the running algorithm, which includes the camera and imu parameters.

Here [structvio_data.yaml](https://github.com/danping/structvio/blob/master/structvio_data.yaml) and [euroc_data.yaml](https://github.com/danping/structvio/blob/master/euroc_data.yaml) are the default configurations for StructVIO datasets and Euroc datasets. You can type
```shell
./structvio --help
```
to get the usage of different arguments. Some of them are listed in the following.
```shell
-g,  --gui_on
  Display the GUIs

-t <Image latency (nanoseconds)>,  --img_latency <Image latency
   (nanoseconds)>
  Time latency of image

-i <root path of the input data>,  --input_dir <root path of the input
   data>
  (required)  The root path of the single set of data

-n <name of the data>,  --data_name <name of the data>
  (required)  The name of the data

-r <result dir>,  --result_dir <result dir>
  (required)  The folder to save the results

-c <.yaml file of configuration>,  --cfg_yaml <.yaml file of
   configuration>
  (required)  The .yaml file that specifies the sensor parameters and
  program options

-p <number>,  --point_num <number>
  Number of points used

-l <0|1|2>,  --line_type <0|1|2>
  Type of lines used: 0-structlines, 1-general lines, 2-both

-f <0|1|2>,  --feature_type <0|1|2>
  Type of features used: 0 - point, 1 - line, 2 - both
```
If you want to run point-only VIO, please type
```shell
./structvio -i ./Soft-01 -n Soft-01 -r Soft-01-res -c structvio_data.yaml - f 0
```
You can also change the number of points allowed to be detected by using '-p' option. For example, we change the number to 50.
```shell
./structvio -i ./Soft-01 -n Soft-01 -r Soft-01-res -c structvio_data.yaml - f 0 -p 50
```
To run StructVIO on the [Euroc](https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets) datasets, download the configuration file  [euroc_data.yaml](https://github.com/danping/structvio/blob/master/euroc_data.yaml) and type
```shell
./structvio -i ./MH_01_easy -n mav0 -r MH_01_easy-res -c euroc_data.yaml
```
