import sys
from blur import Blur
from equalised_histogram import Equalised_Histogram
from grayscale import Grayscale
from laplacian import Laplacian
from scharr import ScharrX, ScharrY
from sobel import SobelX, SobelY
from scipy import misc
import matplotlib.pyplot as plt
supported_filters = {"blur": Blur(), 
					"equalised_histogram": Equalised_Histogram(), 
					"grayscale": Grayscale(), 
					"laplacian": Laplacian(), 
					"scharr": ScharrX(), 
					"sobel": SobelX(),
					}
def get_help():
	print("--- Filters supported ---")
	print("blur")
	print("equalised_histogram")
	print("grayscale")
	print("laplacian")
	print("scharr")
	print("sobel")
	print("\n")
	print("--- Usage ---")
	print("python run_operations.py \
		--fiter_name='filter_name' --image='image_name/images_path'")

if __name__ == "__main__":

	args = sys.argv[1:]
	print(args)
	frames = []
	for arg in args:
		if arg == "--help":
			get_help()
		# try:
		key = arg.split("=")[0]
		val = arg.split("=")[1]

		if key == "--filter_name": 
			if val not in supported_filters.keys():
				get_help()
			else:
				filter = supported_filters[val]
				print(filter)

		if key == "--image":
			
			frame = misc.imread(val)
			frames.append(frame)
		# except:
		# 	get_help()
	try:
		# print("Shubham")
		frames = filter.apply(frames)
		frame = frames[0]
		fig=plt.figure()
		plt.imshow(frame)
		plt.show()
	except Exception as e:
		print(e)
		get_help()