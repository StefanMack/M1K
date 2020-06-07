# Elektrische Messtechnik mit dem ADALM1000

In der elektrischen Messtechnik sind Oszilloskope die wichtigsten Messinstrumente. Der Umgang mit ihnen wird in mehreren Praktika im Bachelorstudium Mechatronik gelehrt.
Infolge der Coronapandemie sind Präsenzpraktika leider nur noch sehr eingeschränkt möglich. In technischen Fächern haben solche "Hands On" Praktika vor allem an den praxisorientierten Fachhochschulen einen sehr hohen Stellenwert für die Studierenden.
Die vielen Hurra-Meldungen zur Digitalisierung an den Hochschulen suggerieren, dass auch Praktika erfolgreich in digitale Formate gewandelt werden. Leider ist jedoch der Lernerfolg an einem Oszilloskop-Emulator nahe Null. Es ist ja auch gerade die  Hardwarenähe, welche die Industrie im Mechatronikbereich in Deutschland so erfolgreich macht!

Wenn keine Präsenzpraktika stattfinden dürfen, dann müssen die Studierenden folglich die Praktika Zuhause durchführen unterstützt durch Web-Meetings mit den Assistenten und Professoren.
Dafür ist eine möglichst preiswerte und universelle Messtechnikhardware nötig, denn übliche Stand Alone Oszilloskope und Funktionsgeneratoren sind zu teuer und zu groß, um sie den Studierenden mitzugeben.

Die ADALM1000 Messplatine von Analog Devices bietet hier einen Lösungsweg:
Sie beinhaltet ein Zweikanal-Oszilloskop mit 100 kS/s. Die beiden Oszilloskopkanäle können auch Ströme messen. Alternativ können die Kanäle auch als Spannungs- oder Stromquelle eines Funktionsgenerator (AWG) mit 100 kS/s verwendet werden um Testsignale zu erzeugen. Zusätzlich besitzt der ADLAM1000 auch vier digitale GPIOs, die z.B. für eine I²C-Kommunikation verwendet werden können.

Der ADALM1000 wird via USB mit dem PC verbunden. Angesteuert und ausgelesen wird er mit C++ oder Python-Programmen.

Nähere Infos siehe: wiki.analog.com/university/tools/m1k

In diesem Repository befinden sich Python-Programmbeispiele, die auf dem Pythonpackage pysmu (Wrappe der C-Bibliothek libsmu siehe github.com/analogdevicesinc/libsmu) von Analog Devices basieren.
