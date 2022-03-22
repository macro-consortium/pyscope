"""
Basic test for talking to TheSkyX ImageLink routine
"""

from win32com.client import Dispatch
from win32com.client.gencache import EnsureDispatch

#imagePath = r"C:\Users\kmi\Desktop\testimages\ra1dec10\NorthDownEastRight.fit"
imagePath = r"C:\Users\kmi\Desktop\testimages\ra2dec20.fit"
scale = 0.63

imagelink = EnsureDispatch("TheSkyX.ImageLink")
imagelinkresults = EnsureDispatch("TheSkyX.ImageLinkResults")

image = EnsureDispatch("TheSkyX.ccdsoftImage")
image.Path = imagePath
image.Open()

#imagelink.pathToFITS = imagePath
#imagelink.scale = scale
#imagelink.unknownScale = False

#imagelink.execute()

#print imagelinkresults.succeeded, imagelinkresults.imageScale