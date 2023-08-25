# Object Detection Tutorial

<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/02-object-detection.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/master/tutorials/02-object-detection.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://raw.githubusercontent.com/georgia-tech-db/eva/master/tutorials/02-object-detection.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
  </td>
</table><br><br>

### Connect to EvaDB


```python
%pip install --quiet "evadb[vision,notebook]"
import evadb
cursor = evadb.connect().cursor()
```

    Note: you may need to restart the kernel to use updated packages.


### Download the Surveillance Videos

In this tutorial, we focus on the UA-DETRAC benchmark. UA-DETRAC is a challenging real-world multi-object detection and multi-object tracking benchmark. The dataset consists of 10 hours of videos captured with a Cannon EOS 550D camera at 24 different locations at Beijing and Tianjin in China.


```python
# Getting the video files
!wget -nc "https://www.dropbox.com/s/k00wge9exwkfxz6/ua_detrac.mp4?raw=1" -O ua_detrac.mp4
```

    File ‘ua_detrac.mp4’ already there; not retrieving.


### Load the videos for analysis

We use a regular expression to load all the videos into the table in a single command


```python
cursor.query("DROP TABLE IF EXISTS ObjectDetectionVideos;").df()
cursor.load(file_regex='ua_detrac.mp4', format="VIDEO", table_name='ObjectDetectionVideos').df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Number of loaded VIDEO: 1</td>
    </tr>
  </tbody>
</table>
</div>



### Register YOLO Object Detector as an User-Defined Function (UDF) in EvaDB 


```python
cursor.query("""
            CREATE UDF IF NOT EXISTS Yolo
            TYPE  ultralytics
            'model' 'yolov8m.pt';
      """).df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>UDF Yolo already exists, nothing added.</td>
    </tr>
  </tbody>
</table>
</div>



### Run the YOLO Object Detector on the video


