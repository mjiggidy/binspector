"""
Just thinkin' bout project details here
"""

from __future__ import annotations
import sys, pathlib, dataclasses, typing
from os import PathLike

def mount_point_from_path(file_path:PathLike) -> pathlib.Path:

	file_path = pathlib.Path(file_path)

	if not file_path.exists():
		raise ValueError(f"Path does not exist: {file_path}", file=sys.stderr)
	
	test_path = file_path if file_path.is_dir() else file_path.parent

	while not test_path.is_mount():
		test_path = test_path.parent
	
	return test_path.resolve()


@dataclasses.dataclass(frozen=True)
class BSAvidProjectInfo:

	name             :str
	base_project_dir :pathlib.Path
	base_attic_dir   :pathlib.Path|None = None

	@classmethod
	def from_avp(cls, path_avp:PathLike) -> typing.Self:

		path_avp = pathlib.Path(path_avp)
		if not path_avp.suffix.lower() == ".avp":
			raise ValueError(f"Must be a .avp file (got {path_avp})")
		
		project_name = path_avp.stem
		base_project_dir = path_avp.parent.resolve()

		base_attic_dir = pathlib.Path(mount_point_from_path(path_avp)) / "Unity Attic" / project_name
		base_attic_dir = base_attic_dir.resolve() if base_attic_dir.is_dir() else None

		project_path = path_avp.resolve()
		

		return cls(
			name = project_name,
			project_file_path = project_path,
			base_project_dir = base_project_dir,
			base_attic_dir = base_attic_dir
		)

def avp_path_from_avb_path(avb_path:PathLike) -> pathlib.Path|None:

	test_dir = pathlib.Path(avb_path).parent

	while True:

		test_paths = list(filter(lambda p: not p.stem.startswith("."), test_dir.glob("*.avp", case_sensitive=True)))
		print(test_dir, test_paths)

		if len(test_paths) == 1:
			return test_paths[0]
		
		if test_dir.is_mount():
			break
		
		test_dir = test_dir.parent

	return None

def main(bin_paths:list[PathLike]):

	for avb_path in bin_paths:

		if not pathlib.Path(avb_path).is_file():
			print("Skip ", avb_path, ": Not a file", file=sys.stderr)
			continue

		avp_path = avp_path_from_avb_path(avb_path)

		if avp_path:
			print(BSAvidProjectInfo.from_avp(avp_path))
		else:
			print("Nope")

if __name__ == "__main__":

	if not len(sys.argv) > 1:	
		sys.exit(f"Usage: {pathlib.Path(__file__).name} avid_bin.avb")
	
	main(sys.argv[1:])