# !/usr/bin/python
# -*- coding: utf8 -*-
#                         -.
#                  ,,,,,,    `²╗,
#             ╓▄▌█▀▀▀▀▀▀▀█▓▓▓▓▌▄  ╙@╕
#          ▄█▀Γ,╓╤╗Q╣╣╣Q@╤═ Γ▀▓▓▓▓▄ "▒╦
#        ▄▀,╤╣▒▒▒▒▒▒ÅÅ╨╨╨ÅÅ▒▒▒╤▐▓▓▓▓▄ ╙▒╕ └
#      4Γ,╣▒▒ÅÖ▄▓▓▓▓▓█%─     `Å▒Q█▓▓▓▓ └▒╦ ▐╕
#       ╩▒▒`╓▓▓▓▓▀Γ             ╙▒▀▓▓▓▓ ╚▒╕ █
#      ▒▒ ,▓▓▓▓Γ ,                ì▀▓▓▓▌ ▒▒  ▓
#     ▒▒ ╓▓▓▓▀,Q▒                   ▓▓▓▓ ▒▒⌐ ▓
#    ╓▒ ╒▓▓▓▌╣▒▒                    ▓▓▓▓║▒▒⌐ ▓─
#    ╫Γ ▓▓▓█▒▒▒∩                    ▓▓▓▌▒▒▒ ]▓
#    ╫⌐ ▓▓▓]▒▒▒                    ▓▓▓Θ▒▒▒O ▓▓
#    ║µ ▓▓▌ ▒▒▒╕                 ,█▀Γ╒▒▒▒┘ ▓▓`
#     Θ ▀▓▓ ▒▒▒▒⌐▄                 ,╣▒▒Å ▄▓▓Γ
#     ╚  ▓▓ '▒▒▒▒▓▓▄           ,═Q▒▒▒Ö,▄▓▓█ .
#      ╙  ▓▓ "▒▒▒▒╬█▓▓▄▄     `╙╨╢▄▓▓▓▓▓▓█Γ╒┘
#          ▀▓▄ Å▒▒▒▒ç▀█▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▀,d┘
#            ▀▓▄ ╙▒▒▒▒╗, Γ▀▀▀▀▀▀▀Γ ,╓ê╜
#              ▀█▄▄  ╙ÅÅ▒▒▒╣QQQ╩ÅÅ╙
#                  ▀▀m▄
#
#
__author__ = 'pablogsal'
#--------------------------------------IMPORT STUFF----------------------------------------------#

import numpy
import time
import progress_lib


#--------------------------------------MAIN PROGRAM ---------------------------------------------------------#


max=100    #Define the max iterations in the example
meantime=[]  # This variable is to process the timeout

for i in range(1,max+1):
        start = time.time()   # Start time measure
        time.sleep(.1)        # Do stuff
        end = time.time()     # End time measure
        meantime.append(end - start) # Append time measure to the measure list
        progress_lib.update_progress(float(i) / max, numpy.median(meantime) * (max-i))  #Update the progress bar

print("Fin del programa")   # Print termination