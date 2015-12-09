# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- http://www.MDAnalysis.org
# Copyright (c) 2006-2015 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver Beckstein
# and contributors (see AUTHORS for the full list)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

"""
Topology attribute objects --- :mod:`MDAnalysis.core.topologyattrs'
===================================================================

Common TopologyAttrs used by most topology parsers.

"""
from collections import defaultdict
import itertools
import numpy as np

from ..lib.util import cached
from ..exceptions import NoDataError
from .topologyobjects import TopologyGroup

class TopologyAttr(object):
    """Base class for Topology attributes.

    .. note::   This class is intended to be subclassed, and mostly amounts to a
                skeleton. The methods here should be present in all
                :class:`TopologyAttr` child classes, but by default they raise
                appropriate exceptions.

    Attributes
    ----------
    attrname : str
        the name used for the attribute when attached to a ``Topology`` object
    top : Topology
        handle for the Topology object TopologyAttr is associated with
        
    """
    attrname = 'topologyattrs'
    singular = 'topologyattr'
    top = None

    def __init__(self, values):
        self.values = values

    def __len__(self):
        """Length of the TopologyAttr at its intrinsic level."""
        return len(self.values)

    def __getitem__(self, group):
        """Accepts an AtomGroup, ResidueGroup or SegmentGroup"""
        if group.level == 'atom':
            return self.get_atoms(group)
        elif group.level == 'residue':
            return self.get_residues(group)
        elif group.level == 'segment':
            return self.get_segments(group)

    def __setitem__(self, group, values):
        if group.level == 'atom':
            return self.set_atoms(group, values)
        elif group.level == 'residue':
            return self.set_residues(group, values)
        elif group.level == 'segment':
            return self.set_segments(group, values)

    def get_atoms(self, ag):
        """Get atom attributes for a given AtomGroup"""
        # aix = ag.indices
        raise NoDataError

    def set_atoms(self, ag, values):
        """Set atom attributes for a given AtomGroup"""
        raise NotImplementedError

    def get_residues(self, rg):
        """Get residue attributes for a given ResidueGroup"""
        raise NoDataError

    def set_residues(self, rg, values):
        """Set residue attributes for a given ResidueGroup"""
        raise NotImplementedError

    def get_segments(self, sg):
        """Get segment attributes for a given SegmentGroup"""
        raise NoDataError

    def set_segments(self, sg, values):
        """Set segmentattributes for a given SegmentGroup"""
        raise NotImplementedError


## atom attributes

class AtomAttr(TopologyAttr):
    """Base class for atom attributes.

    """
    attrname = 'atomattrs'
    singular = 'atomattr'

    def get_atoms(self, ag):
        return self.values[ag._ix]

    def set_atoms(self, ag, values):
        self.values[ag._ix] = values

    def get_residues(self, rg):
        """By default, the values for each atom present in the set of residues
        are returned in a single array. This behavior can be overriden in child
        attributes.

        """
        aix = self.top.tt.r2a_1d(rg._ix)
        return self.values[aix]

    def get_segments(self, sg):
        """By default, the values for each atom present in the set of residues
        are returned in a single array. This behavior can be overriden in child
        attributes.

        """
        aix = self.top.tt.s2a_1d(sg._ix)
        return self.values[aix]


class Atomids(AtomAttr):
    """Interface to atomids.
    
    Parameters
    ----------
    atomids : array
        atomids for atoms in the system

    """
    attrname = 'ids'
    singular = 'id'


class Atomnames(AtomAttr):
    """Interface to atomnames.
    
    Parameters
    ----------
    atomnames : array
        atomnames for atoms in the system

    """
    attrname = 'names'
    singular = 'name'


class Atomtypes(AtomAttr):
    """Type for each atom"""
    attrname = 'types'
    singular = 'type'


#TODO: need to add cacheing
class Masses(AtomAttr):
    """Interface to masses for atoms, residues, and segments.
    
    Parameters
    ----------
    masses : array
        mass for each atom in the system

    """
    attrname = 'masses'
    singular = 'mass'

    def get_residues(self, rg):
        masses = np.empty(len(rg))

        resatoms = self.top.tt.r2a_2d(rg._ix)

        for i, row in enumerate(resatoms):
            masses[i] = self.values[row].sum()

        return masses

    def get_segments(self, sg):
        masses = np.empty(len(sg))

        segatoms = self.top.tt.s2a_2d(sg._ix)

        for i, row in enumerate(segatoms):
            masses[i] = self.values[row].sum()

        return masses


