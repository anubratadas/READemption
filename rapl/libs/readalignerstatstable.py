class ReadAlignerStatsTable(object):

    def __init__(self, read_processing_stats, alignment_stats, libs, 
                 output_path):
        self._table = []
        self._read_processing_stats = read_processing_stats
        self._alignment_stats = alignment_stats
        self._libs = libs
        self._output_path = output_path
    
    def write(self):
        self._add_global_countings()
        self._add_reference_wise_coutings()
        table_fh = open(self._output_path, "w")
        table_fh.write("\n".join(["\t".join([str(cell) for cell in row]) 
                                  for row in self._table]) + "\n")
        table_fh.close()
        
    def _add_global_countings(self):
        for title, data in [
            ("Libraries", self._libs),
            ("No. of input reads", 
             self._get_read_process_numbers("total_no_of_reads")),
            ("No. of reads - PolyA detected and removed", 
             self._get_read_process_numbers("polya_removed")),
            ("No. of reads - Single 3' A removed", 
             self._get_read_process_numbers("single_a_removed")),
            ("No. of reads - Unmodified", 
             self._get_read_process_numbers("unmodified")),
            ("No. of reads - Removed as too short", 
             self._get_read_process_numbers("too_short")),
            ("No. of reads - Long enough and used for alignment", 
             self._get_read_process_numbers("long_enough")),
            ("Total no. of aligned reads", 
             self._total_alignment_stat_numbers("no_of_aligned_reads")),
            ("Total no. of unaligned reads", 
             self._total_alignment_stat_numbers("no_of_unaligned_reads")),
            ("Total no. of uniquely aligned reads", 
             self._total_alignment_stat_numbers(
                    "no_of_uniquely_aligned_reads")),
            ("Total no. of alignments", 
             self._total_alignment_stat_numbers("no_of_alignments")),
            ("Total no. of split alignments", 
             self._total_alignment_stat_numbers("no_of_split_alignments")),
            ("Percentage of aligned reads (compared to total input reads)",
             self._perc_aligned_reads()),
            ("Percentage of uniquely aligned reads (in relation to all aligned "
             "reads)", self._perc_uniquely_aligned_reads())]:
            self._table.append([title] + data)

    def _add_reference_wise_coutings(self):
        ref_ids = sorted(list(list(self._alignment_stats.values())[0][
                    "stats_per_reference"].keys()))
        for ref_id in ref_ids:
            self._table.append(
                ["%s - No. of aligned reads" % ref_id] +
                self._alignment_number_per_ref_seq(
                    ref_id, "no_of_aligned_reads"))
            self._table.append(
                ["%s - No. of uniquely aligned reads" % ref_id] +
                self._alignment_number_per_ref_seq(
                    ref_id, "no_of_uniquely_aligned_reads"))
            self._table.append(
                ["%s - No. of alignments" % ref_id] +
                self._alignment_number_per_ref_seq(
                    ref_id, "no_of_alignments"))
            self._table.append(
                ["%s - No. of split alignments" % ref_id] +
                self._alignment_number_per_ref_seq(
                    ref_id, "no_of_split_alignments"))

    def _alignment_number_per_ref_seq(self, ref_id, attribute):
        return [self._alignment_stats[lib]["stats_per_reference"][
                ref_id].get(attribute, 0) for lib in self._libs]

    def _total_alignment_stat_numbers(self, attribute, round_nums=True):
        countings = [self._alignment_stats[lib]["stats_total"].get(
                attribute, 0) for lib in self._libs]
        if round_nums is True:
            return [round(counting) for counting in countings]
        else:
            return countings

    def _get_read_process_numbers(self, attribute):
        return [self._read_processing_stats[lib][attribute]
                for lib in self._libs]

    def _perc_aligned_reads(self):
        return [
            round(self._calc_percentage(aligned_reads, total_reads), 2)
            for aligned_reads, total_reads in
            zip(self._total_alignment_stat_numbers(
                    "no_of_aligned_reads", round_nums=False),
                self._get_read_process_numbers("total_no_of_reads"))]
    
    def _perc_uniquely_aligned_reads(self):
        return [
            round(self._calc_percentage(uniquely_aligned_reads, aligned_reads)
                  , 2)
            for uniquely_aligned_reads, aligned_reads  in zip(
                self._total_alignment_stat_numbers(
                    "no_of_uniquely_aligned_reads"),
                self._total_alignment_stat_numbers(
                    "no_of_aligned_reads"))]

    def _calc_percentage(self, mult, div):
        try:
            return float(mult)/float(div)*100
        except ZeroDivisionError:
            return 0.0