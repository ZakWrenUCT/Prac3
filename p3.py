# Import libraries
from typing import Dict
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
# from __future__ import division

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
freq = 1
dc = 0.5
score = 0
pwm = None
LED_A= None
guess = None
answer = None
userScore=0
end_of_game = True
global scoreDict



# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global answer
    global userScore
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        answer = generate_number()
        userScore=0
        guess = None
        end_of_game=False
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    line = ""
    scores = []
    for key, value in fetch_scores()[1].items():
        temp = [key,value]
        scores.append(temp)
    for i in range(0,3):
        line += ("{} - {} took {} guesses").format(i+1,scores[i][0],scores[i][1])
        print(line)
        line = ""
    pass

def reset():
    global guess
    global answer
    global pwm
    global LED_A
    global userScore
    global end_of_game
    userScore=0
    guess = None
    end_of_game=True
    os.system('clear')
    pwm.stop()
    LED_A.stop()
    # GPIO.cleanup()
    # setup()

# Setup Pins
def setup():
    global answer
    global end_of_game
    global pwm
    global LED_A
    end_of_game=True
    answer = generate_number()
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # Setup regular GPIO
    for i in range(len(LED_value)):
        GPIO.setup(LED_value[i],GPIO.OUT)
        GPIO.output(LED_value[i],GPIO.LOW)
    GPIO.setup(LED_accuracy,GPIO.OUT)
    GPIO.setup(buzzer,GPIO.OUT)

    GPIO.setup(btn_increase,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup PWM channels
    pwm = GPIO.PWM(buzzer,1)
    LED_A = GPIO.PWM(LED_accuracy,100)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=499)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    # Get the scores
    count = -1
    scoreDict = {}
    keyName = ""
    scoreCount = eeprom.read_byte(0)
    for i in eeprom.read_block(1, scoreCount*4):
        count += 1
        if count % 4 == 3:
            scoreDict[keyName] = i
            keyName = ""
            continue
        keyName += chr(i)
    # eeprom.read_block(Self, 0, 32, 32)
    # convert the codes back to ascii
    # return back the results
    return scoreCount, scoreDict


# Save high scores
def save_scores(name,score):
    # fetch scores and update total amount of scores
    scoreCount = fetch_scores()[0]+1
    scoreDict = fetch_scores()[1]
    # include new score
    scoreDict[name]=score
    scoreDict = sorted(scoreDict.items(),key=lambda x: x[1])
    eeprom.write_byte(0,scoreCount)
    # write new scores
    count=4
    for i in scoreDict:
        for letter in i[0]:
            eeprom.write_byte(count,ord(letter))
            count+=1
        eeprom.write_byte(count,i[1])
        count+=1


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global guess
    global userScore
    # print("inc")
    if end_of_game!=True:
        if guess == None:
            guess = 0
            for i in range (len(LED_value)):
                GPIO.output(LED_value[i],GPIO.LOW)
        elif guess < 7:
            guess += 1
            if guess == 1:
                GPIO.output(LED_value[0],GPIO.LOW)
                GPIO.output(LED_value[1],GPIO.LOW)
                GPIO.output(LED_value[2],GPIO.HIGH)
            if guess == 2:
                GPIO.output(LED_value[0],GPIO.LOW)
                GPIO.output(LED_value[1],GPIO.HIGH)
                GPIO.output(LED_value[2],GPIO.LOW)
            if guess == 3:
                GPIO.output(LED_value[0],GPIO.LOW)
                GPIO.output(LED_value[1],GPIO.HIGH)
                GPIO.output(LED_value[2],GPIO.HIGH)
            if guess == 4:
                GPIO.output(LED_value[0],GPIO.HIGH)
                GPIO.output(LED_value[1],GPIO.LOW)
                GPIO.output(LED_value[2],GPIO.LOW)
            if guess == 5:
                GPIO.output(LED_value[0],GPIO.HIGH)
                GPIO.output(LED_value[1],GPIO.LOW)
                GPIO.output(LED_value[2],GPIO.HIGH)
            if guess == 6:
                GPIO.output(LED_value[0],GPIO.HIGH)
                GPIO.output(LED_value[1],GPIO.HIGH)
                GPIO.output(LED_value[2],GPIO.LOW)
            if guess == 7:
                GPIO.output(LED_value[0],GPIO.HIGH)
                GPIO.output(LED_value[1],GPIO.HIGH)
                GPIO.output(LED_value[2],GPIO.HIGH)
        else:
            guess = 0
            for i in range (len(LED_value)):
                GPIO.output(LED_value[i],GPIO.LOW)
        print("Guess: "+str(guess)+ " Score:"+str(userScore))
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # print("guess")
    global guess
    global answer
    global pwm
    global LED_A
    global userScore
    global end_of_game
    global score
    if end_of_game  == False:
        while GPIO.input(btn_submit) == GPIO.LOW:
            time.sleep(0.5)
            if GPIO.input(btn_submit) == GPIO.LOW:
                end_of_game = True
                pass
    # if no
        if guess == None:
            pass
        elif guess == answer and not end_of_game:
            end_of_game = True
            for i in range(len(LED_value)):
                GPIO.output(LED_value[i],GPIO.LOW)
            pwm.stop()
            LED_A.stop()
            print("YOU GUESSED CORRECTLY! SCORE:{}".format(userScore))
            print("Enter Name (MAX 3 CHAR): ")
            name = input("Name: ")
            name = name[:3].upper()
            save_scores(name,userScore)
        elif not end_of_game:
            accuracy_leds(guess, answer)
            trigger_buzzer(guess, answer)
            print("TRY AGAIN")
            userScore+=1

    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds(guess, answer):
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    # - max guess is 8
    global LED_A
    LED_A.stop()
    if guess < answer: 
        LED_A.start(guess/answer)
        # print(guess/answer)
    if guess > answer:
        LED_A.start((8-guess)/(8-answer))
    pass

# Sound Buzzer
def trigger_buzzer(guess,answer):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global pwm
    if abs(answer-guess)==3:
        pwm.ChangeFrequency(1)
        pwm.start(0.5)
    if abs(answer-guess)==2:
        pwm.ChangeFrequency(2)
        pwm.start(0.5)
    if abs(answer-guess)==1:
        pwm.ChangeFrequency(4)
        pwm.start(0.5)   
    pwm.start(0.5)  
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        eeprom.clear(64)
        eeprom.populate_mock_scores()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
#when restart through hold, the success screen comes up twice