import sys
import avb

def use_item(item:avb.bin.BinItem) -> bool:

	return item.user_placed

if __name__ == "__main__":

	if not len(sys.argv) > 1:
	
		import pathlib
		sys.exit(f"Usage: {pathlib.Path(__file__).name} bin_path.avb")
	
	print("Opening ", sys.argv[1])

	with avb.open(sys.argv[1]) as bin_handle:

		bin_content = bin_handle.content
		frame_scale = bin_content.mac_image_scale

		print("Frame scale: ", frame_scale) # 4-14; 2-7; 1-3.5

		for bin_item in filter(use_item, bin_content.items):
			print(bin_item.x, "\t", bin_item.y, "\t", bin_item.mob.name)
