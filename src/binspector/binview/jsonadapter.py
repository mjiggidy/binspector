
from __future__ import annotations
import json
from . import binviewitemtypes

CURRENT_VERSION = "1.0"

class BSBinViewJsonAdapter:
	"""JSON Importer/Exporter for a binview"""

	@staticmethod
	def to_json(binview_info:binviewitemtypes.BSBinViewInfo) -> str:
		"""Return a JSON-formatted string  representing a given `BSBinViewInfo`"""

		return json.dumps({
			"name": binview_info.name,
			"version": CURRENT_VERSION,
			"columns": [h.to_json_dict() for h in binview_info.columns]
		}, indent="\t")
	
	@staticmethod
	def from_json(json_string:str) -> binviewitemtypes.BSBinViewInfo:
		"""Return a `BSBinViewInfo` object from a given binview JSON string"""

		binview_parsed = json.loads(json_string)

		if binview_parsed.get("version") != CURRENT_VERSION:
			raise ValueError("Unsupported binview json version")
		
		return binviewitemtypes.BSBinViewInfo(
			name    = binview_parsed.get("name", "NoName"),
			columns = [BSBinViewJsonAdapter._column_from_json(col) for col in binview_parsed.get("columns",[])]
		)
		
	@staticmethod
	def _column_from_json(column_json:str) -> binviewitemtypes.BSBinViewColumnInfo:
		"""Column info from JSON string"""

		import avbutils

		return binviewitemtypes.BSBinViewColumnInfo(
			field_id     = avbutils.bins.BinColumnFieldIDs[column_json["field_id"]],
			format_id    = avbutils.bins.BinColumnFormat[column_json["format_id"]],
			display_name = column_json["display_name"],
			is_hidden    = bool(column_json["is_hidden"])
		)