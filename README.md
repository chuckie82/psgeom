# psgeom

Python code for detector geometries, supporting translation between different programs, easy manipulation of the geometry, and access to the real-space coordinates of pixels. Currently we support interfaces to:

* psana
* CrystFEL
* cheetah

An interfact to cctbx.xfel is planned.

Developers Note:

This code is hot off the press. That said, things seem to be working as of 7/10/15. Fire away! Check out the test.py file if you want to see how the implementation is verified.

TJ Lane <tjlane@slac.stanford.edu>

------

** Set up **

Psgeom is a pure python library which can be set up in 3 simple steps:
1) Get a copy from psgeom github
git clone https://github.com/LinacCoherentLightSource/psgeom.git
2) Create your virtual environment
virtualenv psgeom
source psgeom/bin/activate
3) Install
python setup.up install

------

** Example **

Here's a quick example of how to use this code. Imagine I have a geometry file
on the psana machines `1-end.data` that I want to load and manipulate. You can
find an example of such a file in the `ref_files` directory in this repo.

Then,

```
from psgeom import camera

cspad = camera.Cspad.from_psana_file('1-end.data')
print cspad.draw_tree()     # see the heirarchy of sensors
print cspad.xyz             # get the xyz coordinates of all pixels

cspad.to_cheetah_file('my_new_cheetah_geom.h5')
```

-------

*** Documentation ***

Information about the psana geometry:
https://confluence.slac.stanford.edu/display/PSDM/Detector+Geometry

List of high quality geometries generated by users and optical metrologies generated by LCLS:
https://confluence.slac.stanford.edu/display/PSDM/Geometry+History

CrystFEL Geometry:
http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html

--------

Functionality left to add:
* documentation, some is there, but more is good.
* smart ways to visualize the geometry and intensities
* additional sensor elements
* If requested, legacy interface to mimic PSCalib
* think: dynamically expose leaf properties to parents
* think: should mask be included


