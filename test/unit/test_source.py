import unittest
import scipy.sparse as sps
import numpy as np

from porepy.grids.structured import CartGrid
from porepy.numerics.fv import source
from porepy.params.data import Parameters


class TestSource(unittest.TestCase):
    def test_integral(self):
        g, d = setup_3d_grid()
        src_disc = source.Integral()
        lhs, rhs = src_disc.assemble_matrix_rhs(g, d)

        rhs_t = np.array([0, 0, 0, 0, 1, 0, 0, 0])

        self.assertTrue(src_disc.ndof(g) == g.num_cells)
        self.assertTrue(np.all(rhs == rhs_t))
        self.assertTrue(lhs.shape == (8, 8))
        self.assertTrue(lhs.nnz == 0)


def setup_3d_grid():
    g = CartGrid([2, 2, 2], physdims=[1, 1, 1])
    g.compute_geometry()
    d = {"param": Parameters(g)}
    src = np.zeros(g.num_cells)
    src[4] = 1
    d["param"].set_source("flow", src)
    return g, d


if __name__ == "__main__":
    unittest.main()
