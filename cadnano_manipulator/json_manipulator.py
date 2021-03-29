from core.manipulator import Manipulator
import logging
from pathlib import Path
import click

import ipdb

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
@click.option('--merge-cadnano',  type=click.Path(exists=True), default=None,
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
@click.option('--select-subset', type=int, default=None,
              help='subset of helices NOTIMPLEMENTED YET')
def main(cadnano, merge_cadnano, shift_row, shift_col, shift_pos, fix_legacy,
         remove_skips, remove_loops, select_subset):
    """ manipulate cadnano design files

        CADNANO is the name of the design file [.json]
    """
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    cadnano = Path(cadnano)
    if cadnano.suffix != ".json":
        logger.error(".json file required!")
        raise IOError
    manipulator = Manipulator(cadnano)
    logger.info(f"Design initialized from file: {cadnano} ")

    if select_subset is None:
        selection = manipulator.find_helices("all")
    else:
        raise NotImplementedError

    if fix_legacy:
        manipulator.fix_legacy()
        out_json = cadnano.with_name(f"{cadnano.stem}_fix_legacy.json")
        manipulator.generate_json_file(out_json)
        return
    elif merge_cadnano is not None:
        merge_cadnano = Path(merge_cadnano)
        manipulator.add_file(merge_cadnano)
        out_json = cadnano.with_name(f"{cadnano.stem}_{merge_cadnano.name}")
        manipulator.generate_json_file(out_json)
        return

    mod_str = ""
    if shift_pos is not None:
        manipulator.shift_position(selection=selection, shift=shift_pos)
        mod_str += f"_pos{shift_pos}"
    if shift_row is not None:
        if shift_row % 2:
            logger.warning(
                "Shifting by odd number of rows: Cadnano2 will not display crossovers!")
        manipulator.shift_helix(selection=selection,
                                shift=shift_row, direction="row")
        mod_str += f"_row{shift_row}"
    if shift_col is not None:
        if shift_col % 2:
            logger.warning(
                "Shifting by odd number of columns: Cadnano2 will not display crossovers!")
        manipulator.shift_helix(selection=selection,
                                shift=shift_col, direction="col")
        mod_str += f"_col{shift_col}"
    out_json = cadnano.with_name(f"{cadnano.stem}{mod_str}.json")
    manipulator.generate_json_file(out_json)


if __name__ == "__main__":
    cli()
