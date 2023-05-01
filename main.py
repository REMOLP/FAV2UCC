### HELP TEXT DOCS FUNC ###
def helpText():
    print("format <inputfile> - format file to contain all text only on one line.")
    print("extract <inputfile> <nwords> <truerng?> - extract only small portion of the text from previously formatted text. truerng argument is a boolean (default false).")
    print("extractsrt <inputfile> <nindexes> - extract only few segments from the .srt file and return it.\n")
    print("refinesrt <inputfile> <outputfile> - refine YouTube auto-generated subtitles (changing the [ __ ] to other kind of string for better LLM compatibility).\n")
    print("aisummsrt <inputfile> <algotype (rng, lilo, lilofull)> <nindexes> <inputvideofile> <outputvideofile> - speaks for itself, let AI cook.")

if __name__ == "__main__":
    helpText()
    print("\n\n(note: this is just a sneak peak of what's coming)")
