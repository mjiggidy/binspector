from __future__ import annotations
import enum, typing

if typing.TYPE_CHECKING:
	import avb

class BSSiftMatchTypes(enum.IntEnum):
	"""How to match text for sifting"""

	# NOTE: SiftItems are listed in reverse order

	Contains       = 1
	"""Column contains a given string"""

	BeginsWith     = 2
	"""Column begins with a given string"""
 
	MatchesExactly = 3
	"""Column matches exactly a given string"""

	@classmethod
	def from_sift_item(cls, sift_item:avb.bin.SiftItem) -> typing.Self:
		"""Lookup the sift method based on the method `int`"""

		return cls(sift_item.method)