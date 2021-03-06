#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:28:56 2016
remove_missing.py
wrapper for vcftools to remove individual samples from a vcf with a percent
missing
@author: scott
"""
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('INvcf', metavar="INvcf", type=str,
                    help='path to vcf IN file')
parser.add_argument('-p', "--miss", type=float, default=1,
                    help="percent missing after which an ind is removed")
parser.add_argument('-m', "--max", type=float, default=1,
                    help="max missing after which a site is removed")
args = parser.parse_args()

command = "vcftools --vcf " + args.INvcf + " --missing-indv --stdout"
print command
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
proc.wait()


f = open("remove_inds.out", 'w')
for line in iter(proc.stdout.readline, ''):
    if line.startswith("INDV"):
        pass
    else:
        if float(line.split()[4]) >= args.miss:
            f.write(line.split()[0]+"\n")
f.close()

command = "vcftools --vcf " + args.INvcf + " --max-missing " + args.max + " --remove remove_inds.out --recode --out " + args.INvcf + ".nomiss"
print command
proc = subprocess.Popen(command, shell=True)
proc.wait()
