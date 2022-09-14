Object Detection tutorial
=========================

.. container:: cell markdown

   .. rubric:: Object detection tutorial
      :name: object-detection-tutorial

   run this notebook on `google
   colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/object_detection.ipynb>`__

.. container:: cell markdown

   .. rubric:: Launch EVA DB
      :name: launch-eva-db

   Run the command ``python eva.py`` in the server where you want to
   deploy EVA

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

.. container:: cell code

   .. code:: python

      cursor = connection.cursor()
      cursor

   .. container:: output execute_result

      ::

         <eva.server.db_api.EVACursor at 0x7fc9e6fd7490>

.. container:: cell markdown

   .. rubric:: Upload the survellience video to analyse
      :name: upload-the-survellience-video-to-analyse

.. container:: cell code

   .. code:: python

      cursor.execute('LOAD FILE "data/ua_detrac/ua_detrac.mp4" INTO ObjVidTst3;')
      response = cursor.fetch_all()
      print(response)

   .. container:: output stream stdout

      ::

         @status: 0
         @batch: Batch Object:
         @dataframe:                                                    0
         0  Video successfully added at location: data/ua_...
         @batch_size: 1
         @identifier_column: None
         @query_time: 0.03165829399949871

.. container:: cell markdown

   .. rubric:: Visualize Video
      :name: visualize-video

.. container:: cell code

   .. code:: python

      from ipywidgets import Video
      Video.from_file("../data/ua_detrac/ua_detrac.mp4", embed=True)

   .. container:: output execute_result

      .. code:: json

         {"version_major":2,"version_minor":0,"model_id":"26b472c03faf467d96ea5a1a215e91fd"}

.. container:: cell markdown

   .. rubric:: Optional - Register FasterRCNN (object detection) model
      into EVA
      :name: optional---register-fasterrcnn-object-detection-model-into-eva

   .. rubric:: Syntax
      :name: syntax

   ``CREATE UDF [ IF NOT EXISTS ] <name>        INPUT  ( [ <arg_name> <arg_data_type> ] [ , ... ] )       OUTPUT ( [ <result_name> <result_data_type> ] [ , ... ] )       TYPE  <udf_type_name>       IMPL  '<path_to_implementation>'``

   .. rubric:: Required Parameters
      :name: required-parameters

   ``<name>`` - specifies the unique identifier for the UDF.

   ``[ <arg_name> <arg_data_type> ] [ , ... ]`` - specifies the name and
   data type of the udf input arguments. Name is kept for consistency
   (ignored by eva right now), arguments data type is required.
   ``ANYDIM`` means the shape is inferred at runtime.

   ``[ <result_name> <result_data_type> ] [ , ... ]`` - specifies the
   name and data type of the udf output arguments. Users can access a
   specific output of the UDF similar to access a column of a table. Eg.
   ``<name>.<result_name>``

   ``<udf_type_name>`` - specifies the identifier for the type of the
   UDF. UDFs of the same type are assumed to be interchangeable. They
   should all have identical input and output arguments. For example,
   object classification can be one type.

   ``<path_to_implementation>`` - specifies the path to the
   implementation class for the UDF

.. container:: cell code

   .. code:: python

      cursor.execute("""CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
            INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
            OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                      scores NDARRAY FLOAT32(ANYDIM))
            TYPE  Classification
            IMPL  'src/udfs/fastrcnn_object_detector.py';
            """)
      response = cursor.fetch_all()
      print(response)

   .. container:: output stream stdout

      ::

         @status: 0
         @batch: Batch Object:
         @dataframe:                                                    0
         0  UDF FastRCNNObjectDetector already exists, not...
         @batch_size: 1
         @identifier_column: None
         @query_time: 0.007647731001270586

.. container:: cell markdown

   .. rubric:: Run Object detector on the video
      :name: run-object-detector-on-the-video

.. container:: cell code

   .. code:: python

      cursor.execute("""SELECT id, FastRCNNObjectDetector(data) FROM ObjVidTst3 where id<5""")
      response = cursor.fetch_all()

.. container:: cell markdown

   .. rubric:: Visualize output of Object detector on the video
      :name: visualize-output-of-object-detector-on-the-video

.. container:: cell code

   .. code:: python

      print(response)

   .. container:: output stream stdout

      ::

         @status: 0
         @batch: Batch Object:
         @dataframe:    objvidtst3.id                      fastrcnnobjectdetector.labels  \
         0              0  [person, car, car, car, car, car, car, car, ca...   
         1              1  [person, car, car, car, car, car, car, car, ca...   
         2              2  [person, car, car, car, car, car, car, car, ca...   
         3              3  [person, car, car, car, car, car, car, car, ca...   
         4              4  [person, car, car, car, car, car, car, car, ca...   

                                fastrcnnobjectdetector.bboxes  \
         0  [[636.24609375, 363.6267700195, 670.9285888672...   
         1  [[636.348815918, 364.4110412598, 671.456970214...   
         2  [[636.6950683594, 367.780670166, 671.499389648...   
         3  [[637.3386230469, 370.0677490234, 671.13787841...   
         4  [[637.3938598633, 371.9588928223, 671.40667724...   

                                fastrcnnobjectdetector.scores  
         0  [0.9973133206, 0.9954667091, 0.9945367575, 0.9...  
         1  [0.9986808896, 0.9966157079000001, 0.994604766...  
         2  [0.9988935590000001, 0.9963032007, 0.994643449...  
         3  [0.9984733462000001, 0.9947209358, 0.993759810...  
         4  [0.9979975820000001, 0.9953624606, 0.994491815...  
         @batch_size: 5
         @identifier_column: None
         @query_time: 14.30591533400002

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
          fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') #codec
          video=cv2.VideoWriter(output_video_path, fourcc, fps, (width,height))

          frame_id = 0
          # Capture frame-by-frame
          ret, frame = vcap.read()  # ret = 1 if the video is captured; frame is the image

          while ret:
              df = detections
              df = df[['fastrcnnobjectdetector.bboxes', 'fastrcnnobjectdetector.labels']][df.index == frame_id]
              if df.size:
                  dfLst = df.values.tolist()
                  for bbox, label in zip(dfLst[0][0], dfLst[0][1]):
                      x1, y1, x2, y2 = bbox
                      #print(bbox[0], label)
                      #x2, y2 = bbox[1]
                      x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                      img=cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness) # object bbox
                      cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, thickness-1) # object label
                  video.write(img)

              frame_id+=1
              ret, frame = vcap.read()

          video.release()
          vcap.release()

.. container:: cell code

   .. code:: python

      from ipywidgets import Video
      input_path = '../data/ua_detrac/ua_detrac.mp4'
      output_path = 'video.mp4'
      annotate_video(response.batch.frames, input_path, output_path)
      Video.from_file(output_path)

   .. container:: output execute_result

      .. code:: json

         {"version_major":2,"version_minor":0,"model_id":"490e3e6887ac4d90b174a9741019fb39"}

.. container:: cell code

   .. code:: python
