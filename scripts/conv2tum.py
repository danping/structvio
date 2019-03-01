#!/usr/bin/python
import argparse
import sys

def read_euroc_groundtruth(filename):
    file = open(filename)
    data = file.read()
    lines = data.replace(","," ").replace("\t"," ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip()!=""] for line in lines if len(line)>0 and line[0]!="#"]
    list = [(float(l[0])*1e-9,l[1:4]+l[5:8]+[l[4]]) for l in list if len(l)>1]
    return list

def read_structvio_result(filename):
    file = open(filename)
    data = file.read()
    lines = data.replace(","," ").replace("\t"," ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip()!=""] for line in lines if len(line)>0 and line[0]!="#"]
    list = [(float(l[1])+float(l[2])*1e-9,l[7:10]+l[4:7]+[l[3]]) for l in list if len(l)>1]
    return list

def read_vicon_result(filename):
    file = open(filename)
    data = file.read()
    lines = data.replace(","," ").replace("\t"," ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip()!=""] for line in lines if len(line)>0 and line[0]!="#"]
    list = [(float(l[0]),l[1:8]) for l in list if len(l)>1]
    return list


def write_tum_result(list, filename):
    file = open(filename, "w")
    file.writelines("# timestamp tx ty tz qx qy qz qw\n")
    for l in list:
        ts = l[0]
        pq = l[1]
        file.writelines("%s %s %s %s %s %s %s %s\n"%(l[0],pq[0],pq[1],pq[2],pq[3],pq[4],pq[5],pq[6]))

def conv2tum(type, input, output, skip_secs = 0):
    if type=='structvio':
        res = read_structvio_result(input)
        t0 = res[0][0]
        res = [l for l in res if l[0] >t0 + skip_secs]
        write_tum_result(res, output)
    elif type=='okvis':
        res = read_okvis_result(input)
        t0 = res[0][0]
        res = [l for l in res if l[0] >t0 + skip_secs]
        write_tum_result(res, output)
    elif type=='vins':
        res = read_vins_result(input)
        t0 = res[0][0]
        res = [l for l in res if l[0] >t0 + skip_secs]
        write_tum_result(res, output)
    elif type=='euroc':
        res = read_euroc_groundtruth(input)
        t0 = res[0][0]
        res = [l for l in res if l[0] >t0 + skip_secs]
        write_tum_result(res, output)



def cvt_main():
    example_cmd = """
    %(prog)s -t structvio -i <input file> -o <output file>
    """

    parser = argparse.ArgumentParser(description="convert the results into tum's format",usage=example_cmd)
    parser.add_argument('-t','--type',choices=['structvio','euroc'],default='structvio')
    parser.add_argument('-i', '--input', action='store', required=True, help="Path of the input file")
    parser.add_argument('-o', '--output', help="Path of the output file", nargs="?")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    args = parser.parse_args()
    type = args.type
    input = args.input
    output = args.output
    conv2tum(type,input,output)


if __name__ == "__main__":
    cvt_main()