```python
yolo_query = cursor.table("ObjectDetectionVideos")
yolo_query = yolo_query.filter("id < 20")
yolo_query = yolo_query.select("id, Yolo(data)")

response = yolo_query.df()
print(response)
```

        objectdetectionvideos.id  \
    0                          0   
    1                          1   
    2                          2   
    3                          3   
    4                          4   
    5                          5   
    6                          6   
    7                          7   
    8                          8   
    9                          9   
    10                        10   
    11                        11   
    12                        12   
    13                        13   
    14                        14   
    15                        15   
    16                        16   
    17                        17   
    18                        18   
    19                        19   
    
                                              yolo.labels  \
    0   [car, car, car, car, car, car, person, car, ca...   
    1   [car, car, car, car, car, car, car, car, car, ...   
    2   [car, car, car, car, car, car, car, person, ca...   
    3   [car, car, car, car, car, car, car, car, car, ...   
    4   [car, car, car, car, car, car, car, car, car, ...   
    5   [car, car, car, car, car, car, person, car, ca...   
    6   [car, car, car, car, car, car, car, person, ca...   
    7   [car, car, car, car, car, car, car, car, car, ...   
    8   [car, car, car, car, car, car, person, car, ca...   
    9   [car, car, car, car, car, car, car, person, ca...   
    10  [car, car, car, car, car, car, car, person, ca...   
    11  [car, car, car, car, car, car, person, car, ca...   
    12  [car, car, car, car, car, car, car, person, ca...   
    13  [car, car, car, car, car, car, person, car, ca...   
    14  [car, car, car, car, car, car, person, car, ca...   
    15  [car, car, car, car, car, car, person, car, ca...   
    16  [car, car, car, car, car, car, car, person, ca...   
    17  [car, car, car, car, car, car, car, person, ca...   
    18  [car, car, car, car, car, car, car, person, mo...   
    19  [car, car, car, car, car, person, car, car, ca...   
    
                                              yolo.bboxes  \
    0   [[828.603515625, 277.01861572265625, 959.62792...   
    1   [[832.1552734375, 278.1466064453125, 959.63830...   
    2   [[835.5642700195312, 279.1689147949219, 959.64...   
    3   [[839.2291259765625, 279.876953125, 959.635620...   
    4   [[843.063232421875, 280.84881591796875, 959.62...   
    5   [[847.2269897460938, 282.40478515625, 959.6654...   
    6   [[850.6966552734375, 283.1654052734375, 959.43...   
    7   [[854.817626953125, 283.79345703125, 959.55505...   
    8   [[859.06787109375, 285.23321533203125, 959.824...   
    9   [[862.5375366210938, 286.3861083984375, 959.53...   
    10  [[631.713623046875, 222.67929077148438, 744.18...   
    11  [[871.2513427734375, 288.50506591796875, 959.5...   
    12  [[636.3242797851562, 223.41517639160156, 750.0...   
    13  [[170.86529541015625, 409.34344482421875, 291....   
    14  [[174.27420043945312, 404.84698486328125, 293....   
    15  [[887.9122924804688, 292.99810791015625, 959.5...   
    16  [[892.8345336914062, 293.4510803222656, 959.53...   
    17  [[182.45166015625, 392.1574401855469, 296.3449...   
    18  [[901.4002075195312, 295.100341796875, 959.572...   
    19  [[647.9462890625, 226.44598388671875, 770.2973...   
    
                                              yolo.scores  
    0   [0.91, 0.86, 0.85, 0.83, 0.76, 0.73, 0.72, 0.7...  
    1   [0.92, 0.85, 0.84, 0.83, 0.78, 0.76, 0.76, 0.7...  
    2   [0.92, 0.84, 0.84, 0.82, 0.81, 0.75, 0.73, 0.7...  
    3   [0.91, 0.84, 0.82, 0.8, 0.8, 0.75, 0.74, 0.72,...  
    4   [0.9, 0.85, 0.83, 0.8, 0.76, 0.73, 0.72, 0.72,...  
    5   [0.89, 0.86, 0.84, 0.8, 0.78, 0.74, 0.72, 0.72...  
    6   [0.89, 0.87, 0.85, 0.81, 0.79, 0.73, 0.72, 0.7...  
    7   [0.9, 0.87, 0.84, 0.83, 0.83, 0.79, 0.73, 0.67...  
    8   [0.89, 0.88, 0.83, 0.82, 0.79, 0.71, 0.68, 0.6...  
    9   [0.88, 0.87, 0.84, 0.82, 0.8, 0.75, 0.74, 0.74...  
    10  [0.88, 0.88, 0.85, 0.82, 0.8, 0.79, 0.76, 0.71...  
    11  [0.9, 0.9, 0.85, 0.8, 0.79, 0.77, 0.69, 0.68, ...  
    12  [0.9, 0.88, 0.83, 0.81, 0.78, 0.78, 0.78, 0.67...  
    13  [0.9, 0.89, 0.89, 0.83, 0.81, 0.81, 0.72, 0.71...  
    14  [0.9, 0.89, 0.88, 0.84, 0.82, 0.81, 0.75, 0.72...  
    15  [0.89, 0.88, 0.87, 0.84, 0.82, 0.78, 0.76, 0.7...  
    16  [0.88, 0.88, 0.87, 0.82, 0.81, 0.76, 0.75, 0.7...  
    17  [0.9, 0.89, 0.87, 0.83, 0.82, 0.78, 0.72, 0.69...  
    18  [0.88, 0.88, 0.83, 0.82, 0.8, 0.78, 0.75, 0.7,...  
    19  [0.89, 0.87, 0.81, 0.8, 0.78, 0.77, 0.73, 0.72...  


### Visualizing output of the Object Detector on the video


```python
import cv2
from pprint import pprint
from matplotlib import pyplot as plt

def annotate_video(detections, input_video_path, output_video_path):
    color1=(207, 248, 64)
    color2=(255, 49, 49)
    thickness=4

    vcap = cv2.VideoCapture(input_video_path)
    width = int(vcap.get(3))
    height = int(vcap.get(4))
    fps = vcap.get(5)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') #codec
    video=cv2.VideoWriter(output_video_path, fourcc, fps, (width,height))

    frame_id = 0
    # Capture frame-by-frame
    # ret = 1 if the video is captured; frame is the image
    ret, frame = vcap.read() 

    while ret:
        df = detections
        df = df[['yolo.bboxes', 'yolo.labels']][df.index == frame_id]
        if df.size:
            dfLst = df.values.tolist()
            for bbox, label in zip(dfLst[0][0], dfLst[0][1]):
                x1, y1, x2, y2 = bbox
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # object bbox
                frame=cv2.rectangle(frame, (x1, y1), (x2, y2), color1, thickness) 
                # object label
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color1, thickness) 
                # frame label
                cv2.putText(frame, 'Frame ID: ' + str(frame_id), (700, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color2, thickness) 
            video.write(frame)

            # Stop after twenty frames (id < 20 in previous query)
            if frame_id == 20:
                break

            # Show every fifth frame
            if frame_id % 5 == 0:
                plt.imshow(frame)
                plt.show()

        
        frame_id+=1
        ret, frame = vcap.read()

    video.release()
    vcap.release()
```


```python
from ipywidgets import Video, Image
input_path = 'ua_detrac.mp4'
output_path = 'video.mp4'

annotate_video(response, input_path, output_path)
Video.from_file(output_path)
```


    
![png](02-object-detection_files/02-object-detection_14_0.png)
    



    
![png](02-object-detection_files/02-object-detection_14_1.png)
    



    
![png](02-object-detection_files/02-object-detection_14_2.png)
    



    
![png](02-object-detection_files/02-object-detection_14_3.png)
    





    Video(value=b'\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free\x00\t5X...')



### Drop the function if needed


```python
cursor.query("DROP UDF IF EXISTS Yolo").df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>UDF Yolo successfully dropped</td>
    </tr>
  </tbody>
</table>
</div>


