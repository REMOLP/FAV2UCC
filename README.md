# FAV2UCC - the long-awaited successor to the original FAVTUCC project is here!
Yeah, it is finally here! Still under development, but at least it is. The usage and docs are below.

# Prerequisites
To use the program make sure that you have:
- [koboldcpp](https://github.com/LostRuins/koboldcpp) and of course the model. I recommend [Vicuna 7B](https://huggingface.co/eachadea/ggml-vicuna-7b-1.1) or [WizardLM 7B](https://huggingface.co/TheBloke/WizardLM-7B-uncensored-GGML) the most.
- Python 3.6 at least (I suppose)
- ffmpeg

When it comes to video files, when it comes to downloading file from your desired platform of choice, it is the best to use [yt-dlp](https://github.com/yt-dlp/yt-dlp).
For .srt subtitles, it easiest to just grab YouTube subtitles from the video of course. But of course not all will have them. In that case, use [OpenAI's Whisper](https://github.com/openai/whisper) or [this port to .cpp](https://github.com/ggerganov/whisper.cpp) for CPU usage ;) Put the .srt transcription in the "transcriptions" folder of course.

Don't change folder structure even if some types of files do not need to be placed in a certain folder. It is for the sake of keeping it future proof.

# Usage
The CLI usage of the program is really not that complicated at all. You should understand it in no time by looking at the help message. Just run ```python ./main.py```
But here's the most basic usage of the most important function of the program: ```python ./main.py aisummsrt ./transcriptions/invideo.srt lilo 28 ./invideo.mp4 finaloutput.mp4```

For more advanced usage, head to the configuration file (fav2ucc.config.ini) and mess around a little with it.

When it comes to merging .srt files together into one file from few others, make sure that the files follow this format:
```bash
filename-p1.srt
filename-p2.srt
...
filename-pX.srt
```
Nonetheless, please keep in mind that the merging isn't perfect so recheck the file just in case in the splitted start-end sections per file.

### Some more info on the actual status of the project right now:
- I keep providing some logs and sample video outputs [here.](https://www.youtube.com/@__Ianr__) Just search for "FAV2UCC" and read some descriptions of these videos.
- there is still a long way to go until the project will satisfy my own needs :)
- speaking of satisfying needs, if possible, I would want to try to make it as friendly as possible, both for devs and end users.
- would be good to make a actual GUI in the future for easier use. For now just CLI.
