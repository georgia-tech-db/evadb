Hacker News
==========

Dependency
----------

* Requests-HTML

Parameters
----------

Optional:

* ``maxitem`` stablishes a limit on how many rows to get for the users and the items table. If this argument is ommited, the maximum number of rows will be set to the number obtained from the official API `max_items <https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty>`. It is important to highlight that the number provided by the API is big and queries will take a long time to execute.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE hacker_news_data WITH ENGINE = 'hackernews', PARAMETERS = {
        "maxitem": "500"
   };

Supported Tables
----------------

* ``items``: Contains information about individual items on HackerNews, such as posts, comments, and other content. Each row represents a unique item with attributes like ID, type, author, timestamp, text, URL, score, title, and more.

* ``users``: Stores details about HackerNews users, including their ID, registration date, karma, about information, and a list of submitted items. Each row corresponds to a unique user on the platform.

* ``top_stories``: Consists of IDs referencing the top stories on HackerNews. Use this table to retrieve a list of top stories and then fetch detailed information from the ``items`` table.

* ``new_stories``: Similar to ``top_stories``, this table contains IDs of the newest stories on HackerNews. Retrieve the latest stories and their details using the ``items`` table.

* ``best_stories``: Stores IDs of the best-rated stories on HackerNews. Retrieve detailed information about these stories from the ``items`` table.

* ``ask_stories``: Contains IDs of stories categorized as "Ask HN." Fetch additional details about these stories using the ``items`` table.

* ``show_stories``: Holds IDs of stories categorized as "Show HN." Retrieve more information about these stories from the ``items`` table.

* ``job_stories``: Includes IDs of job-related stories on HackerNews. Obtain additional details about these job stories using the ``items`` table.

* ``updates``: Provides information about updates on HackerNews, including the number of new items and new profiles. Use this table to monitor changes and updates on the platform.

.. code-block:: sql

   SELECT * FROM hacker_news_data.top_stories;

Here is the query output:

.. code-block:: 

    +----+-----------------+-----+-----------------------------------------------+--------+
    |    | by              | ... | title                                         | type   |
    |----+-----------------|-----|-----------------------------------------------+--------|
    |  0 | gdss            | ... | SUQL: Conversational Search over Structure... | story  |
    |  1 | catskull        | ... | Insomnia REST client updated to require si... | story  |
    |  2 | meitros         | ... | OpenAI's employees were given two explanat... | story  |
    |  3 | WhereIsTheTruth | ... | Argentina sanctions UK/Israeli companies: ... | story  |
    |  4 | mihaitodor      | ... | Parkinson's Progression Halted by Inhibiti... | story  |
    |  5 | Prontoapp       | ... | Show HN: I created an app to help friends ... | story  |
    |  6 | soopurman       | ... | A City on Mars: Reality kills space settle... | story  |
    |  7 | positivesumsum  | ... | Stop Reading the News                         | story  |
    |  8 | lifeisstillgood | ... | UK Covid inquiry: no countries political l... | story  |
    |  9 | impish9208      | ... | We Now Need College Courses to Teach Young... | story  |
    +----+-----------------+-----+-----------------------------------------------+--------+

