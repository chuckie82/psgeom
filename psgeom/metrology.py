

"""
metrology.py

code for interpreting CSPAD, and hopefully later ePix, optical metrologies
generated by the detector group at LCLS
"""

import numpy as np


def _read_metrology(self, metrology_file):
    """
    Parse a flat text file containing a metrology. We assume the metrology
    is of the form:
    
    # quad 0
    1 x1 y1 z1
    2 x2 y2 z2
    3 ...
    
    # quad 1
    1 x1 y1 z1
    2 x2 y2 z2
    3 ...
    
    ...
    
    """
    
    # read the metrology and discard the first col
    met = np.genfromtxt(metrology_file)[:,1:]
    
    if not met.shape == (32*4, 3):
        raise IOError('metrology file appears to be in the wrong format... '
                      'could not understand file format of: %s' % metrology_file)
    
    quad_metrologies = np.array( np.vsplit(met, 4) )
    return quad_metrologies

    
def _qc_angle(self, v, w, two_by_one_index, tol=0.148):
    """
    Perform a quality control check on the angle between two basis vectors.
    
    A note on the `tol` value:
    
    The longest 2x1 side is 388 pixels long. Therefore to achive single
    pixel accuracy in the metrology, the angle between the two 2x1 sides
    should be less than
    
        theta = | arctan( 1 pixel / 388 pixels ) - pi / 2 |
    
    which is ~0.0026 rad = 0.148 and this is what we've
    set the tolerance to for now.
    """
    
    # compute the angle between the vectors
    value = np.degrees( np.arcsin(np.dot(v, w) / ( np.linalg.norm(v) * np.linalg.norm(w) ) ))
    
    if not np.abs(value) <= tol:
        if self.verbose:
            print "WARNING: Metrology quality control failed for 2x1: %d" % two_by_one_index
            print '--> s/f vectors are not orthogonal :: enforcing orthogonality!'
            print "    Angle: %f // tol: %f" % (value, tol)
        passed = False
    else:
        passed = True
        
    return passed


