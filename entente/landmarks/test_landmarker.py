from entente.landmarks.landmarker import Landmarker
from entente.landmarks.serialization import dump_landmarks
from lacecore import Mesh, shapes
import numpy as np
import pytest
from ..test_surface_regressor import source_target_landmarks


def test_landmarker(tmp_path):
    source_mesh, target_mesh, landmarks, expected_landmarks = source_target_landmarks()

    landmarker = Landmarker(source_mesh, landmarks)

    transferred = landmarker.transfer_landmarks_onto(target_mesh)
    np.testing.assert_array_equal(transferred["origin"], expected_landmarks["origin"])
    np.testing.assert_array_equal(
        transferred["near_opposite_corner"], expected_landmarks["near_opposite_corner"]
    )

    source_mesh_path = str(tmp_path / "source.obj")
    landmark_path = str(tmp_path / "landmarks.json")

    source_mesh.write_obj(source_mesh_path)
    dump_landmarks(landmarks, landmark_path)

    landmarker = Landmarker.load(
        source_mesh_path=source_mesh_path, landmark_path=landmark_path
    )
    transferred = landmarker.transfer_landmarks_onto(target_mesh)
    np.testing.assert_array_equal(transferred["origin"], expected_landmarks["origin"])
    np.testing.assert_array_equal(
        transferred["near_opposite_corner"], expected_landmarks["near_opposite_corner"]
    )


def test_landmarker_wrong_topology():
    source_mesh = shapes.cube(np.zeros(3), 1.0)

    # Create a second mesh with a different topology.
    target_mesh = source_mesh.faces_flipped()

    # Landmarks are empty; we don't get that far.
    landmarker = Landmarker(source_mesh, {})

    with pytest.raises(ValueError, match="Target mesh must have the same topology"):
        landmarker.transfer_landmarks_onto(target_mesh)


def test_landmarker_quad():
    tri_mesh = shapes.cube(np.zeros(3), 1.0)
    quad_mesh = Mesh(v=np.zeros((0, 3)), f=np.zeros((0, 4), dtype=np.int64))

    with pytest.raises(ValueError, match="Source mesh should be triangulated"):
        # Landmarks are empty; we don't get that far.
        Landmarker(quad_mesh, {})

    landmarker = Landmarker(tri_mesh, {})
    with pytest.raises(ValueError, match="Target mesh must be triangulated"):
        landmarker.transfer_landmarks_onto(quad_mesh)
