
import imp

window_helper = imp.load_source('window_helper','window_helper.py')

window_helper.make_window(centerpoint=(-5,-3,0),diameter=2)
window_helper.make_window(centerpoint=(4,-3,0),diameter=1)

window_helper.make_window("w3",centerpoint=(0,3,0),diameter=3)