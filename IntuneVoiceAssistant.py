import os
import azure.cognitiveservices.speech as speechsdk
import openai

# Speech Services
speech_key = ""
speech_region = "" #"eastus"
language = "" #"en-US"
voice = "" #"en-US-JennyMultilingualNeural"

# Open Ai
openai.api_key = ""
openai.api_base =  "https://XXXXXXX.openai.azure.com/"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
deployment_id= "" #"gpt-35-turbo"

# Prompt
base_message = [{"role":"system","content":"You are an Microsoft Intune senior expert voice assistant who can answer all intune related questions. You are friendly and concise. You only provide factual answers to queries, and do not provide answers that are not related to Microsoft products or intune."}]


#######################
###### Functions ######
#######################
def ask_openai(prompt):
    base_message.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
    engine="gpt-35-turbo",
    messages = base_message,
    temperature=0.24,
    max_tokens=50,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)

    text = response['choices'][0]['message']['content'].replace('\n', ' ').replace(' .', '.').strip()
    print('Azure OpenAI response:' + text)
    base_message.append({"role": "assistant", "content": text})
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to speaker for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

def chat_with_open_ai():
    while True:
        print("Azure OpenAI is listening. Say 'Stop' or press Ctrl-Z to end the conversation.")
        try:
            speech_recognition_result = speech_recognizer.recognize_once_async().get()
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = speech_recognition_result.text
                if text == "Stop.": 
                    print("Conversation ended.")
                    break
                if text == "Reset.":
                    print("Reset")
                    base_message = [{"role":"system","content":"You are an AI voice assistant that helps to answer questions."}]
                if "Hey," in text: 
                    print("Recognized  speech: {}".format(speech_recognition_result.text))
                    ask_openai(speech_recognition_result.text)
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
                break
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
        except EOFError:
            break

#######################
######## Start ########
#######################
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_config.speech_recognition_language=language
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_config.speech_synthesis_voice_name=voice
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

try:
    chat_with_open_ai()
except Exception as err:
    print("Encountered exception. {}".format(err))