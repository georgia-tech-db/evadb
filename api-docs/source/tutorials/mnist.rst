Working with mnist data tutorial
================================

.. container:: cell markdown

   run this notebook on `google
   colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/mnist.ipynb>`__

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

.. container:: cell code

   .. code:: python

      cursor = connection.cursor()

.. container:: cell markdown

   .. rubric:: Upload the survellience video to analyse
      :name: upload-the-survellience-video-to-analyse

.. container:: cell code

   .. code:: python

      cursor.execute('LOAD FILE "data/mnist/mnist.mp4" INTO MNISTVid')
      response = cursor.fetch_all()

.. container:: cell markdown

   .. rubric:: Visualize Video
      :name: visualize-video

.. container:: cell code

   .. code:: python

      from IPython.display import Video
      Video("../data/mnist/mnist.mp4", embed=True)

.. container:: cell markdown

   .. rubric:: Load video into EVA
      :name: load-video-into-eva

.. container:: cell code

   .. code:: python

      cursor.execute("""CREATE UDF IF NOT EXISTS MnistCNN
                        INPUT  (data NDARRAY (3, 28, 28))
                        OUTPUT (label TEXT(2))
                        TYPE  Classification
                        IMPL  'tutorials/apps/mnist/eva_mnist_udf.py';
              """)
      response = cursor.fetch_all()
      print(response)

   .. container:: output stream stdout

      ::

         @status: 0
         @batch: Batch Object:
         @dataframe:                                                   0
         0  UDF MnistCNN successfully added to the database.
         @batch_size: 1
         @identifier_column: None
         @query_time: 0.0354332719980448

.. container:: cell markdown

   .. rubric:: Run Object detector on the video
      :name: run-object-detector-on-the-video

.. container:: cell code

   .. code:: python

      cursor.execute("""SELECT data, MnistCNN(data).label FROM MNISTVid""")
      response = cursor.fetch_all()
      print(response)

   .. container:: output stream stdout

      ::

         @status: 0
         @batch: Batch Object:
         @dataframe:                                           mnistvid.data  mnistcnn.label
         0     [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...               6
         1     [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...               6
         2     [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...               6
         3     [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...               6
         4     [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...               6
         ...                                                 ...             ...
         1195  [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], ...               6
         1196  [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], ...               6
         1197  [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], ...               6
         1198  [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], ...               6
         1199  [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], ...               6

         [1200 rows x 2 columns]
         @batch_size: 1200
         @identifier_column: None
         @query_time: 2.1762317229986365

.. container:: cell markdown

   .. rubric:: Visualize output of Mnist on the video
      :name: visualize-output-of-mnist-on-the-video

.. container:: cell code

   .. code:: python

      # !pip install matplotlib
      import matplotlib.pyplot as plt
      import numpy as np

      # create figure (fig), and array of axes (ax)
      fig, ax = plt.subplots(nrows=5, ncols=5, figsize=[6,8])

      df = response.batch.frames
      for axi in ax.flat:
          idx = np.random.randint(len(df))
          img = df['mnistvid.data'].iloc[idx]
          label = df['mnistcnn.label'].iloc[idx]
          axi.imshow(img)
          
          axi.set_title(f'label: {label}')

      plt.show()

   .. container:: output display_data

      .. image:: assests/ff77c302d89f3534fa0ce208db38992276194896.png

.. container:: cell code

   .. code:: python
