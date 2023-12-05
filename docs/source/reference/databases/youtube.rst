YouTube
==========

The connection to YouTube is based on the `YouTube Data API <https://developers.google.com/youtube/v3>`_.

Dependency
----------

* pytube


Parameters
----------

Required:

* ``youtube_token`` is your API key. Instructions for obtaining this key can be found `here <https://developers.google.com/youtube/v3/getting-started>`_.

Optional:

* ``youtube_urls`` is a comma separated list of YouTube URLs. The pytube package is used to parse different YouTube URL formats.

* ``search_query`` is the query you are searching for. Your request can use the Boolean NOT (-) and OR (|) operators to exclude or find videos associated with several search terms. Note that the pipe character must be URL-escaped with %7C.
* ``max_results`` the maximum number of items that should be returned in the result set. Acceptable values are 0 to 50, inclusive. The default value is 5.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE youtube_data WITH ENGINE = 'youtube', PARAMETERS = {
        "youtube_token": <INSERT API KEY>,
        "youtube_urls": "https://www.youtube.com/watch?v=7__r4FVj-EI, https://youtu.be/BYVZh5kqaFg"
   };

or

.. code-block:: text

   CREATE DATABASE youtube_data WITH ENGINE = 'youtube', PARAMETERS = {
        "youtube_token": <INSERT API KEY>,
        "search_query": "evadb",
        "max_results": 3
   };

Supported Tables
----------------

* ``snippet``: Contains information such as the time the YouTube video was published, the video title, the description, the channel name and id, thumbnails, tags, and categories.

.. code-block:: sql

   SELECT * FROM youtube_data.snippet

* ``statistics``: Contains the view count, like count, favorite count, and comment count.

.. code-block:: sql

   SELECT * FROM youtube_data.statistics

.. note::

   Looking for another table from Hackernews? Please raise a `Feature Request <https://github.com/georgia-tech-db/evadb/issues/new/choose>`_.
