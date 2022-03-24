# Elektrische Messtechnik mit dem ADALM1000 aka M1K

In der elektrischen Messtechnik sind Oszilloskope die wichtigsten Messinstrumente. Der Umgang mit ihnen wird in mehreren Praktika im Bachelorstudium Mechatronik geübt.
Infolge der Coronapandemie sind Präsenzpraktika leider nur noch sehr eingeschränkt möglich. In technischen Fächern jedoch haben solche "Hands On" Praktika vor allem an den praxisorientierten Fachhochschulen einen sehr hohen Stellenwert für die Studierenden.
Die vielen Hurra-Meldungen zur Digitalisierung an den Hochschulen suggerieren, dass auch Praktika erfolgreich in digitale Formate gewandelt werden. Leider ist jedoch der Lernerfolg an einem Oszilloskop-Emulator nahe Null. Es ist ja auch gerade die Hardwarenähe, welche die Industrie im Mechatronikbereich in Deutschland so erfolgreich macht! Und Rückmeldungen von Studierenden bestätigen, dass sie sich wegen des Praxisbezugs für eine FH und nicht für eine Uni entschieden haben.

Wenn keine Präsenzpraktika stattfinden dürfen, dann müssen die Studierenden folglich die Praktika Zuhause durchführen unterstützt durch Web-Meetings mit den Assistenten und Professoren.
Dafür ist eine möglichst preiswerte und universelle Messtechnikhardware nötig, denn übliche Bench Top Oszilloskope und Funktionsgeneratoren sind zu teuer und zu groß, um sie den Studierenden mitzugeben.

Die ADALM1000 ("ADALM" steht für "Analog Devices Advanced Learning Modul") Messplatine von Analog Devices, die übrigens meistens als "M1K" bezeichnet wird, bietet hier einen Lösungsweg:
Sie beinhaltet ein Zweikanal-Oszilloskop mit 200 kS/s. Die beiden Oszilloskopkanäle können auch Ströme messen. Alternativ können die Kanäle auch als Spannungs- oder Stromquelle eines Funktionsgenerator (AWG) mit 100 kS/s verwendet werden um Testsignale zu erzeugen. Zusätzlich besitzt der M1K auch vier digitale GPIOs, die z.B. für eine I²C-Kommunikation verwendet werden können.

Der M1K wird via USB mit dem PC verbunden. Angesteuert und ausgelesen wird er mit C++ oder Python-Programmen.

Nähere Infos siehe: wiki.analog.com/university/tools/m1k

In diesem Repository befinden sich Python-Programmbeispiele, die auf dem Pythonpackage pysmu (Wrapper der C-Bibliothek libsmu siehe github.com/analogdevicesinc/libsmu) von Analog Devices basieren.

Z.B. ist im Verzeichnis `/BattMeas` eine Anwendung des M1K vorgestellt, um den Verlauf der komplexen Impedanz und deren Abhängigkeit von der Frequenz beim Ladevorgang eines Akkus zu messen. Das Jupyter-Notebook hierzu wird unter folgendem Link im nbviewer angezeigt: [**Elektrische Eigenschaften von Akkus mit dem M1K messen**](https://nbviewer.jupyter.org/github/StefanMack/M1K/blob/master/BattMeas/BattMessM1k.ipynb)

Weiter wurde die quelloffene Benutzeroberfläche "Alice Desktop 1.38" (siehe wiki.analog.com/university/tools/m1k/alice/desk-top-users-guide) von Analog Devices vereinfacht, debugged und mit deutschsprachigen Tooltips versehen. Die Studis können mit diesem Pythonmodul "smuc" das M1K als "virtuelles Instrument" auf ihren Rechnern verwenden. smuc wird als Teil einer WinPython-Distribution auf den PC geladen. Zusätzlich ist eine Treiberinstallation von Analog Devices nötig, welche die M1K-spezifischen Bibliotheken "libsmu" sowie "pysmu" installiert.
Übrigens: „smuc‟ steht für Source Measurement Unit Control.

![Screenshot smuc](/smuc_screenshot.png)

Download smuc als WinPython-Distribution (WinPython 3.771) inkl. der IDE Spyder und der smuc Python-Quellcodedateien (v1.0 vom 22.1.21) als selbstentpackende ZIP-Datei (ca. 446 MB):  
https://magentacloud.de/s/4dtWtGwCKxpwm53
  
Download Installationsdatei für M1K-Treiber, libsmu-Bibliothek (1.0.2) und Python-Bibliothek pysmu:  
https://magentacloud.de/s/A5YDLPCSm6dEn7Q

Eine PDF-Installationsanleitung für Windows 10 und Ubuntu-Linux finden Sie im Verzeichnis "Smuc" in diesem Repository.
