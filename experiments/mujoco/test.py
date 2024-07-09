import FramesViewer.utils as fv_utils
import mujoco
import mujoco.viewer
import mujoco_viewer
import numpy as np
from FramesViewer.viewer import Viewer
from scipy.spatial.transform import Rotation as R

from mini_bdx.placo_walk_engine import PlacoWalkEngine

# fv = Viewer()
# fv.start()
model = mujoco.MjModel.from_xml_path("../../mini_bdx/robots/bdx/scene.xml")
data = mujoco.MjData(model)
# viewer = mujoco.viewer.launch_passive(model, data)
viewer = mujoco_viewer.MujocoViewer(model, data)
pwe = PlacoWalkEngine(
    "/home/antoine/MISC/mini_BDX/mini_bdx/robots/bdx/robot.urdf",
    ignore_feet_contact=True,
)
pwe.set_traj(0.05, 0, 0.3)


def draw_frame(pose, i):
    pose = fv_utils.rotateInSelf(pose, [0, 90, 0])
    viewer.add_marker(
        pos=pose[:3, 3],
        mat=pose[:3, :3],
        size=[0.005, 0.005, 0.1],
        type=mujoco.mjtGeom.mjGEOM_ARROW,
        rgba=[1, 0, 0, 1],
        label=str(i),
    )


def orient_reward():
    euler = R.from_matrix(pwe.robot.get_T_world_fbase()[:3, :3]).as_euler("xyz")
    euler[0] = 0
    euler[1] = 0
    desired_quat = R.from_euler("xyz", euler).as_quat()
    current_quat = data.body("base").xquat

    # swap w for current_quat
    current_quat = [current_quat[3], current_quat[1], current_quat[2], current_quat[0]]


prev = data.time
while True:
    t = data.time
    dt = t - prev

    pwe.tick(dt)
    next_footsteps = pwe.get_footsteps_in_world()
    for i, footstep in enumerate(next_footsteps):
        draw_frame(footstep, i)
    # orient_reward()
    print(data.qfrc_actuator)
    data.ctrl[:] = list(pwe.get_angles().values())
    # pos = data.body("base").xpos
    # quat = data.body("base").xquat
    # rot = R.from_quat(quat).as_matrix()
    # T_world_body = np.eye(4)
    # T_world_body[:3, :3] = rot
    # T_world_body[:3, 3] = pos

    # T_world_rightFoot = np.eye(4)
    # pos = data.body("foot_module").xpos
    # quat = data.body("foot_module").xquat
    # mat = R.from_quat(quat).as_matrix()
    # T_world_rightFoot[:3, :3] = mat
    # T_world_rightFoot[:3, 3] = pos

    # T_body_rightFoot = np.linalg.inv(T_world_body) @ T_world_rightFoot

    # fv.pushFrame(T_world_body, "aze")
    # fv.pushFrame(T_world_rightFoot, "aze2")

    mujoco.mj_step(model, data, 4)  # 4 seems good

    viewer.render()

    prev = t
