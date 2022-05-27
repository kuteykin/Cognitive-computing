"""Python Pizza Parlor (using IBM Watson services)"""
# Loading libraries, Initializing variables and defining functions
from ibm_watson import SpeechToTextV1
from ibm_watson import TextToSpeechV1
import pyaudio  # used to record from mic
import pydub  # used to load a WAV file
import pydub.playback  # used to play a WAV file
import wave  # used to save a WAV file

def speech_to_text(file_name):
    """Use Watson Speech to Text to convert audio file to text."""
    # create Watson Speech to Text client 
    stt = SpeechToTextV1()

    # open the audio file 
    with open(file_name, 'rb') as audio_file:
        # pass the file to Watson for transcription
        result = stt.recognize(audio=audio_file,
            content_type='audio/wav', model='es-ES_BroadbandModel').get_result()
        
    # Get the 'results' list. This may contain intermediate and final
    # results, depending on method recognize's arguments. We asked 
    # for only final results, so this list contains one element.
    results_list = result['results'] 

    # Get the final speech recognition result--the list's only element.
    speech_recognition_result  = results_list[0]

    # Get the 'alternatives' list. This may contain multiple alternative
    # transcriptions, depending on method recognize's arguments. We did
    # not ask for alternatives, so this list contains one element.
    alternatives_list = speech_recognition_result['alternatives']

    # Get the only alternative transcription from alternatives_list.
    first_alternative = alternatives_list[0]

    # Get the 'transcript' key's value, which contains the audio's 
    # text transcription.
    transcript = first_alternative['transcript']

    return transcript  # return the audio's text transcription


def text_to_speech(text_to_speak, file_name):
    """Use Watson Text to Speech to convert text to specified voice
       and save to a WAV file."""
    # create Text to Speech client
    tts = TextToSpeechV1()

    # open file and write the synthesized audio content into the file
    with open(file_name, 'wb') as audio_file:
        audio_file.write(tts.synthesize(text_to_speak, 
            accept='audio/wav', voice='es-ES_LauraV3Voice').get_result().content)

def record_audio(file_name):
    """Use pyaudio to record 4 seconds of audio to a WAV file."""
    FRAME_RATE = 44100  # number of frames per second
    CHUNK = 1024  # number of frames read at a time
    FORMAT = pyaudio.paInt16  # each frame is a 16-bit (2-byte) integer
    CHANNELS = 2  # 2 samples per frame
    SECONDS = 4  # total recording time
 
    recorder = pyaudio.PyAudio()  # opens/closes audio streams

    # configure and open audio stream for recording (input=True)
    audio_stream = recorder.open(format=FORMAT, channels=CHANNELS, 
        rate=FRAME_RATE, input=True, frames_per_buffer=CHUNK)
    audio_frames = []  # stores raw bytes of mic input
    print(f'Recording {SECONDS} seconds of audio')

    # read 2.5 seconds of audio in CHUNK-sized pieces
    for i in range(0, int(FRAME_RATE * SECONDS / CHUNK)):
        audio_frames.append(audio_stream.read(CHUNK))

    print('Recording complete')
    audio_stream.stop_stream()  # stop recording
    audio_stream.close()  
    recorder.terminate()  # release underlying resources used by PyAudio

    # save audio_frames to a WAV file
    with wave.open(file_name, 'wb') as output_file:
        output_file.setnchannels(CHANNELS)
        output_file.setsampwidth(recorder.get_sample_size(FORMAT))
        output_file.setframerate(FRAME_RATE)
        output_file.writeframes(b''.join(audio_frames))

def play_audio(file_name):
    """Use the pydub module to play a WAV file."""
    sound = pydub.AudioSegment.from_wav(file_name)
    pydub.playback.play(sound)
    
def order_pizza(order_no):
    """Main function to start the ordering"""
    size = 0
    pepperoni = 0

    # Prompt 
    play_audio('prompt.wav')

    # Determine the Size of pizza (pequeña / mediana/ larga)
    while size not in ['pequeña', 'mediana', 'grande']:
        play_audio('size_request.wav')
        # print(size_request)
        record_audio('size_respond.wav')
        size = speech_to_text('size_respond.wav') 
        print(f'Size: {size}')
        if size not in ['pequeña', 'mediana', 'grande']:
            play_audio('repeat.wav')
        
    # Determine pepperoni (si/no)
    while pepperoni not in ['si', 'no']:
        play_audio('pepperoni_request.wav')
        # print(pepperoni_request)
        record_audio('pepperoni_respond.wav')
        pepperoni = speech_to_text('pepperoni_respond.wav')
        print(f'Pepperoni: {pepperoni}')
        if pepperoni == 'si':
            pepperoni_pref = 'con'
        elif pepperoni == 'no':
            pepperoni_pref = 'sin'
        else:
            pepperoni = 0
    
        if pepperoni == 0:
            play_audio('repeat.wav')                                                                
    
    # Repeating the order
    order = 'Pediste pizza ' + size + ' ' + pepperoni_pref + ' pepperoni.'
    print(f'No. {order_no}: {size.upper()} {pepperoni_pref.upper()} pepperoni.')
    text_to_speech(order, 'order.wav')
    play_audio('order.wav')

    
# Step 1 Prepare audio for the bot via TTS service  
prompt = '¡Buenos días, bienvenido a Robo-Pizza! Vamos a hacer el pedido.'
text_to_speech(prompt, 'prompt.wav')
repeat = 'Perdona, no entiendo. Por favor, dime otra vez'
text_to_speech(repeat, 'repeat.wav')
size_request = '¿Que tamaño de pizza prefieres - pequeña, mediana o grande?'
text_to_speech(size_request, 'size_request.wav')
pepperoni_request = '¿Ponemos pepperoni, sí o no?'
text_to_speech(pepperoni_request, 'pepperoni_request.wav')

#Step 2 Ordering
status = input('ENTER to order, "q" to Quit ')
order_no = 0
while status !='q':
    order_no += 1
    order_pizza(order_no)
    status = input('ENTER for next order, "q" to Quit ')