drpy
====
This is a python port (with limited features) of a perl script named [drpl-1.04][1],  
which provides functionality of text to text conversion by looking up a dictionary.  
The drpy provides a feature of converting Japanese kanji and kana text into   
an orthographic style kanji and kana text using a dictionary named [Maruya-kun version 3.0][2].  

[1]: http://homepage3.nifty.com/01117/drpl.html   "drpl"
[2]: http://hp.vector.co.jp/authors/VA005156/     "Maruya-kun"


Installation
----

    $ chmod 755 drpy.py

Usage
----
### Dictionary creation ###

    $ ./drpy.py -c -D dic/maruyaex-v03

The execution of above command with options produces maruyaex-v03.trie and maruyaex-v03.db files under the dic directory.

### Text conversion ###

    $ echo "山の彼方の空遠く幸い住むと人の言う" | ./drpy.py -u -D dic/maruyaex-v03
    山の彼方の空遠く幸ひ住むと人の云ふ

The execution of above command with options converts the original text sent from echo command via a pipe 
"山の彼方の空遠く幸い住むと人の言う"  
into an orthographic style text  
"山の彼方の空遠く幸ひ住むと人の云ふ."

You can also specify an input file name with an option "-i" as described below. 

    $ ./drpy.py -u -D dic/maruyaex-v03 -i sample.txt  
    山の彼方の空遠く幸ひ住むと人の云ふ


