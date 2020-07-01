# thesisNGT
This program was developed and tested using Python 3.6.1 on Ubuntu 16.04.6.
#### Additional packages that must be installed:
 <ul>
  <li>spaCy</li>
  <li>nl_core_news_sm (pertains to spaCy, but needs to be downloaded separately)</li>
</ul>

#### Files included in download:
<ul>
<li><i>main.py</i><br>Signs the input using the JASigning avatar<br></li>
<li><i>sign.py</i><br>Contains functions for creating a Sign object for the provided gloss<br></li>
<li><i>functionsGrammar.py</i><br>Contains functions for pre-processsing the sentence<br></li>
<li><i>functionsMain.py</i><br>Contains functions for processing the sentence<br></li>
<li><i>functionsAux.py</i><br>Contains functions that are used in sign.py or offer extra functionality<br></li>
<li><i>sendsigml.py</i><br>Sends SiGML files to the avatar<br></li>
<li><i>dictFile.py</i><br>Contains the dictionary of encoded NGT signs available to the avtatar<br></li>
<li><i>HamNoSysDict.py</i><br>Contains a dictionary of all known HamNoSys notations and their respectve categories<br></li>
<li><i>SiGML-Player.AppImage</i><br>Contains the JASigning avatar<br></li>
</ul>

The program can be used by making a call to main.py with a glossed NGT sentence. The JASigning avatar will sign the sentence in NGT
as long as the SiGML Player is running.
#### Possible flags to add to call to main.py:
<ul>
<li><i>spell</i><br>Fingerspells complete input<br><b>Usage: main.py spell 'string'</b></li>
<li><i>explain</i><br>Explains the SiGML-code of the sign<br><b>Usage: main.py explain 'gloss'</b></li>
<li><i>add</i><br>Adds sign to the dictionary<br><b>Usage: main.py add 'gloss' 'HamNoSys-SiGML' 'SAMPA'</b></li>
</ul>
