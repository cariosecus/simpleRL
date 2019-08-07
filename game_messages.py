import tcod as libtcod
import textwrap
from collections import deque


class Message:
	def __init__(self, text, color=libtcod.white):
		self.text = text
		self.color = color

	def __repr__(self):
		return f"Message('{self.text}', color = {self.color})"


# TODO: rewrite using bounded deque object instead of list
class MessageLog:
	def __init__(self, x, width, height, length):
		self.messages = deque([], length)
		self.x = x
		self.width = width
		if length < height:
			self.height = length
		else:
			self.height = height
		self.length = length
		self.bottom = 0
		# pre-load empty messages so it doesn't crash
		# I don't like this but it's an easy fix
		for _ in range(0, self.height):
			self.messages.appendleft(Message('', libtcod.white))

	def add_message(self, message):
		new_msg_lines = textwrap.wrap(message.text, self.width)
		for line in new_msg_lines:
			self.messages.appendleft(Message(line, message.color))

	def scroll(self, num):
		new_bottom = self.bottom + num
		if new_bottom >= 0 and new_bottom < len(self.messages) - self.height:
			self.bottom = new_bottom

	def __repr__(self):
		return f"MessageLog({self.x}, {self.width}, {self.height})"
