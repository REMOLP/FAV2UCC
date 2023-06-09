import os
import sys

from fav2ucc import *

### HELP TEXT DOCS FUNC ###
def helpText():
    print("FAV2UCC version 0.8\n")
    print("extractsrt <inputfile> <nindexes> - extract only few segments from the .srt file and return it.")
    print("refinesrt <inputfile> <outputfile> - refine YouTube auto-generated subtitles (changing the [ __ ] to other kind of string for better LLM compatibility).")
    print("mergesrtfull <inputfolder> - merge x amount of .srt files into one, consecutive file. File syntax in the docs.")
    print("aisummsrt <inputfile> <algotype (rng, lilo, lilofull)> <nindexes> <inputvideofile> <outputvideofile> - speaks for itself, let AI cook.\n")

if __name__ == "__main__":
    cliArgs = sys.argv

    # print(cliArgs) # Just for testing

    if len(cliArgs)<=1:
        helpText()
        print("No args passed.")
        sys.exit(0)

    if cliArgs[1] == "extractsrt":
        import random        
        
        srtLastIndex = getSrtSubs(cliArgs[2], 1, 1)[0]
        srtSubsObj = getSrtSubs(cliArgs[2], random.randint(1, srtLastIndex), int(cliArgs[3]))[1]
        srtSubsObjLastTS = srtSubsObj[-1][2]

        fullChunkOfText = ""
        for i in range(len(srtSubsObj)):
          fullChunkOfText += srtSubsObj[i][3]+" "
        
        print(f"--// {srtSubsObj[0][1]} //--")
        print(fullChunkOfText)
    elif cliArgs[1] == "refinesrt":
        replaceSwearWordsFromSRT(cliArgs[2], cliArgs[3])
    elif cliArgs[1] == "mergesrtfull":
        print(type(cliArgs[2]))
        mergeSrtFiles(cliArgs[2])        
    elif cliArgs[1] == "aisummsrt":
      # TODO:
      # - lilo and lilofull per portion additional checks if the provided text by LLM is actually in timewise order (string starting index seems the best)
      # and actually sort it before trimming and adding to the array
      # - additional offset specified by the user, so for example if a word starts at 00:02:00.000 then with adding prefix offset of 00:00:01.000
      # it will start at 00:01:59.000 instead of course. Same for the suffix offset.
      # DONE - additional LLM repetition checks needed
      # DONE - cutting clips by tags flag in the .ini file: yes or no (for now you need to type out tags)
      # DONE - better flexibility from configuration file, that is: LLM parameters from .ini
      import random
      from time import sleep

      promptFile = open(loadedIniFile["General"]["prompt_txt_file_path"], "r", encoding="utf-8")
      vicunaInitPrompt = promptFile.read()
      promptFile.close()

      # Taking the LLM arguments from .ini config file here.
      maxLenFromIni = int(loadedIniFile["LLM"]["max_output_length"])
      temperatureFromIni = float(loadedIniFile["LLM"]["temperature"])
      topPFromIni = float(loadedIniFile["LLM"]["top_p"])
      # We need to do some additional thing with out stop sequences to be properly formatted.
      stopSeqsFromIni = str(loadedIniFile["LLM"]["stop_sequences"])
      stopSeqsFromIni = stopSeqsFromIni.replace("\\n", "\n")
      stopSeqsFromIni = stopSeqsFromIni.replace("\\t", "\t")
      # And finally splitting to an array. Splitting when found: <eoss>
      # <eoss> = End of stop sequence.
      stopSeqsFromIni = stopSeqsFromIni.split("<eoss>")
      print(f"maxLenFromIni = {maxLenFromIni}")
      print(f"temperatureFromIni = {temperatureFromIni}")
      print(f"topPFromIni = {topPFromIni}")
      if stopSeqsFromIni[-1] == "":
          stopSeqsFromIni.pop(-1)
      print(f"stopSeqsFromIni = {stopSeqsFromIni}")

      # sys.exit(1) # Just for testing.

      tempVidsList = []
      srtLastIndex = getSrtSubs(cliArgs[2], 1, 1)[0]
      globalIter = 0

      # Below important part related used slicing algorithm.
      # LILO - Linear in, linear out.
      if cliArgs[3] == "lilofull":
          liloIters = srtLastIndex//int(cliArgs[4])
          mainLoopIters = liloIters
      elif cliArgs[3] == "lilo":
          liloIters = srtLastIndex//int(cliArgs[4])
          mainLoopIters = int(loadedIniFile["General"]["main_loop_iters"])
      else:
          # liloIters = None
          mainLoopIters = int(loadedIniFile["General"]["main_loop_iters"])


      # Few more globals before main loop
      liloCounter = 0
      liloStartSkip = int(loadedIniFile["Algorithms"]["lilo_start_skip"]) # Amount of skip for the loop itself

      # Here it is lads!
      for clipN in range(mainLoopIters):
          print(f"--// PROGRESS: {clipN}/{mainLoopIters} //--")
          # The checks below should be moved to the checks below to individual CLI argument value.
          # Will do it later.
          if liloStartSkip == -2 and clipN < 1:
              liloCounter += int(loadedIniFile["Algorithms"]["lilo_first_index_overwrite"])
              continue
          elif clipN < liloStartSkip:
              liloCounter += int(cliArgs[4])
              continue

      
          if cliArgs[3] == "rng":
              srtSubsObj = getSrtSubs(cliArgs[2], random.randint(1, srtLastIndex), int(cliArgs[4]))[1]
              srtSubsObjLastTS = srtSubsObj[-1][2]
          elif cliArgs[3] == "lilofull":
              try:
                  srtSubsObj = getSrtSubs(cliArgs[2], liloCounter, int(cliArgs[4]))[1]
                  srtSubsObjLastTS = srtSubsObj[-1][2]
              except:
                  print("Probably out of index, skipping. Will add additional checks later.\n")
                  continue
          elif cliArgs[3] == "lilo":
              srtSubsObj = getSrtSubs(cliArgs[2], liloCounter, int(cliArgs[4]))[1]
              srtSubsObjLastTS = srtSubsObj[-1][2]              
          else:
              srtSubsObj = getSrtSubs(cliArgs[2], int(cliArgs[3]), int(cliArgs[4]))[1]
              srtSubsObjLastTS = srtSubsObj[-1][2]

          liloCounter += int(cliArgs[4]) # Linear counter
          # print(f"srtSubsObj = {srtSubsObj}")
          # print(f"srtSubsObjLastTS = {srtSubsObjLastTS}")

          wordPerTimestamp = convert_to_timestamps(srtSubsObj)
          fullChunkOfText = " ".join(wordPerTimestamp[1])
          # print(f"Before -> {wordPerTimestamp}")
          wordPerTimestamp[0].append(srtSubsObjLastTS)
          # print(f"After -> {wordPerTimestamp}")
          print(f"\n\n{fullChunkOfText}\n")

          ### KoboldCPP API - START ###
          finalPrompt = vicunaInitPrompt.replace("{yourTextHere}", fullChunkOfText)
          # print(finalPrompt)
          myDaddy = slapMeDaddy(finalPrompt, maxLenFromIni, temperatureFromIni, topPFromIni, stopSeqsFromIni)
          # print(myDaddy)
          print(myDaddy["results"][0]["text"])

          # Removing unnecessary junk below
          quotesOnly = myDaddy["results"][0]["text"].split("\n")
          # sys.exit(1) # Just for testing.
      		
          if quotesOnly[-1] == "User:" or quotesOnly[-1] == "\nUser:":
              quotesOnly.pop(-1)

          # print(f"quotesOnly = {quotesOnly}")

          preFinalQuotesOnly = []
          for i in range(len(quotesOnly)):
          		splittedQuote = quotesOnly[i].split(" ")
          		splittedQuote.pop(0)
          		try:
          		    splittedQuote[-1] = splittedQuote[len(splittedQuote)-1].replace("\n", "")
          		    preFinalQuotesOnly.append(" ".join(splittedQuote))
          		except:
          		    print("Something went wrong with splittedQuote variable manipulation. Skipping. (don't worry, probably just junk unnecessary data :))")


          # print(f"preFinalQuotesOnly = {preFinalQuotesOnly}")

          quoteTags = loadedIniFile["General"]["quote_tags"].split(",")
          finalQuotesOnly = []
          for quote in preFinalQuotesOnly:
              try:
                  noQuotationMarks = quote.split(" - ")[0].replace("\"", "")

                  if USE_TAGS == True:
                      thisQuoteTag = quote.split(" - ")[1][:-1]
                      if thisQuoteTag in quoteTags:
                          finalQuotesOnly.append(noQuotationMarks)
                  else:
                      finalQuotesOnly.append(noQuotationMarks)
              except:
                  print("Quote too long, skipping...")
          
          print(f"\nfinalQuotesOnly = {finalQuotesOnly}")
          
          # Removing duplicates
          quotesForVideo = []
          
          for i in range(len(finalQuotesOnly)):
              isDuplicate = False
              for j in range(i+1, len(finalQuotesOnly)):
                  howSimilar = stringSimilarity(finalQuotesOnly[i].lower(), finalQuotesOnly[j].lower())
                  if howSimilar >= 0.5:
                      isDuplicate = True
                      break
              if not isDuplicate:
                  if finalQuotesOnly[i] not in quotesForVideo:
                      quotesForVideo.append(finalQuotesOnly[i])
          
          print(f"\nquotesForVideo = {quotesForVideo}")
          
          # One more important check with quotesForVideo variable.
          # Sometimes there can be actually duplicates regardless of the previous string comparison check.
          # For now it actually messes up everything so will need to re-check the logic behind this part of the code later.
          # for v in range(len(quotesForVideo)):
              # for b in range(len(quotesForVideo)):
                  # try:
                      # if textStartIndex(quotesForVideo[b].lower(), quotesForVideo[v].lower()) != -1:
                          # quotesForVideo.pop(b)
                  # except IndexError:
                      # print("Additional per sentece check for quotesForVideo variable failed because of IndexError. Fix later.")

          print(f"quotesForVideo = {quotesForVideo}\n")
          ### KoboldCPP API - END ###

          # Trimming the videos here pog :D
          for thisQuote in range(len(quotesForVideo)):
              aiGenOut = quotesForVideo[thisQuote]
              textStartingIndex = textStartIndex(noDiacriticSigns(fullChunkOfText).lower(), noDiacriticSigns(aiGenOut).lower())

              if textStartingIndex == -1:
                  continue

              nSpaceChars = howManySpacesUntilIndex(noDiacriticSigns(fullChunkOfText).lower(), textStartingIndex)
              print(f"Spaces until index: {nSpaceChars}")
              nSpaceCharsAI = howManySpaces(aiGenOut)
              print(f"Spaces in AI returned string: {nSpaceCharsAI}")

              clipStartingTS = wordPerTimestamp[0][nSpaceChars]
              clipEndingTS = wordPerTimestamp[0][nSpaceChars+nSpaceCharsAI+1]
              print(f"clipStartingTS = {clipStartingTS}\tclipEndingTS = {clipEndingTS}")

              if clipN == 0:
                  trimInputClipv3_2(cliArgs[5], "srt__tempvid"+str(i)+"-"+str(globalIter)+".mp4", clipStartingTS, clipEndingTS, True)
              else:
                  trimInputClipv3_2(cliArgs[5], "srt__tempvid"+str(i)+"-"+str(globalIter)+".mp4", clipStartingTS, clipEndingTS)
              # tempVidsList.append(TEMP_VIDS_FOLDER+"/srt__tempvid"+str(i)+"-"+str(globalIter)+".mp4")
              tempVidsList.append("srt__tempvid"+str(i)+"-"+str(globalIter)+".mp4")
              
              globalIter += 1
              # liloCounter += int(cliArgs[4])
              sleep(1)

      if len(tempVidsList) > 1:
        # Create a text file with the list of video file names
        with open(TEMP_VIDS_FOLDER+"/filestomerge.txt", "w", encoding="utf-8") as f:
            for video in tempVidsList:
                f.write(f"file '{video}'\n")

        concatTrimmedInputs(cliArgs[6])

        # Define the file extension of the temporary files to delete
        file_extension = GLOBAL_VIDEO_EXT_OUT
        
        # Loop through all files in the directory and delete the ones with the specified extension
        for filename in os.listdir(TEMP_VIDS_FOLDER):
            if filename.endswith(file_extension):
                os.remove(os.path.join(TEMP_VIDS_FOLDER+"/", filename))
