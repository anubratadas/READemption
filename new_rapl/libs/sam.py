import csv
import sys
from subprocess import Popen, PIPE

class SamParser(object):
    """A parser for SAM files.

    Warning: It does not cover the full SAM specification but only
    handles the output generated by Segemehl.

    Further infos about the SAM format can be found here:

    http://samtools.sourceforge.net/

    SAM uses the 1-based coordinate system i.e. the first nucleotide
    of a genome has the position 1.

    """

    def __init__(self, samtools_bin="samtools"):
        self._samtools_bin = samtools_bin

    def entries_bam(self, bam_file):
        for entry in self.entries(self.bam_to_sam_stream(bam_file)):
            yield(entry)

    def entries(self, sam_fh):
        for split_line in self._split_lines(sam_fh):
            if not split_line[0].startswith("@"):
                yield(SamEntry(split_line))

    def bam_to_sam_stream(self, bam_file):
        return(Popen("%s view -h %s" % (self._samtools_bin, bam_file), 
                  stdout=PIPE, shell=True).stdout)

    def _split_lines(self, sam_fh):
        """Convert byte to string and split down."""
        for line in sam_fh:
            yield(str(line, encoding="utf8")[:-1].split("\t"))

    def ref_seq_ids_and_lengths_bam(self, bam_file):
        return(self.ref_seq_ids_and_lengths(self.bam_to_sam_stream(bam_file)))
            
    def ref_seq_ids_and_lengths(self, sam_fh):
        ref_seq_ids_and_lengths = {}
        for split_line in self._split_lines(sam_fh):
            if split_line[0].startswith("@SQ"):
                ref_seq = split_line[1].replace("SN:", "")
                length = int(split_line[2].replace("LN:", ""))
                ref_seq_ids_and_lengths[ref_seq] = length
            # Stop as soon there the first entry line is found 
            if not split_line[0].startswith("@"):
                break
        return(ref_seq_ids_and_lengths)

    def mapping_countings_bam(self, bam_file, ref_seq_ids):
        return(self.mapping_countings(self.bam_to_sam_stream(bam_file), 
                                      ref_seq_ids))

    def mapping_countings(self, sam_fh, ref_seq_ids):
        ref_seqs_and_mappings = {}
        ref_seqs_and_mapped_reads = {}
        for ref_seq in ref_seq_ids:
            ref_seqs_and_mappings[ref_seq] = 0
            ref_seqs_and_mapped_reads[ref_seq] = 0
        for entry in self.entries(sam_fh):
            try:
                ref_seqs_and_mappings[entry.reference] += 1
                ref_seqs_and_mapped_reads[
                    entry.reference] += 1.0/float(entry.number_of_hits_as_int)
            except:
                sys.stderr.write(
                    "SAM entry with unspecified reference found! Stoping\n")
                sys.exit(2)
        return(ref_seqs_and_mappings, ref_seqs_and_mapped_reads)

class SamEntry(object):

    def __init__(self, split_sam_line):
        # SAM mendatory fields
        self.query_id = split_sam_line[0]
        self.flag = int(split_sam_line[1])
        self.reference = split_sam_line[2]
        self.start = int(split_sam_line[3])
        self.mapping_quality = int(split_sam_line[4])
        self.cigar = split_sam_line[5]
        self.mate_next_frag = split_sam_line[6]
        self.mate_start = int(split_sam_line[7])
        self.template_length = int(split_sam_line[8])
        self.sequence = split_sam_line[9]
        self.phred_quality = split_sam_line[10]

        # Extra fields
        self.distance = split_sam_line[11]
        self.mismatches = split_sam_line[12]
        self.number_of_hits = split_sam_line[13]
        try:
            self.xa = split_sam_line[14] # Query / Mate
        except IndexError:
            pass

        # Secondary values
        self.end = None
        self.strand = None
        self.number_of_hits_as_int = None
        
        # Generate secondary values
        self._calculate_end()
        self._set_strand()
        self._set_number_of_hits_as_int()

    def _calculate_end(self):
        self.end = self.start + len(self.sequence) - 1
    
    def _set_strand(self):
        if self.flag == 0: 
            self.strand = "+"
        elif self.flag == 16: 
            self.strand = "-"
        else:
            self.strand = None
            sys.stderr.write("Warning. Unknown flag. No strand allocation.")

    def _set_number_of_hits_as_int(self):
        self.number_of_hits_as_int = int(self.number_of_hits.split(":")[-1])
