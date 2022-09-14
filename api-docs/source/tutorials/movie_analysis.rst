Sentiment analysis tutorial
===========================

.. container:: cell markdown

   .. rubric:: Sentiment analysis tutorial
      :name: sentiment-analysis-tutorial

   run this notebook on `google
   colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/movie_analysis.ipynb>`__

.. container:: cell markdown

   .. rubric:: Launch EVA DB
      :name: launch-eva-db

   Run the command ``eva_server`` in the server where you want to deploy
   EVA

.. container:: cell markdown

   .. rubric:: Establish Connection With Eva DB
      :name: establish-connection-with-eva-db

.. container:: cell code

   .. code:: python

      import sys
      sys.path.insert(0,'..')
      from eva.server.db_api import connect

.. container:: cell code

   .. code:: python

      import nest_asyncio
      nest_asyncio.apply()
      connection = connect(host = '0.0.0.0', port = 5432) # hostname, port of the server where EVADB is running
      cursor = connection.cursor()

.. container:: cell code

   .. code:: python

      # Download UDFS
      !wget https://www.dropbox.com/s/me2dif7393twdx7/gender.py
      !wget https://www.dropbox.com/s/erebvb3nxn9vycl/face_detector.py

      # Download models
      !wget https://www.dropbox.com/s/0y291evpqdfmv2z/gender.pth

      # Download videos
      !wget https://www.dropbox.com/s/f5447euuuis1vdy/test.mp4
      !wget https://www.dropbox.com/s/f5447euuuis1vdy/short.mp4
      !wget https://www.dropbox.com/s/xf8b1vsrfa03a14/short2.mp4

.. container:: cell markdown

   .. rubric:: Load the example video to analyse
      :name: load-the-example-video-to-analyse

.. container:: cell code

   .. code:: python

      cursor.execute("LOAD FILE 'short2.mp4' INTO TIKTOK;")
      response = cursor.fetch_all()
      print(response)
      cursor.execute("""SELECT id FROM TIKTOK WHERE id < 5""")
      response = cursor.fetch_all()
      print(response)

.. container:: cell markdown

   .. rubric:: Visualize Video
      :name: visualize-video

.. container:: cell code

   .. code:: python

      from IPython.display import Video
      Video("short2.mp4", embed=True)

.. container:: cell markdown

   .. rubric:: Create GenderCNN UDF
      :name: create-gendercnn-udf

.. container:: cell code

   .. code:: python

      cursor.execute("""CREATE UDF IF NOT EXISTS 
                        GenderCNN
                        INPUT (data NDARRAY UINT8(3, 224, 224)) 
                        OUTPUT (label TEXT(10)) TYPE  
                        Classification IMPL 'gender.py';
              """)
      response = cursor.fetch_all()
      print(response)

.. container:: cell markdown

   .. rubric:: Run Face Detection on the video
      :name: run-face-detection-on-the-video

.. container:: cell code

   .. code:: python

      cursor.execute("""SELECT id, FaceDetector(data).bboxes FROM TIKTOK WHERE id < 30""")
      response = cursor.fetch_all()
      print(response)

.. container:: cell markdown

   .. rubric:: Detect Gender of the faces in the video
      :name: detect-gender-of-the-faces-in-the-video

.. container:: cell code

   .. code:: python

      cursor.execute("""SELECT id, bbox, GenderCNN(Crop(data, bbox)) FROM TIKTOK JOIN LATERAL  Unnest(FaceDetector(data)) AS Face(bbox, conf)  WHERE id < 10;""")
      response = cursor.fetch_all()
      print(response)

.. container:: cell markdown

   .. rubric:: Visualize output of Gender on the video
      :name: visualize-output-of-gender-on-the-video

.. container:: cell code

   .. code:: python

      import cv2
      def annotate_video(detections, input_video_path, output_video_path):
          color=(0,255,0)
          thickness=3

          vcap = cv2.VideoCapture(input_video_path)
          width = int(vcap.get(3))
          height = int(vcap.get(4))
          fps = vcap.get(5)
          fourcc = cv2.VideoWriter_fourcc(*'MP4V') #codec
          video=cv2.VideoWriter(output_video_path, fourcc, fps, (width,height))

          frame_id = 0
          # Capture frame-by-frame
          ret, frame = vcap.read()  # ret = 1 if the video is captured; frame is the image

          while ret:
              df = detections
              df = df[['Face.bbox', 'gendercnn.label']][df['tiktok.id'] == frame_id]
              
              if df.size:
                  for bbox, label in df.values:
                      x1, y1, x2, y2 = bbox
                      x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                      img=cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness) # object bbox
                      cv2.putText(img, str(label), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, thickness-1) # object label
                  video.write(img)

              frame_id+=1
              ret, frame = vcap.read()

          video.release()
          vcap.release()

.. container:: cell code

   .. code:: python

      #!pip install ipywidgets
      from ipywidgets import Video
      input_path = 'short2.mp4'
      output_path = 'annotated_short2.mp4'
      annotate_video(response.batch.frames, input_path, output_path)
      Video.from_file(output_path)
