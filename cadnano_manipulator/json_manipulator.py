from core.manipulator import Manipulator
import logging
from pathlib import Path
import click
import json
import sys

__version__ = 0.8


def search_input_parse(searchterm):
    searchterm = searchterm.strip()
    if searchterm.find("-") < 0:
        return (searchterm.split(","))
    else:
        boundaries = searchterm.split("-")
        helixlist = str()
        for i in range(int(boundaries[0]), int(boundaries[1])+1):
            helixlist = helixlist+str(i)+","
        return (helixlist[0:len(helixlist)-1].split(","))


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli():
    pass


@cli.command()
@click.argument('cadnano', type=click.Path(exists=True))
@click.option('--merge',  type=click.Path(exists=True), default=None,
              help="merge with a second cadnano design")
@click.option('--shift-row', type=int, default=None,
              help='shift helices by N rows. affected by selection')
@click.option('--shift-col', type=int, default=None,
              help='shift helices by N columns. affected by selection')
@click.option('--shift-pos', type=int, default=None,
              help='shift helices by N base positions. affected by selection')
@click.option('--fix-legacy', is_flag=True,
              help='attempt to fix legacy design for version < 0.7')
@click.option('--remove-skips', is_flag=True,
              help='remove all skips. affected by selection')
@click.option('--remove-loops', is_flag=True,
              help='remove all loops. affected by selection')
@click.option('--helix-subset', default=None,
              help='subset of helices selected by their number. format: "[1,2,3]"')
def main(cadnano, merge, shift_row, shift_col, shift_pos, fix_legacy,
         remove_skips, remove_loops, helix_subset):
    """ manipulate cadnano design files

        CADNANO is the name of the design file [.json]
    """
    logger = logging.getLogger("cli")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    cadnano = Path(cadnano)
    if cadnano.suffix != ".json":
        logger.error(".json file required!")
        raise IOError
    manipulator = Manipulator(cadnano)
    logger.debug(f"Design initialized from file: {cadnano} ")

    mod_str = ""
    if helix_subset is None:
        selection = manipulator.find_helices()
    else:
        try:
            helix_num_selection = json.loads(helix_subset)
        except ValueError:
            logger.error("Helix selection does not match required format.")
            sys.exit(1)

        logger.info(f"Using helix subset: {helix_num_selection}")
        selection = manipulator.find_helices(helix_num_selection)
        select_str = "-".join([str(s) for s in helix_num_selection])
        mod_str += f"_helix-{select_str}"

    if fix_legacy:
        logger.info(
            "Removing empty segments on the right reduces filesize and cadnano2 speed/robustness.")
        logger.info(
            "If no changes are reported by the manipulator your bug is not yet covered.")
        manipulator.fix_legacy()
        mod_str += "_fix_legacy"
    elif merge is not None:
        logger.info(f"Merging {cadnano.name} with {merge}.")
        if any([shift_pos, shift_row, shift_col]):
            logger.warning("Parsed modifications are ignored due to merge.")
        merge = Path(merge)
        manipulator.add_file(merge)
        mod_str += f"_{merge.name}"
    else:
        if shift_pos is not None:
            logger.info(
                f"Shifting selected helices by {shift_pos}  base positions.")
            manipulator.shift_position(selection=selection, shift=shift_pos)
            mod_str += f"_pos{shift_pos}"
        if shift_row is not None:
            logger.info(f"Shifting selected helices by {shift_row} rows.")
            if shift_row % 2:
                logger.warning(
                    "Shifting by odd number of rows: Cadnano2 will not display crossovers!")
            manipulator.shift_helix(selection=selection,
                                    shift=shift_row, direction="row")
            mod_str += f"_row{shift_row}"
        if shift_col is not None:
            logger.info(f"Shifting selected helices by {shift_row} columns.")
            if shift_col % 2:
                logger.warning(
                    "Shifting by odd number of columns: Cadnano2 will not display crossovers!")
            manipulator.shift_helix(selection=selection,
                                    shift=shift_col, direction="col")
            mod_str += f"_col{shift_col}"

        if remove_skips:
            logger.info("Removing all skips in selected helices.")
            manipulator.erase_skips()
            mod_str += "_no-skips"
        if remove_loops:
            logger.info("Removing all loops in selected helices.")
            manipulator.erase_loops()
            mod_str += "_no-loops"

        # TODO: delete helices option

    out_json = cadnano.with_name(f"{cadnano.stem}{mod_str}.json")
    logger.info(f"Writing file {out_json}")
    manipulator.generate_json_file(out_json)


if __name__ == "__main__":
    cli()