def _twobyone_to_bg(self, quad_metrology, quad_index, two_by_one_index):
    """
    Convert a 2x1 in the optical metrology into two basis grid elements.

    Parameters
    ----------
    quad_metrology : np.ndarray, float
        A 32 x 3 array of the corner positions of each 2x1 on the quad.

    two_by_one_index : int
        The index of the 2x1 to check out.
        
    Optional Parameters
    -------------------
    tol : float
        The tolerance for a quality control assessment that is performed on
        the optical measurement, including checking things that should be
        orthogonal are, distances are correct, etc. The float `tol` can be
        interpreted as a tolerane for error for each of these in units of
        mm.
        
    Returns
    -------
    bgs : tuple
        A 2-tuple of (p,s,f,shape) for each ASIC in the two by one.
    """

    if not quad_metrology.shape == (32,3):
        raise ValueError('Invalid quad_metrology, must be shape (32,3), got: %s' % str(quad_metrology.shape))
    

    # below is the sequence in which each 2x1 is optically measured, and
    # thus this sequence is read out of the metrology
                
    scan_sequence = np.array([1,0,3,2,4,5,7,6])
        
    shape = (185, 194) # always the same, for each ASIC

    # rip out the correct corner positions for the 2x1 we want
    i = int(np.where( scan_sequence == two_by_one_index )[0]) * 4
    xyz_2x1 = quad_metrology[i:i+4,:] # the four corners of the 2x1

    
    # The metrology is for sensor points that are actually *outside* the
    # physical ASIC chip. To account for this, we apply a `p_offset`,
    # which effectively centers the ASIC between these measured points.
    # Practically, we take the average center of each side of the rectangle
    # measured in the metrology
    
    # 0.10992 mm : pixel size
    # 0.27480 mm : gap between ASICS in a 2x1
    
    fl = 2 * 194 * 0.10992 + 0.27480  # length of the long side of a 2x1
    sl = 185 * 0.10992                # length of the short side of a 2x1
    h  = np.sqrt( fl*fl + sl*sl )     # length of hypothenuse of an ASIC

    # Next, we build a basis grid representation of each 2x1, which consists
    # of two individual ASICS. Each ASIC has an "origin" which denotes the
    # position of the first pixel in memory -- this is denoted p0 for the 
    # first ASIC and p1 for the second. The values "s" and "f" define the
    # grid of pixels along the slow and fast scan directions (here, short
    # and long sizes) of the 2x1 respectively.
    
    # The s/f vectors are computed by averaging the vectors that define each
    # side in the optical measurement.
    
    # The p vector is measured based on placing a point the correct distance
    # along the diagonal between two measured points. This is checked for
    # correctness by ensuring that the diagonal used is orthogonal to the
    # other 2x1 diagonal measured
    
    # NOTE : later, we swap x to reach CXI convention -- this is done after
    #        we position the quads in _generate_positional_basis()
    
    if two_by_one_index in [0,1]:

        s = 0.10992 * self._unit( (xyz_2x1[0,:] - xyz_2x1[1,:]) +
                                  (xyz_2x1[3,:] - xyz_2x1[2,:]) )
        f = 0.10992 * self._unit( (xyz_2x1[2,:] - xyz_2x1[1,:]) +
                                  (xyz_2x1[3,:] - xyz_2x1[0,:]) )
        
        diagonal = (xyz_2x1[3,:] - xyz_2x1[1,:]) / 1000.
        r = xyz_2x1[1,:] / 1000.
        

    elif two_by_one_index in [2,3,6,7]:

        s = 0.10992 * self._unit( (xyz_2x1[1,:] - xyz_2x1[2,:]) +
                                  (xyz_2x1[0,:] - xyz_2x1[3,:]) )
        f = 0.10992 * self._unit( (xyz_2x1[3,:] - xyz_2x1[2,:]) + 
                                  (xyz_2x1[0,:] - xyz_2x1[1,:]) )
                                  
        diagonal = (xyz_2x1[0,:] - xyz_2x1[2,:]) / 1000.
        r = xyz_2x1[2,:] / 1000.


    elif two_by_one_index in [4,5]:

        s = 0.10992 * self._unit( (xyz_2x1[2,:] - xyz_2x1[3,:]) +
                                  (xyz_2x1[1,:] - xyz_2x1[0,:]) )
        f = 0.10992 * self._unit( (xyz_2x1[0,:] - xyz_2x1[3,:]) +
                                  (xyz_2x1[1,:] - xyz_2x1[2,:]) )

        diagonal = (xyz_2x1[1,:] - xyz_2x1[3,:]) / 1000.
        r = xyz_2x1[3,:] / 1000.
        

    else:
        raise ValueError('two_by_one_index must be in 0...7')
        
    center = np.mean(xyz_2x1, axis=0) / 1000.
    offset = (np.linalg.norm(diagonal) - h) / 2. # this is a magnitude
    p0 = r + offset * self._unit(diagonal)
    p1 = p0 + shape[1] * f + 0.27480 * self._unit(f) # for 3px gap
        
        
    # --- perform some quality control checks ---
            
    # (1) ensure s/f orthogonal
    
    self._qc_angle(s, f, two_by_one_index)
    
    # --- end QC ---------------------------------
    
    
    # no matter what, correct the s/f vectors so they are orthogonal
    axis = np.cross(s, f)

    # the angle between s/f
    theta = np.arccos(np.dot(s, f) / ( np.linalg.norm(s) * np.linalg.norm(f) ))
    rot = ((np.pi / 2.0) - theta) / 2.0
    
    # rotate each vector -- below `rot` is deg ccw wrt x-axis in the ref
    # frame of '+axis'
    Rs = utils.ER_rotation_matrix(axis,  rot)
    Rf = utils.ER_rotation_matrix(axis, -rot)
    
    s = np.dot(Rs, s)
    f = np.dot(Rf, f)
    
    assert np.abs( np.dot(s, f) ) < 1e-10
    
    # return a tuple of basis grid objects
    bgs = ( (p0.copy(), s.copy(), f.copy(), shape), 
            (p1.copy(), s.copy(), f.copy(), shape) )
    
    return bgs
    