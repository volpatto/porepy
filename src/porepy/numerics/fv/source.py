"""
Discretization of the source term of an equation for FV methods.
"""
import numpy as np
import scipy.sparse as sps

from porepy.numerics.mixed_dim.solver import Solver


class Integral(Solver):
    """
    Discretization of the integrated source term
    int q * dx
    over each grid cell.

    All this function does is returning a zero lhs and
    rhs = param.get_source.physics.
    """

    def __init__(self, keyword="flow", physics=None):
        """ Set the discretization, with the keyword used for storing various
        information associated with the discretization.

        Paramemeters:
            keyword (str): Identifier of all information used for this
                discretization.
        """
        self.keyword = keyword
        self.known_keywords = ["flow", "transport", "mechanics"]

        # The physics keyword is kept for consistency for now, but will soon be purged.
        if physics is None:
            self.physics = keyword
        else:
            self.physics = physics

    # ------------------------------------------------------------------------------#

    def _key(self):
        """ Get the keyword of this object, on a format friendly to access relevant
        fields in the data dictionary

        Returns:
            String, on the form self.keyword + '_'.

        """
        return self.keyword + "_"

    # ------------------------------------------------------------------------------#

    def ndof(self, g):
        """ Return the number of degrees of freedom associated to the method.
        For scalar equations, the ndof equals the number of cells. For vector equations,
        we multiply by the dimension.

        Parameter:
            g: grid, or a subclass.

        Returns:
            int: the number of degrees of freedom.

        """
        if self.physics == "flow":
            return g.num_cells
        elif self.physics == "transport":
            return g.num_cells
        elif self.physics == "mechanics":
            return g.num_cells * g.dim
        else:
            raise ValueError(
                'Unknown keyword "%s".\n Possible keywords are: %s'
                % (self.keyword, self.known_keywords)
            )

    # ------------------------------------------------------------------------------#

    def assemble_matrix_rhs(self, g, data):
        """ Return the (null) matrix and right-hand side for a discretization of the
        integrated source term. Also discretize the necessary operators if the data
        dictionary does not contain a source term.

        Parameters:
            g : grid, or a subclass, with geometry fields computed.
            data: dictionary to store the data.

        Returns:
            lhs (sparse dia, self.ndof x self.ndof): Null lhs.
            sources (array, self.ndof): Right-hand side vector.

        The names of data in the input dictionary (data) are:
        param (Parameter Class) with the source field set for self.keyword. The assigned
            source values are assumed to be integrated over the cell volumes.
        """
        return self.assemble_matrix(g, data), self.assemble_rhs(g, data)

    # ------------------------------------------------------------------------------#

    def assemble_matrix(self, g, data):
        """ Return the (null) matrix and for a discretization of the integrated source
        term. Also discretize the necessary operators if the data dictionary does not
        contain a source term.

        Parameters:
            g (Grid): Computational grid, with geometry fields computed.
            data (dictionary): With data stored.

        Returns:
            scipy.sparse.csr_matrix (self.ndof x self.ndof): Null system matrix of this
                discretization.
        """
        if not self._key() + "source" in data.keys():
            self.discretize(g, data)

        return data[self._key() + "source"]

    # ------------------------------------------------------------------------------#

    def assemble_rhs(self, g, data):
        """ Return the rhs for a discretization of the integrated source term. Also
        discretize the necessary operators if the data dictionary does not contain a
        source term.

        Parameters:
            g (Grid): Computational grid, with geometry fields computed.
            data (dictionary): With data stored.

        Returns:
            scipy.sparse.csr_matrix (self.ndof): Right hand side vector representing the
                source.
        """
        if not self._key() + "bound_source" in data.keys():
            self.discretize(g, data)

        param = data["param"]
        sources = param.get_source(self)
        assert sources.size == self.ndof(
            g
        ), "There should be one source value for each cell"
        return data[self._key() + "bound_source"] * sources

    # ------------------------------------------------------------------------------#

    def discretize(self, g, data, faces=None):
        """ Discretize an integrated source term.

        Parameters:
            g : grid, or a subclass, with geometry fields computed.
            data: dictionary to store the data.

        Stores:
            lhs (sparse dia, self.ndof x self.ndof): Null lhs, stored as
                self._key() + "source".
            sources (array, self.ndof): Right-hand side vector, stored as
                self._key() + "bound_source".

        The names of data in the input dictionary (data) are:
        param (Parameter Class) with the source field set for self.keyword. The assigned
            source values are assumed to be integrated over the cell volumes.
        """
        lhs = sps.csc_matrix((self.ndof(g), self.ndof(g)))
        rhs = sps.diags(np.ones(self.ndof(g))).tocsc()
        data[self._key() + "source"] = lhs
        data[self._key() + "bound_source"] = rhs
