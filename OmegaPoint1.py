import textwrap
import ChatBot
import OmegaPoint
from importlib import reload
reload(ChatBot)
reload(OmegaPoint)

role_user = "Experienced User Researcher"
aim = "Provide an analysis of the interviews,"
information = """
Different interviews are labeled using the ### symbols.
### Interview with Thomas
I dislike Cola. I am politically on the left.
### Interview with Edward
I like Cola. I am politically on the right.
### Interview with Mary
I dislike Cola. I am politically on the left.
I have a visual impairment.
### Interview with John
I dislike Cola. I am politically on the right.
I have a visual impairment.
### Interview with Karen
I like Pepsi. I am politically on the right.
I have no disabilities.
"""
min_iterations = 2
max_iterations = 4

O = OmegaPoint.OmegaPoint(role_user, aim, information, min_iterations, max_iterations)
output, History = O.run()
