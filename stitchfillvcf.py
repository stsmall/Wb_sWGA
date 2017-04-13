#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 12:24:29 2017
This program should be run on a vcf that has been filtered by removing sites
found to be in repeated regions and minimum filtering via XXX


@author: scott
"""
import re
from math import log10
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('INvcf', metavar="INvcf", type=str,
                    help='path to vcf file')
parser.add_argument('-s', "--stitch", type=str, required=True,
                    help="stitch vcf")
args = parser.parse_args()


def stitch2vcf(vcf, stitch):
    """takes a stitch-ed vcf and the original vcf and fills missing sites
    """
    impute = {}
    with open(stitch, 'r') as stitchvcf:
        for line in stitchvcf:
            if line.startswith("#"):
                pass
            else:
                x = line.strip().split()
                # assume all the same chromosome
                impute[x[1]] = x
    f = open(vcf + '.impute', 'w')
    still_miss = 0
    with open(vcf, 'r') as vcffile:
        for line in vcffile:
            if line.startswith("##") or line.startswith("#"):
                f.write(line)
            else:
                x = line.split()
                # fill missing
                miss = [i for i, s in enumerate(x) if re.search(r'\./\.', s)]
                for missgt in miss:
                    fixgt = impute[x[1]][missgt].split(":")
                    if fixgt[0] == "./.":
                        still_miss += 1
                        oldgt = ["./.", ".", ".", ".", "."]
                    else:
                        newgt = fixgt[0]
                        if newgt == '0/0':
                            AD = "20,0"    # AD
                        elif newgt == "0/1":
                            AD = "10,10"
                        else:
                            AD = "0,20"
                        try:
                            gltemp = [-10 * log10(float(a))
                                      for a in fixgt[1].split(",")]
                        except ValueError:
                            gltemp = [-10 * log10(float(a) + .000001)
                                      for a in fixgt[1].split(",")]
                        gl = ",".join(map(str, gltemp))  # PL
                        oldgt = x[missgt].split(":")
                        oldgt[0] = newgt
                        oldgt[1] = AD
                        oldgt[2] = '20'
                        oldgt[3] = '99'
                        oldgt[4] = gl
                    x[missgt] = ":".join(oldgt)
                # rewrite PL as GL; GL = PL/-10.0
                for sample in range(9, len(x)):
                    if "./." not in x[sample]:
                        gl = x[sample].split(":")
                        glnew = [float(a)/-10.0
                                 for a in gl[-1].split(",")]
                        gl[-1] = ",".join(map(str, glnew))
                        x[sample] = ":".join(gl)
                    else:
                        pass
                # addfields
                fields = x[8].split(":")
                fields[-1] = "GL"
                x[8] = ":".join(fields)
                if "0/0" in line or "1/1" in line or "0/1" in line:
                    f.write("{}\n".format("\t".join(x)))
                else:
                    # line is empty
                    print(line)
    f.close()
    print("missing\t{}".format(still_miss))
    return(None)

if __name__ == '__main__':
    stitch2vcf(args.INvcf, args.stitch)
