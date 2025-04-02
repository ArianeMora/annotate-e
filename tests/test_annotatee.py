
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import shutil
import tempfile
import unittest
import pandas as pd
import os
import shutil
from annotatee import *
from annotatee.annotate import pipeline

class TestClass(unittest.TestCase):

    @classmethod
    def setup_class(self):
        local = True
        # Create a base object since it will be the same for all the tests
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))

        self.data_dir = os.path.join(THIS_DIR, 'test_data/')
        if local:
            self.tmp_dir = os.path.join(THIS_DIR, 'test_data/tmp/')
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
            os.mkdir(self.tmp_dir)
        else:
            self.tmp_dir = tempfile.mkdtemp(prefix='test_data')

    @classmethod
    def teardown_class(self):
        shutil.rmtree(self.tmp_dir)

    def test_annotate(self):
        # Start with a simple dataset to run the pipeline
        id_col = 'Entry'
        seq_col = 'Sequence'
        label_col = 'label'
        rows = [['AXE2_TALPU', 'query', 'MHSKFFAASLLGLGAAAIPLEGVMEKRSCPAIHVFGARETTASPGYGSSSTVVNGVLSAYPGSTAEAINYPACGGQSSCGGASYSSSVAQGIAAVASAVNSFNSQCPSTKIVLVGYSQGGEIMDVALCGGGDPNQGYTNTAVQLSSSAVNMVKAAIFMGDPMFRAGLSYEVGTCAAGGFDQRPAGFSCPSAAKIKSYCDASDPYCCNGSNAATHQGYGSEYGSQALAFVKSKLG'],
                ['AXE2_TALPU', 'reference', 'MHSKFFAASLLGLGAAAIPLEGVMEKRSCPAIHVFGARETTASPGYGSSSTVVNGVLSAYPGSTAEAINYPACGGQSSCGGASYSSSVAQGIAAVASAVNSFNSQCPSTKIVLVGYSQGGEIMDVALCGGGDPNQGYTNTAVQLSSSAVNMVKAAIFMGDPMFRAGLSYEVGTCAAGGFDQRPAGFSCPSAAKIKSYCDASDPYCCNGSNAATHQGYGSEYGSQALAFVKSKLG'],
                ['AXE2_GEOSE', 'reference', 'MKIGSGEKLLFIGDSITDCGRARPEGEGSFGALGTGYVAYVVGLLQAVYPELGIRVVNKGISGNTVRDLKARWEEDVIAQKPDWVSIMIGINDVWRQYDLPFMKEKHVYLDEYEATLRSLVLETKPLVKGIILMTPFYIEGNEQDPMRRTMDQYGRVVKQIAEETNSLFVDTQAAFNEVLKTLYPAALAWDRVHPSVAGHMILARAFLREIGFEWVRSR'], 
                ['AXE7A_XYLR2', 'query', 'MFNFAPKQTTEMKKLLFTLVFVLGSMATALAENYPYRADYLWLTVPNHADWLYKTGERAKVEVSFCLYGMPQNVEVAYEIGPDMMPATSSGKVTLKNGRAVIDMGTMKKPGFLDMRLSVDGKYQHHVKVGFSPELLKPYTKNPQDFDAFWKANLDEARKTPVSVSCNKVDKYTTDAFDCYLLKIKTDRRHSIYGYLTKPKKAGKYPVVLCPPGAGIKTIKEPMRSTFYAKNGFIRLEMEIHGLNPEMTDEQFKEITTAFDYENGYLTNGLDDRDNYYMKHVYVACVRAIDYLTSLPDWDGKNVFVQGGSQGGALSLVTAGLDPRVTACVANHPALSDMAGYLDNRAGGYPHFNRLKNMFTPEKVNTMAYYDVVNFARRITCPVYITWGYNDNVCPPTTSYIVWNLITAPKESLITPINEHWTTSETNYTQMLWLKKQVK'],
                ['A0A0B8RHP0_LISMN', 'reference', 'MKKLLFLGDSVTDAGRDFENDRELGHGYVKIIADQLEQEDVTVINRGVSANRVADLHRRIEADAISLQPDVVTIMIGINDTWFSFSRWEDTSVTAFKEVYRVILNRIKTETNAELILMEPFVLPYPEDRKEWRGDLDPKIGAVRELAAEFGATLIPLDGLMNALAIKHGPTFLAEDGVHPTKAGHEAIASTWLEFTK']]
       
        df = pd.DataFrame(rows, columns=[id_col, label_col, seq_col])
        # Save this to a reference and then a fasta file
        with open(os.path.join('/disk1/ariane/vscode/annotate-e/tests/tmp/', 'ref.fasta'), 'w+') as fout:
            for i, method, seq in df[[id_col, label_col, seq_col]].values:
                fout.write(f'>{i}\n{seq}\n')
        # Pass these two files to the pipeline
        pipeline('test', df, id_col, seq_col, '/disk1/ariane/vscode/annotate-e/tests/tmp/', '/disk1/ariane/vscode/annotate-e/tests/tmp/ref.fasta', 'complete', methods=['foldseek'])
                
        
        
            