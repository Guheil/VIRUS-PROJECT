import wave
import os
import sys

def check_wav_file(file_path):
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist"
            
        with wave.open(file_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            comp_type = wav_file.getcomptype()
            comp_name = wav_file.getcompname()
            
            return {
                "status": "valid",
                "channels": channels,
                "sample_width": sample_width,
                "frame_rate": frame_rate,
                "n_frames": n_frames,
                "comp_type": comp_type,
                "comp_name": comp_name
            }
    except Exception as e:
        return f"Error analyzing WAV file: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "script/assets/audio/boss_music.wav"
    
    result = check_wav_file(file_path)
    if isinstance(result, dict):
        print(f"File: {file_path}")
        print(f"Status: {result['status']}")
        print(f"Channels: {result['channels']}")
        print(f"Sample width: {result['sample_width']}")
        print(f"Frame rate: {result['frame_rate']}")
        print(f"Number of frames: {result['n_frames']}")
        print(f"Compression type: {result['comp_type']}")
        print(f"Compression name: {result['comp_name']}")
        print("WAV file is valid")
    else:
        print(result)