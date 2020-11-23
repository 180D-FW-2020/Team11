import speech_recognition as sr
import time 
import json
import csv


words_times = []

class voiceAction:

	def __init__(self, phrases):
		self.phrases = phrases
		self.active = False

	def listen(self):
		self.active = True

	def stop(self):
		self.active = False

	def voiceCheck(self):
		if self.active:
			r = sr.Recognizer()

			with sr.Microphone() as source:
				r.adjust_for_ambient_noise(source)

				
				print("Please say something...")

				audio = r.listen(source)

				mic_input = ""


				try:
					mic_input = r.recognize_google(audio)

					#start timing					
					start = time.time()


					print("You said : \n " + mic_input)

					
					#stop timing
					stop = time.time()

					#calculate delta
					delta = stop - start
					delta_str = str(delta)
					entry = [mic_input,delta_str]
					print(entry)

					print("\n")


					words_times.append(entry)

					


					#Check for conditionals
					for key in self.phrases:
						if(key.lower() in mic_input.lower()):
							self.phrases[key]()

					

				except Exception as e:
					print("Error : " + str(e))




currentlyListening = True
finalize = False

def p1():
	print("Phrase Match: Start")
def p2():
	print("Phrase Match: Stop")
def p3():
	print("Phrase Match: Power up")
def p4():
	print(words_times)
	with open('output.csv', 'w') as result_file:
		wr = csv.writer(result_file, dialect='excel')
		wr.writerows(words_times)

phrases_usecases = {
	"start" : p1,
	"stop" : p2,
	"power up" : p3,
	"final" : p4
}

v = voiceAction(phrases_usecases)
v.listen()
while currentlyListening:
	v.voiceCheck()
	#stop = time.time()
	#print(stop-start)


	




