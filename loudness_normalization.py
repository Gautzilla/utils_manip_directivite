import soundfile as sf
import pyloudnorm as pyln
import os

AUDIO_FOLDER = r'C:\Users\Gauthier\source\repos\manip_directivite\data\audio'


def equalize(files: list) -> list:
    reference, fs = sf.read(files[0])
    meter = pyln.Meter(fs)
    target_loudness = meter.integrated_loudness(reference)
    for file in files[1:]:
        audio, fs = sf.read(file)
        loudness = meter.integrated_loudness(audio)
        gain = 10**((target_loudness - loudness)/20)
        audio *= gain
        sf.write(file = file, data = audio, samplerate = fs)


if __name__ == '__main__':
    audio_files = [os.path.join(AUDIO_FOLDER, filename) for filename in os.listdir(AUDIO_FOLDER)]
    equalize([file for file in audio_files if 'Close' in file and 'Front' in file])
    equalize([file for file in audio_files if 'Far' in file and 'Front' in file])
    equalize([file for file in audio_files if 'Close' in file and 'Side' in file])
    equalize([file for file in audio_files if 'Far' in file and 'Side' in file])