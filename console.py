from transit import RouteError, build_sample_line

MENU = """
========= RUTA CIRCULAR DE BUS =========
 1. Ver la ruta
 2. Agregar parada al inicio
 3. Agregar parada al final
 4. Agregar parada después de otra
 5. Eliminar parada
 6. Buscar parada
 7. Recorrer la ruta hacia adelante
 8. Recorrer la ruta hacia atrás
 9. Avanzar el bus una parada
10. Retroceder el bus una parada
 0. Salir
========================================"""


def show_route(line):
    state = line.snapshot()
    if state["size"] == 0:
        print("\nLa ruta está vacía.")
        return
    print(f"\n{state['name']} | {state['size']} paradas | vuelta completa: {state['total_minutes']} min")
    print(f"Vueltas del bus: {state['laps']} | tiempo recorrido: {state['elapsed_minutes']} min\n")
    for stop in state["stops"]:
        marks = []
        if stop["name"] == state["terminal"]:
            marks.append("terminal")
        if stop["name"] == state["bus_at"]["name"]:
            marks.append("🚌 bus aquí")
        label = f"  <- {', '.join(marks)}" if marks else ""
        print(f"  [{stop['stop_behind']}] <- {stop['name']} ({stop['minutes']} min) -> [{stop['stop_ahead']}]{label}")


def ask_minutes():
    return input("Minutos hasta la parada que sigue: ").strip()


def add_stop(line, position):
    reference = None
    if position == "after":
        reference = input("¿Después de qué parada?: ")
    name = input("Nombre de la nueva parada: ")
    stop = line.add_stop(name, ask_minutes(), position, reference)
    print(f"\nParada '{stop.name}' agregada.")


def remove_stop(line):
    stop = line.remove_stop(input("Nombre de la parada a eliminar: "))
    print(f"\nParada '{stop.name}' eliminada.")


def find_stop(line):
    stop = line.find_stop(input("Nombre de la parada a buscar: "))
    print(f"\nEncontrada: {stop.name} ({stop.minutes} min)")
    print(f"  Parada de atrás: {stop.stop_behind.name}")
    print(f"  Parada de adelante: {stop.stop_ahead.name}")


def print_traversal(title, names):
    if not names:
        print("\nLa ruta está vacía.")
        return
    print(f"\n{title}:")
    print("  " + " -> ".join(names + [names[0]]))


def traverse(line, direction):
    state = line.snapshot()
    if direction == "ahead":
        print_traversal("Recorrido hacia adelante desde el bus", state["ahead"])
    else:
        print_traversal("Recorrido hacia atrás desde el bus", state["behind"])


def drive(line, direction):
    stop = line.drive_ahead() if direction == "ahead" else line.drive_behind()
    print(f"\nEl bus llegó a: {stop.name}")


def main():
    line = build_sample_line()
    actions = {
        "1": lambda: show_route(line),
        "2": lambda: add_stop(line, "start"),
        "3": lambda: add_stop(line, "end"),
        "4": lambda: add_stop(line, "after"),
        "5": lambda: remove_stop(line),
        "6": lambda: find_stop(line),
        "7": lambda: traverse(line, "ahead"),
        "8": lambda: traverse(line, "behind"),
        "9": lambda: drive(line, "ahead"),
        "10": lambda: drive(line, "behind"),
    }
    while True:
        print(MENU)
        try:
            option = input("Elige una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if option == "0":
            print("Hasta luego.")
            break
        action = actions.get(option)
        if action is None:
            print("\nOpción no válida, intenta de nuevo.")
            continue
        try:
            action()
        except RouteError as error:
            print(f"\nError: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nOperación cancelada.")


if __name__ == "__main__":
    main()
