# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Obtained from the official API documentation
from requests_html import HTML

col_id = ["id", int]		        # The item's unique id
col_deleted = ["deleted", bool]		# True if the item is deleted
col_type = ["type", str]		# The type of item. One of "job", "story", "comment", "poll" or "pollopt"
col_by = ["by", str]	                # The username of the item's author 
col_time = ["time", int] 	        # Creation date of the item, in Unix Time
col_text = ["text", HTML] 	        # The comment, story or poll text in HTML
col_dead = ["dead", bool]	        # True if the item is dead 
col_parent = ["parent", int]		# The comment's parent: either another comment or the relevant story 
col_poll = ["poll", int]	        # The pollopt's associated poll
col_kids = ["kids", list]	        # The ids of the item's comments, in ranked display order 
col_url = ["url", str]		        # The URL of the story 
col_score = ["score", int]	        # The story's score, or the votes for a pollopt 
col_title = ["title", HTML] 		# The title of the story, poll or job in HTML
col_parts = ["parts", list] 		# A list of related pollopts, in display order
col_descendants = ["descendants", list] # In the case of stories or polls, the total comment count
col_user_id = ["id", str] 	        # The user's unique username. Case-sensitive
col_created = ["created", int]	        # Creation date of the user, in Unix Time
col_karma = ["karma", int]	        # The user's karma
col_about = ["about", HTML]	        # The user's optional self-description in HTML
col_submitted = ["submitted", list]     # List of the user's stories, polls and comments
col_items = ["items", list]	        # List of item ids
col_profiles = ["profiles", list]       # List of profile names

