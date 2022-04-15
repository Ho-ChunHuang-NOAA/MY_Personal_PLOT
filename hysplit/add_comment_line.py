## from mpl_toolkits.basemap import Basemap
import os

fin="color_marker.list"
if os.path.exists( fin ):
    print(fin+" exists")
    f = open (fin, "r")
    fout = open ( "add1", "w" )
    for x in f:
        comm="## "+x
        fout.write(comm)
    f.close()
    fout.close()
else:
    print("can not find "+fin)
