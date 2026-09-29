---
titel: Join
quelle: Projekt Join
---

## Was Join ist

Join ist ein Task-Manager nach dem Vorbild eines Kanban-Boards. Aufgaben lassen
sich Nutzern und Kategorien zuordnen und per Drag-and-Drop zwischen den Spalten
verschieben. Gebaut ist es mit Angular und TypeScript, als Datenschicht dient
Supabase.

Join ist unter benjaminblarr.de/join erreichbar, der Quelltext liegt öffentlich
auf GitHub.

## Join war Teamarbeit zu viert

Join hat Benjamin nicht allein gebaut, sondern in einem Team aus vier Personen.
Das ist für die Einordnung des Projekts wichtiger, als es zunächst klingt: Die
schwierigste Aufgabe war nicht der Code, sondern die Koordination.

Vier Leute, die gleichzeitig an derselben Anwendung arbeiten, kommen sich
zwangsläufig in die Quere, wenn nicht vorher geklärt ist, wer woran sitzt.
Benjamin und sein Team haben das über Trello gelöst und dabei ein Verfahren
angewandt, das er bis heute benutzt: erst sammeln, welche großen Aufgaben es
überhaupt gibt, diese dann in Teilaufgaben zerlegen und diese wiederum, bis am
Ende einzelne To-dos übrig bleiben, die klein genug sind, dass eine Person sie
abschließen kann. Jeder nimmt sich eines und arbeitet es ab.

Der Effekt: Niemand arbeitet doppelt, niemand blockiert einen anderen, und der
Stand ist für alle jederzeit sichtbar.

## Die schwierigste technische Stelle in Join

Technisch war Drag-and-Drop der aufwendigste Teil. Eine Aufgabe von einer Spalte
in die andere zu ziehen sieht für den Anwender nach einer einzigen Bewegung aus.
Dahinter stehen mehrere Dinge gleichzeitig: erkennen, was gerade gezogen wird,
erkennen, wo es fallen gelassen werden soll, die Anzeige währenddessen
nachführen und am Ende den neuen Zustand speichern, ohne dass die Oberfläche
flackert oder eine Aufgabe kurzzeitig an zwei Stellen liegt.

## Warum bei Join Supabase eingesetzt wurde

Supabase war bei Join vorgegeben, wie der übrige Stack auch. Join ist ein
Ausbildungsprojekt der Developer Akademie, und die Technologiewahl gehörte zur
Aufgabenstellung.

Benjamins eigene Einschätzung nach der Arbeit damit: Supabase ist ein sehr gutes
Werkzeug, wenn man kein eigenes Backend bauen will. Man bekommt Datenbank,
Authentifizierung und Ablage als fertigen Dienst und kann sich auf die Anwendung
konzentrieren. Wo es hingegen um eigene Domänenlogik geht, braucht es etwas
anderes. In seinen späteren Projekten übernimmt diese Rolle Django, während
Supabase dort als Infrastruktur darunter liegt.
