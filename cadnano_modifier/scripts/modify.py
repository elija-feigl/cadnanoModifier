#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import sys
from pathlib import Path

import click

from cadnano_modifier.version import get_version
from cadnano_modifier.core.manipulator import Manipulator


logger = logging.getLogger(__name__)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(get_version())
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli():
    pass


@cli.command()
@click.argument('cadnano', type=click.Path(exists=True))
def fix(cadnano):
    """ fix faulty cadnano design files for DNA Origami for:
            legacy cadnano (< 2.)
            json_modifier06.py

            CADNANO is the name of the design file [.json]
    """
    cadnano = Path(cadnano)
    if cadnano.suffix != ".json":
        logger.error(".json file required!")
        raise IOError

    manipulator = Manipulator(cadnano)
    logger.debug(f"Design initialized from file: {cadnano}.")
    logger.info(
        "Removing empty segments on the right reduces filesize and cadnano2 speed/stability.")

    status = manipulator.fix_legacy()
    if status:
        out_json = cadnano.with_name(f"{cadnano.stem}_fix_legacy.json")
        logger.info(f"Writing file {out_json}")
        manipulator.generate_json_file(out_json)
    else:
        logger.info("Nothing to do. (or your bug is not yet covered).")


@cli.command()
@click.argument('cadnano', type=click.Path(exists=True))
@click.argument('merge',  type=click.Path(exists=True))
def merge(cadnano, merge):
    """ merge two cadnano design files for DNA Origami

            CADNANO is the name of the first design file [.json]\n
            MERGE is the name of the second design file [.json]
    """
    cadnano = Path(cadnano)
    merge = Path(merge)

    if cadnano.suffix != ".json" or merge.suffix != ".json":
        logger.error(".json file required!")
        raise IOError

    manipulator = Manipulator(cadnano)
    logger.debug(f"Design initialized from file: {cadnano} ")

    logger.info(f"Merging {cadnano.name} with {merge}.")
    merge = Path(merge)
    manipulator.add_file(merge)

    out_json = cadnano.with_name(f"{cadnano.stem}_{merge.stem}.json")
    logger.info(f"Writing file {out_json}")
    manipulator.generate_json_file(out_json)


@cli.command()
@click.argument('cadnano', type=click.Path(exists=True))
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
def modify(cadnano, shift_row, shift_col, shift_pos, fix_legacy,
           remove_skips, remove_loops, helix_subset):
    """ manipulate cadnano design files for DNA Origami

         CADNANO is the name of the design file [.json]
    """
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
        logger.info(f"Shifting selected helices by {shift_col} columns.")
        if shift_col % 2:
            logger.warning(
                "Shifting by odd number of columns: Cadnano2 will not display crossovers!")
        manipulator.shift_helix(selection=selection,
                                shift=shift_col, direction="col")
        mod_str += f"_col{shift_col}"

    if remove_skips:
        logger.info("Removing all skips in selected helices.")
        manipulator.erase_skips(selection=selection)
        mod_str += "_no-skips"

    if remove_loops:
        logger.info("Removing all loops in selected helices.")
        manipulator.erase_loops(selection=selection)
        mod_str += "_no-loops"

    # TODO: delete_helices option

    if mod_str == "":
        logger.warning("Nothing to do.")
    else:
        out_json = cadnano.with_name(f"{cadnano.stem}{mod_str}.json")
        logger.info(f"Writing file {out_json}")
        manipulator.generate_json_file(out_json)
