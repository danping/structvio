#!/usr/bin/python
import os
import argparse
import copy
from evo.core import sync,geometry
from evo.core.metrics import *
from evo.tools.file_interface import *
from evo.main_ape import *

# This is a small program to evaluate the loop closing error of a visual-inertial system
# The computation of the loop closing error is described in the paper
#   StructVIO : Visual-inertial Odometry with Structural Regularity of Man-made Environments
#   by Danping Zou etc.
# Note : install the evo package first
#   https://michaelgrupp.github.io/evo/

def read_structvio_trajectory_file(file_path):
    file = open(file_path)
    data = file.read()
    lines = data.replace(","," ").replace("\t"," ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip()!=""] for line in lines if len(line)>0 and line[0]!="#"]
    mat = np.array(list).astype(float)
    stamps = mat[:, 1]+mat[:,2]*1e-9# n x 1
    xyz = mat[:,7:10]
    quat = mat[:,[4,5,6,3]]

    return PoseTrajectory3D(xyz,quat,stamps)


def read_arcode_trajectory_file(file_path):
    file = open(file_path)
    data = file.read()
    lines = data.replace(","," ").replace("\t"," ").split("\n")
    list = [[float(v.strip()) for v in line.split(" ") if v.strip()!=""] for line in lines if len(line)>0 and line[0]!="#"]
    mat = np.array(list).astype(float)

    stamps = mat[:, 0]# n x 1
    xyz = mat[:, 1:4]  # n x 3
    quat = mat[:, 4:]  # n x 4
    return PoseTrajectory3D(xyz, quat, stamps)


def read_arcode_trajectory_files(file_dir):
    name_part1 = os.path.basename(file_dir)+"-ArUco-a.txt"
    name_part2 = os.path.basename(file_dir)+"-ArUco-b.txt"
    file_path_part1 = os.path.join(file_dir,name_part1)
    file_path_part2 = os.path.join(file_dir,name_part2)

    trj_part1 = read_arcode_trajectory_file(file_path_part1)
    trj_part2 = read_arcode_trajectory_file(file_path_part2)
    return (trj_part1,trj_part2)


def merge_arcode_trajeoctries(trj_part01,trj_part02):
    timestamps = trj_part01.timestamps.copy()
    xyz = trj_part01.positions_xyz.copy()
    quat = trj_part01.orientations_quat_wxyz.copy()

    return PoseTrajectory3D(np.concatenate((xyz,trj_part02.positions_xyz)),
                            np.concatenate((quat,trj_part02.orientations_quat_wxyz)),
                            np.concatenate((timestamps,trj_part02.timestamps)))


def align_trajectory_by_arcode(trj_est, trj_ar):
    trj_ar01_sync, trj_est_sync = sync.associate_trajectories(trj_ar[0], trj_est)

    trj_copy = copy.deepcopy(trj_est_sync)  # otherwise np arrays will be references and mess up stuff
    r_a, t_a,s = geometry.umeyama_alignment(trj_copy.positions_xyz.T,
                                          trj_ar01_sync.positions_xyz.T,
                                          False)

    se3 = lie.se3(r_a,t_a)
    return se3

def align_trajectory_by_vicon_whole(trj_est, trj_vicon):
    trj_vicon_sync, trj_est_sync = sync.associate_trajectories(trj_vicon, trj_est)
    trj_copy = copy.deepcopy(trj_est_sync)  # otherwise np arrays will be references and mess up stuff
    r_a, t_a, s = geometry.umeyama_alignment(trj_copy.positions_xyz.T,
                                             trj_vicon_sync.positions_xyz.T,
                                             False)
    res = lie.se3(r_a,t_a)
    return res

def align_trajectory_by_vicon(trj_est, trj_vicon):
    trj_vicon01,trj_vicon02 = split_vicon_trajectory(trj_vicon)
    trj_vicon01_sync, trj_est_sync = sync.associate_trajectories(trj_vicon01, trj_est)
    trj_copy = copy.deepcopy(trj_est_sync)  # otherwise np arrays will be references and mess up stuff
    r_a, t_a, s = geometry.umeyama_alignment(trj_copy.positions_xyz.T,
                                             trj_vicon01_sync.positions_xyz.T,
                                             False)
    res = (lie.se3(r_a,t_a),trj_vicon01,trj_vicon02)
    return res


def split_vicon_trajectory(trj_vicon):
    dt = trj_vicon.timestamps[2:]-trj_vicon.timestamps[1:-1]
    ind = dt.argmax()+2
    trj_vicon_01 = PoseTrajectory3D(trj_vicon.positions_xyz[0:ind,:],trj_vicon.orientations_quat_wxyz[0:ind,:],
                                    trj_vicon.timestamps[0:ind])
    trj_vicon_02 = PoseTrajectory3D(trj_vicon.positions_xyz[ind:,:],trj_vicon.orientations_quat_wxyz[ind:,:],
                                    trj_vicon.timestamps[ind:])
    return trj_vicon_01,trj_vicon_02



def evaluate_results(structvio_res_path, data_folder):
    ape_res = []
    trj_est = read_structvio_trajectory_file(structvio_res_path)
    name = os.path.basename(data_folder)
    print(name)

    vicon_path = os.path.join(data_folder, 'vicon.txt')
    arcode_a_path = os.path.join(data_folder, name + '-ArUco-a.txt')
    arcode_b_path = os.path.join(data_folder, name + '-ArUco-b.txt')

    if( os.path.exists(vicon_path)):
        print("using Vicon ground truth:")
        print(vicon_path)
        #read the ground truth
        trj_vicon = read_tum_trajectory_file(vicon_path)
        res = align_trajectory_by_vicon(trj_est, trj_vicon)
        trj_est.transform(res[0])

        trj1,trj2 = sync.associate_trajectories(trj_vicon,trj_est)
        ape_res = ape(trj1, trj2,PoseRelation.translation_part)
    elif os.path.exists(arcode_a_path) and os.path.exists(arcode_b_path):
        #read the ground truth
        print("using ArUco ground truth:")
        print(arcode_a_path)
        print(arcode_b_path)
        trj_ar = read_arcode_trajectory_files(data_folder)
        if trj_ar[1].timestamps[0] > trj_est.timestamps[-1]:
            print('Incomplete trajectory!')
            exit(-1)

        se3 = align_trajectory_by_arcode(trj_est,trj_ar)
        trj_est.transform(se3)
        trj_ar_merge = merge_arcode_trajeoctries(trj_ar[0],trj_ar[1])
        trj1,trj2 = sync.associate_trajectories(trj_ar_merge,trj_est)
        ape_res = ape(trj1, trj2, PoseRelation.translation_part)
    else:
        print('cannot find any ground truth files!')
        exit(-1);

    return ape_res


def main():
    example_cmd = """
    %(prog)s -r state.txt -d Mech-01 
    """

    parser = argparse.ArgumentParser(description="Evaluate the loop closing error of the StructVIO output.", usage=example_cmd)

    parser.add_argument('-r', '--result', action='store', required=True,help="Path of the 'state.txt'")
    parser.add_argument('-d', '--data', action='store', required=True, help="Path of the data folder")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    args = parser.parse_args()
    ape = evaluate_results(args.result,args.data)
    print("The loop closing errors are listed as:")
    for key,val in ape.stats.items():
        print("\t"+ key + "\t" + str(val))

if __name__ == "__main__":
    main()