#TODO: need to add cacheing
class Charges(AtomAttr):
    """Interface to charges for atoms, residues, and segments.
    
    Parameters
    ----------
    charges : array
        charge for each atom in the system

    """
    attrname = 'charges'
    singular = 'charge'

    def get_residues(self, rg):
        charges = np.empty(len(rg))

        resatoms = self.top.tt.r2a_2d(rg._ix)

        for i, row in enumerate(resatoms):
            charges[i] = self.values[row].sum()

        return charges

    def get_segments(self, sg):
        charges = np.empty(len(sg))

        segatoms = self.top.tt.s2a_2d(sg._ix)

        for i, row in enumerate(segatoms):
            charges[i] = self.values[row].sum()

        return charges


## residue attributes

class ResidueAttr(TopologyAttr):
    """Base class for Topology attributes.

    .. note::   This class is intended to be subclassed, and mostly amounts to a
                skeleton. The methods here should be present in all
                :class:`TopologyAttr` child classes, but by default they raise
                appropriate exceptions.

    """
    attrname = 'residueattrs'
    singular = 'residueattr'

    def get_atoms(self, ag):
        rix = self.top.tt.a2r(ag._ix)
        return self.values[rix]

    def get_residues(self, rg):
        return self.values[rg._ix]

    def set_residues(self, rg, values):
        self.values[rg._ix] = values

    def get_segments(self, sg):
        """By default, the values for each residue present in the set of
        segments are returned in a single array. This behavior can be overriden
        in child attributes.

        """
        rix = self.top.tt.s2r_1d(sg._ix)
        return self.values[rix]


class Resids(ResidueAttr):
    """Interface to resids.
    
    Parameters
    ----------
    resids : array
        resids for residue in the system

    """
    attrname = 'resids'
    singular = 'resid'

    def set_atoms(self, ag, resids):
        """Set resid for each atom given. Effectively moves each atom to
        another residue.

        """
        
        rix = np.zeros(len(ag), dtype=np.int32)

        # get resindexes for each resid
        for i, item in enumerate(resids):
            try:
                rix[i] = np.where(self.values == item)[0][0]
            except IndexError:
                raise NoDataError("Cannot assign atom to a residue that doesn't already exist.")

        self.top.tt.move_atom(ag._ix, rix)


class Resnames(ResidueAttr):
    """Interface to resnames.
    
    Parameters
    ----------
    resnames : array
        resnames for residues in the system

    """
    attrname = 'resnames'
    singular = 'resname'


## segment attributes

class SegmentAttr(TopologyAttr):
    """Base class for segment attributes.

    """
    attrname = 'segmentattrs'
    singular = 'segmentattr'

    def get_atoms(self, ag):
        six = self.top.tt.a2s(ag._ix)
        return self.values[six]

    def get_residues(self, rg):
        six = self.top.tt.r2s(rg._ix)
        return self.values[six]

    def get_segments(self, sg):
        return self.values[sg._ix]

    def set_segments(self, sg, values):
        self.values[sg._ix] = values


class Segids(SegmentAttr):
    attrname = 'segids'
    singular = 'segid'


class Bonds(AtomAttr):
    """Bonds for atoms"""
    attrname = 'bonds'
    # Singular is the same because one Atom might have
    # many bonds, so still asks for "bonds" in the plural
    singular = 'bonds'

    def __init__(self, values):
        """
        Arguments
        ---------
        values - list of tuples of indices.  Should be zero based
        to match the atom indices

        Eg:  [(0, 1), (1, 2), (2, 3)]
        """
        self.values = values
        self._cache = dict()

    def __len__(self):
        return len(self._bondDict)

    @property
    @cached('bd')
    def _bondDict(self):
        """Lazily built mapping of atoms:bonds"""
        bd = defaultdict(list)

        for b in self.values:
            # We always want the first index
            # to be less than the last
            # eg (0, 1) not (1, 0)
            # and (4, 10, 8) not (8, 10, 4)
            if b[0] < b[-1]:
                b = b[::-1]
            for a in b:
                bd[a].append(b)
        return bd

    def get_atoms(self, ag):
        unique_bonds =  set(itertools.chain(
            *[self._bondDict[a] for a in ag._ix]))
        bond_idx = np.array(sorted(unique_bonds))
        return TopologyGroup(bond_idx, ag._u, self.singular[:-1])
        #return TopologyGroup(unique_bonds)


class Angles(Bonds):
    """Angles for atoms"""
    attrname = 'angles'
    singular = 'angles'


class Dihedrals(Bonds):
    """Dihedrals for atoms"""
    attrname = 'dihedrals'
    singular = 'dihedrals'


class Impropers(Bonds):
    attrname = 'impropers'
    singular = 'impropers'
