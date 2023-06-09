import os
import sys
import time
import argparse
from simple_diarizer.diarizer import Diarizer
import pprint


t0 = time.time()
diar = Diarizer(
    embed_model='ecapa',  # 'xvec' and 'ecapa' supported
    cluster_method='sc'  # 'ahc' 'sc' and 'nme-sc' supported
)

parser = argparse.ArgumentParser()
parser.add_argument(dest='audio_name', type=str)
parser.add_argument("--number_of_speakers",
                    dest='number_of_speaker', default=None, type=int)
parser.add_argument("--max_speakers", dest='max_speakers',
                    default=25, type=int)
parser.add_argument(dest='outputfile', nargs="?", default=None)
args = parser.parse_args()

WAV_FILE = args.audio_name
num_speakers = args.number_of_speaker if args.number_of_speaker != "None" else None
max_spk = args.max_speakers
output_file = args.outputfile

diar = Diarizer(
    embed_model='ecapa',  # supported types: ['xvec', 'ecapa']
    cluster_method='sc',  # supported types: ['ahc', 'sc']
    window=1,  # size of window to extract embeddings (in seconds)
    period=0.6  # hop of window (in seconds)
)

segments = diar.diarize(WAV_FILE,
                        num_speakers=None,
                        # max_speakers=5,
                        threshold=0.1,
                        outfile=None)


pprint.pprint(segments)
t1 = time.time()
feature_t = t1 - t0
print("Time used for extracting features:", feature_t)

json = {}
_segments = []
_speakers = {}
seg_id = 1
spk_i = 1
spk_i_dict = {}

for seg in segments:

    segment = {}
    segment["seg_id"] = seg_id

    if seg['label'] not in spk_i_dict.keys():
        spk_i_dict[seg['label']] = spk_i
        spk_i += 1

    spk_id = "spk" + str(spk_i_dict[seg['label']])
    segment["spk_id"] = spk_id
    segment["seg_begin"] = round(seg['start'])
    segment["seg_end"] = round(seg['end'])

    if spk_id not in _speakers:
        _speakers[spk_id] = {}
        _speakers[spk_id]["spk_id"] = spk_id
        _speakers[spk_id]["duration"] = seg['end']-seg['start']
        _speakers[spk_id]["nbr_seg"] = 1
    else:
        _speakers[spk_id]["duration"] += seg['end']-seg['start']
        _speakers[spk_id]["nbr_seg"] += 1

    _segments.append(segment)
    seg_id += 1

for spkstat in _speakers.values():
    spkstat["duration"] = round(spkstat["duration"])

json["speakers"] = list(_speakers.values())
json["segments"] = _segments


pprint.pprint(json["segments"])
pprint.pprint(json["speakers"])
