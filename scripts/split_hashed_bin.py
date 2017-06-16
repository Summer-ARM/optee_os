#!/usr/bin/env python
#
# Copyright (c) 2017, ARM Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import argparse
import struct

def write_header_v2(outf, magic, arch, flags, init_size, \
		init_load_addr_hi, init_load_addr_lo, paged_size):
	version = 2;
	outf.write(struct.pack('<IBBHI', \
		magic, version, arch, flags, 2))
	outf.write(struct.pack('<IIII', \
		init_load_addr_hi, init_load_addr_lo, 1, init_size))
	outf.write(struct.pack('<IIII', \
		0, 0, 2, paged_size))

def append_to(out_fname, start_offs, inf, max_bytes=0xffffffff):
	outf = open(out_fname, 'wb');
	#print "Appending %s@0x%x 0x%x bytes at position 0x%x" % \
		#( inf, start_offs, max_bytes, int(outf.tell()) )
	inf.seek(start_offs)
	while True :
		nbytes = min(16 * 1024, max_bytes)
		if nbytes == 0 :
			break
		#print "Reading %s %d bytes" % (inf, nbytes)
		buf = inf.read(nbytes)
		if not buf :
			break
		outf.write(buf)
		max_bytes -= len(buf)
	outf.close()

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--in_file', \
		required=True, type=argparse.FileType('rb'), \
		help='Input file')

	parser.add_argument('--out_header_v2', \
		help='Output filename for tee header v2')

	parser.add_argument('--out_pager_v2', \
		help='Output filename for tee pager v2')

	parser.add_argument('--out_pageable_v2', \
		help='Output filename tee pageable v2')

	return parser.parse_args();

def main():
	args = get_args()

	header_v1_size = struct.calcsize('<IBBHIIIII')
	data = args.in_file.read(header_v1_size)
	(magic, version, arch_id, flags, init_size, \
		init_load_addr_hi, init_load_addr_lo, \
		init_mem_usage, paged_size) = \
		struct.unpack('<IBBHIIIII', data)

	if args.out_header_v2 is not None:
		header_v2_file = open(args.out_header_v2, 'wb')
		write_header_v2(header_v2_file, magic, \
				arch_id, flags, init_size, \
				init_load_addr_hi, init_load_addr_lo, \
				paged_size)
		header_v2_file.close()

	if args.out_pager_v2 is not None:
		append_to(args.out_pager_v2, header_v1_size, \
				args.in_file, init_size)

	# Skip ZERO sized pageable image
	if args.out_pageable_v2 is not None and paged_size != 0:
		append_to(args.out_pageable_v2, header_v1_size + init_size, \
				args.in_file)

	args.in_file.close()

if __name__ == "__main__":
	main()
