import random
from collections import defaultdict
from time import sleep
from typing import Callable, Generator, List

import typer

CLEAR = "\033c"


def fifty_fity_move():
    """50-50 chance to move one character."""
    return 1 if random.random() > 0.5 else 0


def nearly_fifty_fity_move():
    """Nearly 50-50 chance to move one character."""
    threshold = random.gauss(0.5, 0.25)
    return 1 if random.random() > threshold else 0


def progress_generator(
    char: str, progress_strategy: Callable[[], int]
) -> Generator[str, None, None]:
    """Simple random progress strategy."""
    current = 0
    while True:
        current += progress_strategy()
        yield char * current


def add_final_position_suffix(position):
    """Append a suffix to a position, e.g. 1 -> 1st."""
    unit = position[-1]
    if unit == "1":
        return f"{position}st"
    elif unit == "2":
        return f"{position}nd"
    elif unit == "3":
        return f"{position}rd"
    else:
        return f"{position}th"


def race(
    competitors: List[str] = typer.Argument(..., help="Competitors in the race"),
    character: str = typer.Option("\U0001F434"),
    finish_character: str = typer.Option("\U0001F3C1"),
    target_length: int = typer.Option(30),
    update_interval_seconds: float = typer.Option(0.2),
    seed: int = typer.Option(1234),
):
    """Simulate a race in your terminal."""
    random.seed(seed)

    character_length = len(character.encode("utf-8"))
    fudge_factor = 1 if character_length == 1 else int(character_length / 2)
    max_competitor_length = max(len(c) for c in competitors)

    # create generators for the progress of each competitor
    competitor_progresses = {
        competitor: progress_generator(
            character, progress_strategy=nearly_fifty_fity_move
        )
        for competitor in competitors
    }
    final_positions = defaultdict(str)
    next_final_position = 1
    while True:
        print(CLEAR, end="")
        progress_bars = []
        for name, competitor_progress in competitor_progresses.items():
            progress = next(competitor_progress)
            remaining = target_length - len(progress)
            progress_bar = f"{progress}{' ' * fudge_factor * remaining}"

            # deal with a competitor finishing or already finished
            if not remaining and not final_positions[name]:
                final_positions[name] = add_final_position_suffix(
                    str(next_final_position)
                )
                next_final_position += 1
                final_progress_bar = progress_bar
            elif final_positions[name]:
                progress_bar = final_progress_bar

            # e.g. Name |---------->      |🏁
            name_part = name + " " * (max_competitor_length - len(name) + 1)
            progress_bars.append(
                f"{name_part}|{progress_bar}|{finish_character} {final_positions[name]}"
            )

        print("\n".join(progress_bars))

        # check for all competitors finishing
        if all(v for v in final_positions.values()):
            winner = [k for k, v in final_positions.items() if v == "1st"].pop()
            print(f"\n\U0001F3C6{winner} wins!\U0001F3C6")
            break

        sleep(update_interval_seconds)


if __name__ == "__main__":
    typer.run(race)
